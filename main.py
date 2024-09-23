from conva_ai import ConvaAI
from utils import SourceItem, get_md_normal_text, get_md_hyperlink, extract_citations

import streamlit as st
import threading
import time

task_complete = threading.Event()

ASSISTANT_ID = "547979d3e0b541baba824a2919623401"
API_KEY = "68e509b36d54471e8433d06f09a3207b"
ASSISTANT_VERSION = "1.0.0"


PROGRESS_MESSAGES = {
    0: "Searching for relevant information...",
    30: "Processing search results...",
    60: "Reading results...",
    90: "Generating answer...",
}

st.set_page_config(page_title="Perplexipedia - by Conva.AI")


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


def get_answer_and_postprocess(query, results):
    response = get_answer(query)
    response, sources, answer = handle_response(response)
    results["response"] = response
    results["sources"] = sources
    results["answer"] = answer
    task_complete.set()


def simulate_progress_update():
    progress_bar = pbph.progress(0, "Searching for relevant information...")
    progress = 0
    while not task_complete.is_set():
        # Simulate progress updates
        time.sleep(4)
        progress += 30
        progress = min(progress, 90)
        progress_bar.progress(progress, PROGRESS_MESSAGES[progress])
    progress_bar.progress(100)


def execute_action(key):
    st.session_state.status = "processing"
    st.session_state.query_value = st.session_state[key]
    if ASSISTANT_ID and API_KEY:
        results = {}
        threading.Thread(target=get_answer_and_postprocess, args=(st.session_state[key], results)).start()
        simulate_progress_update()
        task_complete.wait()
        st.session_state.status = "success"
        st.session_state.response = results.get("response")
        st.session_state.sources = results.get("sources")
        st.session_state.answer = results.get("answer")


def execute_action_btn(value):
    st.session_state.status = "processing"
    st.session_state.query_value = value
    if ASSISTANT_ID and API_KEY:
        results = {}
        threading.Thread(target=get_answer_and_postprocess, args=(value, results)).start()
        simulate_progress_update()
        task_complete.wait()
        st.session_state.status = "success"
        st.session_state.response = results.get("response")
        st.session_state.sources = results.get("sources")
        st.session_state.answer = results.get("answer")


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
    client = ConvaAI(
        assistant_id=ASSISTANT_ID,
        api_key=API_KEY,
        assistant_version=ASSISTANT_VERSION,
    )

    response = client.invoke_capability_name(
        query="Answer the user's query based on the provided context. User's query: ({})".format(query),
        capability_name="wikipedia_qa",
        timeout=600,
        stream=False,
    )
    return response


def postprocess_response(response, sources):
    citations = extract_citations(response)

    final_sources = {k: v for k, v in sources.items() if k in citations}
    for index, fs in enumerate(final_sources.items()):
        fs[1].index = index

    for _, fs in final_sources.items():
        response = response.replace(fs.id, str(fs.index + 1))

    return final_sources, response


def handle_response(response):
    tmp = response.parameters.get("sources", [])
    sources = {"cit{}".format(i + 1): SourceItem("cit{}".format(i + 1), tmp[i], "") for i in range(len(tmp))}
    sources, answer = postprocess_response(response.message, sources)
    return response, sources, answer


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
