import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import re
import ast
import operator
import time

# ==========================================================
# SAFE MATH SYSTEM
# ==========================================================

variables = {}

allowed_operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}

def safe_eval(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return allowed_operators[type(node.op)](
            safe_eval(node.left),
            safe_eval(node.right)
        )
    elif isinstance(node, ast.UnaryOp):
        return allowed_operators[type(node.op)](
            safe_eval(node.operand)
        )
    else:
        raise TypeError("Unsupported expression")

def eval_math(expr):
    for var in variables:
        if isinstance(variables[var], (int, float)):
            expr = re.sub(rf'\b{var}\b', str(variables[var]), expr)
    try:
        node = ast.parse(expr, mode='eval').body
        return safe_eval(node)
    except:
        return expr

# ==========================================================
# HIPPO GAME ENGINE
# ==========================================================

hippogame_enabled = False
game_window = None
canvas = None
objects = {}
keys_pressed = set()
current_color = "white"

def setup_game():
    global game_window, canvas
    game_window = tk.Toplevel(window)
    game_window.title("HippoGame Engine")
    game_window.geometry("600x600")

    canvas = tk.Canvas(game_window, bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)

    game_window.bind("<KeyPress>", key_down)
    game_window.bind("<KeyRelease>", key_up)
    game_window.focus_set()

def key_down(event):
    keys_pressed.add(event.keysym)

def key_up(event):
    if event.keysym in keys_pressed:
        keys_pressed.remove(event.keysym)

# ==========================================================
# LANGUAGE INTERPRETER
# ==========================================================

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
            variables[name] = eval_math(value)

def run_line(line):
    global hippogame_enabled, current_color

    # Import hippogame
    if line == "import hippogame":
        hippogame_enabled = True
        setup_game()
        return ""

    # Assignment
    if "=" in line and not line.startswith("print"):
        parse_assignment(line)
        return ""

    # Print
    if line.startswith("print"):
        expr = line[len("print"):].strip()
        return eval_expression(expr)

    # ==================================================
    # GAME ENGINE COMMANDS
    # ==================================================

    if hippogame_enabled:

        # Clear screen
        if line == "clear":
            canvas.delete("all")
            return ""

        # Set color
        if line.startswith("set_color"):
            current_color = line.split()[1]
            return ""

        # Draw rectangle
        if line.startswith("draw_rect"):
            parts = line.split()
            name = parts[1]
            x = int(eval_math(parts[2]))
            y = int(eval_math(parts[3]))
            w = int(eval_math(parts[4]))
            h = int(eval_math(parts[5]))
            obj = canvas.create_rectangle(x, y, x+w, y+h, fill=current_color)
            objects[name] = obj
            return ""

        # Draw circle
        if line.startswith("draw_circle"):
            parts = line.split()
            name = parts[1]
            x = int(eval_math(parts[2]))
            y = int(eval_math(parts[3]))
            r = int(eval_math(parts[4]))
            obj = canvas.create_oval(x-r, y-r, x+r, y+r, fill=current_color)
            objects[name] = obj
            return ""

        # Draw text
        if line.startswith("draw_text"):
            parts = re.split(r'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', line)
            name = parts[1]
            x = int(eval_math(parts[2]))
            y = int(eval_math(parts[3]))
            text = parts[4].strip('"')
            obj = canvas.create_text(x, y, text=text, fill=current_color, font=("Arial", 18))
            objects[name] = obj
            return ""

        # Move object
        if line.startswith("move"):
            parts = line.split()
            name = parts[1]
            dx = int(eval_math(parts[2]))
            dy = int(eval_math(parts[3]))
            if name in objects:
                canvas.move(objects[name], dx, dy)
            return ""

        # Key check
        if line.startswith("if_key"):
            parts = line.split()
            key = parts[1]
            action = " ".join(parts[2:])
            if key in keys_pressed:
                run_line(action)
            return ""

        # Sleep
        if line.startswith("sleep"):
            seconds = float(line.split()[1])
            time.sleep(seconds)
            return ""

        # Update screen
        if line == "update":
            game_window.update()
            return ""

    return ""

def run_program(code):
    output.delete(1.0, tk.END)
    variables.clear()

    for line in code.split("\n"):
        line = line.strip()
        if line:
            result = run_line(line)
            if result != "":
                output.insert(tk.END, result + "\n")

# ==========================================================
# GUI
# ==========================================================

window = tk.Tk()
window.title("HiHippo IDE 1.0")
window.geometry("900x700")

top_frame = tk.Frame(window)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

def on_run():
    run_program(editor.get(1.0, tk.END))

def save_program():
    code = editor.get(1.0, tk.END)
    file_path = filedialog.asksaveasfilename(
        defaultextension=".hippo",
        filetypes=[("Hippo files","*.hippo")]
    )
    if file_path:
        with open(file_path, "w") as f:
            f.write(code)
        messagebox.showinfo("Saved", "Program saved!")

def load_program():
    file_path = filedialog.askopenfilename(
        filetypes=[("Hippo files","*.hippo")]
    )
    if file_path:
        with open(file_path, "r") as f:
            code = f.read()
        editor.delete(1.0, tk.END)
        editor.insert(tk.END, code)
        messagebox.showinfo("Loaded", "Program loaded!")

tk.Button(top_frame, text="Run Code", font=("Arial", 12), command=on_run).pack(side=tk.LEFT, padx=5)
tk.Button(top_frame, text="Save", font=("Arial", 12), command=save_program).pack(side=tk.LEFT, padx=5)
tk.Button(top_frame, text="Load", font=("Arial", 12), command=load_program).pack(side=tk.LEFT, padx=5)

editor = scrolledtext.ScrolledText(window, font=("Consolas", 12), height=20)
editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,5))

output = scrolledtext.ScrolledText(window, font=("Consolas", 12), height=10, bg="#111", fg="#0f0")
output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

window.mainloop()
