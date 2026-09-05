# Contributing to YouTube MCP Server

Thank you for your interest in contributing to **YouTube MCP Server**! This project is an open-source Model Context Protocol (MCP) server providing 33 specialized tools for YouTube research, analytics, transcripts, and AI-driven creator workflows.

---

## 🛠️ Development Setup

### 1. Prerequisites
* **Python 3.10+** (Python 3.12 recommended)
* **uv** (recommended package manager) or standard `pip`
* **Git**

### 2. Fork and Clone
```bash
git clone https://github.com/<your-username>/youtube-mcp.git
cd youtube-mcp
```

### 3. Set Up Virtual Environment
```bash
# Create and sync virtual environment with dev dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your YOUTUBE_API_KEY (optional for tests)
```

---

## 🧪 Running Tests

We maintain 100% mocked isolation for our test suite so you can run the full test suite without burning any live YouTube quota:

```bash
# Run all unit tests
uv run pytest -v

# Run with coverage report
uv run pytest --cov=youtube_mcp -v
```

---

## 📐 Code Guidelines

* **PEP 8**: Follow standard Python conventions.
* **Type Annotations**: All public functions, MCP tool methods, and helpers must include full type annotations (`Dict[str, Any]`, `Optional[str]`, etc.).
* **Error Resilience**:
  * Never return fake or fabricated data.
  * Use `_execute_api_request` for Google API calls to leverage automatic multi-key quota rotation.
  * Handle HTTP errors gracefully using `_handle_http_error(e)`.
* **Zero-Quota Fallbacks**: When adding new tools, consider whether a public Atom XML feed, caption stream, or heuristic algorithm can serve the request without consuming API quota.

---

## 🚀 Submitting a Pull Request

1. Create a descriptive feature branch:
   ```bash
   git checkout -b feat/my-new-tool
   ```
2. Write unit tests for your changes in `tests/`.
3. Verify that all tests pass (`pytest -v`).
4. Commit your changes using conventional commit formatting (`feat: ...`, `fix: ...`, `docs: ...`):
   ```bash
   git commit -m "feat(tools): add video tags density analyzer"
   ```
5. Push to your fork and open a Pull Request against the `main` branch.

---

## 📜 License
By contributing to this repository, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
