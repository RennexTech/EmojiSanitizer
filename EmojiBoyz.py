import tkinter as tk
from tkinter import messagebox
import re

class EmojiStripper:
    def __init__(self, root):
        self.root = root
        self.root.title("EMOJI SANITIZER // SYSTEM-X")
        self.root.geometry("1200x750")
        self.root.configure(bg='#000000')
        self.root.minsize(900, 600)
        
        # Comprehensive Emoji regex
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FA6F"
            "\u2600-\u26FF\u2700-\u27BF"
            "]+", flags=re.UNICODE
        )
        
        # AI Artifacts regex (Markdown stars, hashes, etc.)
        self.ai_pattern = re.compile(r'[\*#$_\-`~>]')
        
        self.setup_ui()
        self.setup_shortcuts()
    
    def setup_ui(self):
        # Fonts
        self.label_font = ("Segoe UI", 11, "bold")
        self.text_font = ("Segoe UI", 14)
        self.btn_font = ("Segoe UI", 11, "bold")
        self.input_hint_font = ("Segoe UI", 9, "italic")
        
        # Main Layout Root configuration
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        main_container = tk.Frame(self.root, bg='#000000')
        main_container.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        
        # Split Pane configuration
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1) # The text boxes area
        main_container.grid_rowconfigure(1, weight=0) # The button area
        main_container.grid_rowconfigure(2, weight=0) # The status bar area

        # --- LEFT SIDE: INPUT (CREAM/AMBER) ---
        left_side = tk.Frame(main_container, bg='#000000')
        left_side.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left_side.grid_rowconfigure(1, weight=1) # Make text box expandable
        left_side.grid_columnconfigure(0, weight=1)
        
        tk.Label(left_side, text="📥 RAW INPUT", 
                font=self.label_font, bg='#000000', fg='#b58900').grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.input_text = tk.Text(
            left_side, wrap=tk.WORD, font=self.text_font,
            bg='#fdf6e3', fg='#1a1a1a', 
            insertbackground='#b58900', 
            selectbackground='#eee8d5',
            padx=20, pady=20, undo=True,
            borderwidth=0, highlightthickness=2, highlightcolor='#b58900'
        )
        self.input_text.grid(row=1, column=0, sticky="nsew")
        self.input_text.bind("<<Modified>>", self.on_content_changed)

        # --- RIGHT SIDE: OUTPUT (BLACKISH) ---
        right_side = tk.Frame(main_container, bg='#000000')
        right_side.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        right_side.grid_rowconfigure(1, weight=1) # Make text box expandable
        right_side.grid_columnconfigure(0, weight=1)
        
        tk.Label(right_side, text="📤 SANITIZED OUTPUT", 
                font=self.label_font, bg='#000000', fg='#ffffff').grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        self.output_text = tk.Text(
            right_side, wrap=tk.WORD, font=self.text_font,
            bg='#111111', fg='#ffffff', 
            insertbackground='#ffffff', 
            selectbackground='#333333',
            padx=20, pady=20,
            borderwidth=0, highlightthickness=1, highlightbackground='#333333'
        )
        self.output_text.grid(row=1, column=0, sticky="nsew")
        self.output_text.config(state=tk.DISABLED)

        # --- ACTION BUTTONS ROW ---
        btn_frame = tk.Frame(main_container, bg='#000000', pady=15)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        # 1. COPY
        self.copy_btn = tk.Button(
            btn_frame, text="📋 COPY TEXT", 
            command=self.copy_to_clipboard,
            font=self.btn_font, 
            bg='#2ea043', fg='#ffffff', 
            activebackground='#3fb950', activeforeground='#ffffff',
            relief=tk.FLAT, cursor="hand2", 
            padx=15, pady=10
        )
        self.copy_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.copy_btn.config(state=tk.DISABLED)

        # 2. PASTE
        self.paste_btn = tk.Button(
            btn_frame, text="📥 PASTE", 
            command=self.paste_from_clipboard,
            font=self.btn_font, 
            bg='#b58900', fg='#000000', 
            activebackground='#d69f00', activeforeground='#000000',
            relief=tk.FLAT, cursor="hand2", 
            padx=15, pady=10
        )
        self.paste_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 3. RESET
        self.reset_btn = tk.Button(
            btn_frame, text="🗑 RESET", 
            command=self.clear_fields,
            font=self.btn_font, 
            bg='#dc322f', fg='#ffffff', 
            activebackground='#ff4444', activeforeground='#ffffff',
            relief=tk.FLAT, cursor="hand2", 
            padx=15, pady=10
        )
        self.reset_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 4. CUSTOM STRIPPER BOX
        custom_strip_frame = tk.Frame(btn_frame, bg='#1a1a1a', padx=10)
        custom_strip_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        tk.Label(custom_strip_frame, text="STRIP CUSTOM CHARS:", 
                 font=("Segoe UI", 8, "bold"), bg='#1a1a1a', fg='#888888').pack(anchor='w')
        
        self.custom_strip_entry = tk.Entry(
            custom_strip_frame, font=("Consolas", 12),
            bg='#000000', fg='#00ff41', borderwidth=0,
            insertbackground='#00ff41', highlightthickness=1, 
            highlightbackground='#333333', highlightcolor='#00ff41'
        )
        self.custom_strip_entry.pack(fill=tk.X, pady=(0, 5))
        self.custom_strip_entry.bind("<KeyRelease>", lambda e: self.process_text())

        # --- BOTTOM STATUS BAR ---
        bottom_bar = tk.Frame(main_container, bg='#000000')
        bottom_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        self.stats_lbl = tk.Label(
            bottom_bar, text="READY TO PURGE",
            font=("Segoe UI", 9, "bold"), bg='#000000', fg='#444444'
        )
        self.stats_lbl.pack(side=tk.LEFT)

        tk.Label(
            bottom_bar, text="Symbols Cleanup Enabled (*) | Shortcuts: Ctrl+Enter, Esc, Ctrl+Shift+V",
            font=("Segoe UI", 8), bg='#000000', fg='#666666'
        ).pack(side=tk.RIGHT)

    def setup_shortcuts(self):
        self.root.bind("<Control-Shift-V>", lambda e: self.paste_from_clipboard())
        self.root.bind("<Control-Return>", lambda e: self.copy_to_clipboard())
        self.root.bind("<Escape>", lambda e: self.clear_fields())

    def on_content_changed(self, event=None):
        if self.input_text.edit_modified():
            self.process_text()
            self.input_text.edit_modified(False)

    def paste_from_clipboard(self):
        try:
            content = self.root.clipboard_get()
            if content:
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.process_text()
                self.stats_lbl.config(text="✓ CONTENT PASTED", fg='#b58900')
        except tk.TclError:
            pass

    def process_text(self):
        raw_data = self.input_text.get("1.0", tk.END).strip()
        if not raw_data:
            self.update_output("", 0)
            return

        # 1. Remove Emojis
        emojis_found = self.emoji_pattern.findall(raw_data)
        clean_data = self.emoji_pattern.sub(r'', raw_data)
        
        # 2. Clean symbols / Artifacts (*, #, $, etc.)
        clean_data = self.ai_pattern.sub('', clean_data)
        
        # 3. Clean User Custom Characters
        custom_chars = self.custom_strip_entry.get()
        if custom_chars:
            # Escape special characters for regex
            escaped_custom = re.escape(custom_chars)
            clean_data = re.sub(f'[{escaped_custom}]', '', clean_data)

        # 4. Fix Whitespace
        clean_data = re.sub(r' +', ' ', clean_data) 
        clean_data = re.sub(r'\n\s*\n', '\n\n', clean_data)
        
        self.update_output(clean_data.strip(), len(emojis_found))

    def update_output(self, text, count):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)
        self.output_text.config(state=tk.DISABLED)

        if text:
            self.stats_lbl.config(text=f"✓ {count} EMOJIS + AI SYMBOLS PURGED // {len(text)} CHARS", fg='#b58900')
            self.copy_btn.config(state=tk.NORMAL, bg='#2ea043', text="📋 COPY TEXT")
        else:
            self.stats_lbl.config(text="READY TO PURGE", fg='#444444')
            self.copy_btn.config(state=tk.DISABLED, bg='#1a3a1a')

    def copy_to_clipboard(self):
        clean_text = self.output_text.get("1.0", "end-1c")
        if clean_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(clean_text)
            
            # Feedback
            self.copy_btn.config(text="✓ COPIED!", bg="#00ff41", fg="#000000")
            self.root.after(1000, lambda: self.copy_btn.config(text="📋 COPY TEXT", bg="#2ea043", fg="#ffffff"))

    def clear_fields(self):
        self.input_text.delete("1.0", tk.END)
        self.custom_strip_entry.delete(0, tk.END)
        self.process_text()
        self.input_text.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmojiStripper(root)
    root.mainloop()
