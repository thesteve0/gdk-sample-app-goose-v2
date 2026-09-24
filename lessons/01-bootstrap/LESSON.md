# Lesson 1: Project Bootstrap

## Goal
Create a clean Python project layout for a GDK agentic application using `uv`, a `src/` layout, and safe environment configuration.

## Directory structure

Students work in the repository root, managed by `uv`. The complete reference implementation for this lesson is kept in `lessons/01-bootstrap/src/`.

Repo root:
```
gdk-sample-app-goose-build-v2/
  pyproject.toml
  .env.example
  .gitignore
  src/
    gdk_hello/
      __init__.py
      main.py
  lessons/
    01-bootstrap/   # lesson explanation and complete solution
```



## Step 1.1: pyproject.toml

Create `pyproject.toml` at repo root with:

```toml
[project]
name = "gdk-hello"
version = "0.1.0"
description = "GDK Python hello-world CLI tutorial"
requires-python = ">=3.11"
dependencies = [
    "goose-sdk==0.1.0a9",
    "click",
    "python-dotenv",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
package = true
```

**Why:**
* `goose-sdk` -> imported as `goose`
* `click` -> CLI wrapper later
* `python-dotenv` -> load `.env`
* `src/` layout -> importable, best practice
* `hatchling` -> minimal build backend

## Step 1.2: .env.example

Create `.env.example` at repo root with:

```
# Add API-key variables named by your provider JSON when authentication is
# required. The bundled local provider does not require one.
# EXAMPLE_PROVIDER_API_KEY=replace-me
```

**Why:**
Provider JSON will become the source of truth for endpoints and model names in Lesson 2. A local `.env` is reserved for real API-key values when a provider requires authentication; `.env.example` documents the pattern without containing a secret.

## Step 1.3: .gitignore

Create `.gitignore` at repo root with:
```
__pycache__/
*.pyc
.env
.venv/
/.idea/
/out/
```

## Step 1.4: src layout

Create files at the repository root:

- `src/gdk_hello/__init__.py` — package marker
- `src/gdk_hello/main.py` — a small entry point that prints `Hello from gdk_hello`

## Step 1.5: Create the environment with uv

From repo root:
```bash
uv sync
```

`uv` detects the package from `pyproject.toml`, creates the shared virtual environment, and installs the versions in the committed `uv.lock`.

This creates a shared environment for all lessons.

The `goose-sdk` distribution installs the Python package imported as `goose`. The course pins a tested SDK version and updates it deliberately during course development.

## Success criteria

- `uv sync` completes successfully.
- `uv run python -m src.gdk_hello.main` prints `Hello from gdk_hello`.
- You can identify where package source, dependencies, locked versions, lesson material, and local secrets belong.

## Next
Once these files exist, we'll do a minimal provider smoke test in Lesson 2.