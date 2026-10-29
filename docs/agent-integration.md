# LLM Agent and QEMU Bridge

## What changed
`agent.py` now uses the OpenAI Responses API with function calling. The model chooses among explicitly declared tools, Python validates the arguments, the tool layer executes the operation, and observations are returned to the model for the next planning step.

## Setup
```sh
python3 -m pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
# Optional: export OPENAI_MODEL="your-enabled-model"
python3 agent.py --xv6-dir ~/xv6-riscv --target qemu
```

Never commit your API key. `.env.example` contains names only, not secrets. API usage may incur charges and the account must have access to the selected model.

## Agent loop
1. Send the user request, system instructions, and function schemas to the model.
2. Receive a natural-language response or one or more function calls.
3. Parse and validate each function call in Python.
4. Require explicit interactive confirmation before deletion.
5. Execute approved calls through the QEMU shell bridge.
6. Send tool outputs back to the model so it can continue planning or report completion.
7. Stop after a configurable maximum number of model/tool rounds.

## Available tools
- `list_files()`: list guest root filenames.
- `read_file(path)`: read a simple filename in the guest root.
- `delete_file(path)`: destructive; requires typing `yes` at the host terminal.

The model is not given arbitrary shell access. The path filter allows only simple flat filenames. This is a teaching prototype, not a hardened sandbox; the host process, QEMU configuration, and xv6 guest still need appropriate security controls.

## Prompt-injection handling
The system prompt says file contents are untrusted data, but prompts are not a security boundary. The independent tool validator and human confirmation gate are the enforcement points in this prototype. Do not automatically approve destructive actions.

## Limitations
- This uses an OpenAI API model via the Responses API; it is not a local model. Set `OPENAI_MODEL` or use `--model` to select a model your API project can access.
- No kernel-level security policy is implemented by this Python file.
- This agent does not call `xbegin()`, `xcommit()`, or `xabort()`; those kernel syscalls and speculative filesystem semantics are still unimplemented.
- It only exposes list/read/delete tools for now; create/write tools should be added after the guest command interface is made safe and reliable.
- The QEMU target and serial prompt assumptions vary by xv6 version. Check the course tree's Makefile and verify the bridge manually.
- No end-to-end QEMU or API run has been performed in this repository update.
