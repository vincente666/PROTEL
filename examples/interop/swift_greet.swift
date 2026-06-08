// Swift function called from PROTEL via EXTERNAL / @_cdecl("swift_greet").
import Foundation

@_cdecl("swift_greet")
public func swift_greet(_ name: UnsafePointer<CChar>, _ value: Int32) {
    let label = String(cString: name)
    print("Swift: swift_greet(name=\(label), value=\(value))")
}