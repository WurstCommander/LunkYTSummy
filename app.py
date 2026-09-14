import re
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
from config_manager import ConfigManager
from gemini_response_parser import GeminiResponseParser
from gemini_summary_service import GeminiSummaryService


def extract_clean_youtube_url(url: str) -> str | None:
  """Extrahiert die 11-stellige Video-ID und baut eine saubere URL ohne Tracking-Parameter."""
  pattern = r"(?:https?:\/\/)?(?:www\.|m\.)?(?:youtube\.com\/(?:watch\?.*?\bv=|(?:embed|shorts|live|v)\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
  match = re.search(pattern, url)
  if match:
    video_id = match.group(1)
    return f"https://www.youtube.com/watch?v={video_id}"
  return None


class YouTubeSummaryApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Lunk YT Summy - Don't get clickbaited!")
    self.root.geometry("900x720")
    self.root.configure(bg="#f8fafc")

    self.full_markdown_text = ""
    self.is_first_chunk = True
    self.config_manager = ConfigManager()
    self.response_parser = GeminiResponseParser()
    self.summary_service = GeminiSummaryService()

    # Header-Bereich
    header_frame = tk.Frame(root, bg="#f8fafc")
    header_frame.pack(fill=tk.X, padx=20, pady=(15, 5))

    top_row = tk.Frame(header_frame, bg="#f8fafc")
    top_row.pack(fill=tk.X)

    tk.Label(
        top_row,
        text="Lunk YouTube Summarizer",
        font=("Segoe UI", 16, "bold"),
        bg="#f8fafc",
        fg="#0f172a",
    ).pack(side=tk.LEFT)

    self.key_btn = tk.Button(
        top_row,
        text="🔑 Change API key",
        command=self.prompt_api_key,
        font=("Segoe UI", 9),
        bg="#e2e8f0",
        fg="#334155",
        relief=tk.FLAT,
        padx=8,
        pady=2,
        cursor="hand2",
    )
    self.key_btn.pack(side=tk.RIGHT)

    tk.Label(
        header_frame,
        text="Paste a YouTube link — the link will be cleaned up and analyzed automatically.",
        font=("Segoe UI", 9),
        bg="#f8fafc",
        fg="#64748b",
    ).pack(anchor="w", pady=(2, 0))

    # Eingabe-Bereich
    input_frame = tk.Frame(root, bg="#f8fafc")
    input_frame.pack(fill=tk.X, padx=20, pady=10)

    self.url_entry = tk.Entry(
        input_frame,
        font=("Segoe UI", 10),
        relief=tk.SOLID,
        bd=1,
        highlightthickness=0,
    )
    self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
    self.url_entry.bind("<Return>", lambda event: self.start_summary())
    self.add_context_menu(self.url_entry)

    self.submit_btn = tk.Button(
        input_frame,
        text="Summarize",
        command=self.start_summary,
        font=("Segoe UI", 10, "bold"),
        bg="#0284c7",
        fg="white",
        activebackground="#0369a1",
        activeforeground="white",
        relief=tk.FLAT,
        padx=18,
        pady=6,
        cursor="hand2",
    )
    self.submit_btn.pack(side=tk.RIGHT)

    control_frame = tk.Frame(root, bg="#f8fafc")
    control_frame.pack(fill=tk.X, padx=20, pady=(10, 4))

    tk.Label(
        control_frame,
        text="Summary:",
        font=("Segoe UI", 10, "bold"),
        bg="#f8fafc",
        fg="#1e293b",
    ).pack(side=tk.LEFT)

    self.copy_btn = tk.Button(
        control_frame,
        text="Copy to clipboard",
        command=self.copy_to_clipboard,
        font=("Segoe UI", 9),
        bg="#e2e8f0",
        fg="#334155",
        relief=tk.FLAT,
        padx=10,
        pady=2,
        cursor="hand2",
    )
    self.copy_btn.pack(side=tk.RIGHT)

    # Ausgabefeld
    self.output_text = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        font=("Segoe UI", 11),
        bg="#ffffff",
        fg="#334155",
        relief=tk.SOLID,
        bd=1,
        padx=16,
        pady=16,
        spacing2=4,
    )
    self.output_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    self.setup_markdown_tags()

  def setup_markdown_tags(self):
    self.output_text.tag_config(
        "h1",
        font=("Segoe UI", 15, "bold"),
        foreground="#0f172a",
        spacing1=14,
        spacing3=6,
    )
    self.output_text.tag_config(
        "h2",
        font=("Segoe UI", 13, "bold"),
        foreground="#1e293b",
        spacing1=12,
        spacing3=4,
    )
    self.output_text.tag_config(
        "h3",
        font=("Segoe UI", 11, "bold"),
        foreground="#334155",
        spacing1=10,
        spacing3=2,
    )
    self.output_text.tag_config(
        "bold", font=("Segoe UI", 11, "bold"), foreground="#0f172a"
    )
    self.output_text.tag_config(
        "timestamp",
        font=("Segoe UI", 11, "bold"),
        foreground="#0369a1",
        background="#e0f2fe",
    )
    self.output_text.tag_config(
        "bullet", font=("Segoe UI", 11, "bold"), foreground="#0284c7"
    )
    self.output_text.tag_config(
        "divider", foreground="#cbd5e1", spacing1=8, spacing3=8
    )
    self.output_text.tag_config(
        "status", font=("Segoe UI", 11, "italic"), foreground="#64748b"
    )
    self.output_text.tag_config("body", foreground="#334155")

  def prompt_api_key(self) -> str | None:
    current_key = self.config_manager.load_api_key()
    new_key = simpledialog.askstring(
        "Gemini API Key",
        "Enter your Google Gemini API key:\n(It will be saved permanently in key.ini)",
        initialvalue=current_key,
        parent=self.root,
    )
    if new_key and new_key.strip():
      self.config_manager.save_api_key(new_key.strip())
      messagebox.showinfo(
          "Saved",
          "API key was saved successfully to key.ini!",
          parent=self.root,
      )
      return new_key.strip()
    return current_key if current_key else None

  def start_summary(self):
    api_key = self.config_manager.load_api_key()
    if not api_key:
      api_key = self.prompt_api_key()
      if not api_key:
        messagebox.showerror(
            "Missing API key",
            "No request can be sent without an API key.",
        )
        return

    raw_input = self.url_entry.get().strip()
    clean_url = extract_clean_youtube_url(raw_input)
    if not clean_url:
      messagebox.showwarning(
          "Invalid URL",
          "Could not detect a valid YouTube video ID. Please check the link.",
      )
      return

    self.url_entry.delete(0, tk.END)
    self.url_entry.insert(0, clean_url)

    self.full_markdown_text = ""
    self.is_first_chunk = True

    self.submit_btn.config(
        state=tk.DISABLED, text="⏳ Analyzing...", bg="#94a3b8"
    )

    self.output_text.config(state=tk.NORMAL)
    self.output_text.delete("1.0", tk.END)
    self.output_text.insert(
        tk.END,
        "⏳ Fetching the video from Gemini and analyzing the audio track...\n"
        "Please wait a moment (initialization can take a bit longer for long videos)...\n",
        ("status",),
    )
    self.output_text.config(state=tk.DISABLED)

    threading.Thread(
        target=self.fetch_gemini_summary, args=(clean_url, api_key), daemon=True
    ).start()

  
  def fetch_gemini_summary(self, yt_url, api_key):
    try:
      self.summary_service.stream_summary(
          yt_url, api_key, self.handle_gemini_text
      )

    except Exception as e:
      self.full_markdown_text = f"\n\n[Fehler: {str(e)}]"
      self.root.after(0, self.render_markdown, self.full_markdown_text)

    finally:
      self.root.after(0, self.reset_ui_state)  

  def handle_gemini_text(self, text):
    if self.is_first_chunk:
      self.full_markdown_text = ""
      self.is_first_chunk = False

    self.full_markdown_text += text
    self.root.after(0, self.render_markdown, self.full_markdown_text)
 
  def reset_ui_state(self):
    self.submit_btn.config(
        state=tk.NORMAL, text="Summarize", bg="#0284c7"
    )

  def render_markdown(self, text):
    self.response_parser.render(self.output_text, text)

  def copy_to_clipboard(self):
    if self.full_markdown_text:
      self.root.clipboard_clear()
      self.root.clipboard_append(self.full_markdown_text)
      self.copy_btn.config(text="✓ Copied!", bg="#bbf7d0", fg="#166534")
      self.root.after(
          2000,
          lambda: self.copy_btn.config(
              text="Copy to clipboard", bg="#e2e8f0", fg="#334155"
          ),
      )
  def add_context_menu(self, entry_widget):
    menu = tk.Menu(entry_widget, tearoff=0)
    menu.add_command(label="Cut", command=lambda: entry_widget.event_generate("<<Cut>>"))
    menu.add_command(label="Copy", command=lambda: entry_widget.event_generate("<<Copy>>"))
    menu.add_command(label="Paste", command=lambda: entry_widget.event_generate("<<Paste>>"))
    menu.add_separator()
    menu.add_command(label="Select all", command=lambda: entry_widget.select_range(0, tk.END))

    def show_menu(event):
        menu.tk_popup(event.x_root, event.y_root)

    entry_widget.bind("<Button-3>", show_menu)  # Right-click

if __name__ == "__main__":
  root = tk.Tk()
  app = YouTubeSummaryApp(root)
  root.mainloop()
  
  