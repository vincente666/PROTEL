# 7.2 EMACS PROTEL Mode

**PROTEL Introductory Manual 2026** — Vincente D'Ingianni

---

## 7.2 EMACS PROTEL Mode

The PROTEL 2026 distribution includes **EMACS PROTEL mode** for GNU Emacs. It provides:

- **Keyword highlighting** for PROTEL 2026 reserved words (UPPERCASE keywords per the Reference Manual)
- **Comment** recognition (`%` to end of line)
- **String** highlighting (single-quoted PROTEL strings)
- **Pascal-style indentation** for `BLOCK` / `ENDBLOCK`, `IF` / `ENDIF`, and related structures

The mode file is `emacs/protel-mode.el` in the PROTEL project tree. It honors Bill Conn, original author of EMACS PROTEL mode at Nortel/BNR.

---

## 7.2.1 Enabling PROTEL mode in `.emacs`

The PROTEL tree includes a ready-made **`.emacs`**. You may use it in either of these ways:

**Option A — copy to `~/.emacs` (recommended)**

```bash
cp /path/to/PROTEL/.emacs ~/.emacs
```

Edit the copy once and set your checkout path (required when the file is not inside the PROTEL tree):

```elisp
(setq protel-user-root "/path/to/PROTEL")
```

The project `.emacs` also searches, in order: `PROTEL_ROOT` environment variable, the directory containing this init file (if it still lives inside PROTEL), the `protel` executable on your `PATH`, then `~/PROTEL`.

**Option B — load from the project directory**

```bash
cd /path/to/PROTEL
emacs -l .emacs
```

When `.emacs` remains inside the PROTEL tree, `protel-root` is discovered automatically.

After Emacs loads this block, `protel-mode` is available and **file-name detection is automatic** for:

| Extension | Mode started |
|-----------|--------------|
| `.protel` | `protel-mode` |
| `.pt` | `protel-mode` |
| `.ptl` | `protel-mode` |
| `.P` | `protel-mode` (legacy Nortel/BNR suffix; case-sensitive match) |
| `.AA01` … `.ZZ99` | `protel-mode` (PLS edition suffix: two letters + two digits) |

The PLS pattern matches any extension of the form **`.LLNN`** where `L` is a letter (`A`–`Z` or `a`–`z`) and `N` is a decimal digit. Examples: `vdi.aa01`, `module.AB18`, `Hello.aa01`.

No extra `auto-mode-alist` configuration is required in `.emacs`; `protel-mode.el` registers these extensions when it is loaded.

### Optional: user-wide install

To install the mode once under your home directory instead of pointing at the project tree:

```bash
mkdir -p ~/.emacs.d/lisp
cp /path/to/PROTEL/emacs/protel-mode.el ~/.emacs.d/lisp/
```

Then in `.emacs`:

```elisp
(add-to-list 'load-path "~/.emacs.d/lisp")
(require 'protel-mode)
```

---

## 7.2.2 Verifying automatic detection

1. Restart Emacs (or evaluate the `.emacs` block with `M-x eval-buffer`).
2. Open a PROTEL source file, for example `examples/Hello.protel`, legacy `examples/Hello.P`, or PLS `examples/Hello.aa01`.
3. Confirm the mode line shows **`PROTEL`** (not `Fundamental`).
4. Alternatively, run `M-x describe-mode` — it should report `protel-mode`.

To enable the mode manually on the current buffer (for example, a buffer without a recognized extension):

```
M-x protel-mode RET
```

---

## 7.2.3 Syntax highlighting and faces

`protel-mode` uses Emacs **Font Lock** to highlight keywords, comments, and strings. The mode does **not** hard-code RGB colors in the buffer; it assigns syntax classes to named **faces**, and Emacs (or your color theme) supplies the actual display attributes.

| Syntax | Face | Default appearance |
|--------|------|------------------|
| Reserved keywords | `protel-keyword-face` | **Bold white** (via `face-remap` from `font-lock-keyword-face`) |
| `%` comments | `protel-comment-face` | *Green italic* |
| `#!` shebang (line 1) | `protel-comment-face` | *Green italic* (runnable scripts, §7.0.5) |
| `'...'` strings | `protel-string-face` | Orange (inherits theme string color) |

Font Lock applies the standard `font-lock-*` faces; `protel-mode` **remaps** them to `protel-*` faces so highlighting works reliably and you can customize colors with `set-face-attribute` or `M-x customize-face`.

The project `.emacs` in the PROTEL distribution loads `protel-mode`, enables global Font Lock, and sets the `protel-*` face colors (bold keywords, green italic comments).

### Customizing colors in `.emacs`

Override any face after loading the mode:

```elisp
(with-eval-after-load 'protel-mode
  ;; Bold keywords (default)
  (set-face-attribute 'protel-keyword-face nil :weight 'bold)

  ;; Green italic comments (default)
  (set-face-attribute 'protel-comment-face nil
                      :foreground "green"
                      :slant 'italic)

  ;; Optional: softer green on dark backgrounds
  ;; (set-face-attribute 'protel-comment-face nil :foreground "dark olive green"))
```

Use `M-x customize-face RET protel-comment-face RET` to adjust interactively.

