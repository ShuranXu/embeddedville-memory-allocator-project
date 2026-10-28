#!/usr/bin/env sh
set -eu
test "$(uname -r)" = "7.2.13" || { echo "expected Linux 7.2.13 guest" >&2; exit 2; }
mountpoint -q /sys/kernel/tracing || mount -t tracefs tracefs /sys/kernel/tracing
trace=/sys/kernel/tracing
echo 0 > "$trace/tracing_on"; : > "$trace/trace"
for event in kmalloc kfree mm_page_alloc mm_page_free; do echo 1 > "$trace/events/kmem/$event/enable"; done
echo 1 > "$trace/tracing_on"; insmod /opt/ev/ev_kmalloc_probe.ko; rmmod ev_kmalloc_probe; echo 0 > "$trace/tracing_on"
cat /proc/slabinfo > /evidence/slabinfo.txt; cat /proc/buddyinfo > /evidence/buddyinfo.txt; cat "$trace/trace" > /evidence/kmem-trace.txt

