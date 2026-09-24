# Building Agentic Applications with the Goose GDK

An evolving, instructor-led course for learning how to build a custom agentic Python application with the **Goose Development Kit (GDK)**.

This repository uses the `goose-sdk` Python package (imported as `goose`) to work directly with providers, messages, streamed responses, and—later in the course—tools. It does **not** extend the existing Goose application or wrap the Goose CLI. The goal is to understand and assemble the parts of an agentic application one concept at a time.

> [!IMPORTANT]
> This course is under active development. The root source is the exercise currently being worked on and may be incomplete. The numbered lesson directories contain the accompanying explanations and complete reference implementations.

## Who this is for

The primary format is an **in-person course or workshop** led by an instructor. Lessons are small conceptual units, so several may be taught in one class session.

You can also use the repository for self-study. Goose can act as a tutor by following [`AGENTS.md`](AGENTS.md), presenting one step at a time, and waiting for you before moving ahead. Self-study support is secondary to the instructor-led experience.

## Learning goals

By the end of the course, learners should understand how to:

- Structure a Python GDK application managed with `uv`.
- Load a declarative provider configuration.
- Check an OpenAI-compatible provider and discover its models.
- Select a configured model for an individual request.
- Construct provider messages and system instructions.
- Process streamed text, completion metadata, and errors.
- Define tools and complete the tool-request/tool-result round trip.
- Wrap the application in a usable command-line interface.

The curriculum will evolve as it is implemented and taught. Lessons may be added, removed, divided, combined, reordered, or corrected.

## Course roadmap

| Lesson | Topic | Status | Materials |
|---:|---|---|---|
| 1 | Project bootstrap with `uv` and a `src/` layout | Complete | [`lessons/01-bootstrap/`](lessons/01-bootstrap/) |
| 2 | Provider configuration and connectivity smoke test | Complete | [`lessons/02-provider-smoke-test/`](lessons/02-provider-smoke-test/) |
| 3 | First streaming model call | Complete | [`lessons/03-streaming-call/`](lessons/03-streaming-call/) |
| 4 | System instructions, message roles, and multi-turn conversation | **Active** | [`lessons/04-conversation/`](lessons/04-conversation/) |
| 5 | Explicit model selection with `--model` | Planned | — |
| 6 | Defining a provider tool | Planned | — |
| 7 | Executing tools and returning results | Planned | — |
| 8 | Command-line interface, configuration, and error handling | Planned | — |
| Later | Multi-model calls and additional topics identified through teaching | Planned | — |

**Status meanings:**

- **Complete** — ready to teach and validated against its stated success criteria.
- **Active** — the root source is currently exercising or revising this material.
- **Draft** — lesson material exists but is not yet considered complete.
- **Planned** — expected direction; scope and sequence may change.

## How the repository is organized

```text
.
├── src/gdk_hello/            # current exercise; changes as the course advances
├── lessons/
│   ├── 01-bootstrap/
│   ├── 02-provider-smoke-test/
│   ├── 03-streaming-call/
│   └── 04-conversation/
├── instructor-notes/         # instructor-only pacing and teaching guidance
├── custom_aa_llama_qwen3_6-35b.json
├── .env.example
├── pyproject.toml
└── uv.lock
```

### Root source

Students write code in `src/gdk_hello/`. It represents the lesson currently being developed, not a stable or production-ready application. When an exercise is complete and validated, the root source moves forward to the next exercise.

### Lesson directories

Each numbered lesson is both an instructional reference and a solution:

- `LESSON.md` explains the lesson and highlights important code snippets.
- `src/` contains the complete reference implementation for that lesson.

The complete solution is already present in the lesson directory; it is not copied from the root at the end of class. Lesson material is intentionally editable and may be corrected as the SDK and course evolve.

### Instructor notes

`instructor-notes/` contains one teaching guide per implemented lesson. These files are for pacing guidance, discussion prompts, live-demo preparation, and teaching cautions rather than student instructions.

## Prerequisites

The course currently targets **Linux**. A dev container that can run the full course is a longer-term goal.

You need:

