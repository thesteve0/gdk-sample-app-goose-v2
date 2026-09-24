# Lesson 1 Instructor Notes: Project Bootstrap

## Teaching objective

Give learners a clean, understandable Python project before introducing provider or inference concepts. Students should leave the lesson able to identify the package layout, dependency manifest, environment template, and command used to run the package.

## Suggested pacing

- Course orientation and GDK-versus-Goose distinction: 5 minutes
- Walk through `pyproject.toml`: 10 minutes
- Create and explain the `src/` package layout: 10 minutes
- Create the environment and run the placeholder: 10 minutes
- Review and questions: 5 minutes

Adjust for the class’s Python and `uv` experience. The lesson is a small conceptual unit, not necessarily a complete class session.

## Before class

- Verify the documented Python and `uv` versions work on the classroom Linux environment.
- Run `uv sync` from a clean checkout.
- Confirm the committed `uv.lock` resolves on the target machines.
- Decide whether students will clone during class or arrive with the repository and dependencies prepared.

## Discussion prompts

- Why use a `src/` layout instead of putting a module at the repository root?
- What does the build backend do, and what does it not do?
- Why does the package install as `goose` even though the distribution is named `goose-sdk`?
- Which files may contain secrets, and why is `.env` ignored?

## Live-demo cautions

- Run commands from the repository root.
- Do not spend lesson time teaching linting, formatting, or packaging internals beyond what learners need for the course.
- The repository may be newer than the text in this lesson snapshot. Check dependency versions and commands before teaching it.
- Avoid implying that the current package name is permanent; it may evolve with the course.

## Checkpoint

Learners can run the lesson’s documented command and explain the roles of `pyproject.toml`, `uv.lock`, `src/gdk_hello/`, and `.env.example`.
