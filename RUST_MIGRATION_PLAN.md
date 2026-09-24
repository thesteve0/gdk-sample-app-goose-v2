# Python-to-Rust Course Migration Plan

> **Temporary migration document**
>
> Copy this file to the root of the new Rust repository. It records decisions,
> translation guidance, and migration checkpoints. Delete it after the Rust
> course, `README.md`, and `AGENTS.md` are complete and independently validated.

## Purpose

Migrate **Building Agentic Applications with the Goose GDK** from its current
Python implementation to a new Rust repository without losing the course's
instructor-led structure, provider neutrality, incremental pedagogy, or
validation standards.

This is a migration, not an in-place conversion. Do not rewrite the existing
Python working tree into Rust. Create a new repository and copy only reviewed,
intentional material.

## Executive conclusion

The course can use the official Rust GDK rather than internal Goose crates.
`goose-sdk` is the Rust crate from which the Python and Kotlin APIs are
generated. Its documented Rust API supports the concepts already introduced by
the course: declarative providers, model configuration, messages, streaming,
usage data, errors, and provider tools.

At the time of this analysis (2026-09-24):

- The current Python course pins `goose-sdk==0.1.0a9`.
- The corresponding published Rust release is `goose-sdk` version
  `0.1.0-alpha.9`.
- The SDK is explicitly documented as **alpha**. Pin an exact version and review
  the API reference and changelog before every upgrade.
- The published Rust crate requires Rust `1.94.1` and uses edition 2021 at that
  release.
- The documented in-process Rust API is enabled with the crate's `uniffi`
  feature. The feature name is surprising for native Rust callers, but it is the
  official documented interface at this release.
- Goose `main` already identifies itself as `0.1.0-alpha.10`, but that release
  had not appeared in the crates.io sparse index during this analysis. Start
  the migration from the published `0.1.0-alpha.9` tag unless the team
  deliberately chooses and records a newer released version.

The strongest migration strategy is therefore:

1. Preserve the course model and conceptual sequence.
2. Replace Python and `uv` mechanics with Rust and Cargo mechanics.
3. Translate against the pinned public `goose-sdk` API, not against internal
   `goose`, `goose-providers`, or workspace-only implementation details.
4. Treat every migrated lesson as Draft until it passes its Rust success
   criteria and any required live-provider validation.

## Scope and source snapshot

Before copying material, record the exact commit of the Python repository from
which the migration starts. The source worktree had uncommitted Lesson 4 and
other edits when this analysis was written, so “copy the current files” is not a
reproducible migration boundary.

Record these values in the new repository or in the first migration commit:

- Python course source commit: **TBD**
- Rust GDK version: initially `=0.1.0-alpha.9`
- Rust toolchain: initially `1.94.1`, subject to a successful build spike
- Provider configuration used for live validation: **TBD**
- Migration owner: **TBD**

## What should not change

The following parts of the current `README.md` and `AGENTS.md` are
language-independent and should be preserved:

- Instructor-led workshops are primary; Goose-assisted self-study is secondary.
- Lessons are small, concept-focused increments.
- The root source is the current exercise and may be incomplete.
- Every lesson contains an explanation and a complete reference solution.
- Lesson solutions exist from the outset; they are not copied from the root at
  the end of class.
- Instructor notes remain separate from learner-facing material.
- The bundled provider and model are replaceable defaults, not requirements.
- Learners begin with the first configured model and add explicit model
  selection later.
- Live-provider validation has priority for lessons that make provider calls.
- Validation checks structural behavior rather than exact model text.
- Lesson prose, source, root workflow, roadmap, and instructor notes remain in
  sync.
- Secrets and `.env` are never committed.
- Agents preserve unrelated work and verify Goose-specific claims against
  current official documentation or the exact pinned SDK source.
- The instructor owns sequencing, scope, and release decisions.

## `README.md` analysis and required changes

### 1. Title and introduction

**Keep:** the course name and the distinction between a custom GDK application
and an extension or wrapper around the Goose CLI.

**Change:**

