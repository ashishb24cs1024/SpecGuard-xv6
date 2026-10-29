# SpecGuard — Externalization Barriers for Speculative Processes

**Platform:** xv6-riscv in QEMU  
**Status:** Design/test scaffold plus host-side agent prototype. The kernel implementation is not complete.

## Goal
Add speculative filesystem operations to xv6 so a process can make tentative changes and then commit or abort them. During speculation, the process should see its own tentative changes while outside processes continue to see the original filesystem.

Planned system-call interface:
- `xbegin()` — start speculation
- `xcommit()` — commit changes
- `xabort()` — discard changes

## Repository contents
- `agent.py` — host-side Python agent/tool-dispatch prototype that communicates with xv6 through QEMU's serial shell.
- `docs/agent-integration.md` — agent architecture, run instructions, caveats, and planned integration.
- `docs/design.md` — shadow-block architecture and filesystem invariants.
- `docs/testing.md` — planned test matrix and benchmarking guidance.
- `docs/implementation-checklist.md` — implementation roadmap.
- `user/specguard_test.c` — starter test skeleton (not yet integrated into the xv6 build).

## Agent prototype
The current agent uses deterministic planners rather than a real LLM. It demonstrates a small tool registry, basic input validation, human confirmation for deletion, and a scripted prompt-injection scenario. It does not yet call `xbegin()`, `xcommit()`, or `xabort()`, and it does not implement an independent kernel-level defense against an approved delete. See [docs/agent-integration.md](docs/agent-integration.md).

## Not implemented yet
- Kernel system calls or syscall registration
- Shadow-block read/write routing
- Atomic commit through xv6 filesystem logging
- Abort cleanup, output buffering, conflict handling
- Agent-to-SpecGuard transaction integration
- QEMU results, benchmarks, GDB evidence

Do not claim these features work until implemented and tested against the exact course xv6-riscv tree.

## Design overview
1. Associate speculative processes with a speculation ID; children inherit the context.
2. Store tentative block contents in bounded shadow storage.
3. Speculative reads see their shadow copy; outside processes see real blocks.
4. Shadow exhaustion must fail safely—never write speculative data directly to disk as a fallback.
5. Commit applies shadow changes through the filesystem log transaction, respecting transaction limits.
6. Abort discards shadows and buffered external output.
7. Console output and pipe writes to outside readers are withheld until commit; same-speculation pipe communication must keep working.
8. Define and test a conflict policy for blocks changed both inside and outside speculation.

## Build baseline
Use the course-provided xv6-riscv source tree. First verify the unmodified baseline:

```sh
make qemu
```

Exit QEMU with `Ctrl-A`, then `X`. This scaffold is not a replacement for the course source tree. `user/specguard_test.c` will not compile until the system calls are implemented and added to the user/kernel syscall interface.

## Planned implementation order
1. Verify baseline and course revision.
2. Add syscall plumbing and process speculation state.
3. Implement shadow allocation/lookup and read/write routing.
4. Implement commit and abort.
5. Handle console/pipe output and process inheritance.
6. Add conflict/capacity handling and correctness tests.
7. Connect the agent to the implemented transaction interface.
8. Collect QEMU logs, benchmarks, and GDB evidence.
9. Prepare submission ZIP and required two-page handwritten report.

## Evaluation evidence
Measure write cost inside and outside speculation for 1 KB–64 KB files, including shadow-table exhaustion. Keep raw QEMU logs and produce graphs only from measured data. Retain a GDB session log showing a real bug found and fixed, and make small Git commits with design-journal notes regularly.
