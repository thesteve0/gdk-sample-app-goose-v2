# Lesson 3 Instructor Notes: Streaming Call

## Teaching objective

Introduce the first inference request while keeping message construction and roles to the minimum needed for per-request model selection, asynchronous streaming, and structural chunk handling. Lesson 4 revisits messages and system instructions in depth.

## Suggested pacing

- Review provider setup and first-model selection: 5 minutes
- Construct `ProviderMessage` and discuss roles/content: 15 minutes
- Explain `ProviderModelConfig` and `provider.stream(...)`: 10 minutes
- Walk through the asynchronous chunk loop: 15 minutes
- Run, inspect usage, and review: 10 minutes

## Before class

- Complete the Lesson 2 connectivity check against the provider you will use.
- Make one full streaming request and confirm the current pinned SDK’s Python variant names.
- Confirm the provider supports streaming and returns text.
- Check that the chosen model can answer promptly enough for a live demonstration.
- Review the lesson prose against its complete `src/` solution; this lesson is still a draft and may contain stale wording.

## Discussion prompts

- Why is model selection per request even though models are declared by the provider?
- Why is message content represented as a list?
- Why are text, completion metadata, and errors represented as different chunk variants?
- Why should streamed text go to stdout while diagnostics go to stderr?
- What does an end chunk prove that receiving one text chunk does not?

## Live-demo cautions

- Generated wording is nondeterministic. Validate structure, not a specific answer.
- Streaming output may appear buffered if printing does not flush.
- A model advertised by the endpoint may still fail during inference because of server capacity, unsupported options, or provider incompatibility.
- Do not introduce tool chunks in detail yet; identify them only as a later lesson topic.
- Avoid broad exception handling without explaining what information it preserves or obscures.

## Checkpoint

Learners receive streamed text, observe normal stream completion, and can identify the provider, selected model, system instruction, user message, stream, and handled chunk types in the code.
