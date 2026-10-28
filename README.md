# Efficient Memory Allocator Project

Public starter workspace for the EmbeddedVille Premium/VIP capstone. You will
build a single-threaded, variable-size allocator over a caller-owned 64 KiB
arena and collect evidence from the pinned Linux 7.2.13 allocation path.

Start with:

```sh
./project doctor
./project baseline
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

