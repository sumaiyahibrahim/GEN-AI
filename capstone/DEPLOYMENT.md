# Deployment notes

Status: configuration prepared; no deployment or shareable URL has been created.

## Local Docker demonstration
Install Docker Desktop from its official source and ensure it is running. From the repo root:
```sh
docker compose up -d --build
docker compose exec ollama ollama pull qwen2.5:1.5b
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec app python -m internship.cli doctor
docker compose exec app python -m internship.cli index
docker compose logs --tail=100 app
```
Open http://127.0.0.1:8501. Model downloads require internet access. CPU inference can be slow.
The container setup has not been tested here because Docker and dependencies are unavailable.
The image version should be pinned to a tested digest for a reproducible staging release.

## Mentor-assigned staging environment
Confirm available CPU/RAM/storage, model licensing, who may access the demo and approved data.
Use an authenticated reverse proxy or the company's private network; do not expose the Ollama
port publicly. The app has no built-in authentication or separate workspaces. Add those controls
before any wider deployment. Configure persistent volumes and check file permissions for the
non-root app user. View container logs and `.runtime/usage.jsonl` to investigate failures.

The localhost binding is intentional. The mentor must supply the actual private staging
address, access controls and deployment credentials. Record that URL only after a successful
deployment and a real remote access test.
