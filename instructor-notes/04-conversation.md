# Lesson 4 Instructor Notes: System Instructions and Conversation History

## Teaching objective

Make the request boundary explicit. Learners should understand that the system instruction and ordered message history are inputs to each provider call, and that streamed assistant text must be reconstructed before it can become an assistant turn in a later request.

## Suggested pacing

- Contrast system instructions with user messages: 10 minutes
- Refactor Lesson 3 streaming into a text-returning helper: 15 minutes
- Add the assistant and follow-up user turns: 15 minutes
- Run both requests and inspect the ordered history: 10 minutes
- Review and questions: 5 minutes

## Before class

- Validate Lesson 3 against the provider that will be used in class.
- Run the Lesson 4 reference solution and confirm two requests complete promptly.
- Choose short prompts and a concise system instruction so local inference does not dominate class time.
- Confirm the provider preserves ordinary user/assistant history for the selected model.
- Review the lesson prose against its complete `src/` solution.

## Discussion prompts

- What behavior belongs in a system instruction rather than a user message?
- Why does the second request include the first user message as well as the assistant reply?
- What information would be lost if only the follow-up user message were sent?
- Why does the helper both print and return streamed text?
- Why should the course validate message ordering rather than exact generated wording?

## Live-demo cautions

- Models may ignore length instructions. Treat concision as an observable prompt effect, not a deterministic assertion.
- The second request resends earlier text and therefore uses more input tokens.
- Do not imply that the provider object stores application conversation history between these calls; point to the explicit `messages` argument.
- Keep `MessageRole.TOOL` conceptual until the tool-result lesson.
- Avoid adding an interactive input loop here. Two fixed turns make message ordering visible and keep this lesson focused.
- If inference is slow, shorten the first prompt or system instruction rather than skipping the second live provider call.

## Checkpoint

Learners can distinguish the system instruction from user and assistant messages, reconstruct the first streamed reply, append it with the correct role, and make a follow-up request with all prior turns in order.