### Beautify with Pb

`protel-mode` pipes the buffer (or active region) through **Pb**, the PROTEL beautifier (keyword uppercasing per the Reference Manual).

| Key | Command | Action |
|-----|---------|--------|
| `C-c C-f` | `protel-beautify` | Beautify region, or whole buffer if no region |
| `C-c C-b` | `protel-beautify` | Same (mnemonic: **b**eautify / **P**b) |
| `TAB` | `protel-indent-line` | Indent current line (Pascal style) |
| `C-M-\` | `indent-region` | Indent active region (built-in) |

**Why `C-c C-f`?** In Emacs language modes, `C-c` is the standard mode-specific prefix. **`C-c C-f`** is widely used for *format* / *beautify*:

| Mode | `C-c C-f` |
|------|-----------|
| `go-mode` | `gofmt` |
| `rust-mode` | `rustfmt` |
| `csharp-mode` | reformat |
| Many `clang-format` setups | format buffer/region |

PROTEL follows that convention. `C-c C-b` is a secondary mnemonic binding for Pb.

Pb must be on your `PATH`, or set in `.emacs`:

```elisp
(setq protel-root "/path/to/PROTEL")
;; optional:
(setq protel-beautify-command "/path/to/PROTEL/Pb")
(setq protel-beautify-extra-args "--bold")   ; ANSI bold keywords on stdout
```

### Other options

| Variable | Default | Purpose |
|----------|---------|---------|
| `protel-indent-offset` | `3` | Spaces to indent nested block bodies |
| `protel-beautify-command` | *(auto)* | Path to Pb |
| `protel-beautify-extra-args` | `""` | Extra Pb flags (e.g. `--bold`) |

Example:

```elisp
(with-eval-after-load 'protel-mode
  (setq protel-indent-offset 3
        protel-root "/path/to/PROTEL"))
```

---

## 7.2.4 Terminal Emacs (emacs-nox / `emacs -nw`)

**PROTEL mode works in terminal Emacs** — no GUI or X11 required. This includes **emacs-nox** on Linux and **`emacs -nw`** in macOS Terminal or iTerm.

| Feature | Terminal support |
|---------|------------------|
| `protel-mode` auto-detection | Yes |
| Pascal-style **indentation** (`TAB`, `protel-indent-offset`) | Yes |
| **Bold** keywords | Yes (terminal bold attribute; macOS Terminal and iTerm support this) |
| Comment **colors** | Yes (green foreground on tty) |
| Comment *italic* | Optional — many terminals ignore italic; color still applies |
| Strings / other faces | Yes (terminal color palette) |

From the PROTEL project directory:

```bash
emacs -nw -l .emacs examples/Hello.protel
```

On Linux with a separate nox build:

```bash
emacs-nox -l /path/to/PROTEL/.emacs /path/to/PROTEL/examples/Hello.protel
```

Ensure **Font Lock** is on (`M-x font-lock-mode` or `(global-font-lock-mode 1)` in `.emacs`, already set in the project file). If keywords are not bold, verify your terminal profile allows bold text (Terminal.app: Settings → Profiles → Text → “Use bold fonts”).

---

## 7.2.5 Requirements

- **GNU Emacs** 26.1 or later (lexical binding is enabled in `protel-mode.el`)
- **`cc-mode`** — included with standard Emacs and emacs-nox packages; `protel-mode` requires it for derived-mode support

---

## 7.2.6 Related development tools

| Tool | Manual section | Purpose |
|------|----------------|---------|
| `protel` | §7.1 | Transpile and compile PROTEL sources |
| `Pb` | §7.0 | Beautify / uppercase keywords |
| `protel-mode` | §7.2 (this section) | Emacs editing support |

For foreign-language linking from PROTEL, see §7.3.

---

## 7.2.7 Troubleshooting

| Symptom | Likely cause | Remedy |
|---------|--------------|--------|
| `Cannot open load file: protel-mode` | `load-path` does not include `emacs/` | In `~/.emacs`, set `(setq protel-user-root "/path/to/PROTEL")` |
| `PROTEL mode not loaded` warning at startup | Copied `~/.emacs` without checkout path | Set `protel-user-root` in `~/.emacs`, or add PROTEL `protel` to `PATH` |
| `Cannot find Pb` on beautify | Pb not on PATH | Set `protel-root` or `protel-beautify-command` after mode loads |
| Buffer stays in `Fundamental` mode | `protel-mode` not loaded, or wrong extension | Add `(require 'protel-mode)`; use `.protel`, `.P`, `.AA01`-style PLS suffix, or `M-x protel-mode` |
| No keyword highlighting | Font-lock not enabled | `M-x font-lock-mode` (normally on by default) |
| `Cannot open load file: cc-mode` | Incomplete Emacs install | Use a full GNU Emacs build, not a minimal editor |
| No bold in Terminal | Terminal profile disables bold | Enable bold fonts in Terminal.app / iTerm; `protel-keyword-face` uses `:weight bold` |
| Plain text in emacs-nox | Font Lock off or mode not loaded | `M-x global-font-lock-mode`; `(require 'protel-mode)` in `.emacs` |