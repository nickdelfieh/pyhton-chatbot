import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import re
import math
import webbrowser

chat_folder = None
current_chat_file = None
settings_file = "chat_settings.txt"


def contains_large_number(s, max_digits=10):
    return any(len(num) > max_digits for num in re.findall(r'\d+', s))


def process_message(user_input):
    if user_input in ["exit", "bye"]:
        root.quit()
        return "Bye! See you later."
    elif user_input in ["hi", "hello", "hey"] or user_input.endswith(" hi"):
        return "hi!"
    elif "how are you" in user_input:
        return "I'm just a code, but I'm running fine!"
    elif "whats your name" in user_input or "who are you" in user_input or "your name" in user_input:
        return "I'm Python chatbot. Not the language, just the bot."
    elif any(op in user_input for op in ["+", "-", "*", "/", "**", "%", "^"]) or "sqrt" in user_input or "√" in user_input:
        if "^" in user_input and contains_large_number(user_input):
            return "Sorry, that power is too big for me to calculate."
        try:
            math_input = user_input.replace("^", "**")
            math_input = re.sub(r'√\s*(\d+)', r'sqrt(\1)', math_input)
            allowed_names = {"__builtins__": {}, "sqrt": math.sqrt}
            result = eval(math_input, allowed_names)
            return f"The answer is {round(result, 2) if isinstance(result, float) else result}"
        except Exception:
            return "I couldn't understand that math expression."
    else:
        return "I don't understand that yet."


def save_chat_folder(path):
    with open(settings_file, "w") as f:
        f.write(path)


def load_chat_folder():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            path = f.read().strip()
            if os.path.isdir(path):
                return path
    return None


def choose_chat_folder():
    global chat_folder
    chat_folder = load_chat_folder()
    if not chat_folder:
        chat_folder = filedialog.askdirectory(title="Select folder to save chat history")
        if not chat_folder:
            messagebox.showerror("No folder", "You must select a folder to continue.")
            root.destroy()
        else:
            save_chat_folder(chat_folder)


def update_chat_list(search_text=""):
    chat_listbox.delete(0, tk.END)
    if not chat_folder:
        return
    files = sorted(f for f in os.listdir(chat_folder) if f.endswith(".txt"))
    for f in files:
        display_name = f[:-4]
        if search_text.lower() in display_name.lower():
            chat_listbox.insert(tk.END, display_name)


def load_chat(filename):
    global current_chat_file
    current_chat_file = filename + ".txt"
    path = os.path.join(chat_folder, current_chat_file)
    chat_window.config(state='normal')
    chat_window.delete(1.0, tk.END)
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            for line in lines:
                if line.startswith("You: "):
                    chat_window.insert(tk.END, "You: ", "prefix_user")
                    chat_window.insert(tk.END, line[5:] + "\n", "user")
                elif line.startswith("Python: "):
                    chat_window.insert(tk.END, "Python: ", "prefix_bot")
                    chat_window.insert(tk.END, line[8:] + "\n", "bot")
                else:
                    chat_window.insert(tk.END, line + "\n")
    except:
        chat_window.insert(tk.END, "[Could not load chat file]\n")
    chat_window.config(state='disabled')
    entry.config(state='normal')
    send_btn.config(state='normal')


def save_current_chat():
    if not current_chat_file:
        return
    path = os.path.join(chat_folder, current_chat_file)
    with open(path, "w", encoding="utf-8") as f:
        content = chat_window.get(1.0, tk.END).strip().splitlines()
        for line in content:
            f.write(line + "\n")


def send_message():
    user_msg = entry.get().strip()
    if not user_msg:
        return

    chat_window.config(state='normal')
    chat_window.insert(tk.END, "You: ", "prefix_user")
    chat_window.insert(tk.END, user_msg + "\n", "user")

    response = process_message(user_msg.lower())
    chat_window.insert(tk.END, "Python: ", "prefix_bot")
    chat_window.insert(tk.END, response + "\n", "bot")

    chat_window.config(state='disabled')
    chat_window.see(tk.END)
    entry.delete(0, tk.END)
    save_current_chat()


def scale_fonts(event):
    width = root.winfo_width()
    new_size = int(width / 60)
    new_size = max(18, min(new_size, 22))
    chat_window.tag_config("user", font=("Arial", new_size))
    chat_window.tag_config("bot", font=("Arial", new_size))
    chat_window.tag_config("prefix_user", foreground="blue", font=("Arial", new_size, "bold"))
    chat_window.tag_config("prefix_bot", foreground="green", font=("Arial", new_size, "bold"))
    entry.config(font=("Arial", new_size))
    send_btn.config(font=("Arial", new_size))
    chat_listbox.config(font=("Arial", new_size + 2))
    create_btn.config(font=("Arial", new_size + 2))
    delete_btn.config(font=("Arial", new_size + 2))
    rename_btn.config(font=("Arial", new_size + 2))
    search_entry.config(font=("Arial", new_size))


