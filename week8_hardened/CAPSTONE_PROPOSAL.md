# Proposed capstone SupportDesk AI

Status: proposal prepared; mentor sign-off pending. This is not a record of approval.

## Problem and users
Support staff repeatedly search product documentation to answer routine questions. A generic
chat model may guess policy details or return information without evidence. A document-based
assistant could shorten the search process while allowing staff to inspect the passages used.
The intended demonstration user is a support employee working with an approved document set.

## Proposed solution
Build a local application that indexes text documents and text-based PDFs, retrieves relevant
passages, and generates an answer with numbered source references. A separate tool-using view
can look up fictional ticket records, retrieve a policy and draft an update. The application
does not send email, change accounts or access a real customer database.

## Technical approach
Python provides the shared modules and exercise runners. Ollama supplies local generation and
embedding HTTP APIs. Chroma stores vectors and document metadata. Streamlit supplies the local
interface, while LangChain provides a separate orchestration comparison for Week 5. Docker
Compose defines a reproducible application and local model-server environment. The default
corpus is explicitly fictional and contains no actual OPASH SOFTWARE policies or client data.

## Scope and acceptance criteria
The core demonstration should index the twelve supplied documents, answer eight in-domain
questions with inspectable sources, and abstain on two questions outside the corpus. Test
results should report retrieval and citation checks separately from human grounding review.
The tool demonstration should use at least two actual tools and answer a follow-up in the
same session. Empty inputs, missing models and unsupported documents should fail clearly.
Streaming, cache behavior, retries and usage logging should be demonstrated and measured.

## Delivery and limitations
Planned deliverables are source code, setup instructions, tests, an evaluation file, Docker
configuration, deployment notes and a 10–15-minute presentation. A private staging deployment
needs the mentor's approved environment, resources and access controls. Small local models
may be slow or unreliable on multi-step tool tasks. OCR, authentication, multi-user isolation,
enterprise security review and production service guarantees are outside this prototype.

## Value and review
The project combines embeddings, RAG, prompting, structured output, tool use and operational
concerns in one coherent demonstration. It is suitable for evaluating the internship's
technical exercises if the mentor accepts the proposed scope. The mentor should confirm the
deadline, local-model substitutions, comparison option and deployment arrangement before the
project is treated as an approved final submission.
