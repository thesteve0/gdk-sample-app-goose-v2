# AGENTS.md

Guidance for coding agents and for Goose when assisting learners in **Building Agentic Applications with the Goose GDK**.

## Project purpose

This repository is an evolving, instructor-led course for building a custom Python agentic application with the Goose Development Kit (GDK). It uses the `goose-sdk` package directly; it is not an extension of the Goose application or a wrapper around the Goose CLI.

Optimize first for a live class taught by an instructor. Goose-assisted self-study is useful, but secondary.

## Read before changing anything

1. Read `README.md`.
2. Inspect `git status` and preserve all unrelated staged and unstaged work.
3. Read the active root implementation under `src/gdk_hello/`.
4. Read the relevant `lessons/<number>-<topic>/LESSON.md` and its complete `src/` solution.
5. Read the corresponding file in `instructor-notes/`, when one exists.
6. Read the provider JSON used by the active lesson.
7. For any Goose- or GDK-specific API, field, type, command, or behavior, consult current official documentation or the pinned SDK source. Do not rely on memory.

## Repository model

- `src/gdk_hello/` is the exercise currently being developed. It may be incomplete.
- `lessons/` contains numbered instructional units.
- A lesson’s `LESSON.md` contains explanations and only important snippets.
- A lesson’s `src/` contains its complete reference solution from the outset.
- Do **not** copy root source into a lesson directory at lesson completion. The solution is already there.
- `instructor-notes/` contains one instructor guide per implemented lesson.
- Lessons are living material. Correct them when the SDK changes, an error is found, or teaching experience suggests a clearer approach.

## Pedagogy and scope

- Make changes in small, concept-focused increments.
- Introduce only the concepts required by the active lesson.
- Explain why a GDK abstraction is needed, not only how to type it.
- Preserve opportunities for learners to write and reason about code.
- Do not scaffold the final application or future lessons prematurely.
- Ask the instructor before making uncertain curriculum, sequencing, or architecture decisions.
- Lessons are small conceptual units; several may fit in one workshop session.
- Keep the roadmap status table in `README.md` current when lesson state or ordering changes.

The evolving direction includes providers, model selection, messages, streaming, system instructions, tools, the tool-result round trip, and a Click CLI. The roadmap is not constrained to a fixed number of lessons.

## Lesson requirements

Every implemented `LESSON.md` should include:

- A clear goal.
- Concepts introduced.
- Prerequisites.
- Incremental instructions.
- Important illustrative snippets, but not an unnecessary duplicate of the full solution.
- A run or validation command.
- Expected structural behavior.
- Explicit success criteria.
- The conceptual next step.

Keep lesson prose, its `src/` solution, root workflow, and instructor notes consistent. If code behavior changes, update every affected explanation in the same change.

Do not add deliberate failure-path exercises yet. They may be introduced after the course has been taught and evaluated several times.

## Provider and model conventions

- Provider JSON is the source of truth for provider endpoint, authentication behavior, model declarations, and provider capabilities.
- The bundled provider JSON is a replaceable default, not a required service or model.
- Learners copy and modify an existing valid provider JSON; they are not expected to author the full configuration format from scratch. Link to the official fields and examples.
- Before Click is taught, keep a default provider path in source and allow an optional positional path override.
- When Click is introduced, replace that interface with a named `--provider` option.
- Initially select the first configured model and explain that simplification.
- Introduce `--model` in a dedicated later lesson and validate it against models declared in the provider JSON.
- Preserve room for applications that call multiple models.
- Never hardcode the included Qwen model or llama.cpp as a universal requirement.

For providers using static API-key authentication, provider JSON identifies the API-key environment variable and `.env` supplies its value. Official custom providers may also support other authentication mechanisms; introduce those only when the curriculum calls for them. Use `python-dotenv`; never commit `.env`, credentials, or secret-bearing provider files.

Official custom-provider reference: <https://goose-docs.ai/docs/getting-started/providers#configure-custom-provider>

## Development environment

- Target Linux for now.
- Require Python 3.11 or newer.
- Use `uv` for environments, dependency changes, locking, and command execution.
- Use `python3`, never `python`, for direct interpreter commands outside `uv run`.
- Keep one dotenv implementation: `python-dotenv`.
- Commit `uv.lock`.
- During course development, update dependencies and the lockfile together.
- At a course release, pin the tested Goose SDK and lock dependencies for the release tag.
- A full dev-container workflow is a future goal, not a current assumption.

The course should support either an instructor-provided endpoint or a learner-run compatible provider. Learners running llama.cpp must choose a model appropriate for their hardware.

## Validation

- Prefer validation against a real, live provider whenever a lesson makes provider calls.
- If a required provider is unavailable, ask the instructor to start or supply one. Do not substitute mocked success for live validation without approval.
- Offline tests are useful for pure logic but are lower priority than end-to-end provider behavior.
- Because model responses are nondeterministic, assert structural outcomes rather than exact generated text.
- Use formatting, linting, type checking, and tests internally when useful, but do not turn those tools into course topics unless the instructor changes the curriculum.
- After changing Python or configuration files, run the narrowest relevant checks and the lesson’s documented command.
- Report exactly what was and was not validated.

## Documentation rules

- `README.md` is the comprehensive, navigable course landing page.
- Keep lesson-specific details in the relevant `LESSON.md`.
- Keep instructor-only advice in `instructor-notes/`.
- Call this material a “course” or “workshop.”
- External links are supplemental; core lesson instructions must stand on their own once setup is complete.
- Do not add contribution guidance unless the instructor asks; the project is not currently soliciting contributions.
- Use uppercase `AGENTS.md` for this file.
- Before documenting Goose-specific syntax or behavior, verify it against official documentation. Cite the authoritative page where it benefits the learner.

## Repository hygiene

- Never overwrite unrelated user changes.
- Do not edit generated caches, virtual environments, IDE metadata, or build output.
- Keep `.idea/`, `out/`, `.venv/`, `.env`, Python caches, and similar artifacts untracked.
- Do not restore removed planning documents after their durable guidance has moved into `README.md` and this file.
- Keep numeric prefixes on lesson directories.
- Package names must remain internally consistent, but may evolve with instructor approval as the course develops.

## Goose-assisted self-study mode

Use this mode only when a learner asks Goose to guide them through the course. Normal repository maintenance does not need to pause after every small change.

When tutoring:

1. Ask which lesson the learner is taking and confirm their provider setup.
2. Read that lesson, its solution, and the active root state, but do not reveal the complete solution prematurely.
3. Explain one concept or assign one small implementation step at a time.
4. Ask the learner to write or run the step.
5. Wait for their result or explicit approval before advancing.
6. Diagnose the observed output and use the lesson’s success criteria as checkpoints.
7. Prefer hints and focused snippets over replacing the learner’s entire file.
8. Do not introduce concepts from later lessons unless needed to unblock the current one.
9. Ask clarifying questions instead of assuming the bundled provider, endpoint, model, or hardware is available.
10. Encourage the learner to understand and type the code so they develop practical fluency.

## Instructor authority

The instructor owns curriculum scope, sequencing, and release decisions. When these instructions conflict with an explicit instructor request, follow the request, note the deviation when relevant, and update the course documentation if the decision is durable.