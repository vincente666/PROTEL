/* JNI bridge: JavaCallsProtel.protelAdd -> EXPORTed protel_add (C ABI). */
#include <jni.h>
#include <stdint.h>

extern int16_t protel_add(int16_t a, int16_t b);

JNIEXPORT jshort JNICALL
Java_JavaCallsProtel_protelAdd(JNIEnv *env, jclass clazz, jshort a, jshort b)
{
    (void)env;
    (void)clazz;
    return (jshort)protel_add(a, b);
}