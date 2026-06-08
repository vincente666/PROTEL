/* C ABI entry point: embeds Python and calls greet_helper.greet (PROTEL EXTERNAL). */
#include <Python.h>
#include <stdint.h>

static int py_ready;

static void ensure_python(void)
{
    if (py_ready) {
        return;
    }
    Py_Initialize();
    if (PyRun_SimpleString("import sys\n"
                           "sys.path.insert(0, 'examples/interop')\n") != 0) {
        PyErr_Print();
    }
    py_ready = 1;
}

void python_greet(const char* name, int16_t value)
{
    PyObject *mod, *func, *args, *result;

    ensure_python();

    mod = PyImport_ImportModule("greet_helper");
    if (mod == NULL) {
        PyErr_Print();
        return;
    }

    func = PyObject_GetAttrString(mod, "greet");
    if (func == NULL || !PyCallable_Check(func)) {
        PyErr_Print();
        Py_DECREF(mod);
        return;
    }

    args = Py_BuildValue("(si)", name != NULL ? name : "", (int)value);
    result = PyObject_CallObject(func, args);
    if (result == NULL) {
        PyErr_Print();
    } else {
        Py_DECREF(result);
    }

    Py_DECREF(args);
    Py_DECREF(func);
    Py_DECREF(mod);
}