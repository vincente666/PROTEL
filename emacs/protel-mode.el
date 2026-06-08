;;; protel-mode.el --- Major mode for PROTEL -*- lexical-binding: t; -*-

;; Recreated in honor of Bill Conn, the original author of EMACS PROTEL Mode in the 1990s.
;; Keywords from PROTEL Reference Manual Appendix A / PROTEL 2026.

;;; Commentary:
;; Provides keyword capitalization support, syntax highlighting, and
;; Pascal-style indentation for PROTEL source in GNU Emacs.
;;
;; Works in terminal Emacs (emacs-nox, \"emacs -nw\") as well as GUI Emacs.
;; Bold keywords and indentation do not require X11; colors use the terminal
;; palette when running on a tty.

(require 'cc-mode)
(require 'files)  ; executable-find

(defgroup protel nil
  "Major mode for editing PROTEL source."
  :group 'languages)

(defcustom protel-indent-offset 3
  "Indentation offset for PROTEL block bodies."
  :type 'integer
  :group 'protel)

(defcustom protel-root nil
  "PROTEL 2026 checkout directory (contains Pb and emacs/protel-mode.el).
Used to find Pb when it is not on PATH.  Usually set from ~/.emacs."
  :type 'directory
  :group 'protel)

(defcustom protel-beautify-command nil
  "Command used to beautify PROTEL source, normally the Pb driver.
When nil, `protel--locate-pb' searches PATH and PROTEL-ROOT."
  :type 'string
  :group 'protel)

(defcustom protel-beautify-extra-args nil
  "Extra arguments for Pb, e.g. \"--bold\"."
  :type 'string
  :group 'protel)

(defface protel-keyword-face
  '((t :inherit font-lock-keyword-face :weight bold)
    (tty :foreground "white" :weight bold))
  "Face used for PROTEL reserved keywords."
  :group 'protel)

(defface protel-comment-face
  '((t :foreground "green" :slant italic)
    (tty :foreground "green"))
  "Face used for PROTEL % comments and the optional first-line shebang."
  :group 'protel)

(defface protel-string-face
  '((t :inherit font-lock-string-face))
  "Face used for PROTEL single-quoted strings."
  :group 'protel)

(defvar protel-mode-map
  (let ((map (make-sparse-keymap)))
    map)
  "Keymap for `protel-mode'.")

(defvar protel-mode-syntax-table
  (let ((table (make-syntax-table)))
    (modify-syntax-entry ?% "<" table)
    (modify-syntax-entry ?\n ">" table)
    (modify-syntax-entry ?' "\"" table)
    table)
  "Syntax table for `protel-mode'.")

(defvar protel-keywords-regexp
  (regexp-opt
   '("$EJECT" "$LI" "$OBJECT" "$REFDESC" "$TYPEDESC" "$UNIVERSAL_PTR" "$VARDESC"
     "ABSTRACT" "AREA" "AS" "BIND" "BLOCK" "BOOL" "BY" "CASE" "CAST" "CLASS"
     "CREATE" "DCL" "DEFINITIONS" "DESC" "DO" "DOWN" "ELSE" "ENDAREA" "ENDBLOCK"
     "ENDCASE" "ENDCLASS" "ENDDO" "ENDIF" "ENDOVLY" "ENDSELECT" "ENDSTRUCT"
     "ENTRY" "EXIT" "EXTERNAL" "EXCLUSIVE" "FALSE" "FIXED" "FAST" "FOR" "FORWARD"
     "FROM" "HIDDEN" "IF" "IN" "INCL" "INIT" "INTERFACE" "INTRINSIC" "IS"
     "LITERAL" "METHOD" "MOD" "NIL" "NONTRANSPARENT" "NOTINCL" "OF" "OPERAND"
     "OPERATIONS" "OUT" "OVERRIDING" "OVER" "OVLY" "PACK" "PERPROCESS" "PRIVATE"
     "PROC" "PROTECTED" "PTR" "QUICK" "REF" "REFDESC" "REFINES" "RETURN" "RETURNS"
     "SECTION" "SELECT" "SELF" "SET" "SUPER" "SHARED" "STRUCT" "TABLE" "TDSIZE"
     "THEN" "TO" "TRUE" "TYPE" "TYPEDESC" "UNRESTRICTED" "UP" "UPB" "UPDATES"
     "USES" "VAL" "VARDESC" "VARIABLE" "WHILE" "WITH")
   'words))

(defvar protel-font-lock-keywords
  (list (list "^#![^\n]*" 0 'font-lock-comment-face)
        (list protel-keywords-regexp 0 'font-lock-keyword-face)
        (list "%.*" 0 'font-lock-comment-face)
        (list "'\\(?:''\\|[^']\\)*'" 0 'font-lock-string-face)))

(defun protel--executable-find (command)
  "Like `executable-find', but safe when Emacs is not fully initialized."
  (and (fboundp #'executable-find)
       (funcall #'executable-find command)))

(defun protel--locate-pb ()
  "Return absolute path to Pb, or nil."
  (or
   (when protel-beautify-command
     (let ((cmd protel-beautify-command))
       (if (file-name-absolute-p cmd)
           (when (file-exists-p cmd) cmd)
         (or (protel--executable-find cmd) cmd))))
   (protel--executable-find "Pb")
   (when protel-root
     (let ((pb (expand-file-name "Pb" protel-root)))
       (when (file-exists-p pb) pb)))
   (when-let ((protel-bin (protel--executable-find "protel")))
     (let ((pb (expand-file-name "Pb" (file-name-directory protel-bin))))
       (when (file-exists-p pb) pb)))))

(defun protel-beautify-region (start end)
  "Run Pb on the region from START to END, replacing it with beautified text."
  (let* ((pb (protel--locate-pb))
         (args (let ((extra (or protel-beautify-extra-args "")))
                 (if (or (null extra) (string= extra ""))
                     ""
                   (concat " " extra))))
         (cmd (concat (shell-quote-argument pb) args)))
    (unless pb
      (user-error "Cannot find Pb; set `protel-beautify-command' or `protel-root'"))
    (shell-command-on-region start end cmd nil t)
    (when font-lock-mode
      (font-lock-flush))))

(defun protel-beautify-buffer ()
  "Run Pb on the entire buffer, uppercasing PROTEL reserved keywords."
  (interactive)
  (protel-beautify-region (point-min) (point-max)))

(defun protel-beautify ()
  "Beautify the active region, or the entire buffer when the region is inactive.
Pipes source through Pb (Introductory Manual 7.0)."
  (interactive)
  (if (use-region-p)
      (protel-beautify-region (region-beginning) (region-end))
    (protel-beautify-buffer)))

(defun protel-indent-line ()
  "Indent current line in Pascal/PROTEL style."
  (interactive)
  (let ((pos (point))
        (offset protel-indent-offset))
    (save-excursion
      (beginning-of-line)
      (cond
       ((looking-at "\\s-*\\(?i:\\(BLOCK\\|THEN\\|DO\\|ELSE\\)\\)")
        (indent-line-to 0))
       ((looking-at "\\s-*\\(?i:\\(ENDBLOCK\\|ENDIF\\|ENDDO\\|ENDCASE\\|ENDSELECT\\)\\)")
        (indent-line-to 0))
       (t
        (if (save-excursion
              (goto-char (line-beginning-position))
              (looking-at "[ \t]+"))
            (indent-line-to offset)
          (indent-line-to 0)))))))

(define-derived-mode protel-mode fundamental-mode "PROTEL"
  "Major mode for editing PROTEL 2026 programs."
  :group 'protel
  (setq-local syntax-table protel-mode-syntax-table)
  (setq-local comment-start "% ")
  (setq-local comment-start-skip "%+ *")
  (setq-local font-lock-keywords-case-fold-search t)
  (setq-local font-lock-defaults '(protel-font-lock-keywords))
  (setq-local indent-line-function #'protel-indent-line)
  (setq-local require-final-newline t)
  ;; Map standard Font Lock faces to PROTEL-specific faces (bold keywords, etc.).
  (face-remap-add-relative 'font-lock-keyword-face 'protel-keyword-face)
  (face-remap-add-relative 'font-lock-comment-face 'protel-comment-face)
  (face-remap-add-relative 'font-lock-string-face 'protel-string-face)
  (font-lock-mode 1))

;; C-c C-f — format/beautify (same convention as go-mode, rust-mode, etc.)
(define-key protel-mode-map (kbd "C-c C-f") #'protel-beautify)
;; Mnemonic alternative: C-c C-b for Pb beautifier
(define-key protel-mode-map (kbd "C-c C-b") #'protel-beautify)
(define-key protel-mode-map (kbd "TAB") #'protel-indent-line)
(define-key protel-mode-map (kbd "C-M-\\") #'indent-region)

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.protel\\'" . protel-mode))
(add-to-list 'auto-mode-alist '("\\.pt\\'" . protel-mode))
(add-to-list 'auto-mode-alist '("\\.ptl\\'" . protel-mode))
(add-to-list 'auto-mode-alist '("\\.P\\'" . protel-mode))
;; PLS edition suffixes: .AA01 through .ZZ99 (two letters + two digits).
(add-to-list 'auto-mode-alist '("\\.[A-Za-z][A-Za-z][0-9][0-9]\\'" . protel-mode))

(provide 'protel-mode)
;;; protel-mode.el ends here
