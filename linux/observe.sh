#!/bin/sh
set -eu
test "$(uname -r)" = "7.2.13" || { echo "expected Linux 7.2.13 guest" >&2; exit 2; }
grep -qs ' /sys/kernel/tracing ' /proc/mounts || mount -t tracefs tracefs /sys/kernel/tracing
trace=/sys/kernel/tracing
echo 0 > "$trace/tracing_on"; : > "$trace/trace"
for event in kmalloc kfree mm_page_alloc mm_page_free; do echo 1 > "$trace/events/kmem/$event/enable"; done
echo 1 > "$trace/tracing_on"; insmod /opt/ev/ev_kmalloc_probe.ko; rmmod ev_kmalloc_probe; echo 0 > "$trace/tracing_on"
cat /proc/slabinfo > /evidence/slabinfo.txt; cat /proc/buddyinfo > /evidence/buddyinfo.txt; cat "$trace/trace" > /evidence/kmem-trace.txt
/opt/ev/slabinfo -X > /evidence/slabinfo-extended.txt 2>&1 || true
sync
for file in slabinfo.txt buddyinfo.txt kmem-trace.txt slabinfo-extended.txt; do
  echo "EV_EVIDENCE_BEGIN:$file"
  cat "/evidence/$file"
  echo "EV_EVIDENCE_END:$file"
done

