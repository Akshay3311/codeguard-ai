# Software Metrics & Technical Debt Evaluation Standards

## Cyclomatic Complexity (McCabe Metric)
- **1–10**: Simple, well-structured procedure; low risk; highly testable.
- **11–20**: Moderate risk and complexity; requires comprehensive unit tests.
- **21–50**: High risk; complex logic; refactoring strongly recommended.
- **> 50**: Very high risk; un-testable; urgent refactoring required.

## Maintainability Index (MI)
- The Maintainability Index evaluates software quality on a scale derived from Halstead Volume, Cyclomatic Complexity, and Lines of Code:
  - **85–100**: High maintainability (Green)
  - **65–84**: Moderate maintainability (Yellow)
  - **0–64**: Low maintainability / High technical debt (Red)

## Halstead Complexity Measures
- **Volume ($V$)**: Quantifies information content and size of the implementation.
- **Difficulty ($D$)**: Measures the mental effort required to write or understand the code.
- **Effort ($E$)**: Represents mental activity required for maintenance.

## Technical Debt Calculation Philosophy
- Technical debt is the implied cost of future refactoring required due to choosing quick, suboptimal solutions over better architectural approaches.
- In CodeGuard AI, technical debt is calculated mathematically as a weighted function of:
  1. Security vulnerabilities (weighted heavily due to exploit risk)
  2. Code smells and maintainability index deficit
  3. Potential runtime bugs and unhandled exception risks
  4. Cyclomatic and cognitive complexity density
  5. Code duplication and bloated file size
