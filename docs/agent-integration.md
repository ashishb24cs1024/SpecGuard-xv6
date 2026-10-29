# Host-Side Agent and QEMU Bridge

## Purpose
`agent.py` is an application-layer teaching prototype. It launches xv6 under QEMU, sends commands through the guest shell's serial console, and demonstrates a small tool registry plus a scripted prompt-injection scenario.

## Components
- `XV6Bridge`: starts the configured Make target and reads/writes the QEMU process streams.
- `TOOLS` and `validate_action()`: define allowed tool names, validate argument shapes and simple flat filenames, and require confirmation for destructive actions.
- `RulePlanner`: deterministic interactive planner for listing and reading files.
- `InjectedPlanner`: scripted demonstration that reacts to the word `delete` in observed file content.
- `Agent`: loops through planner proposals, validates them, executes tools, and records observations.

## Running
From a host terminal, point the script at the course xv6 tree:

```sh
python3 agent.py --xv6-dir ~/xv6-riscv --target qemu
python3 agent.py --xv6-dir ~/xv6-riscv --target qemu --demo-injection
```

Check the actual Makefile first. The default target in the script is `qemu-nox`, which may not match the course xv6-riscv repository. The bridge also assumes a shell prompt ending in `$ ` and a serial console attached to the child process. These assumptions have not been verified in the target course environment.

For the injection demo, `inbox.txt` must exist in the guest root filesystem and contain the word `delete` to trigger the scripted branch.

## Important limitations
- This is not a real LLM-backed agent; the planners are deterministic demonstrations.
- The current `summarize <path>` route reads the file but does not pass the contents through the summarize tool.
- The path check is a simple filename filter for a flat directory, not a general filesystem authorization mechanism.
- `--allow-delete` allows the Python tool layer to run `rm`; no independent kernel-level security mechanism is implemented here. Do not claim that the kernel blocks the approved deletion.
- The current agent does not call SpecGuard's planned `xbegin()`, `xcommit()`, or `xabort()` syscalls. Those syscalls and kernel features are not implemented in this repository yet.
- QEMU compatibility and end-to-end behavior have not been tested against the course's exact xv6 source tree.

## Relationship to SpecGuard
The agent is a separate host-side demonstration. A future integration could wrap approved filesystem work in the SpecGuard transaction interface, but only after the kernel syscalls and speculative filesystem semantics are implemented and tested. Prompt-injection defense and filesystem transaction isolation are distinct security properties.
