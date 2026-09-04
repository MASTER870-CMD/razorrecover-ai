# Contributing to RazorRecover AI

Thank you for your interest in contributing to RazorRecover AI!

## Code of Conduct
We are committed to providing a welcoming, inclusive, and harassment-free experience for everyone.

## Architecture Guidelines
When contributing to RazorRecover AI, always respect the core fintech safety principle:
1. **Never allow LLMs to directly control money movement.**
2. All recovery recommendations must flow through the deterministic **Policy Engine** before execution.
3. Every recovery action must be followed by independent **Verification**.
4. Every state change and decision must generate an immutable **Audit Log**.

## Development Workflow
1. Fork the repository and create a branch for your feature: `git checkout -b feature/my-feature`.
2. Follow PEP 8 standards for Python and ESLint/Prettier standards for TypeScript.
3. Ensure all tests pass: `pytest` and `npm run test` (or `npm run build`).
4. Submit a Pull Request with a clear summary of changes.
