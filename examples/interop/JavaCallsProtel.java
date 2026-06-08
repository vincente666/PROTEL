/** Java program calling an EXPORTed PROTEL procedure via JNI (C ABI bridge). */
public final class JavaCallsProtel {
    static {
        System.loadLibrary("javacallsprotel");
    }

    private static native short protelAdd(short a, short b);

    public static void main(String[] args) {
        short sum = protelAdd((short) 40, (short) 2);
        System.out.println("Java: protel_add(40, 2) = " + sum);
    }
}