# Agent trace and memory

The agent exposes only three allowlisted tools: document search, fictional ticket lookup,
and bounded arithmetic. Tool arguments are validated. The calculator evaluates a restricted
syntax tree; it does not use eval or execute arbitrary code. Email text is drafted, never sent.

Conversation memory is an in-memory message history for one session. The recorded follow-up
tests whether information from the first task is reused. It is not long-term persistent memory.
The loop stops after six model steps or twelve tool calls, and history is bounded.

`agent_run_and_memory.json` records requests, tool actions, observations and final answers.
It deliberately does not log private internal chain-of-thought. This public execution trace
provides reviewable evidence of what the tools actually did. A completed agent response
without the required tool calls is not counted as a successful multi-tool demonstration.
