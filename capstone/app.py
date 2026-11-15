"""Run from repository root: python -m streamlit run capstone/app.py"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import streamlit as st
from internship.client import OllamaClient
from internship.documents import load_chunks
from internship.rag import KnowledgeBase, answer_messages, validate_citations
from internship.agent import SupportAgent

st.set_page_config(page_title='SupportDesk AI', page_icon='📚', layout='wide')
st.title('SupportDesk AI')
st.caption('Document questions with source references · local models · fictional demo data')

@st.cache_resource
def resources():
    client = OllamaClient()
    return client, KnowledgeBase(client)

try:
    client, kb = resources()
except Exception as exc:
    st.error(f'Setup is incomplete: {exc}')
    st.code('python -m internship.cli doctor')
    st.stop()

with st.sidebar:
    st.header('Knowledge base')
    st.write(f'Chat model: `{client.settings.chat_model}`')
    st.write(f'Indexed chunks: {kb.collection.count()}')
    if st.button('Index fictional sample documents'):
        try:
            with st.spinner('Embedding sample documents…'):
                count = kb.index(load_chunks(sorted((ROOT / 'data/sample_docs').glob('*.md'))))
            st.success(f'Indexed {count} chunks.')
        except Exception as exc:
            st.error(str(exc))
    uploads = st.file_uploader('Upload PDF, TXT or Markdown', type=['pdf', 'txt', 'md'], accept_multiple_files=True)
    if st.button('Index uploaded documents', disabled=not uploads):
        try:
            paths = []
            upload_dir = client.settings.runtime / 'uploads'
            upload_dir.mkdir(parents=True, exist_ok=True)
            for upload in uploads:
                if upload.size > 10 * 1024 * 1024:
                    raise ValueError('Each file must be smaller than 10 MB.')
                content = upload.getvalue()
                # Prefix avoids collisions and prevents path traversal from uploaded filenames.
                name = Path(upload.name.replace('\\', '/')).name
                path = upload_dir / f'{hashlib.sha256(content).hexdigest()[:12]}_{name}'
                path.write_bytes(content)
                paths.append(path)
            with st.spinner('Reading and indexing…'):
                count = kb.index(load_chunks(paths))
            st.success(f'Indexed {count} chunks.')
        except Exception as exc:
            st.error(str(exc))
    st.caption('Uploaded content stays on the configured machine. Local cache and uploads persist in .runtime/. '
               'This demo has no authentication; use localhost or a private staging environment.')

qa_tab, agent_tab = st.tabs(['Document Q&A', 'Tool-using assistant'])
with qa_tab:
    question = st.text_input('Ask a question about the indexed documents', max_chars=2000)
    if st.button('Answer with references'):
        try:
            with st.spinner('Retrieving evidence…'):
                hits = kb.search(question)
            answer = st.write_stream(client.stream_chat(answer_messages(question, hits)))
            valid, note = validate_citations(answer, hits)
            (st.info if valid else st.warning)(note)
            for i, hit in enumerate(hits, 1):
                with st.expander(f'[{i}] {hit["source"]} · page {hit["page"]}'):
                    st.write(hit['text'])
                    st.caption(f'Cosine distance: {hit["distance"]:.4f}; lower means more similar.')
        except Exception as exc:
            st.error(f'Could not complete the answer: {exc}')
with agent_tab:
    st.write('Tools: document search, sample ticket lookup, and calculator. Email output is a draft only.')
    if 'support_agent' not in st.session_state:
        st.session_state.support_agent = SupportAgent(client, kb)
    if st.button('Reset conversation'):
        st.session_state.support_agent = SupportAgent(client, kb)
    task = st.text_area('Task', value='Look up T-1001, find the response-time policy, and draft a short update.', max_chars=2000)
    if st.button('Run assistant'):
        try:
            with st.spinner('Running tools…'):
                result = st.session_state.support_agent.run(task)
            st.write(result['answer'])
            if result['status'] != 'completed':
                st.warning(result['status'])
            with st.expander('Tool actions and results'):
                st.json(result['trace'])
        except Exception as exc:
            st.error(str(exc))
