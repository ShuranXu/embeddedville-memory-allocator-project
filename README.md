# Efficient Memory Allocator Project

Public starter workspace for the EmbeddedVille Premium/VIP capstone. You will
build a single-threaded, variable-size allocator over a caller-owned 64 KiB
arena and collect evidence from the pinned Linux 7.2.13 allocation path.

Start with:

```sh
./project doctor
./project baseline
./project linux-observe
./project build
./project test
```

The assessed implementation is `src/allocator.c`. It must not call `malloc`,
`calloc`, `realloc`, or `free`. The guided tutorial, hidden traces, evaluator,
solutions, and completion credential are hosted on EmbeddedVille and are not
part of this public repository.

Kernel observation is read-only and uses a GPL-2.0-only helper module. The
course and QEMU helper scripts are pinned to Linux 7.2.13 commit
`3c172eede0d6b889ead876f45cc843070209208f`.
The released `linux/out` image boots without a network device and writes
`slabinfo`, buddy-order, and tracefs evidence into `evidence/`.

`./project linux-observe` also derives four beginner-readable views without
changing the raw captures: `kmalloc-request-table.csv`, `kmem-timeline.txt`,
`buddy-orders.csv`, and `linux-observation-summary.json`. The summary records
the Linux identity and SHA-256 digest of every raw input. Re-running the
command replaces only these generated observation files; it never changes
`src/allocator.c` or an allocator report you have started editing.

If you already have a Codespace from `memory-allocator-project-v1.0.0`, commit
or export your work before changing versions. Then merge or copy only the
updated `tools/project.py` helper into your existing workspace, or create a
fresh Codespace from `memory-allocator-project-v1.1.0` and bring your
learner-owned `src/allocator.c` and `evidence/allocator-report.json` forward.

