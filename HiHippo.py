import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import re
import json

# ------------------------
# Interpreter
# ------------------------
variables = {}

def eval_math(expr):
    for var in variables:
        if isinstance(variables[var], (int, float)):
            expr = re.sub(rf'\b{var}\b', str(variables[var]), expr)
    try:
        return eval(expr)
    except:
        return expr

def eval_expression(expr):
    expr = expr.replace("(", "").replace(")", "")
    parts = re.split(r'\+(?=(?:[^"]*"[^"]*")*[^"]*$)', expr)
    result = ""
    for part in parts:
        part = part.strip()
        if part in variables:
            result += str(variables[part])
        elif part.startswith('"') and part.endswith('"'):
            result += part.strip('"')
        else:
            try:
                result += str(eval_math(part))
            except:
                result += part
    return result

def parse_assignment(line):
    parts = line.split(",")
    for p in parts:
        name, value = p.split("=")
        name = name.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            variables[name] = value.strip('"')
        else:
            try:
                variables[name] = eval_math(value)
            except:
                variables[name] = value

def run_line(line):
    if "=" in line and not line.startswith("print"):
        parse_assignment(line)
    elif line.startswith("print"):
        expr = line[len("print"):].strip()
        return eval_expression(expr)
    return ""

def run_program(code):
    output.delete(1.0, tk.END)
    for line in code.split("\n"):
        line = line.strip()
        if line:
            result = run_line(line)
            if result != "":
                output.insert(tk.END, result + "\n")

# ------------------------
# GUI Setup
# ------------------------
window = tk.Tk()
window.title("HiHippo")
window.geometry("800x600")

# Top frame for buttons
top_frame = tk.Frame(window)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

# Buttons
def on_run():
    run_program(editor.get(1.0, tk.END))

def save_program():
    code = editor.get(1.0, tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
    if file_path:
        try:
            json.dump({"code": code}, open(file_path, "w"))
            messagebox.showinfo("Saved", f"Program saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def load_program():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
    if file_path:
        try:
            data = json.load(open(file_path, "r"))
            editor.delete(1.0, tk.END)
            editor.insert(tk.END, data.get("code", ""))
            messagebox.showinfo("Loaded", f"Program loaded from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

run_button = tk.Button(top_frame, text="Run Code", font=("Arial", 12), command=on_run)
run_button.pack(side=tk.LEFT, padx=5)

save_button = tk.Button(top_frame, text="Save Program", font=("Arial", 12), command=save_program)
save_button.pack(side=tk.LEFT, padx=5)

load_button = tk.Button(top_frame, text="Load Program", font=("Arial", 12), command=load_program)
load_button.pack(side=tk.LEFT, padx=5)

# Editor
editor = scrolledtext.ScrolledText(window, font=("Consolas", 12), height=20)
editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,5))

# Output console
output = scrolledtext.ScrolledText(window, font=("Consolas", 12), height=10, bg="#111", fg="#0f0")
output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

window.mainloop()
