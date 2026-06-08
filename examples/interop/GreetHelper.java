/** Java helper invoked from PROTEL via the java_greet JNI embedding shim. */
public final class GreetHelper {
    private GreetHelper() {
    }

    public static void greet(String name, short value) {
        System.out.println("Java: java_greet(name=" + name + ", value=" + value + ")");
        System.out.flush();
    }
}