- “custom agentic Python application” to “custom agentic Rust application.”
- The Python package/import explanation to an exact pinned Cargo dependency.
- State that the course consumes the public `goose-sdk` crate directly.
- Include the SDK's alpha warning near setup rather than hiding it in maintainer
  documentation.

**Remove:** references to the PyPI package and importing it as `goose` from the
Rust course's primary description.

### 2. Learning goals

Keep the conceptual goals for providers, models, messages, system instructions,
streaming, tools, tool results, and a CLI.

Replace the first goal with a Cargo-based Rust application goal. Add only the
Rust concepts required by the application, such as:

- `Result` and error propagation;
- enums and `match` for stream chunks;
- ownership of conversation history;
- asynchronous execution with Tokio.

Do not turn the course into a general Rust course. Explain these concepts when
the GDK use case first requires them.

### 3. Roadmap and status

The conceptual sequence can remain:

1. project bootstrap;
2. provider configuration and connectivity;
3. first streaming request;
4. system instructions, roles, and multi-turn history;
5. explicit model selection;
6. defining a provider tool;
7. executing tools and returning results;
8. command-line interface, configuration, and error handling.

Required changes:

- Lesson 1 becomes a Cargo/Rust bootstrap.
- “Click CLI” becomes a generic CLI until a Rust argument parser is selected.
- Do not copy Python statuses. Begin migrated lessons as **Draft** and promote
  them only after Rust validation.
- Set the active lesson from the actual new repository state, not from the
  source repository's Lesson 4 state.

### 4. Repository organization

Remove Python-specific paths and files:

- `src/gdk_hello/`
- `__init__.py`
- `pyproject.toml`
- `uv.lock`

Use Rust equivalents:

- `src/main.rs`
- `Cargo.toml`
- committed `Cargo.lock`
- optionally `rust-toolchain.toml`

Decide before writing final commands whether lesson solutions are independent
Cargo packages or workspace members. Two viable models are:

#### Option A: independent lesson packages

Each lesson has its own `Cargo.toml`, `Cargo.lock`, and `src/main.rs`.

- Advantage: every solution is independently runnable and explicit.
- Cost: repeated manifests and lockfiles must be updated together.

#### Option B: one workspace

The root exercise and lesson solutions are workspace packages with one lockfile.

- Advantage: one dependency resolution and easier whole-course checks.
- Cost: package names and `cargo run -p ...` commands add workspace concepts
  before the curriculum needs them.

**Recommendation:** use a single root binary package for the active exercise and
perform a short spike with one lesson snapshot before choosing. Prefer the
simplest model that makes every documented lesson command reproducible.

A likely non-workspace shape is:

```text
.
├── src/
│   └── main.rs
├── lessons/
│   ├── 01-bootstrap/
│   │   ├── LESSON.md
│   │   ├── Cargo.toml
│   │   └── src/main.rs
│   └── ...
├── instructor-notes/
├── custom_aa_llama_qwen3_6-35b.json
├── .env.example
├── .gitignore
├── AGENTS.md
├── Cargo.toml
├── Cargo.lock
├── README.md
├── RUST_MIGRATION_PLAN.md
└── rust-toolchain.toml
```

### 5. Prerequisites and setup

Replace:

- Python 3.11+
- `uv`
- `uv sync`
- virtual-environment instructions

With:

- the tested Rust toolchain;
- Cargo;
- any native build prerequisites discovered by the clean build spike;
- the exact build or fetch command used by the course.

For the initial `0.1.0-alpha.9` spike, test Rust `1.94.1`. Do not claim a lower
minimum version without proving it.

Document `Cargo.lock` as the reproducible dependency resolution for this
application/course repository. Update `Cargo.toml` and `Cargo.lock` together.

### 6. GDK dependency policy

The initial manifest should use the public `goose-sdk`, enable `uniffi`, and pin
an exact alpha version. Verify the final manifest with Cargo rather than copying
an untested example from this plan.

Do not build the course against:

- a moving `main` branch;
- the large internal `goose` application crate;
- internal `goose-providers` types when the public GDK bindings provide the
  required operation.

