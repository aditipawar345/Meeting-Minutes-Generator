# Meeting Minutes Generator 

**Model Used:** `llama-3.3-70b-versatile` (via Groq Cloud API)  
**Framework:** Streamlit, Python-docx, Groq Python SDK  

---

## 📌 Problem Statement

In fast-paced collaborative environments, teams frequently conduct meetings without structured note-taking. Consequently, critical discussions, decisions, and action items are often lost or forgotten. Manual transcription and formatting into formal minutes of the meeting (MoM) is time-consuming and prone to human omission or bias.

The **Meeting Minutes Generator** automates this process by processing raw, conversational meeting transcripts and extracting formal, structured minutes containing:
1. **Meeting Summary** (2–3 concise sentences)
2. **Attendees** (list of individuals present)
3. **Decisions** (explicit choices and resolutions agreed upon)
4. **Action Items** (tabular format with task description, assigned owner, and target deadline)

The generated minutes can be reviewed interactively and downloaded instantly as either raw plain text (`.txt`) or professionally formatted Word documents (`.docx`).

---

## 🚀 Features

- **Zero Hallucination Guardrails:** Prompt engineering ensures the model uses strictly stated facts. If decisions or owners are omitted, it explicitly tags them as `"Not mentioned"` or `"Owner not assigned"`.
- **Dual Input Modes:** Upload `.txt` transcript files or paste transcript text directly.
- **Sidebar Sample Loader:** Built-in test cases pre-loaded for quick demonstration and grading.
- **Export Formats:**
  - Plain Text (`.txt`)
  - Microsoft Word document (`.docx`) with structured tables and styled headings.
- **Low-Latency Inference:** Powered by Groq's LPU architecture running Meta's `llama-3.3-70b-versatile`.

---

## 📂 Project Structure

```
meeting-minutes-ps3/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── .env                       # API keys (ignored by git)
├── .env.example               # Template for environment variables
├── .gitignore                 # Files excluded from version control
├── README.md                  # Project documentation and guide
├── sample_transcript.txt      # Primary sample meeting transcript
├── Report.md                  # Comprehensive 2-page project report
└── test_transcripts/          # Dedicated test suite
    ├── 1_basic_sample.txt
    ├── 2_no_decisions.txt
    ├── 3_unassigned_owner.txt
    ├── 4_short_transcript.txt
    └── 5_long_transcript.txt
```

---

## 🛠️ Setup and Installation

### 1. Prerequisites
- Python 3.10+ installed
- Free API key from [Groq Console](https://console.groq.com)

### 2. Clone / Download Repository
```bash
git clone https://github.com/aditipawar345/Meeting-Minutes-Generator.git
cd meeting-minutes-ps3
```

### 3. Create and Activate Virtual Environment
- **Windows:**
  ```powershell
  python -m venv venv
  venv\Scripts\activate
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure API Key
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```
*(Alternatively, enter your key directly into the sidebar in the Streamlit web interface).*

### 6. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Test Suite & Validation Cases

The application includes 5 comprehensive test scenarios located in `test_transcripts/`:

| Test Case | Scenario | Expected Behavior |
|:---|:---|:---|
| **1. Basic Sample** | Standard multi-speaker sync with bugs, decisions, and tasks. | Extracts attendees, 2 decisions, and assigns owners/deadlines cleanly. |
| **2. No Decisions** | Progress status sync without final decisions. | Outputs `"Not mentioned"` under `## Decisions`. |
| **3. Unassigned Owner** | Action item agreed on without a designated volunteer. | Flags `"Owner not assigned"` in Action Items table. |
| **4. Short Transcript** | 2-line quick agreement. | Yields concise minutes without hallucinating missing context. |
| **5. Long Sprint Review** | 15+ lines covering multiple cross-functional workstreams. | Parses multiple decisions and diverse action items accurately. |
| **6. Empty Input** | Submitting without transcript. | Displays informative warning: *"Please upload or paste a transcript first."* |

---

## 📄 License
Academic project for Generative AI coursework. Free for educational use.
