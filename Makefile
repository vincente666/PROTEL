PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip

.PHONY: all venv install test examples hello beautify interop-swift interop-rust interop-python interop-java clean

all: venv test

venv:
	python3 -m venv .venv
	$(PIP) install -q -r requirements.txt
	$(PIP) install -q -r requirements-dev.txt

install: venv
	chmod +x protel protel-run Pb examples/Hello.protel
	@echo "PROTEL 2026 tools installed."
	@echo "  Compile/run: ./protel examples/Hello.protel --run"
	@echo "  Direct run:  export PATH=\"$$(pwd):$$PATH\" && ./examples/Hello.protel"
	@echo "  (use \$$PWD or \$$HOME/PROTEL in PATH — quoted ~/PROTEL does not expand)"

test: venv
	$(PYTHON) -m pytest tests/ -v

examples: venv
	@for f in examples/*.protel; do \
		echo "=== $$f ==="; \
		$(PYTHON) protel "$$f" --emit-c -o "build/$$(basename $$f .protel).c"; \
	done

hello: venv
	chmod +x examples/Hello.protel
	$(PYTHON) protel examples/Hello.protel -o build/Hello --run

hello-p: venv
	$(PYTHON) protel examples/Hello.P -o build/Hello.P --run

hello-pls: venv
	$(PYTHON) protel examples/Hello.aa01 -o build/Hello.aa01 --run

vdi: venv
	$(PYTHON) protel vdi.aa01 -c -o build/vdi.aa01.o

beautify: venv
	$(PYTHON) Pb examples/Hello.protel build/Hello.pretty.protel

interop-swift: venv
	chmod +x examples/interop/build_interop.sh
	examples/interop/build_interop.sh

interop-rust: venv
	chmod +x examples/interop/build_interop_rust.sh
	examples/interop/build_interop_rust.sh

interop-python: venv
	chmod +x examples/interop/build_interop_python.sh
	examples/interop/build_interop_python.sh

interop-java: venv
	chmod +x examples/interop/build_interop_java.sh
	examples/interop/build_interop_java.sh

clean:
	rm -rf .venv __pycache__ src/__pycache__ tests/__pycache__ .pytest_cache build/a.out build/interop
	find . -name '*.pyc' -delete