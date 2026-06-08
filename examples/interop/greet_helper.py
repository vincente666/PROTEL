"""Python helper invoked from PROTEL via the python_greet C embedding shim."""


def greet(name: str, value: int) -> None:
    print(f"Python: python_greet(name={name}, value={value})", flush=True)