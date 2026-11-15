# Basic RAG pipeline

1. Read text from PDF pages or UTF-8 text/Markdown documents.
2. Split text into overlapping chunks while retaining filename and page.
3. Request semantic vectors from the local embedding API.
4. Store vectors, text and metadata in persistent Chroma.
5. Embed a question and retrieve its closest chunks using cosine distance.
6. Ask the local language model to answer using only the retrieved evidence.
7. Display source passages and check that citation numbers exist.

The citation checker validates source numbering, not logical entailment. A generated answer
can cite a real passage incorrectly, so the ten evaluation cases require grounding review.
No retrieval threshold is claimed to guarantee relevance. Missing evidence should lead to an
explicit abstention. OCR and encrypted PDFs are not supported.
