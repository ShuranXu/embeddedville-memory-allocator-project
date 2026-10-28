#!/usr/bin/env bash
set -euo pipefail

version=7.2.13
commit=3c172eede0d6b889ead876f45cc843070209208f
archive_sha256=08e7b0c4f2dd1971f972da274b5e589a98989390ac56acd7a1a5af922363ea6c
linux_dir="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$linux_dir/.." && pwd)"
work="$linux_dir/work"
source="$work/linux-$version"
rootfs="$work/rootfs"
out="$linux_dir/out"
archive="$work/linux-$version.tar.xz"

mkdir -p "$work" "$out"
if [[ ! -f "$archive" ]]; then
  curl --fail --location --output "$archive" "https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-$version.tar.xz"
fi
printf '%s  %s\n' "$archive_sha256" "$archive" | sha256sum --check --status
if [[ ! -d "$source" ]]; then
  tar -C "$work" -xf "$archive"
fi

make -C "$source" defconfig
scripts_config="$source/scripts/config"
for option in MODULES KALLSYMS KPROBES FTRACE TRACING TRACEPOINTS SLUB SLUB_DEBUG DEBUG_FS PROC_FS DEVTMPFS DEVTMPFS_MOUNT SERIAL_8250 SERIAL_8250_CONSOLE VIRTIO_PCI NET_9P NET_9P_VIRTIO 9P_FS; do
  "$scripts_config" --file "$source/.config" --enable "$option"
done
"$scripts_config" --file "$source/.config" --set-str SYSTEM_TRUSTED_KEYS ""
"$scripts_config" --file "$source/.config" --set-str SYSTEM_REVOCATION_KEYS ""
make -C "$source" olddefconfig
make -C "$source" -j"$(nproc)" bzImage modules
make -C "$source" M="$linux_dir" modules
cc -O2 -static -Wall -Wextra "$source/tools/mm/slabinfo.c" -o "$out/slabinfo"

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
cp "$source/arch/x86/boot/bzImage" "$out/bzImage"
cp "$source/.config" "$out/kernel.config"
(cd "$out" && sha256sum bzImage initramfs.cpio.gz kernel.config slabinfo > SHA256SUMS)
printf 'Built Linux %s (%s) QEMU artifacts in %s\n' "$version" "$commit" "$out"

