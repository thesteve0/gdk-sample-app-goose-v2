# Lesson 2 Instructor Notes: Provider Smoke Test

## Teaching objective

Separate provider configuration and connectivity from model inference. Learners should understand that parsing a declarative provider configuration, discovering advertised models, and generating a response are distinct checks.

## Suggested pacing

- Review the provider JSON: 10 minutes
- Explain configuration parsing versus network activity: 10 minutes
- Walk through the OpenAI-compatible model-list request: 10 minutes
- Run the smoke test and interpret output: 10 minutes
- Review and questions: 5 minutes

## Before class

- Ensure either the shared endpoint is available or local llama.cpp setup instructions have been completed.
- Test the included provider JSON against the endpoint you will demonstrate.
- Confirm the advertised model ID exactly matches the JSON model name.
- Have an alternate, hardware-appropriate model configuration ready if the bundled example is unsuitable.
- Check whether the active root exercise accepts the planned positional provider path yet; teach the actual implemented interface.

## Discussion prompts

- What does `declarative_provider_from_json(...)` validate locally?
- Why does a successful model-list request not prove that inference works?
- Why should provider JSON, rather than `.env`, define the endpoint and model list?
- What could cause a configured model name not to match the server’s advertised ID?

## Live-demo cautions

- Provider availability is part of this lesson’s validation. If none is running, stop and start or obtain one rather than replacing the demonstration with a mock.
- A local server may need startup time before the endpoint responds.
- Relative provider paths require running from the repository root.
- This lesson derives `{base_url}/v1/models` directly and does not yet apply configured authentication, custom headers, or alternate base paths. Use an equivalent unauthenticated endpoint for the demonstration.
- Never display or commit a real API key. Use `.env` for authenticated-provider credentials.
- The included provider and 35B model are examples, not requirements.

## Checkpoint

Learners can run the smoke test, see at least one advertised model, and explain the difference among parsing configuration, reaching an endpoint, discovering models, and performing inference.
