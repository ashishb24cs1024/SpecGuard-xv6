# Design Notes

## Required invariants
- Outside processes must not observe uncommitted speculative block contents.
- A speculative process must see its own tentative writes.
- Shadow-table exhaustion must fail safely; no direct-to-disk fallback.
- Abort must discard shadow state and buffered external output.
- Commit must finish the filesystem log transaction before releasing buffered output.
- Child processes created during speculation share the same context.
- Conflicts must follow a documented, tested policy.

## Proposed shadow storage
A bounded table stores `(speculation_id, block_number, block_data)` entries. The exact size and lock strategy must be checked against the course xv6 revision.

The block access path must route speculative reads to an existing shadow entry and speculative writes to shadow storage. Inspect the provided buffer-cache and filesystem-log code before choosing the exact interception point; modifying `bread()` alone may not cover every write path.

## Commit and abort
Commit should apply changes through the required filesystem log transaction. Respect xv6 log capacity; do not claim atomicity if changes are split across transactions. Abort frees the speculation's shadow entries without changing real blocks.

## External effects
Buffer console output until commit. Delay pipe writes when the reader is outside the speculation, but preserve communication within the same speculation. Define safe buffer-overflow behavior.

## Conflict policy — pending
Choose and implement one policy: abort on conflict, overwrite outside changes, or track block versions/read sets. No policy is claimed implemented yet.

## Failure cases to review
- Nested `xbegin()`
- Process exit during speculation
- Shadow exhaustion
- Commit failure/crash recovery
- Lock-order inversions
- Concurrent child processes sharing one speculation
- Filesystem transaction-size limits

## Likely files
`kernel/proc.h`, `kernel/proc.c`, `kernel/bio.c`, `kernel/log.c`, `kernel/fs.c`, `kernel/file.c`, `kernel/pipe.c`, `kernel/console.c`, `kernel/sysproc.c`, `kernel/syscall.c`, `kernel/syscall.h`, `kernel/defs.h`, `user/user.h`, `user/usys.pl`, and `Makefile`. Exact changes depend on the course tree.
