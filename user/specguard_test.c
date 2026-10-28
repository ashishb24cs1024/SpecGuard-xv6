/*
 * SpecGuard user-space test skeleton.
 * Not included in the stock xv6 build yet. It will compile only after
 * xbegin(), xcommit(), and xabort() are registered and user stubs exist.
 */
#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"

int
main(void)
{
  printf("SpecGuard test skeleton: kernel system calls are not implemented yet.\n");

  /*
   * Planned tests:
   * 1. xbegin(); write a test file; xabort(); verify original contents.
   * 2. xbegin(); write a test file; xcommit(); verify new contents.
   * 3. Read the file from a non-speculative process while speculation is active.
   * 4. Repeat with file creation/deletion and a child created by fork().
   *
   * Add error checks and filesystem setup once integrated with the course tree.
   */
  exit(0);
}
