# Test plan

## Automated offline checks
Run `python -m unittest discover -s tests -v`. These tests use simulated model HTTP responses
only where needed to test the protocol. They are not real inference demonstrations. Coverage
includes chunking, file validation, safe tools, structured-output validation, citation-number
checking, retries, cache separation, streaming completion and bounded agent behavior.

## Required live checks
| Test | Expected behavior | Status |
| --- | --- | --- |
| Doctor | All dependencies and configured models found | Pending |
| Index 12 sample files | Nonzero stored chunks, no duplicate accumulation on unchanged re-index | Pending |
| Ten evaluation questions | Responses saved; review sources and unsupported claims | Pending |
| Empty question | Clear validation error | Pending |
| Image-only PDF | Explicit no-readable-text error | Pending |
| Oversized upload | Rejected before indexing | Pending |
| Out-of-corpus question | Explicit insufficient-evidence response | Pending |
| Repeated identical question | Cached response; no new generation tokens logged | Pending |
| Stop model service | Useful error after bounded retries | Pending |
| Multi-tool request | At least two tools used and results reflected in final answer | Pending |
| Follow-up question | Retains earlier task context in same session | Pending |
| Docker deployment | Health and app demo work in mentor-approved environment | Pending |

Record actual outcomes, software versions, model names, execution date, latency and failures.
Do not change Pending to Passed without running the corresponding check.
