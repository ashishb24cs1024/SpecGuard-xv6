# Implementation Checklist

## Baseline
- [ ] Identify course xv6-riscv revision.
- [ ] Build and boot unmodified xv6; save logs.
- [ ] Inspect course skeleton and actual function prototypes.

## System calls
- [ ] Add syscall numbers, handlers, user declarations and stubs.
- [ ] Add process speculation state.
- [ ] Propagate context through `fork()`.
- [ ] Build and test syscall return paths.

## Shadow blocks
- [ ] Implement shadow table, locking, lookup, allocation and cleanup.
- [ ] Route speculative reads and writes.
- [ ] Test read-your-writes and outside isolation.
- [ ] Test exhaustion; ensure no real-disk fallback.

## Commit/abort and external effects
- [ ] Abort frees shadows without changing real blocks.
- [ ] Commit uses filesystem log and respects capacity.
- [ ] Buffer console output until commit.
- [ ] Handle pipe writes to outside readers and internal pipes.
- [ ] Test create/delete, process exit, and error paths.

## Evaluation
- [ ] Choose and implement conflict policy.
- [ ] Test nested begin and shadow exhaustion.
- [ ] Investigate crash/recovery behavior.
- [ ] Capture QEMU logs and a real GDB bug-fix session.
- [ ] Measure write cost inside/outside speculation for 1–64 KB.
- [ ] Generate graph from raw measurements.
- [ ] Maintain regular design-journal commits.
- [ ] Prepare submission ZIP and two-page handwritten report.
