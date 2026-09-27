# TalentLens AI

TalentLens AI is a professional portfolio project for an entry-level AI/ML Engineer role.

## What it demonstrates

- Python application development
- Semantic resume/job matching using Sentence Transformers
- Skill extraction and skill-gap analysis
- RAG (retrieval-augmented generation)
- Prompt engineering
- Local LLM integration with Ollama
- Streamlit UI
- FastAPI REST endpoint
- Modular software architecture
- Automated unit tests

## Architecture

Resume PDF + Job Description
        |
        v
Text extraction -> Skill extraction
        |                 |
        v                 v
Sentence Transformer   Skill coverage
        |                 |
        +---------> Match score
                         |
                         v
                 Interview Copilot
                         |
                         v
                  RAG Career Q&A
                         |
                         v
                    Ollama LLM

## Setup (Windows / VS Code)

### 1. Create the environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again.

### 2. Optional: configure Ollama

Install Ollama and make sure its local service is running. Then pull the model specified in `.env.example`, or change `OLLAMA_MODEL` to a model you already have.

Copy `.env.example` to `.env`:

```powershell
copy .env.example .env
```

The app works without Ollama, but LLM-generated interview packs and answers will use fallback mode.

### 3. Run the Streamlit app

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit.

### 4. Run the REST API

Open a second terminal:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn api:app --reload
```

Health check:

```text
http://127.0.0.1:8000/health
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## How the score works

Overall Match = 70% semantic similarity + 30% explicit skill coverage.

This is a portfolio metric, not a hiring decision or a scientifically validated recruitment score.

## Interview explanation

> "I built TalentLens AI, a Python-based AI/ML application that compares a resume with a target job description. I use Sentence Transformers to generate embeddings and cosine similarity for semantic matching. I also perform explicit skill extraction and calculate skill coverage. For the generative part, I added a RAG pipeline that retrieves relevant resume/JD chunks before sending grounded context to a local Ollama LLM. The application is exposed through Streamlit and a FastAPI REST endpoint."

## Suggested improvements

- Add PostgreSQL or MySQL for user/project history.
- Add authentication.
- Add ML evaluation dataset and precision/recall metrics.
- Add vector database such as FAISS or Chroma.
- Add Docker.
- Add CI with GitHub Actions.
- Add structured JSON output from the LLM.
- Add resume section parsing and explainable skill evidence.
