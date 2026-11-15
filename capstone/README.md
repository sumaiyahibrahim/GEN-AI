# SupportDesk AI capstone

Weeks 9–12 are represented by one application refined through build, testing, deployment and
documentation. The source is prepared; it has not been run end-to-end in this environment.

Run from the repository root after setup:
`python -m streamlit run capstone/app.py --server.address 127.0.0.1`.
Open the address Streamlit prints. Index the fictional sample corpus in the sidebar, ask a
policy question and expand its references. The second tab demonstrates a bounded agent.

Entry points: `app.py` for the interface; shared `internship/rag.py`, `client.py`, `tools.py`
and `agent.py` for application behavior. See ARCHITECTURE.md, TESTS.md and DEPLOYMENT.md.
The proposal is in `week8_hardened/CAPSTONE_PROPOSAL.md`; approval remains pending.
