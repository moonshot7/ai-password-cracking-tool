import itertools
import string

def brute_force_attack(hashes, max_length=16):
    charset = string.ascii_lowercase + string.digits
    cracked = {}

    for length in range(1, max_length + 1):
        chars = string.ascii_lowercase + string.digits
        for length in range(1, max_length + 1):
             for combo in itertools.product(chars, repeat=length):
                 yield ''.join(combo)
