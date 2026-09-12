import re
import tkinter as tk


class GeminiResponseParser:

  def render(self, output_text, text):
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)

    for line in text.split("\n"):
      if line.startswith("### "):
        self._insert_inline_formatted(output_text, line[4:], tags=("h3",))
        output_text.insert(tk.END, "\n")
      elif line.startswith("## "):
        self._insert_inline_formatted(output_text, line[3:], tags=("h2",))
        output_text.insert(tk.END, "\n")
      elif line.startswith("# "):
        self._insert_inline_formatted(output_text, line[2:], tags=("h1",))
        output_text.insert(tk.END, "\n")
      elif line.strip() in ("---", "***", "___"):
        output_text.insert(tk.END, "─" * 55 + "\n", ("divider",))
      elif line.startswith("  * ") or line.startswith("  - "):
        output_text.insert(tk.END, "    • ", ("bullet",))
        self._insert_inline_formatted(output_text, line[4:], tags=("body",))
        output_text.insert(tk.END, "\n")
      elif line.startswith("* ") or line.startswith("- "):
        output_text.insert(tk.END, "• ", ("bullet",))
        self._insert_inline_formatted(output_text, line[2:], tags=("body",))
        output_text.insert(tk.END, "\n")
      else:
        self._insert_inline_formatted(output_text, line, tags=("body",))
        output_text.insert(tk.END, "\n")

    output_text.see(tk.END)
    output_text.config(state=tk.DISABLED)

  def _insert_inline_formatted(self, output_text, text, tags=()):
    #pattern = r"(\*\*.*?\*\*|\b\d{1,2}:\d{2}(?::\d{2})?\b)"
        
    pattern = r"(\*\*.*?\*\*|\*[^*\n]+\*|\b\d{1,2}:\d{2}(?::\d{2})?\b)"
    tokens = re.split(pattern, text)

    for token in tokens:
      if not token:
        continue
      if token.startswith("**") and token.endswith("**") and len(token) >= 4:
        content = token[2:-2]
        output_text.insert(tk.END, content, (*tags, "bold"))
        # fuer fettgeschriebene einzelwoerter, noch nicht getestet!!
      elif token.startswith("*") and token.endswith("*") and len(token) >= 4:
        content = token[1:-1]
        output_text.insert(tk.END, content, (*tags, "bold"))
      elif re.match(r"^\d{1,2}:\d{2}(?::\d{2})?$", token):
        output_text.insert(tk.END, f" {token} ", (*tags, "timestamp"))
      else:
        output_text.insert(tk.END, token, tags)