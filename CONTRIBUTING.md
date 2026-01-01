# Contributing to Map Reader LLM

Thank you for your interest in contributing to Map Reader LLM! This document provides guidelines for contributions.

---

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to maintain a welcoming and inclusive community.

---

## How to Contribute

### Reporting Issues

- **Bug reports**: Use the [GitHub Issues](https://github.com/saross/map-reader-llm/issues) tracker
- Include: Python version, operating system, error messages, and steps to reproduce
- Check existing issues before creating a new one

### Feature Requests

- Open an issue describing the feature and its use case
- Label with `enhancement`

### Pull Requests

1. **Fork** the repository
2. **Create a branch** for your feature: `git checkout -b feature/your-feature-name`
3. **Make changes** following our coding standards (below)
4. **Test** your changes
5. **Commit** with a clear message following conventional commits format
6. **Push** and open a Pull Request

---

## Coding Standards

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints where practical
- Maximum line length: 100 characters
- Use `pathlib` for file paths

### Documentation

- Use UK/Australian spelling (colour, behaviour, organisation)
- Expand acronyms on first use: "Vision-Language Model (VLM)"
- Include docstrings for all functions and classes
- Use Google-style docstrings

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```text
type(scope): subject

body

footer
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## Development Setup

```bash
git clone https://github.com/saross/map-reader-llm.git
cd map-reader-llm
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Questions?

Open an issue or contact the maintainers listed in [CITATION.cff](CITATION.cff).

---

## Licence

By contributing, you agree that your contributions will be licensed under the Apache 2.0 Licence (code) and CC-BY 4.0 (documentation).