If a missing capability forces use of an internal crate, stop and get an
explicit architecture decision from the instructor and Goose developers. Record
why the public GDK is insufficient and pin an exact revision.

### 7. Provider configuration

The high-level README guidance can remain. The official GDK loads declarative
provider JSON with `declarative_provider_from_json`, and environment-variable
placeholders are resolved when the provider is constructed.

Before reusing the bundled JSON unchanged:

1. Parse it with Rust `goose-sdk` `0.1.0-alpha.9`.
2. Construct the provider successfully.
3. Validate the exact `base_url`/`base_path` behavior against the live endpoint.
4. Verify authentication, headers, model names, and streaming.
5. Compare it with the current official custom-provider schema.

Do not hand-maintain a parallel Rust version of Goose's provider schema. It is
reasonable to parse only the small subset needed by course logic—for example,
the first configured model—while passing the original JSON string to the GDK.

### 8. Provider path and model selection

Replace Python commands such as:

```text
uv run python -m src.gdk_hello.main [provider.json]
```

With the tested Rust command shape. Before a dedicated CLI lesson, that will
probably be:

```text
cargo run -- [provider.json]
```

The `--` separates Cargo arguments from application arguments.

Keep the initial “first model in the provider JSON” simplification. In Rust,
parse the model name separately and construct `ProviderModelConfig`; provider
construction itself does not select the first model implicitly.

### 9. API keys and `.env`

Remove `python-dotenv` references.

Choose one of these policies and use it consistently:

- read secrets from the process environment and ask learners to export them; or
- load `.env` with one selected Rust crate before constructing the provider.

The Goose workspace uses `dotenvy`, making it a plausible choice, but that does
not make it mandatory for this course. Select and test it deliberately.

Retain `.env.example`, ignore `.env`, and never place real credentials in
provider JSON.

### 10. Running and expected behavior

Replace every `uv run python ...` command with its tested Cargo equivalent.
Rewrite the active-exercise paragraph from the actual Rust checkpoint.

Keep these expectations:

- the provider endpoint must be running;
- output is nondeterministic;
- streaming success is structural;
- usage is optional because not every provider reports it.

### 11. Validation philosophy

Keep the current philosophy and replace Python checks with the narrowest
applicable Rust checks:

```text
cargo fmt --check
cargo check
cargo clippy --all-targets
cargo test
cargo run -- [lesson arguments]
```

Do not automatically use `--all-features`: enabling every dependency feature
can compile unrelated GDK functionality and increase classroom build cost.
Likewise, do not make all warnings fatal until that policy is proven stable with
the pinned toolchain and SDK.

For provider lessons, additionally run the documented command against a live
provider and report exactly what was and was not exercised.

### 12. Troubleshooting

Keep the existing categories but translate them:

- Provider config not found: explain process working directory and the Cargo
  invocation from repository root.
- Provider unreachable: keep endpoint/server/firewall checks.
- Configured model missing: compare provider model IDs with configured names.
- Authentication failure: check the configured environment-variable name and
  whether `.env` was loaded before provider construction.
- Add Rust build failures: wrong toolchain, stale lockfile, missing native build
  prerequisite, or missing GDK feature.

The current Lesson 2 manually requests `/v1/models`. Reassess that exercise in
Rust rather than translating `urllib` literally. If it remains a direct HTTP
smoke test, choose a Rust HTTP client deliberately and ensure it honors the
provider's authentication and custom headers.

### 13. Maintainer guidance and references

Retain the summary directing maintainers to `AGENTS.md`.

Replace the Python package reference with:

- official GDK SDK overview and API reference;
- exact tagged `goose-sdk` source and changelog;
- crates.io release page;
- official provider configuration documentation.

## `AGENTS.md` analysis and required changes

### Project purpose

Replace “custom Python agentic application” and Python-package wording with a
custom Rust application using the exact pinned public `goose-sdk` crate.

Keep the instructor-led priority and the statement that this is not a Goose CLI
wrapper or Goose extension.

### Read before changing anything

Keep the current workflow, but make it Rust-specific:

