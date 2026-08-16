# OWASP Top 10 Security Guidance for Python Applications

## Code Injection & Arbitrary Code Execution
- **Dynamic Code Execution**: Never call `eval()`, `exec()`, or `compile()` with untrusted or user-supplied input. An attacker can craft inputs executing arbitrary OS commands or reading secrets.
- **Safe Alternatives**: Use `ast.literal_eval()` for safely evaluating Python literals (strings, numbers, tuples, lists, dicts, booleans, and None).

## Command Injection
- **Subprocess Security**: Avoid `shell=True` when invoking system processes with `subprocess.Popen`, `subprocess.run`, or `os.system`.
- **Recommended Pattern**:
  ```python
  import subprocess
  # Pass arguments as a list with shell=False (default)
  result = subprocess.run(["git", "clone", repo_url, target_dir], check=True, capture_output=True)
  ```

## SQL Injection
- **Parameterized Queries**: Never construct SQL queries by concatenating strings or formatting strings with `%`, `.format()`, or f-strings.
- **Remediation**: Always use query parameter binding provided by database drivers (DB-API) or ORMs (SQLAlchemy, Django ORM).

## Insecure Deserialization
- **Python Pickle**: The `pickle` module is not secure against untrusted data. A crafted payload can trigger arbitrary code execution during unpickling via `__reduce__`.
- **PyYAML Loader**: Calling `yaml.load()` without specifying a safe loader allows arbitrary Python class instantiation. Always use `yaml.safe_load()` or `yaml.load(stream, Loader=yaml.SafeLoader)`.

## Secrets Management
- Never commit API keys, database credentials, private keys, or passwords into source code repositories.
- Use environment variables (via `python-dotenv`, `pydantic-settings`, or cloud secrets managers like AWS Secrets Manager / GCP Secret Manager).

## Cryptographic Best Practices
- Avoid obsolete hash algorithms like MD5 and SHA-1 for digital signatures, password hashes, and integrity checks due to known collision attacks.
- Use SHA-256 or SHA-512 for cryptographic hashing and Argon2 / bcrypt for password storage.
