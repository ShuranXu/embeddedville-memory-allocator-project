#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 /path/to/linux-7.2.13" >&2
  exit 2
fi

source_dir="$(realpath "$1")"
linux_dir="$(cd "$(dirname "$0")" && pwd)"
rootfs="${TMPDIR:-/tmp}/embeddedville-memory-allocator-rootfs"
out="$linux_dir/out"

mkdir -p "$out"
test "$(make -s -C "$source_dir" kernelversion)" = "7.2.13"
cc -O2 -static -Wall -Wextra "$source_dir/tools/mm/slabinfo.c" -o "$out/slabinfo"
rm -rf "$rootfs"
mkdir -p "$rootfs"/{bin,proc,sys,dev,tmp,opt/ev,evidence}
cp "$(command -v busybox)" "$rootfs/bin/busybox"
for applet in sh mount mkdir cat grep dmesg insmod rmmod poweroff sleep uname sync; do
  ln -s busybox "$rootfs/bin/$applet"
done
cp "$linux_dir/init" "$rootfs/init"
cp "$linux_dir/observe.sh" "$linux_dir/ev_kmalloc_probe.ko" "$out/slabinfo" "$rootfs/opt/ev/"
chmod +x "$rootfs/init" "$rootfs/opt/ev/observe.sh"
(cd "$rootfs" && find . -print0 | cpio --null --create --verbose --format=newc | gzip -9 > "$out/initramfs.cpio.gz")
cp "$source_dir/arch/x86/boot/bzImage" "$out/bzImage"
cp "$source_dir/.config" "$out/kernel.config"
(cd "$out" && sha256sum bzImage initramfs.cpio.gz kernel.config slabinfo > SHA256SUMS)
ls -lh "$out"
