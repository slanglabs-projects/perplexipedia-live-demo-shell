from conva_ai import ConvaAI
from utils import (SourceItem, get_md_normal_text, get_md_hyperlink, extract_citations)

import os
import streamlit as st

ASSISTANT_ID = "547979d3e0b541baba824a2919623401"
API_KEY = "68e509b36d54471e8433d06f09a3207b"
ASSISTANT_VERSION = "1.0.0"

st.set_page_config(page_title="Perplexipedia - by Conva.AI")


# Hack to get playwright to work properly
os.system("playwright install")

if "status" not in st.session_state:
    st.session_state.status = "uninitialized"

if "sources" not in st.session_state:
    st.session_state.sources = {}

if "query_value" not in st.session_state:
    st.session_state.query_value = ""

if "response" not in st.session_state:
    st.session_state.response = None

if "answer" not in st.session_state:
    st.session_state.answer = ""


def execute_action(key):
    st.session_state.status = "processing"
    st.session_state.query_value = st.session_state[key]
    if ASSISTANT_ID and API_KEY:
        response = get_answer(st.session_state[key])
        handle_response(response)


def execute_action_btn(value):
    st.session_state.status = "processing"
    st.session_state.query_value = value
    if ASSISTANT_ID and API_KEY:
        response = get_answer(value)
        handle_response(response)


def reset():
    st.session_state.status = "uninitialized"
    st.session_state.query_value = ""


col1, col2 = st.columns([10, 2])
col1.title("Perplexipedia")
col1.caption("Perplexity, but for wikipedia")
col2.title("")
col2.image("conva.ai.svg", width=100)


with st.container(border=True):
    st.text_area("Type your question below", value=st.session_state.query_value, key="query")
    col1, col2, col3 = st.columns([2, 2, 4])
    col1.button("Get the answer", on_click=execute_action, args=["query"])
    col2.button("Reset", on_click=reset)

    pbph = col3.empty()
    rph = st.empty()

if st.session_state.status == "uninitialized":
    pbph.empty()
    rph.empty()


def get_answer(query):
    progress = 5
    pb = pbph.progress(progress, "Searching for relevant information...")

    progress += 50
    pb.progress(progress, "Processing search results...")

    pb.progress(progress, "Reading results...")

    client = ConvaAI(
        assistant_id=ASSISTANT_ID,
        api_key=API_KEY,
        assistant_version=ASSISTANT_VERSION,
    )

    progress += 25
    pb.progress(progress, "Generating answer...")

    response = client.invoke_capability_name(
        query="Answer the user's query based on the provided context. User's query: ({})".format(query),
        capability_name="wikipedia_qa",
        timeout=600,
        stream=False,
    )

    pb.progress(100, "Completed")
    st.session_state.status = "success"
    return response


def postprocess_response(response):
    sources = st.session_state.sources
    citations = extract_citations(response)

    final_sources = {k: v for k, v in sources.items() if k in citations}
    for index, fs in enumerate(final_sources.items()):
        fs[1].index = index

    for _, fs in final_sources.items():
        response = response.replace(fs.id, str(fs.index + 1))

    return final_sources, response


def handle_response(response):
    tmp = response.parameters.get("sources", [])
    st.session_state.sources = {"cit{}".format(i+1): SourceItem("cit{}".format(i+1), tmp[i], "") for i in range(len(tmp))}
    sources, answer = postprocess_response(response.message)
    st.session_state.response = response
    st.session_state.sources = sources
    st.session_state.answer = answer


if st.session_state.status == "success":
    sources = st.session_state.sources
    answer = st.session_state.answer
    response = st.session_state.response

    with rph.container(border=True):
        st.subheader("Answer")
        st.markdown(get_md_normal_text(answer), unsafe_allow_html=True)

        st.subheader("Sources")
        for _, s in sources.items():
            link = get_md_hyperlink(s.url)
            t = "{}. {} {}".format(s.index + 1, link, s.snippet[:100])
            st.markdown(get_md_normal_text(t), unsafe_allow_html=True)

        st.divider()

        st.subheader("Related")
        for r in response.related_queries:  # noqa
            st.button(r, key=r, on_click=execute_action_btn, args=[r])