def create_new_chat():
    if not chat_folder:
        return
    existing = [f for f in os.listdir(chat_folder) if f.endswith(".txt")]
    next_num = len(existing) + 1
    filename = f"chat{next_num}.txt"
    path = os.path.join(chat_folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write("Python: Hello! This is a new chat.\n")
    update_chat_list()
    load_chat(filename[:-4])


def delete_selected_chat():
    selection = chat_listbox.curselection()
    if not selection:
        messagebox.showinfo("No Selection", "Please select a chat to delete.")
        return
    filename = chat_listbox.get(selection[0]) + ".txt"
    path = os.path.join(chat_folder, filename)
    confirm = messagebox.askyesno("Delete Chat", f"Are you sure you want to delete {filename}?")
    if confirm:
        try:
            os.remove(path)
            update_chat_list()
            chat_window.config(state='normal')
            chat_window.delete(1.0, tk.END)
            chat_window.config(state='disabled')
        except:
            messagebox.showerror("Error", "Could not delete the selected chat.")


def rename_selected_chat():
    selection = chat_listbox.curselection()
    if not selection:
        messagebox.showinfo("No Selection", "Please select a chat to rename.")
        return
    old_name = chat_listbox.get(selection[0])
    new_name = tk.simpledialog.askstring("Rename Chat", f"Enter new name for '{old_name}':")
    if not new_name:
        return
    old_path = os.path.join(chat_folder, old_name + ".txt")
    new_path = os.path.join(chat_folder, new_name + ".txt")
    if os.path.exists(new_path):
        messagebox.showerror("Error", "A chat with that name already exists.")
        return
    try:
        os.rename(old_path, new_path)
        update_chat_list(search_var.get())
    except:
        messagebox.showerror("Error", "Could not rename chat.")

def click_me():
    messagebox.showinfo("Info", "this dos nothing, only CREDITS. now you shold see credits hahahahahah")
    webbrowser.open("https://github.com/nickdelfieh/pyhton-chatbot/wiki/credits")
# Setup window
root = tk.Tk()
root.title("Nick's Chatbot")
root.minsize(899, 600)
root.geometry("800x500")
root.iconbitmap("chatbot.ico")

choose_chat_folder()

left_frame = tk.Frame(root, width=200)
left_frame.pack(side=tk.LEFT, fill='y')

search_var = tk.StringVar()
search_entry = tk.Entry(left_frame, textvariable=search_var, font=("Arial", 12))
search_entry.pack(fill='x')
search_var.trace_add("write", lambda *args: update_chat_list(search_var.get()))

chat_listbox = tk.Listbox(left_frame, font=("Arial", 14))
chat_listbox.pack(fill='both', expand=True)
chat_listbox.bind("<<ListboxSelect>>", lambda e: load_chat(chat_listbox.get(chat_listbox.curselection()[0])) if chat_listbox.curselection() else None)

btn_frame = tk.Frame(left_frame)
btn_frame.pack(fill='x')



create_btn = tk.Button(btn_frame, text="+ Create Chat", command=create_new_chat, font=("Arial", 16))
create_btn.pack(fill='x')

delete_btn = tk.Button(btn_frame, text="- Delete Chat", command=delete_selected_chat, font=("Arial", 16))
delete_btn.pack(fill='x')

rename_btn = tk.Button(btn_frame, text="✎ Rename Chat", command=rename_selected_chat, font=("Arial", 16))
rename_btn.pack(fill='x')

dummy = tk.Button(btn_frame, text="click me", command=click_me, font=("Arial", 16))
dummy.pack(fill='x')

right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill='both', expand=True)

chat_window = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, state='disabled', width=60, height=20)
chat_window.pack(padx=10, pady=10, fill='both', expand=True)

chat_window.tag_config("user", foreground="black", font=("Arial", 14))
chat_window.tag_config("bot", foreground="black", font=("Arial", 14))
chat_window.tag_config("prefix_user", foreground="blue", font=("Arial", 14, "bold"))
chat_window.tag_config("prefix_bot", foreground="green", font=("Arial", 14, "bold"))

input_frame = tk.Frame(right_frame)
input_frame.pack(fill='x', padx=10, pady=(0, 10))

entry = tk.Entry(input_frame, font=("Arial", 14))
entry.pack(side=tk.LEFT, fill='x', expand=True)

send_btn = tk.Button(input_frame, text="Send", font=("Arial", 14), command=send_message)
send_btn.pack(side=tk.LEFT, padx=(5, 0))

entry.bind("<Return>", lambda event: send_message())
root.bind("<Configure>", scale_fonts)

update_chat_list()
root.mainloop()
