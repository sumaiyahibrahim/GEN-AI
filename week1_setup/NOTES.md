# LLM fundamentals

## Tokens
A token is a unit used by a model to represent text. It may be a word, part of a word,
a punctuation mark or another byte sequence. Tokenization differs between models, so
the same sentence can have different token counts. Context limits and usage are usually
measured in tokens rather than words.

## Embeddings
An embedding is a numeric vector representing learned features of text or another input.
Text embeddings can place related meanings near one another. A search system embeds a
query and compares it with stored document vectors, commonly using cosine similarity.
Similarity helps select evidence but does not establish whether a statement is true.

## Next-token prediction
A language model predicts a distribution over possible next tokens from its preceding
context. Repeating that process produces text. A plausible continuation can still be wrong.

## Model types
A base model learns general patterns through pretraining. An instruction-tuned model has
additional training to follow requests. Chat models use message roles and conversation
formats; the exact training and behavior depend on the model.

## This implementation
Python sends HTTP requests to Ollama's local API. Chat uses `/api/chat`; embeddings use
`/api/embed`. No paid provider key is required. Installing software and downloading model
weights still require internet access, storage and sufficient memory.
