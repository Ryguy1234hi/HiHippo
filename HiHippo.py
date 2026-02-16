import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import pygame
import threading
import json
import re

# ===============================
# GLOBAL STATE
# ===============================

variables = {}
objects = {}
loop_block = []
keys_pressed = set()

hippogame_enabled = False
engine_running = False
game_thread = None

current_color = (255, 255, 255)

COLOR_MAP = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "yellow": (255, 255, 0),
}

# ===============================
# EXPRESSION SYSTEM
# ===============================

def eval_math(expr):
    for var in variables:
        expr = re.sub(rf'\b{var}\b', str(variables[var]), expr)
    try:
        return eval(expr)
    except:
        return expr

def eval_expression(expr):
    parts = re.split(r'\+(?=(?:[^"]*"[^"]*")*[^"]*$)', expr)
    result = ""
    for part in parts:
        part = part.strip()
        if part in variables:
            result += str(variables[part])
        elif part.startswith('"') and part.endswith('"'):
            result += part.strip('"')
        else:
            result += str(eval_math(part))
    return result

def parse_assignment(line):
    parts = line.split(",")
    for p in parts:
        name, value = p.split("=")
        variables[name.strip()] = eval_math(value.strip())

# ===============================
# COMMAND HANDLER
# ===============================

def run_line(line):
    global current_color, hippogame_enabled

    if not line:
        return ""

    if line.startswith("import hippogame"):
        hippogame_enabled = True
        return "HippoGame Enabled"

    if "=" in line and not line.startswith("if_key"):
        parse_assignment(line)
        return ""

    if line.startswith("print"):
        expr = line[len("print"):].strip()
        return eval_expression(expr)

    if line.startswith("set_color"):
        color_name = line.split()[1]
        current_color = COLOR_MAP.get(color_name.lower(), (255, 255, 255))
        return ""

    if line.startswith("draw_circle"):
        parts = line.split()
        name = parts[1]
        x = int(eval_math(parts[2]))
        y = int(eval_math(parts[3]))
        radius = int(eval_math(parts[4]))
        objects[name] = {
            "type": "circle",
            "x": x,
            "y": y,
            "r": radius,
            "color": current_color
        }
        return ""

    if line.startswith("move"):
        parts = line.split()
        name = parts[1]
        dx = int(eval_math(parts[2]))
        dy = int(eval_math(parts[3]))
        if name in objects:
            objects[name]["x"] += dx
            objects[name]["y"] += dy
        return ""

    if line.startswith("if_key"):
        parts = line.split()
        key = parts[1]
        action = " ".join(parts[2:])
        if key in keys_pressed:
            run_line(action)
        return ""

    return ""

# ===============================
# PYGAME ENGINE
# ===============================

def engine_loop():
    global engine_running, keys_pressed

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("HippoGame Window")

    clock = pygame.time.Clock()
    engine_running = True

    while engine_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine_running = False
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                keys_pressed.add(pygame.key.name(event.key).capitalize())

            if event.type == pygame.KEYUP:
                keys_pressed.discard(pygame.key.name(event.key).capitalize())

        # Run forever block
        for cmd in loop_block:
            run_line(cmd)

        # Render
        screen.fill((0, 0, 0))

        for obj in objects.values():
            if obj["type"] == "circle":
                pygame.draw.circle(
                    screen,
                    obj["color"],
                    (obj["x"], obj["y"]),
                    obj["r"]
                )

        pygame.display.flip()
        clock.tick(60)

# ===============================
# PROGRAM EXECUTION
# ===============================

def run_program(code):
    global loop_block, objects, variables, engine_running, game_thread

    output.delete("1.0", tk.END)

    variables.clear()
    objects.clear()
    loop_block = []
    engine_running = False

    lines = code.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        if line.strip() == "forever:":
            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                loop_block.append(lines[i].strip())
                i += 1
        else:
            result = run_line(line.strip())
            if result:
                output.insert(tk.END, result + "\n")
            i += 1

    if hippogame_enabled:
        game_thread = threading.Thread(target=engine_loop)
        game_thread.daemon = True
        game_thread.start()

# ===============================
# SAVE / LOAD
# ===============================

def save_program():
    code = editor.get("1.0", tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files","*.json")])
    if file_path:
        json.dump({"code": code}, open(file_path, "w"))
        messagebox.showinfo("Saved", "Program saved.")

def load_program():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
    if file_path:
        data = json.load(open(file_path, "r"))
        editor.delete("1.0", tk.END)
        editor.insert(tk.END, data.get("code", ""))
        messagebox.showinfo("Loaded", "Program loaded.")

# ===============================
# TKINTER IDE
# ===============================

window = tk.Tk()
window.title("HiHippo IDE")
window.geometry("900x700")

top_frame = tk.Frame(window)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

run_button = tk.Button(top_frame, text="Run Code", font=("Arial", 12),
                       command=lambda: run_program(editor.get("1.0", tk.END)))
run_button.pack(side=tk.LEFT, padx=5)

save_button = tk.Button(top_frame, text="Save Program", font=("Arial", 12),
                        command=save_program)
save_button.pack(side=tk.LEFT, padx=5)

load_button = tk.Button(top_frame, text="Load Program", font=("Arial", 12),
                        command=load_program)
load_button.pack(side=tk.LEFT, padx=5)

editor = scrolledtext.ScrolledText(window, font=("Consolas", 12), height=20)
editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,5))

output = scrolledtext.ScrolledText(window, font=("Consolas", 12),
                                   height=10, bg="#111", fg="#0f0")
output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

window.mainloop()
