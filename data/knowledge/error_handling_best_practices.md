# Python Exception & Error Handling Best Practices

## Specific Exception Catching
- Never use a bare `except:` without an exception class. It intercepts `SystemExit`, `KeyboardInterrupt`, and `MemoryError`, preventing clean process termination and masking serious errors.
- Prefer catching precise exception types (e.g., `FileNotFoundError`, `KeyError`, `ValueError`) over broad `Exception`.

## Handling and Logging Failures
- **Never silently swallow exceptions**: Avoid `except Exception: pass`. Silently ignoring failures leads to corrupted data, silent calculation failures, and difficult debugging.
- **Traceback Logging**: Always log errors with stack trace using `logger.exception()` or `logger.error("...", exc_info=True)`.

## Resource Cleanup and Context Managers
- Always manage resources (file handles, network sockets, database connections, mutexes) with Python context managers (`with` statements) to guarantee cleanup even if exceptions occur.
- For custom resources, implement `__enter__` and `__exit__` or use `@contextlib.contextmanager`.
