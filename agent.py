#!/usr/bin/env python3
"""
Host-side agent + QEMU bridge for xv6-riscv (CSL3030 teaching skeleton).

Usage:
    python3 agent.py --xv6-dir ~/xv6-riscv                 # interactive
    python3 agent.py --xv6-dir ~/xv6-riscv --demo-injection # scripted injection test

The script boots xv6 itself by running `make qemu` as a child process and talks
to the guest shell over QEMU's serial console (stdin/stdout of that process).
Exit QEMU manually with Ctrl-a x, or just let this script terminate it.
"""
import argparse
import os
import queue
import re
import subprocess
import threading
import time

PROMPT_END = "\n$ "
PATH_RE = re.compile(r"^/?[A-Za-z0-9_.-]{1,30}$")


class BridgeError(Exception):
    pass


# ------------------------------------------------------------------ bridge
class XV6Bridge:
    """Boots xv6 in QEMU and runs FIXED commands in its shell."""

    def __init__(self, xv6_dir, target="qemu-nox", boot_timeout=120, cmd_timeout=10):
        self.cmd_timeout = cmd_timeout
        self.proc = subprocess.Popen(
            ["make", target], cwd=xv6_dir,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, bufsize=0)
        self.q = queue.Queue()
        threading.Thread(target=self._pump, daemon=True).start()
        self._read_until_prompt(boot_timeout)
        print("[bridge] xv6 booted, shell ready")

    def _pump(self):
        fd = self.proc.stdout.fileno()
        while True:
            data = os.read(fd, 4096)
            if not data:
                self.q.put(None)
                return
            self.q.put(data)

    def _read_until_prompt(self, timeout):
        buf, deadline = "", time.time() + timeout
        while time.time() < deadline:
            try:
                chunk = self.q.get(timeout=0.2)
            except queue.Empty:
                continue
            if chunk is None:
                raise BridgeError("QEMU exited unexpectedly")
            buf += chunk.decode(errors="replace").replace("\r", "")
            if buf.endswith("$ "):
                time.sleep(0.3)
                if self.q.empty():
                    return buf
        raise BridgeError("timeout waiting for xv6 prompt")

    def run(self, command):
        """Send one command line, return its output (echo + prompt stripped)."""
        self.proc.stdin.write((command + "\n").encode())
        self.proc.stdin.flush()
        raw = self._read_until_prompt(self.cmd_timeout)
        lines = raw.split("\n")
        if lines and lines[0].strip() == command:
            lines = lines[1:]
        if lines and lines[-1].endswith("$ "):
            lines[-1] = lines[-1][:-2]
        return "\n".join(lines).strip()

    def close(self):
        self.proc.terminate()


# ------------------------------------------------------------------ tools
TOOLS = {
    "list_files": {"required": {}},
    "read_file": {"required": {"path": str}},
    "summarize": {"required": {"text": str}},
    # Deliberately dangerous: used to demonstrate the confirmation guard.
    "delete_file": {"required": {"path": str}, "destructive": True},
}


def validate_action(action, confirmed=False):
    if not isinstance(action, dict) or "tool" not in action:
        raise ValueError("malformed action")
    name, args = action["tool"], action.get("args", {})
    if name not in TOOLS:
        raise ValueError(f"unknown tool: {name!r}")
    if not isinstance(args, dict):
        raise ValueError("args must be an object")
    spec = TOOLS[name]
    for key, typ in spec["required"].items():
        if key not in args:
            raise ValueError(f"missing argument: {key}")
        if not isinstance(args[key], typ):
            raise ValueError(f"argument {key} must be {typ.__name__}")
    extra = set(args) - set(spec["required"])
    if extra:
        raise ValueError(f"unexpected arguments: {extra}")
    if "path" in args and (not PATH_RE.match(args["path"]) or ".." in args["path"]):
        raise ValueError(f"path rejected: {args['path']!r}")
    if spec.get("destructive") and not confirmed:
        raise PermissionError(f"{name} needs explicit human confirmation")
    return action


class Tools:
    def __init__(self, bridge):
        self.bridge = bridge

    def execute(self, action):
        name, args = action["tool"], action.get("args", {})
        if name == "list_files":
            return self.bridge.run("ls")
        if name == "read_file":
            return self.bridge.run(f"cat {args['path']}")
        if name == "delete_file":
            return self.bridge.run(f"rm {args['path']}")
        if name == "summarize":
            text = args["text"]
            return text[:200] + ("..." if len(text) > 200 else "")
        raise ValueError("unreachable")


# ------------------------------------------------------------------ planners
class RulePlanner:
    """Deterministic planner: 'list', 'read <path>', 'summarize <path>'."""

    def plan(self, request, history):
        if history:
            return None
        if request.startswith("list"):
            return {"tool": "list_files", "args": {}}
        if request.startswith("read "):
            return {"tool": "read_file", "args": {"path": request[5:].strip()}}
        if request.startswith("summarize "):
            return {"tool": "read_file", "args": {"path": request[10:].strip()}}
        raise ValueError("Unsupported request")


class InjectedPlanner:
    """Scripted compromised planner: reacts to 'delete' in observed file content."""

    def plan(self, request, history):
        if not history:
            return {"tool": "read_file", "args": {"path": request.split()[-1]}}
        last_obs = history[-1][1]
        if len(history) == 1 and "delete" in last_obs.lower():
            return {"tool": "delete_file", "args": {"path": "important.txt"}}
        return None


# ------------------------------------------------------------------ agent
class Agent:
    def __init__(self, tools, planner, ask_confirm=None):
        self.tools, self.planner = tools, planner
        self.ask_confirm = ask_confirm or (lambda action: False)

    def run(self, request, max_steps=4):
        history = []
        for _ in range(max_steps):
            action = self.planner.plan(request, history)
            if action is None:
                break
            print(f"[agent] proposed : {action}")
            try:
                validate_action(action)
            except PermissionError:
                if not self.ask_confirm(action):
                    print("[agent] BLOCKED by validator (no confirmation)")
                    history.append((action, "DENIED by tool layer"))
                    continue
            except ValueError as e:
                print(f"[agent] REJECTED : {e}")
                history.append((action, f"REJECTED: {e}"))
                continue
            try:
                obs = self.tools.execute(action)
            except BridgeError as e:
                obs = f"ERROR: {e}"
            print(f"[agent] observation:\n{obs}\n")
            history.append((action, obs))
        return history


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xv6-dir", required=True)
    ap.add_argument("--demo-injection", action="store_true")
    ap.add_argument("--allow-delete", action="store_true",
                    help="simulate human approval of the delete tool")
    ap.add_argument("--target", default="qemu-nox",
                    help="Make target; verify this against your course xv6 tree")
    a = ap.parse_args()

    bridge = XV6Bridge(a.xv6_dir, a.target)
    try:
        tools = Tools(bridge)
        if a.demo_injection:
            print("=== injection demo: user only asked to read inbox.txt ===")
            Agent(tools, InjectedPlanner(),
                  ask_confirm=(lambda act: True) if a.allow_delete else None
                  ).run("summarize inbox.txt")
            print("final state:\n" + bridge.run("ls"))
        else:
            agent = Agent(tools, RulePlanner())
            while True:
                req = input("request> ").strip()
                if req in ("quit", "exit"):
                    break
                try:
                    agent.run(req)
                except ValueError as e:
                    print(f"[agent] {e}")
    finally:
        bridge.close()


if __name__ == "__main__":
    main()