1. Read `README.md`.
2. Inspect Git status and preserve unrelated work.
3. Read `Cargo.toml`, `Cargo.lock`, and `rust-toolchain.toml` when present.
4. Read the active root Rust source.
5. Read the relevant lesson, complete solution, and instructor notes.
6. Read the provider JSON used by the lesson.
7. For GDK behavior, read the official documentation and source for the exact
   pinned `goose-sdk` version.

### Repository model and pedagogy

Preserve these sections almost unchanged. Replace only Python paths and Click
terminology. Use “command-line interface” until a parser is selected.

Add one Rust-specific caution:

> Do not introduce ownership, traits, generic abstractions, workspaces, or async
> machinery before the active lesson needs them. Use the simplest Rust that
> accurately expresses the pinned GDK API.

### Provider and model conventions

Keep the existing conceptual rules, but change them only after the provider JSON
is validated with the Rust crate.

Replace Click sequencing with:

- a default provider path and optional positional override before the CLI
  lesson;
- a named `--provider` option after the selected Rust CLI parser is introduced.

Keep the first-model simplification and later `--model` validation.

Replace `python-dotenv` with the selected environment policy. Continue to ban
committed `.env` files and credentials.

### Development environment

Replace the entire Python/`uv` block with rules such as:

- Target Linux initially.
- Use the toolchain pinned by `rust-toolchain.toml` when present.
- Use Cargo for dependency changes, builds, locking, running, and tests.
- Commit `Cargo.lock` for this application/course repository.
- Update manifests and the lockfile together.
- Pin an exact alpha GDK version; do not use moving branches.
- At a course release, tag the exact validated source and dependency resolution.
- Keep one dotenv approach if application-level `.env` loading is used.

Do not state the MSRV as a timeless course property. Tie it to the pinned GDK
release and revise it intentionally during upgrades.

### Validation

Replace “After changing Python” with:

> After changing Rust source, manifests, lockfiles, or configuration, run the
> narrowest relevant formatting, compilation, lint, and test checks, followed by
> the lesson's documented command.

Recommended internal sequence:

1. `cargo fmt --check`
2. `cargo check`
3. `cargo clippy --all-targets`
4. `cargo test`
5. documented `cargo run` command
6. live-provider check when required

The learner-facing lesson need only show the checks relevant to its goal.

### Repository hygiene

Replace Python artifacts with Rust artifacts:

```gitignore
/target/
.env
/.idea/
/out/
```

Do not ignore `Cargo.lock` for this application/course repository. Remove
`.venv`, `__pycache__`, and `*.pyc` rules unless the new repository retains
Python helper scripts that actually produce them.

Use “Cargo package, crate, binary, and module names” where the old guidance says
only “package names.”

### Documentation, self-study, and instructor authority

These sections are language-independent and should remain. Update paths and
commands only. When tutoring, do not let Rust compiler errors cause the tutor to
skip ahead into later architecture; explain the smallest concept needed to
unblock the active lesson.

## API translation guide

The following mappings are verified for `goose-sdk` `0.1.0-alpha.9`. Re-check
all names when upgrading.

| Python course construct | Rust GDK construct or pattern |
|---|---|
| `from goose import ...` | Import public types from `goose_sdk::bindings` |
| `declarative_provider_from_json(provider_json)` | Same function name; Rust passes an owned `String` and receives an `Arc<Provider>` inside `Result` |
| `ProviderModelConfig(model_name=...)` | `ProviderModelConfig { model_name, ..Default::default() }` |
| `ProviderMessage(...)` | `ProviderMessage { role, content }` |
| `MessageRole.USER` | `MessageRole::User` |
| `MessageRole.ASSISTANT` | `MessageRole::Assistant` |
| `MessageRole.TOOL` | `MessageRole::Tool` |
| `MessageContent.TEXT(text=...)` | `MessageContent::Text { text }` |
| `await provider.stream(...)` | `.stream(model, system, messages, tools).await?` |
| `while chunk := await stream.next_chunk()` | `while let Some(chunk) = stream.next_chunk().await?` |
| `isinstance(chunk, StreamChunk.TEXT_CHUNK)` | `match` or `if let StreamChunk::TextChunk { text }` |
| `StreamChunk.END_CHUNK` | `StreamChunk::EndChunk { usage }` |
| `StreamChunk.ERROR_CHUNK` | `StreamChunk::ErrorChunk { error }` |
| Python exceptions | `Result`, `?`, and intentional user-facing context |
| `asyncio.run(main())` | Tokio async entry point, as used by the official Rust quickstart |
| Python list of messages | `Vec<ProviderMessage>` |
| append streamed text fragments | append to a `String` or collect fragments while printing |

