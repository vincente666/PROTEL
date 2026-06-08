/* C function called from PROTEL via EXTERNAL (examples/interop reference). */
#include <stdint.h>
#include <stdio.h>

void c_greet(const char* name, int16_t value)
{
    if (name == NULL) {
        name = "";
    }
    printf("C: c_greet(name=%s, value=%d)\n", name, (int)value);
}