# Python Clean Code and Refactoring Guidelines

## Function Design and Single Responsibility Principle
- **Function Length**: Functions should ideally not exceed 30–50 lines of code. Excessively long functions usually combine multiple responsibilities, making unit testing difficult and increasing cognitive load.
- **Decomposition Strategy**: Extract sub-operations into private helper functions with clear descriptive names.
- **Parameter Counts**: Functions should have at most 4 to 5 positional parameters. When a function requires more inputs, group them into a `@dataclass`, Pydantic model, or parameter object.

## PEP 8 Naming Conventions
- **Functions and Variables**: Always use `snake_case` (e.g., `calculate_metrics`, `total_files`). Avoid mixed `camelCase` or PascalCase for function names.
- **Classes**: Always use `PascalCase` (CapWords) (e.g., `SecurityScanner`, `AnalysisEngine`).
- **Constants**: Use `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`).

## Control Flow and Nesting
- **Guard Clauses**: Avoid deep nesting of `if/else` statements. Use guard clauses (early `return` or `raise`) at the beginning of the function to validate prerequisites and exit early.
- **Maximum Nesting Depth**: Nesting depth should not exceed 3 levels. High nesting exponentially multiplies execution paths.

## Mutable Default Arguments
- Never use mutable data structures (lists `[]`, dictionaries `{}`, sets `set()`) as default argument values in Python function signatures.
- Default arguments in Python are evaluated once at function definition time. Using mutable defaults creates shared state across all invocations.
- **Correct Pattern**:
  ```python
  def append_item(item, target_list=None):
      if target_list is None:
          target_list = []
      target_list.append(item)
      return target_list
  ```

## Import Hygiene
- Avoid wildcard imports (`from module import *`). Wildcard imports pollute the module's namespace and introduce potential naming collisions.
- Explicitly import only needed identifiers.
