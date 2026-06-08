// Rust program calling an EXPORTed PROTEL procedure (C linkage).
extern "C" {
    fn protel_add(a: i16, b: i16) -> i16;
}

fn main() {
    let sum = unsafe { protel_add(40, 2) };
    println!("Rust: protel_add(40, 2) = {sum}");
}