- Python 3.11 or newer.
- [`uv`](https://docs.astral.sh/uv/).
- Git.
- Access to a compatible model provider.

The class supports either:

- A provider endpoint shared by the instructor, or
- An OpenAI-compatible local server such as llama.cpp.

If you run a model locally, choose one that fits your own RAM/VRAM and hardware. The model in the bundled configuration is an example, not a course requirement.

External links are supplemental. Once dependencies, the provider, and any local model are prepared, the core class should not require learners to leave the course material.

## Setup

Clone the repository, enter it, and create the environment:

```bash
uv sync
```

The committed `uv.lock` makes classroom environments reproducible. While the course is in development, dependencies and the lockfile will continue to be updated. Course releases will pin a tested Goose SDK version and lock dependencies to the corresponding GitHub release tag.

## Provider configuration

The application uses a declarative provider JSON file as the source of truth for:

- The provider engine and endpoint.
- Whether authentication is required.
- The environment variable used for an API key, when applicable.
- Available model names and provider capabilities.

The included [`custom_aa_llama_qwen3_6-35b.json`](custom_aa_llama_qwen3_6-35b.json) is a replaceable default for one local OpenAI-compatible setup. You may copy it and modify the copy for another endpoint or model. Learners are not expected to author the full configuration format from scratch.

Official Goose documentation describes custom providers as shareable JSON configurations that can define compatible API endpoints, preconfigured model lists, authentication, headers, and streaming support. See [Configure LLM Provider](https://goose-docs.ai/docs/getting-started/providers#configure-custom-provider) for the current configuration fields and examples.

### Provider path

Before the Click CLI lesson, examples use a default provider path in source and progressively support overriding it with a positional argument:

```bash
uv run python -m src.gdk_hello.main path/to/provider.json
```

If the argument is omitted, the bundled provider configuration is used. When Click is introduced, this becomes a named `--provider` option.

### Selecting models

Early lessons select the first model listed in the provider JSON to keep the focus on GDK fundamentals. A later lesson will add `--model`, validate the requested name against the provider’s configured models, and cover applications that make calls to more than one model.

### API keys and `.env`

The bundled local provider does not require authentication. For a provider that uses a static API key:

1. Its JSON configuration names the environment variable from which the provider reads the key.
2. Put that variable and value in a local `.env` file.
3. Never commit `.env` or real credentials.

The course uses `python-dotenv` so learners do not need to export secrets manually in every shell. Copy `.env.example` when an authenticated-provider lesson calls for it, and adapt the variable name to the provider JSON you are using.

## Run the active exercise

Unless its `LESSON.md` says otherwise, run lesson code from the repository root:

```bash
uv run python -m src.gdk_hello.main
```

Lesson 4 is now prepared, while the root source remains at the completed Lesson 3 checkpoint until instruction begins. The Lesson 4 exercise makes two streaming requests: it captures the first assistant response, adds it to an ordered message history, and sends a context-dependent follow-up while keeping the system instruction separate from conversation messages.

The configured endpoint must be running and support streaming. A successful run prints two assistant responses; usage diagnostics are also printed when the provider supplies them. Exact generated text depends on the selected provider and model.

## Validation philosophy

Every implemented lesson should define:

- Prerequisites.
- A command to run or otherwise validate the work.
- Expected structural behavior.
- Explicit success criteria.

Live-provider validation is the priority. If a lesson needs a provider and none is available, start one or obtain the shared classroom endpoint rather than treating offline tests as equivalent proof.

Model text is nondeterministic, so inference lessons validate behavior—such as receiving text chunks and reaching the end of a stream—not exact wording. Automated tests, formatting, and linting may be used to keep the repository reliable, but they are supporting project practices rather than course topics.

## Troubleshooting

### Provider configuration is not found

Run the command from the repository root and verify the configured provider path. Before the CLI lesson, relative paths are resolved from the current working directory.

### The provider cannot be reached

Confirm that:

- The local server is running or the shared endpoint is available.
- `base_url` in the provider JSON points to that server.
- A firewall or network policy is not blocking the connection.

### A configured model is missing

Check the model IDs returned by the provider’s model-list endpoint. Model names in the provider JSON must match the IDs advertised by the server.

### Authentication fails

Confirm that:

- The provider JSON is configured to require authentication.
- Its API-key environment-variable name matches the key in `.env`.
- `.env` is in the repository root and the key value does not contain accidental whitespace.

Do not put secrets directly in committed provider JSON files.

## For maintainers and coding agents

Read [`AGENTS.md`](AGENTS.md) before changing the repository. In particular:

- Preserve the small-step, instructor-led pedagogy.
- Keep each lesson’s explanation and complete source consistent.
- Treat the root source as work in progress.
- Validate against a live provider when the lesson requires one.
- Consult current official documentation before asserting GDK API or provider-configuration details.

This repository is not currently soliciting external contributions.

## Official references

- [Goose: Configure LLM Provider](https://goose-docs.ai/docs/getting-started/providers)
- [Goose repository](https://github.com/aaif-goose/goose)
- [Goose SDK Python package](https://pypi.org/project/goose-sdk/)

## License

Licensed under the [Apache License 2.0](LICENSE).