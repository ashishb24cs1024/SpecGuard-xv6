# SpecGuard — Externalization Barriers for Speculative Processes

**Platform:** xv6-riscv in QEMU  
**Status:** Design/test scaffold plus an LLM-backed host-agent prototype. The kernel implementation is not complete.

## Goal
Add speculative filesystem operations to xv6 so a process can make tentative changes and then commit or abort them. During speculation, the process should see its own tentative changes while outside processes continue to see the original filesystem.

Planned system-call interface:
- `xbegin()` — start speculation
- `xcommit()` — commit changes
- `xabort()` — discard changes

## Repository contents
- `agent.py` — Python agent using the OpenAI Responses API and function calling; it validates tool arguments and runs approved operations through the QEMU serial bridge.
- `requirements.txt` — Python dependency.
- `.env.example` — environment-variable names (no secret key).
- `docs/agent-integration.md` — agent architecture, setup, security notes, and limitations.
- `docs/design.md` — shadow-block architecture and filesystem invariants.
- `docs/testing.md` — planned test matrix and benchmarking guidance.
- `docs/implementation-checklist.md` — implementation roadmap.
- `user/specguard_test.c` — starter test skeleton (not yet integrated into xv6 build).

## Run the agent
```sh
python3 -m pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
python3 agent.py --xv6-dir ~/xv6-riscv --target qemu
```
The model defaults to `gpt-6-luna`; set `OPENAI_MODEL` or use `--model` to select a model available to your API project. API usage may incur charges. Never commit your API key.

## Current agent capabilities
- LLM-based natural-language planning with function/tool calling.
- `list_files`, `read_file`, and human-confirmed `delete_file` tools.
- Iterative observation loop: tool results are sent back to the model so it can choose subsequent actions.
- Simple filename validation and an explicit confirmation gate for destructive actions.

## Not implemented yet
- Kernel system calls or syscall registration
- Shadow-block read/write routing
- Atomic commit through xv6 filesystem logging
- Abort cleanup, output buffering, conflict handling
- Agent-to-SpecGuard transaction integration
- Create/write tools and end-to-end test results
- QEMU results, benchmarks, GDB evidence

The agent is an application-layer prototype, not a kernel security boundary. The LLM does not get arbitrary shell access. File contents are treated as untrusted input, but prompt instructions alone are not a security guarantee. Delete requires a host-side confirmation.

## Design overview
1. Associate speculative processes with a speculation ID; children inherit the context.
2. Store tentative block contents in bounded shadow storage.
3. Speculative reads see their shadow copy; outside processes see real blocks.
4. Shadow exhaustion must fail safely—never write speculative data directly to disk as a fallback.
5. Commit applies shadow changes through the filesystem log transaction, respecting transaction limits.
6. Abort discards shadows and buffered external output.
7. Console output and pipe writes to outside readers are withheld until commit; same-speculation pipe communication must keep working.
8. Define and test a conflict policy for blocks changed both inside and outside speculation.

## Implementation order
1. Verify the course xv6-riscv revision and baseline build.
2. Implement syscall plumbing and process speculation state.
3. Implement shadow storage, read/write routing, commit, and abort.
4. Handle process inheritance and external effects.
5. Integrate agent operations with the transaction interface.
6. Test correctness and collect measured QEMU/GDB/benchmark evidence.
