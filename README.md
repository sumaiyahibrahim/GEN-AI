# Sumaiyah Ibrahim - Generative AI Internship

**Intern:** Sumaiyah Ibrahim  
**Role:** Generative AI Intern  
**Company:** OPASH SOFTWARE  
**Mentor:** Mr. Hiren Danecha

## About my work

This repository contains the work I prepared for my Generative AI internship roadmap. I organised it week by week so that each task, program and document is easy to find. The first eight weeks cover the main concepts and practice tasks. Weeks 9 to 12 focus on the final RAG-based capstone project.

I used Python, Ollama, ChromaDB, LangChain and Streamlit. Ollama was selected so the project can run with a local model without requiring a paid API key.

## Project structure

| Folder | Work included |
| --- | --- |
| `week1_setup` | Python setup, first LLM call and basic notes |
| `week2_prompting` | Prompting methods and structured JSON extraction |
| `week3_embeddings` | Embeddings, ChromaDB and semantic search |
| `week4_rag_demo` | Basic RAG pipeline and evaluation questions |
| `week5_orchestration` | LangChain workflow and tool calling |
| `week6_agent` | Multi-step agent, tools and conversation memory |
| `week7_finetuning` | Fine-tuning study and prompting/RAG comparison |
| `week8_hardened` | Streaming, caching, retries and capstone proposal |
| `week9_capstone_core` | Core capstone application |
| `week10_testing_refinement` | Testing, edge cases and improvements |
| `week11_deployment` | Docker and deployment preparation |
| `week12_final_documentation` | Final documentation and presentation material |
| `capstone` | Complete Streamlit RAG application |

## How I run the project on Windows

After installing Python 3.10 or above and Ollama, I open PowerShell in this folder and run:

```powershell
.\setup_windows.ps1
.\run_exercises.ps1
.\start_app.ps1
```

The setup script creates the Python environment, installs the required packages and downloads the local models. The exercise script runs the Week 1-8 tasks. The final command starts the Streamlit capstone application.

## Useful commands

```powershell
python -m unittest discover -s tests -v
python -m internship.cli doctor
python -m internship.cli index
python -m internship.cli ask "What is the refund request window?"
python -m internship.cli evaluate
python -m streamlit run capstone/app.py --server.address 127.0.0.1
```

Generated exercise results are stored in `artifacts`. Local embeddings, uploads, cache files and metrics are stored in `.runtime`. These folders are excluded from Git by default.

## Current progress

The source code, weekly documents, sample knowledge base, evaluation questions and capstone structure are prepared. The offline test suite passes. The remaining practical work is to install Ollama and the dependencies on the final computer, run the live model exercises, capture the actual outputs, test the interface and deploy it to the environment approved by my mentor. I track these items in `MY_PROGRESS.md`.

The sample policies and ticket information in this repository are fictional and are used only for demonstrating the project. No confidential company information is included.

## Repository note

Before submitting, I will check the generated outputs, add only safe files to GitHub, and confirm the local-model approach and final capstone with my mentor. Environment files, model weights, private documents and secrets must not be uploaded.
