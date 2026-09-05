# Lesson 1: Project Bootstrap

## Goal
Create a clean, best-practice Python project layout for a GDK agentic CLI app using `uv`, `src/` layout, and environment configuration.

## Directory structure

Project files live at repo root, managed by `uv`. A snapshot copy is kept in `lessons/01-bootstrap/` for reference.

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
    01-bootstrap/   # snapshot copy of files above
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
    "goose-sdk",
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
OPENAI_BASE_URL=http://127.0.0.1:8080/v1
OPENAI_API_KEY=sk-local-test
MODEL_NAME=bartowski/Muse-Glimmer-30B-GGUF:Q8_0
```

**Why:**
We use an OpenAI-compatible local server. `OPENAI_API_KEY` is required by the provider even if it's a dummy value for local servers.

## Step 1.3: .gitignore

Create `.gitignore` at repo root with:
```
__pycache__/
*.pyc
.env
.venv/
uv.lock
```

## Step 1.4: src layout

Create files at repo root:
* `src/gdk_hello/__init__.py` - empty
* `src/gdk_hello/main.py` - empty placeholder for later

## Step 1.5: Create venv with uv

From repo root:
```bash
uv venv
uv add click python-dotenv
```

`uv` will detect the package from `pyproject.toml` at repo root. The snapshot is copied to `lessons/01-bootstrap/` for reference.

This creates a shared venv for all lessons.

### Installing goose-sdk

`goose-sdk` is now published to PyPI and can be installed directly:

```bash
cd /var/home/stpousty/git/gdk-sample-app-goose-build-v2
uv add goose-sdk
# or
uv pip install goose-sdk
```

The package installs as `goose` and can be imported as `import goose`.

#### Installing goose-sdk from source

Building from source is still available for the latest development build or when you need a platform-specific wheel. The PyPI release previously only shipped a wheel for `macosx_11_0_arm64`; on Linux you can still build from source.

You have the Goose source at `/var/home/stpousty/git/goose`. Build a local wheel with Just:

```bash
cd /var/home/stpousty/git/goose
just --justfile crates/goose-sdk/justfile python-wheel
```

This creates:
`/var/home/stpousty/git/goose/crates/goose-sdk/python/dist/goose_sdk-0.1.0a7-py3-none-linux_x86_64.whl`

Install the wheel into the project's venv:
```bash
cd /var/home/stpousty/git/gdk-sample-app-goose-build-v2
uv pip install /var/home/stpousty/git/goose/crates/goose-sdk/python/dist/goose_sdk-0.1.0a7-py3-none-linux_x86_64.whl
```

The package installs as `goose` and can be imported as `import goose`.

**Why:**
* GDK bindings are generated from Rust via UniFFI
* Building locally avoids platform wheel limitations
* The wheel is specific to your hardware, so building from source is the supported path for Linux

## Next
Once these files exist, we'll do a minimal provider smoke test in Lesson 2.
