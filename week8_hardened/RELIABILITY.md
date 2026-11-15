# Reliability design and measurement limits

- HTTP requests retry network errors, rate limits and selected server errors with bounded
  exponential backoff and jitter. Invalid requests are not retried indefinitely.
- Optional fallback model names may be configured; they must already be installed.
- A SQLite cache keys responses by endpoint, full request, model, schema and options.
  Tool calls bypass the cache. Completed streaming answers can be cached; interrupted ones cannot.
- Usage logs record model, request latency, token counts and cache hits, without raw prompts.
- Empty inputs, unsupported files, empty/scanned PDFs, invalid tools and missing dependencies
  produce explicit errors. Agent steps and tool calls have limits.
- Cost reporting projects measured token averages to 30,000 requests/month. Local provider
  API charges are zero; electricity, hardware and server costs are excluded, not claimed free.

Offline tests exercise request protocol and deterministic behavior with simulated responses.
They do not establish LLM answer quality, real inference latency, actual provider behavior,
Chroma integration or deployment success. Live measurements are generated only after setup.
