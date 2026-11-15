# System architecture

```mermaid
flowchart TD
  U[User] --> UI[Streamlit interface]
  UI --> I[Document ingestion]
  I --> E[Local embedding API]
  E --> V[Chroma index]
  UI --> R[Question retrieval]
  R --> E
  R --> V
  R --> C[Prompt and cited passages]
  C --> M[Local chat API]
  M --> A[Answer and citation checks]
  A --> UI
  UI --> T[Bounded tool agent]
  T --> K[Ticket lookup and calculator]
  T --> R
```

The shared client provides caching, request retries and usage metrics. The separate framework
exercise uses LangChain integrations for comparison. Chroma and SQLite persist on local disk.
The model server and UI should remain private. No real email, account update or external
customer-system write is implemented.
