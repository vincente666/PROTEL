/* Minimal PROTEL 2026 I/O runtime: POSIX write(2) only, no iostream. */
#include <stddef.h>
#include <unistd.h>

#include "protel_io.h"

static void write_cstr(const char* s)
{
    size_t n = 0;
    while (s[n] != '\0') {
        n++;
    }
    if (n > 0) {
        (void)write(1, s, n);
    }
}

void writeln(const char* msg)
{
    if (msg == NULL) {
        msg = "";
    }
    write_cstr(msg);
    {
        const char nl = '\n';
        (void)write(1, &nl, 1);
    }
}