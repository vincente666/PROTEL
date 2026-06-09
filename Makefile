PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip

# System-wide install layout (FHS-oriented).
SYSPREFIX ?= /usr/local/protel
SYSBINDIR ?= /usr/local/bin
SYSMANPREFIX ?= /usr/local/share/man
DESTDIR ?=

# Local developer install (repository checkout).
LOCAL_MANPREFIX ?= $(CURDIR)/man

.PHONY: all venv install install-man install-system install-man-system uninstall-system \
	test examples hello hello-pls beautify interop-swift interop-rust interop-python interop-java clean

all: venv test

venv:
	python3 -m venv .venv
	$(PIP) install -q -r requirements.txt
	$(PIP) install -q -r requirements-dev.txt

# --- Local (checkout) install -------------------------------------------------

install: venv install-man
	chmod +x Pc Pc! Pb examples/Hello.P
	@echo "PROTEL 2026 tools installed (local checkout)."
	@echo "  Compile/run: ./Pc examples/Hello.P --run"
	@echo "  Direct run:  export PATH=\"$$(pwd):$$PATH\" && ./examples/Hello.P"
	@echo "  (use \$$PWD or \$$HOME/PROTEL in PATH — quoted ~/PROTEL does not expand)"
	@echo "  Manual pages: export MANPATH=\"$(LOCAL_MANPREFIX):$$MANPATH\" && man Pc"
	@echo "  System-wide:  sudo make install-system"

install-man:
	mkdir -p $(LOCAL_MANPREFIX)/man1
	install -m 644 man/Pc.1 man/Pb.1 $(LOCAL_MANPREFIX)/man1/
	@echo "Installed man pages to $(LOCAL_MANPREFIX)/man1 (Pc.1, Pb.1)"

# --- System-wide install (/usr/local/protel) ----------------------------------

install-system: install-man-system
	@echo "Installing PROTEL 2026 to $(DESTDIR)$(SYSPREFIX) ..."
	mkdir -p $(DESTDIR)$(SYSPREFIX)
	install -m 755 Pc Pc! Pb $(DESTDIR)$(SYSPREFIX)/
	install -m 644 requirements.txt $(DESTDIR)$(SYSPREFIX)/
	cp -R src $(DESTDIR)$(SYSPREFIX)/
	cp -R examples $(DESTDIR)$(SYSPREFIX)/
	cp -R emacs $(DESTDIR)$(SYSPREFIX)/
	chmod +x $(DESTDIR)$(SYSPREFIX)/examples/Hello.P
	python3 -m venv $(DESTDIR)$(SYSPREFIX)/.venv
	$(DESTDIR)$(SYSPREFIX)/.venv/bin/pip install -q \
		-r $(DESTDIR)$(SYSPREFIX)/requirements.txt
	mkdir -p $(DESTDIR)$(SYSBINDIR)
	ln -sf $(SYSPREFIX)/Pc $(DESTDIR)$(SYSBINDIR)/Pc
	ln -sf $(SYSPREFIX)/Pb $(DESTDIR)$(SYSBINDIR)/Pb
	ln -sf $(SYSPREFIX)/Pc! $(DESTDIR)$(SYSBINDIR)/Pc!
	@echo "PROTEL 2026 installed system-wide."
	@echo "  Toolkit root: $(SYSPREFIX)"
	@echo "  Commands:     $(SYSBINDIR)/{Pc,Pb,Pc!}"
	@echo "  Manual pages: $(SYSMANPREFIX)/man1/{Pc,Pb}.1"
	@echo "  Try: Pc $(SYSPREFIX)/examples/Hello.P --run"
	@echo "       man Pc"

install-man-system:
	mkdir -p $(DESTDIR)$(SYSMANPREFIX)/man1
	install -m 644 man/Pc.1 man/Pb.1 $(DESTDIR)$(SYSMANPREFIX)/man1/
	@echo "Installed man pages to $(DESTDIR)$(SYSMANPREFIX)/man1 (Pc.1, Pb.1)"

uninstall-system:
	rm -f $(DESTDIR)$(SYSBINDIR)/Pc $(DESTDIR)$(SYSBINDIR)/Pb $(DESTDIR)$(SYSBINDIR)/Pc!
	rm -f $(DESTDIR)$(SYSMANPREFIX)/man1/Pc.1 $(DESTDIR)$(SYSMANPREFIX)/man1/Pb.1
	rm -rf $(DESTDIR)$(SYSPREFIX)
	@echo "Removed PROTEL 2026 from $(SYSPREFIX), $(SYSBINDIR), and $(SYSMANPREFIX)/man1"

# --- Development targets ------------------------------------------------------

test: venv
	$(PYTHON) -m pytest tests/ -v

examples: venv
	@for f in examples/*.P; do \
		echo "=== $$f ==="; \
		$(PYTHON) Pc "$$f" --emit-c -o "build/$$(basename $$f .P).c"; \
	done

hello: venv
	chmod +x examples/Hello.P
	$(PYTHON) Pc examples/Hello.P -o build/Hello --run

hello-pls: venv
	$(PYTHON) Pc examples/Hello.aa01 -o build/Hello.aa01 --run

vdi: venv
	$(PYTHON) Pc vdi.aa01 -c -o build/vdi.aa01.o

beautify: venv
	$(PYTHON) Pb examples/Hello.P build/Hello.pretty.P

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