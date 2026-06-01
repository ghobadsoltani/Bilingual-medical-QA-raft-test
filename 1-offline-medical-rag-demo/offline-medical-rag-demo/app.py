"""
Optional Streamlit UI for the offline medical RAG demo.

Run:
    streamlit run app.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402

from src import config  # noqa: E402
from src.pipeline import MedicalRAGPipeline  # noqa: E402

st.set_page_config(page_title="Offline Medical RAG Demo", layout="wide")

st.title("Offline Medical RAG Demo")
st.caption(
    "Educational prototype only — not medical advice. "
    "Answers are grounded in local sample documents."
)

with st.sidebar:
    st.header("Setup")
    index_exists = (config.INDEX_DIR / "meta.json").exists()
    st.write(f"Index ready: **{'Yes' if index_exists else 'No'}**")
    if st.button("Build / rebuild index"):
        with st.spinner("Building index (downloads models on first run)..."):
            pipeline = MedicalRAGPipeline()
            stats = pipeline.build_index()
        st.success(f"Indexed {stats['chunks']} chunks from {stats['documents']} documents.")

question = st.text_input(
    "Your question",
    placeholder="e.g., What lifestyle changes help manage high blood pressure?",
)

if st.button("Get answer", type="primary") and question.strip():
    if not index_exists:
        st.error("Build the index first using the sidebar button.")
    else:
        with st.spinner("Retrieving context and generating answer..."):
            pipeline = MedicalRAGPipeline()
            result = pipeline.ask(question.strip())

        st.subheader("Answer")
        st.write(result["answer"])

        with st.expander("Retrieved sources"):
            for source in result["sources"]:
                st.markdown(
                    f"**{source['title']}** — `{source['chunk_id']}` "
                    f"(score: {source['score']})"
                )

        with st.expander("Context preview"):
            st.text(result["context_preview"])
