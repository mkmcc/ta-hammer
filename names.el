(defun read-lines (filePath)
  "Return a list of lines of a file at filePath."
  (with-temp-buffer
    (insert-file-contents filePath)
    (split-string (buffer-string) "\n" t)))

(defun pick (lst)
  (let* ((n (length lst))
         (i (random n)))
    (nth i lst)))

(defvar first-names
  (read-lines "first-names.dat"))

(defvar last-names
  (read-lines "last-names.dat"))
