
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import tkinter.ttk as ttk


class JSONToHiHippoDecoder:
    """Decoder widget: loads a JSON file with a 'code' field and shows the HiHippo code."""
    def __init__(self, parent):
        self.frame = tk.Frame(parent)

        top_row = tk.Frame(self.frame)
        top_row.pack(fill="x", padx=8, pady=(8, 4))

        self.load_button = tk.Button(top_row, text="Load HiHippo JSON", command=self.load_file, width=18)
        self.load_button.pack(side="left")

        self.save_button = tk.Button(top_row, text="Save Decoded Code...", command=self.save_code, width=18)
        self.save_button.pack(side="left", padx=(8, 0))

        self.validate_button = tk.Button(top_row, text="Validate JSON", command=self.validate_json, width=14)
        self.validate_button.pack(side="left", padx=(8, 0))

        self.output = scrolledtext.ScrolledText(self.frame, font=("Consolas", 12), wrap="none")
        self.output.pack(fill="both", expand=True, padx=8, pady=8)

    def load_file(self):
        file_path = filedialog.askopenfilename(title="Open HiHippo JSON", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read JSON file:\n{e}")
            return

        code = data.get("code")
        if code is None:
            messagebox.showerror("Error", "JSON does not contain a 'code' field.")
            return

        # Insert raw code string exactly as stored
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, code)

    def save_code(self):
        text = self.output.get("1.0", tk.END)
        if not text.strip():
            messagebox.showinfo("Info", "No decoded code to save.")
            return
        path = filedialog.asksaveasfilename(title="Save Decoded HiHippo Code", defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Decoded code saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def validate_json(self):
        """Quickly try to parse whatever is in the output area as JSON and show results.
        This is mainly useful if a user pasted JSON into the decoder output by mistake."""
        txt = self.output.get("1.0", tk.END).strip()
        if not txt:
            messagebox.showinfo("Info", "No text to validate.")
            return
        try:
            parsed = json.loads(txt)
            # Show whether 'code' exists
            has_code = "code" in parsed
            messagebox.showinfo("Valid JSON", f"JSON parsed successfully.\nContains 'code' field: {has_code}")
        except Exception as e:
            messagebox.showerror("Invalid JSON", f"Not valid JSON:\n{e}")


class HiHippoToJSONEncoder:
    """Encoder widget: takes HiHippo raw code and encodes it into {"code": "..."} JSON."""
    def __init__(self, parent):
        self.frame = tk.Frame(parent)

        top_row = tk.Frame(self.frame)
        top_row.pack(fill="x", padx=8, pady=(8, 4))

        self.encode_button = tk.Button(top_row, text="Encode to JSON", command=self.encode, width=16)
        self.encode_button.pack(side="left")

        self.save_button = tk.Button(top_row, text="Save JSON...", command=self.save_json, width=16)
        self.save_button.pack(side="left", padx=(8, 0))

        self.load_code_button = tk.Button(top_row, text="Load HiHippo Code...", command=self.load_code_file, width=18)
        self.load_code_button.pack(side="left", padx=(8, 0))

        mid_row = tk.Frame(self.frame)
        mid_row.pack(fill="both", expand=True, padx=8, pady=(4, 4))

        # Input area (HiHippo source)
        input_label = tk.Label(self.frame, text="HiHippo Code (input):")
        input_label.pack(anchor="w", padx=8)
        self.input = scrolledtext.ScrolledText(self.frame, font=("Consolas", 12), height=12, wrap="none")
        self.input.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Output area (JSON)
        output_label = tk.Label(self.frame, text="Encoded JSON (output):")
        output_label.pack(anchor="w", padx=8)
        self.output = scrolledtext.ScrolledText(self.frame, font=("Consolas", 12), height=10, wrap="none")
        self.output.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def encode(self):
        code = self.input.get("1.0", tk.END).rstrip("\n")
        if not code.strip():
            messagebox.showerror("Error", "HiHippo code cannot be empty.")
            return
        json_obj = {"code": code}
        try:
            json_text = json.dumps(json_obj, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to encode JSON:\n{e}")
            return
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, json_text)

    def save_json(self):
        text = self.output.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "No JSON to save. Encode first.")
            return
        path = filedialog.asksaveasfilename(title="Save JSON", defaultextension=".json",
                                            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not path:
            return
        try:
            # Ensure the output is valid JSON before saving
            parsed = json.loads(text)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Saved", f"JSON saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON:\n{e}")

    def load_code_file(self):
        path = filedialog.askopenfilename(title="Open HiHippo Code", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.input.delete("1.0", tk.END)
            self.input.insert(tk.END, code)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")


def main():
    root = tk.Tk()
    root.title("HiHippo Tools")
    root.geometry("900x700")

    notebook = ttk.Notebook(root)

    # Decoder tab
    decoder_widget = JSONToHiHippoDecoder(notebook)
    notebook.add(decoder_widget.frame, text="JSON → HiHippo Decoder")

    # Encoder tab
    encoder_widget = HiHippoToJSONEncoder(notebook)
    notebook.add(encoder_widget.frame, text="HiHippo → JSON Encoder")

    notebook.pack(fill="both", expand=True)

    # Helpful menu
    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)

    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
        "About",
        "a silly tool for a silly langage\n\n"
    ))
    menubar.add_cascade(label="Help", menu=help_menu)

    root.config(menu=menubar)
    root.mainloop()


if __name__ == "__main__":
    main()