Additional verified public types include:

- `ProviderTool`, containing a name, description, and JSON input schema;
- `MessageContent::ToolRequest` and `MessageContent::ToolResult`;
- `StreamChunk::ToolChunk`;
- `ThinkingChunk` and `RedactedThinkingChunk`;
- `Usage` on `EndChunk` when the provider reports it;
- `GooseError` before stream startup and `GooseStreamError` in a mid-stream
  `ErrorChunk`.

Important semantic details:

- System instructions remain a separate `String` argument to `stream`; they are
  not conversation messages.
- `next_chunk()` returns `Result<Option<StreamChunk>, GooseError>`.
- A normal stream emits `EndChunk` and a later `next_chunk()` returns `None`.
- Mid-stream provider failures are represented by `ErrorChunk`; setup/read
  failures can still be returned as `Err`.
- The SDK exposes `complete()` as well as `stream()`. Do not replace a streaming
  lesson with `complete()` merely because it makes history easier.
- Multi-turn streaming still requires accumulating assistant content so it can
  be appended to history.

## Migration phases

### Phase 0: prove the foundation

Create a disposable Rust spike before drafting full lessons.

- [ ] Install/test Rust `1.94.1`.
- [ ] Create a minimal binary crate.
- [ ] Add exactly pinned `goose-sdk` with `uniffi`.
- [ ] Add the Tokio features required by the official quickstart.
- [ ] Load the existing provider JSON.
- [ ] Select its first configured model.
- [ ] Make one streamed request against a live provider.
- [ ] Observe text and a normal `EndChunk`.
- [ ] Record clean-build time and native prerequisites.
- [ ] Decide independent lesson packages versus a workspace.
- [ ] Decide process environment versus one Rust dotenv crate.

Do not proceed on the assumption that compiling alone proves provider
compatibility.

### Phase 1: create the repository contract

- [ ] Create the new repository and license.
- [ ] Add `Cargo.toml`, `Cargo.lock`, and the chosen toolchain file.
- [ ] Add Rust `.gitignore` rules.
- [ ] Copy only safe provider examples and `.env.example`.
- [ ] Adapt `README.md` and `AGENTS.md` using this analysis.
- [ ] Reset roadmap statuses to the actual Rust state.
- [ ] Add CI only after local commands are stable; do not make CI a learner
  topic by accident.

### Phase 2: migrate Lesson 1

- [ ] Teach the minimum Cargo binary structure.
- [ ] Replace the Python hello world with `src/main.rs`.
- [ ] Document the clean run command and expected output.
- [ ] Validate from a fresh clone or clean checkout.

### Phase 3: migrate provider configuration and smoke test

- [ ] Load `.env` according to the chosen policy.
- [ ] Read and pass provider JSON to the GDK.
- [ ] Decide whether `/v1/models` remains a direct HTTP exercise.
- [ ] If direct HTTP remains, preserve authentication and custom headers.
- [ ] Validate the configured model set against a live endpoint.
- [ ] Keep the bundled endpoint/model replaceable.

### Phase 4: migrate streaming

- [ ] Construct typed messages and model configuration.
- [ ] Handle text, end, and error variants explicitly.
- [ ] Confirm text was observed.
- [ ] Confirm normal completion was observed.
- [ ] Print usage only when present.
- [ ] Validate against a live provider.

### Phase 5: migrate conversation

- [ ] Keep system instructions separate.
- [ ] Accumulate the first streamed assistant response.
- [ ] Append assistant and follow-up user messages in order.
- [ ] Make the second request with the complete history.
- [ ] Avoid unnecessary cloning or abstractions in learner code.

