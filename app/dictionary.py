def dictionary_attack(hashes, wordlist_path):
    with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
        passwords = [line.strip() for line in f]

    cracked = {}
    for pwd in passwords:
        for h in hashes:
            if pwd == h:
                cracked[h] = pwd
    return cracked
