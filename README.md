# CV Job Match Analyzer

This project is a **human-in-the-loop** workflow designed to align resumes with job descriptions accurately. 

It uses **LangGraph** to orchestrate a multi-step process that parses the data, **pauses** to let you verify and edit the extracted skills, and only *then* proceeds to the matching analysis.

## Logic

The core of this application isn't just the web server; it's the state graph defined in `graph.py`. The workflow moves through specific nodes:

1.  **Extraction:** The system reads the PDF.
2.  **Interrupt:** The graph halts execution. The Flask UI renders the extracted data, allowing you to fix OCR errors or add missing context.
3.  **Resumption:** Once you confirm the data via the UI, the graph resumes.
4.  **Analysis:** It parses the Job Description and performs a semantic comparison against your verified profile.

## Project Structure

The codebase is organized around the LangGraph workflow. If you are looking to modify the logic, change it in `graph.py`.

```text
cv_job_match/
├── app.py                 # Entry point. Handles the Flask routes and triggers graph events.
├── graph.py               # PIVOTAL: Defines the StateGraph, edges, and workflow logic.
├── nodes/                 # Individual units of logic called by the graph:
│   ├── parse_cv.py        # Extracts raw text -> structured JSON.
│   ├── confirm_cv.py      # The breakpoint node for human intervention.
│   ├── parse_job.py       # Structures the job description (requirements vs. nice-to-haves).
│   ├── compare.py         # The logic engine: maps CV skills to job description requirements.
│   └── summary.py         # Generates the final readable report.
├── utils/
│   └── pdf_parser.py      # PDF text extraction wrapper.
└── templates/             # Frontend UI.
```
## Setup
- Python 3.8+
- An OpenAI API Key (GPT-4 is recommended for complex reasoning)

```sh
pip install -r requirements.txt
```

### .env file in the root directory
```text
OPENAI_API_KEY=sk-your-key-here
FLASK_SECRET_KEY=dev-key-here
```
Note: You can swap the model in the nodes/ files if you want to test with different LLMs.

## launch
```sh
python app.py
```
Visit http://localhost:5000

## output
application doesn't just give a "percentage match." Because of the structured node approach, the final report breaks down:
- Evidence: Direct quotes from your CV that match requirements.
- Gap Analysis: Specific skills found in the job description but missing from the verified CV data.
- Strategy: Recommendations on how to bridge those gaps before the interview.

## tools
* Orchestration: LangGraph (State management & interruptions)
* Analysis: LangChain + OpenAI GPT-4
* Interface: Flask (handling the user verification step)
* Processing: PyPDF2

### Security Notes
- CV data is processed locally and not stored permanently
- Sessions are cleaned up after analysis


