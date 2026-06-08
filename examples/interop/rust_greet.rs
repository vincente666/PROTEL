// Rust function called from PROTEL via EXTERNAL / #[no_mangle] extern "C".
use std::ffi::CStr;
use std::os::raw::c_char;

#[no_mangle]
pub extern "C" fn rust_greet(name: *const c_char, value: i16) {
    let label = unsafe {
        if name.is_null() {
            "<null>"
        } else {
            CStr::from_ptr(name).to_str().unwrap_or("<invalid utf-8>")
        }
    };
    println!("Rust: rust_greet(name={label}, value={value})");
}