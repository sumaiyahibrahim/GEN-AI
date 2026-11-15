# Prompting RAG and fine-tuning for support questions

## Task and decision
The task is to answer questions about a fictional software product's support policies.
Answers should reflect the current supplied documents, identify their evidence, and avoid
guessing when information is absent. Retrieval augmented generation is the proposed primary
approach because the knowledge is document-based and can change independently of the model.
This analysis uses the comparison option allowed by the internship roadmap. Mentor agreement
on that option is still required. No fine-tuned model or fine-tuning benchmark is claimed.

## Pure prompting
Pure prompting sends instructions and the question to a pretrained instruction-following
model. Examples can demonstrate answer format, tone and expected abstention behavior. The
implementation is simple, and a narrow task can be prototyped without preparing a dataset.
However, a model cannot reliably know private or newly written support policies unless they
are supplied. Asking about the refund window without including the fictional policy may
produce a plausible but unsupported answer. Putting all documents into every prompt is
possible for a small corpus, but context size and repeated processing become constraints.

Its initial engineering effort is low. Inference cost depends on the model, prompt length,
output length, request volume and hosting arrangement. Local inference avoids provider API
charges but still consumes hardware resources and electricity. Accuracy must be measured
against the intended task; fluent wording is not an accuracy measurement.

## Retrieval augmented generation
RAG first retrieves relevant passages from an external corpus, then provides them with the
question to the language model. The proposed application stores document chunks and their
embeddings in Chroma. A query embedding selects candidate passages, and the prompt requests
answers grounded in those passages with source references. A changed policy can be re-indexed
without retraining the generation model.

This approach adds ingestion, chunking, indexing and retrieval work. It can fail if the wrong
passage is retrieved, extraction loses information, or the model ignores evidence. Citation
numbers alone do not prove factual support. Evaluation therefore includes expected sources,
answer checks and human review of the retrieved text. RAG generally fits this task's need
for traceability, but its real performance remains unmeasured until the supplied evaluation
runner is executed with the downloaded models.

## Conceptual fine-tuning approach
Fine-tuning adjusts model parameters using examples of desired behavior. For a narrow support
task, a small dataset could pair questions and context with well-structured answers. LoRA
reduces the number of trainable parameters by learning additional low-rank updates while
keeping much of the original model fixed. It still requires suitable data, training resources,
held-out evaluation, and careful consideration of the model's license and intended use.

Fine-tuning could improve a consistent response format or domain-specific style. It is not
the first choice for injecting changing policy facts: an update may require further training,
and the resulting model does not automatically expose sources. With 50–100 examples, a narrow
experiment might be feasible, but that amount is not evidence of broad reliability. Training
and evaluation examples must be separated to avoid reporting memorization as generalization.
No training was performed for this comparison option.

## Comparison and proposed evaluation
Prompting has the lowest setup effort, RAG adds retrieval infrastructure, and fine-tuning adds
dataset and training work. Their accuracy and latency cannot be ranked numerically without
running comparable tests. A fair experiment would use the same held-out questions, consistent
answer criteria, measured latency and token counts, and a review of unsupported assertions.
The supplied runner records real outputs from prompting and RAG; fine-tuning remains a
documented conceptual alternative rather than a fabricated third experiment.

The proposed choice is RAG with a clear prompt and visible references. Fine-tuning can be
reconsidered if a measured error analysis shows persistent behavioral problems that better
retrieval and prompting do not resolve. The final choice should follow mentor guidance and
actual evaluation rather than assumed performance benefits.
