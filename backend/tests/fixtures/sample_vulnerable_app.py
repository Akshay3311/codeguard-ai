import subprocess
import os
import hashlib

# Hardcoded Secret smell
API_KEY_SECRET = "sk-live-987483920192837482910"


def execute_user_command(cmd):
    # Security: Command Injection
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()


def calculate_weak_hash(data):
    # Security: Weak Cryptographic Algorithm
    return hashlib.md5(data.encode()).hexdigest()


def run_dynamic_calculation(expression):
    # Security: eval() code execution
    return eval(expression)


def fetch_user_data(cursor, user_id):
    # Security: SQL Injection via f-string
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return cursor.execute(query)


def append_to_cache(item, cache_list=[]):
    # Bug: Mutable default argument
    cache_list.append(item)
    return cache_list


def unsafe_file_reader(filename):
    # Bug: Swallowing exceptions with pass
    try:
        with open(filename, "r") as f:
            return f.read()
    except Exception:
        pass


def overly_complex_logic(a, b, c, d, e, f_param):
    # Quality: Too many parameters (>5) & Deep nesting (>4) & High Cyclomatic Complexity
    result = 0
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        result = a + b + c + d + e + f_param
                    else:
                        result = a - b
                else:
                    result = b - c
            else:
                result = c - d
        else:
            result = d - e
    else:
        result = e - f_param
    return result
