#!/usr/bin/env bash
set -euo pipefail
version=7.2.13
commit=3c172eede0d6b889ead876f45cc843070209208f
out="$(cd "$(dirname "$0")" && pwd)/out"
mkdir -p "$out"
echo "Build helper pinned to Linux $version ($commit)."
echo "Fetch https://cdn.kernel.org/pub/linux/kernel/v7.x/linux-$version.tar.xz, verify its kernel.org signature,"
echo "then build with linux/kernel.config. The released course image is produced by the protected release pipeline."

