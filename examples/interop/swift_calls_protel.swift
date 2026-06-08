// Swift program calling an EXPORTed PROTEL procedure (C linkage).
import Foundation

@_silgen_name("protel_add")
func protel_add(_ a: Int16, _ b: Int16) -> Int16

let sum = protel_add(40, 2)
print("Swift: protel_add(40, 2) = \(sum)")