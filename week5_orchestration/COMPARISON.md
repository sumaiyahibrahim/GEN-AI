# Raw pipeline and framework pipeline

The Week 4 implementation calls the local HTTP API directly and uses Chroma's Python
collection API. The Week 5 version uses LangChain's Ollama integrations, Chroma wrapper,
chat prompt template and output parser. Both use the same fictional corpus and local models.

Raw code makes request behavior, retries, caching and metrics explicit. Framework components
reduce integration code but add dependencies and version compatibility considerations.
No claim that one implementation is faster or more accurate is made before measurement.
The framework demonstration writes an actual response when run; reliability features of the
shared raw client do not automatically apply to the separate LangChain client.
