/* C ABI entry point: embeds the JVM and calls GreetHelper.greet (PROTEL EXTERNAL). */
#include <jni.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static JavaVM *jvm;
static int jvm_ready;

static JNIEnv *attach_env(void)
{
    JNIEnv *env = NULL;

    if (jvm == NULL) {
        return NULL;
    }
    if ((*jvm)->GetEnv(jvm, (void **)&env, JNI_VERSION_10) == JNI_EDETACHED) {
        (*jvm)->AttachCurrentThread(jvm, (void **)&env, NULL);
    }
    return env;
}

static void ensure_jvm(void)
{
    JavaVMInitArgs vm_args;
    JavaVMOption options[1];
    char classpath[1024];
    const char *root;
    JNIEnv *env;

    if (jvm_ready) {
        return;
    }

    root = getenv("PROTEL_ROOT");
    if (root == NULL || root[0] == '\0') {
        root = ".";
    }
    snprintf(classpath, sizeof(classpath), "-Djava.class.path=%s/examples/interop", root);
    options[0].optionString = classpath;
    vm_args.version = JNI_VERSION_10;
    vm_args.nOptions = 1;
    vm_args.options = options;
    vm_args.ignoreUnrecognized = JNI_TRUE;

    if (JNI_CreateJavaVM(&jvm, (void **)&env, &vm_args) != 0) {
        fprintf(stderr, "java_greet: JNI_CreateJavaVM failed\n");
        return;
    }
    jvm_ready = 1;
}

void java_greet(const char *name, int16_t value)
{
    JNIEnv *env;
    jclass cls;
    jmethodID mid;
    jstring jname;

    ensure_jvm();
    env = attach_env();
    if (env == NULL) {
        return;
    }

    cls = (*env)->FindClass(env, "GreetHelper");
    if (cls == NULL) {
        (*env)->ExceptionDescribe(env);
        return;
    }

    mid = (*env)->GetStaticMethodID(env, cls, "greet", "(Ljava/lang/String;S)V");
    if (mid == NULL) {
        (*env)->ExceptionDescribe(env);
        (*env)->DeleteLocalRef(env, cls);
        return;
    }

    jname = (*env)->NewStringUTF(env, name != NULL ? name : "");
    (*env)->CallStaticVoidMethod(env, cls, mid, jname, (jshort)value);
    if ((*env)->ExceptionCheck(env)) {
        (*env)->ExceptionDescribe(env);
    }

    (*env)->DeleteLocalRef(env, jname);
    (*env)->DeleteLocalRef(env, cls);
}