I want to build a Goose Development Kit (GDK) Python hello-world CLI app together, step by step, in small interactive pieces so I can learn how GDK works and best practices for building agentic apps with the GDK harness. This is NOT using the Goose application framework or the existing CLI. This is a custom agentic application. 
- GDK overview & Quickstart: https://goose-docs.ai/docs/gdk/ – install, Python quickstart with `openai_provider`, `ProviderModelConfig`, `ProviderMessage`, `stream` loop.
- GDK API Reference: https://goose-docs.ai/docs/gdk/api-reference/ – official types: `Provider`, `ProviderStream.next_chunk`, `ProviderTool`, `StreamChunk` variants `TextChunk`/`ToolChunk`/`EndChunk`/`ErrorChunk`, `MessageContent` enum with `ToolRequest`/`ToolResult`.
- PR #11251 docs: https://github.com/aaif-goose/goose/pull/11251 – confirms SDK API reference for Rust/Python/Kotlin generated from `crates/goose-sdk/src/bindings.rs`.
- Example project: https://github.com/jamadeo/lifewiki – a real GDK agentic app showing project layout, agent-driven build/ask pipeline, and use of `goose-agent/goose-providers`.


Context
- Working directory: current directory
- Start from an empty repo / clean state. We will create files incrementally. Each lesson will get it's own directory and will build off the previous directory
- Goal: a minimal Python CLI that uses goose-sdk to call an OpenAI API local model with a user prompt and can perform a simple tool call.
- I want to learn, not just have you produce code. The highest goal of this project is a tutorial and building my skills and understanding. After each step, explain what we did and why, and ask me before moving to the next step. I want to write the code so I build muscle memory and actually have to dig in. 

** Be sure to ask me questions or clarify any uncertainties directly with me rather than assuming. Do not proceed until I have clarified your question or concern sufficiently **

DO NOT PROCEED TO BUILD ANYTHING YET - we are working together so you are clear on what I want. I will give you constratints and a possible learning path in further chat. Do you understand?

--------------

Constraints for this session
- We will use the installed python sdk but use `uv` to create the venv and manage packages through `uv add`
- Build in tiny increments: one file or one concept per turn.
- Always explain GDK concepts: Provider, ProviderModelConfig, ProviderMessage/MessageContent/MessageRole, ProviderStream, StreamChunk types, ProviderTool, tool call round-trip...
- Prefer the official GDK docs as source of truth: https://goose-docs.ai/docs/gdk/
- Use the Python SDK `goose-sdk` which imports as `goose`. Follow the Quickstart pattern from the docs.
- Keep best practices: project layout with src/, pyproject.toml, .env for OPENAI_API_KEY, small pure functions, clear separation of CLI vs agent logic.
- Do not scaffold the whole app at once. Start with project init, then dependencies, then provider creation, then streaming, then tool definition, then tool handling.

Proposed learning path
1. Project bootstrap: git init, pyproject.toml with goose-sdk, click, python-dotenv, src layout.
2. Minimal provider smoke test: create a script that connects to the local model and validates it is configured properly.
3. First streaming call: build ProviderModelConfig, ProviderMessage, stream a simple prompt, print TextChunk.
4. System prompt and message roles: show how system + user messages flow.
5. Add a simple tool definition: ProviderTool with name, description, input_schema_json for get_current_time.
6. Handle ToolChunk: detect tool request, execute local function, show how to continue the conversation with ToolResult messages.
7. CLI wrapper with click, env loading, and error handling.

Start with step 1, show me the exact commands to execute files to create, explain why each choice matters for GDK apps, and wait for my confirmation before proceeding.
```

---

**Items that will be extremely helpful for you in building this curriculum**

- GDK overview & Quickstart: https://goose-docs.ai/docs/gdk/ – install, Python quickstart with `openai_provider`, `ProviderModelConfig`, `ProviderMessage`, `stream` loop.
- GDK API Reference: https://goose-docs.ai/docs/gdk/api-reference/ – official types: `Provider`, `ProviderStream.next_chunk`, `ProviderTool`, `StreamChunk` variants `TextChunk`/`ToolChunk`/`EndChunk`/`ErrorChunk`, `MessageContent` enum with `ToolRequest`/`ToolResult`.

