# Test Plan

Tests are planned; none are marked as passed until run against the modified xv6 kernel.

| ID | Test | Expected behavior |
|---|---|---|
| T01 | Begin speculation | `xbegin()` returns success and establishes context. |
| T02 | Write then read inside speculation | Reader sees tentative contents. |
| T03 | Outside read during speculation | Reader sees original contents. |
| T04 | Abort a write | Real file remains unchanged. |
| T05 | Commit a write | New contents become visible after commit. |
| T06 | Create then abort | New file does not become visible outside. |
| T07 | Delete then abort | Original file remains visible outside. |
| T08 | Create/delete then commit | Committed namespace changes become visible. |
| T09 | Fork during speculation | Child inherits the same context. |
| T10 | Console output + abort | Buffered output is discarded. |
| T11 | Console output + commit | Output is released after successful filesystem commit. |
| T12 | Pipe inside speculation | Internal communication still works. |
| T13 | Pipe to outside reader | Uncommitted output is withheld. |
| T14 | Shadow exhaustion | Write fails safely; real data is unchanged. |
| T15 | Outside write conflict | Documented conflict policy is enforced. |
| T16 | Nested begin | Defined behavior; no state corruption. |
| T17 | Commit crash/recovery | Filesystem consistency is investigated and documented. |
| T18 | Process exits while speculative | Resources are cleaned up safely. |

## Performance experiment
Measure ordinary and speculative write cost for 1, 2, 4, 8, 16, 32, and 64 KB files (or the exact instructor-required series). Record QEMU configuration, repetitions, measurement method, result, success/failure, and raw log path. Generate graphs from measured data only; do not fabricate values.

Suggested evidence layout:
```text
evidence/
  qemu/
  gdb/
  benchmarks/
    raw/
    results.csv
    write-cost.png
```
