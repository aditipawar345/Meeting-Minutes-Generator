import os
from datetime import date
from io import BytesIO

import streamlit as st
from docx import Document
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Reliable working models on Groq
DEFAULT_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
]

SYSTEM_PROMPT = """You are an expert meeting secretary. Convert the meeting transcript
into formal meeting minutes.

Rules:
- Use ONLY information stated in the transcript. Do not invent names, decisions or deadlines.
- If something is not mentioned, write "Not mentioned".
- Every action item must have an owner. If none is stated, write "Owner not assigned".
- Use exactly these Markdown headings, in this order:

## Meeting Summary
(2-3 sentences)

## Attendees
(bulleted list of names)

## Decisions
(numbered list)

## Action Items
| # | Action | Owner | Deadline |
|---|--------|-------|----------|
"""


def generate_minutes(transcript: str, title: str, meeting_date: str, api_key: str, model: str) -> str:
    client = Groq(api_key=api_key.strip())
    user_msg = (
        f"Meeting title: {title}\n"
        f"Date: {meeting_date}\n\n"
        f"Transcript:\n\"\"\"\n{transcript}\n\"\"\""
    )

    # Try chosen model first; if Groq deprecates/decommissions it, automatically fallback
    models_to_try = [model] + [m for m in DEFAULT_MODELS if m != model]
    last_error = None

    for candidate_model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=candidate_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.2,  # low temperature keeps output factual
            )
            return response.choices[0].message.content
        except Exception as e:
            err_msg = str(e).lower()
            last_error = e
            # Only fall back if the model specifically doesn't exist or was decommissioned
            if "not found" in err_msg or "does not exist" in err_msg or "decommissioned" in err_msg:
                continue
            else:
                raise e

    raise last_error


def minutes_to_docx(minutes_md: str, title: str) -> bytes:
    doc = Document()
    doc.add_heading(title, level=1)
    lines = minutes_md.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line.startswith("## "):
            doc.add_heading(line[3:], level=2)
            i += 1
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
            i += 1
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=3)
            i += 1
        elif line.startswith("|"):
            # Parse consecutive markdown table lines into a formatted Word table
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tline = lines[i].strip()
                if not set(tline) <= set("|-: "):  # skip table separator row
                    cells = [c.strip() for c in tline.strip("|").split("|")]
                    table_lines.append(cells)
                i += 1

            if table_lines:
                num_cols = max(len(row) for row in table_lines)
                table = doc.add_table(rows=len(table_lines), cols=num_cols)
                table.style = "Table Grid"
                for r_idx, row in enumerate(table_lines):
                    for c_idx, cell_value in enumerate(row):
                        if c_idx < num_cols:
                            cell = table.cell(r_idx, c_idx)
                            cell.text = cell_value
                            if r_idx == 0:
                                for p in cell.paragraphs:
                                    for run in p.runs:
                                        run.bold = True
        elif line.startswith(("- ", "* ")):
            doc.add_paragraph(line[2:], style="List Bullet")
            i += 1
        else:
            doc.add_paragraph(line)
            i += 1

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ---------- UI ----------
st.set_page_config(page_title="Meeting Minutes Generator", page_icon="📝", layout="centered")
st.title("📝 Meeting Minutes Generator")
st.caption("Turn a meeting transcript into structured, actionable minutes using Groq.")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")
env_api_key = os.getenv("GROQ_API_KEY", "").strip()
api_key = st.sidebar.text_input(
    "Groq API Key",
    value=env_api_key,
    type="password",
    help="Loaded automatically from .env if present. Or enter here.",
)

selected_model = st.sidebar.selectbox(
    "Model",
    DEFAULT_MODELS,
    index=0,
    help="Select Groq model. Automatically falls back if a model is unavailable on your key."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Quick Load Test Samples")
sample_files = {
    "Select sample...": "",
    "Sample 1: Basic (sample_transcript.txt)": "sample_transcript.txt",
    "Sample 2: No Decisions ('Not mentioned')": "test_transcripts/2_no_decisions.txt",
    "Sample 3: Unassigned Owner ('Owner not assigned')": "test_transcripts/3_unassigned_owner.txt",
    "Sample 4: Short Transcript (2 lines)": "test_transcripts/4_short_transcript.txt",
    "Sample 5: Long Sprint Review (15+ lines)": "test_transcripts/5_long_transcript.txt",
}
selected_sample = st.sidebar.selectbox("Load sample transcript:", list(sample_files.keys()))
default_text = ""
if selected_sample and sample_files[selected_sample]:
    try:
        with open(sample_files[selected_sample], "r", encoding="utf-8") as f:
            default_text = f.read()
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")

col_a, col_b = st.columns(2)
meeting_title = col_a.text_input("Meeting title", "Weekly Project Review")
meeting_date = col_b.date_input("Meeting date", date.today())

uploaded = st.file_uploader("Upload transcript (.txt)", type=["txt"])
pasted = st.text_area(
    "...or paste the transcript here",
    value=default_text,
    height=220,
    placeholder="Paste discussion transcript or select a sample from the sidebar..."
)

if st.button("Generate minutes", type="primary"):
    transcript = uploaded.getvalue().decode("utf-8") if uploaded else pasted
    if not transcript.strip():
        st.warning("Please upload or paste a transcript first.")
    elif not api_key.strip():
        st.error("GROQ_API_KEY is missing. Add it to your .env file or enter it in the sidebar.")
    else:
        with st.spinner("Writing minutes..."):
            try:
                st.session_state["minutes"] = generate_minutes(
                    transcript, meeting_title, str(meeting_date), api_key.strip(), selected_model
                )
                st.success("Minutes generated successfully!")
            except Exception as e:
                st.error(f"API Error: {str(e)}")

if "minutes" in st.session_state:
    minutes = st.session_state["minutes"]
    st.markdown("---")
    st.markdown(minutes)

    d1, d2 = st.columns(2)
    d1.download_button(
        "📥 Download .txt",
        data=minutes,
        file_name=f"{meeting_title.replace(' ', '_').lower()}_minutes.txt",
        mime="text/plain",
    )
    d2.download_button(
        "📥 Download .docx",
        data=minutes_to_docx(minutes, meeting_title),
        file_name=f"{meeting_title.replace(' ', '_').lower()}_minutes.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