### Phase 6: migrate future lessons one at a time

For model selection, tools, tool results, and CLI:

- [ ] Confirm the exact pinned API before writing lesson prose.
- [ ] Create the complete reference solution first.
- [ ] Write incremental learner instructions around that validated solution.
- [ ] Update instructor notes and roadmap in the same change.
- [ ] Validate structural behavior and live-provider behavior where applicable.

## Risk register

| Risk | Mitigation |
|---|---|
| Alpha API changes | Exact version pin, committed lockfile, tagged source links, deliberate upgrade checklist |
| Documentation tracks newer `main` than crates.io | Use docs/API selector for the pinned release and tagged source as final authority |
| Rust build complexity overwhelms early lessons | Prove clean build first; pin toolchain; avoid internal Goose crates and unnecessary features |
| Workspace structure becomes a hidden prerequisite | Decide packaging after a one-lesson spike and document every command explicitly |
| Direct model smoke test ignores auth/headers | Either use a supported GDK capability or reproduce provider auth and headers intentionally |
| Python status is mistaken for Rust readiness | Reset migrated lessons to Draft and revalidate independently |
| Provider JSON drifts | Keep one reviewed example and validate it with both the pinned GDK and a live endpoint |
| Tool round trip differs from assumptions | Build a minimal tool spike before writing the tool lessons |
| `.env` behavior is inconsistent | Choose exactly one policy and load environment values before provider construction |
| `main` is used as a dependency | Ban moving branches; use an exact published version or, by explicit exception, an exact Git revision |

## Definition of migration complete

Delete this file only when all of the following are true:

- [ ] The new repository has an intentional, recorded source-course commit.
- [ ] `README.md` contains no Python, `uv`, PyPI, Click, or
  `src/gdk_hello/` instructions except deliberate historical notes.
- [ ] `AGENTS.md` contains Rust/Cargo development and validation guidance.
- [ ] The exact GDK version and Rust toolchain are pinned and documented.
- [ ] `Cargo.lock` is committed.
- [ ] Every implemented lesson has a complete, runnable Rust solution.
- [ ] Every implemented lesson's prose, source, instructor notes, and roadmap
  status agree.
- [ ] Formatting, compilation, linting, and tests pass from a clean checkout.
- [ ] Every provider-calling lesson has been exercised against a real provider,
  or its lack of live validation is explicitly recorded.
- [ ] Provider JSON, authentication, model selection, streaming end semantics,
  and usage handling are validated.
- [ ] Tool definition and tool-result round trip are validated before those
  lessons are marked Complete.
- [ ] No credentials, `.env`, build output, or source-repository artifacts were
  copied into the new repository.
- [ ] Durable decisions from this file have moved into `README.md`, `AGENTS.md`,
  lesson material, or instructor notes.

## Authoritative references used

Goose-specific claims in this plan were checked against these official sources:

- [GDK SDK overview](https://goose-docs.ai/docs/gdk/sdk)
- [GDK SDK API reference](https://goose-docs.ai/docs/gdk/sdk/api-reference)
- [`goose-sdk` 0.1.0-alpha.9 tagged manifest](https://github.com/aaif-goose/goose/blob/gdk-v0.1.0-alpha.9/crates/goose-sdk/Cargo.toml)
- [`goose-sdk` 0.1.0-alpha.9 tagged Rust API](https://github.com/aaif-goose/goose/blob/gdk-v0.1.0-alpha.9/crates/goose-sdk/src/bindings.rs)
- [`goose-sdk` 0.1.0-alpha.9 tagged SDK guide](https://github.com/aaif-goose/goose/blob/gdk-v0.1.0-alpha.9/documentation/docs/gdk/sdk/index.md)
- [`goose-sdk` 0.1.0-alpha.9 release metadata](https://docs.rs/crate/goose-sdk/0.1.0-alpha.9)
- [Configure LLM Provider](https://goose-docs.ai/docs/getting-started/providers)

When these sources disagree, use the API and manifest from the exact pinned tag
for code, and treat newer documentation as upgrade guidance rather than as the
current course contract.
