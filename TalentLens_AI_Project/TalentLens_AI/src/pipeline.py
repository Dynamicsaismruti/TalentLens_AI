from .skills import extract_skills, skill_gap
from .ml_engine import semantic_similarity, combined_match_score
from .rag import retrieve_context
from .llm import safe_generate


def analyze_resume_job(resume_text: str, job_text: str) -> dict:
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    matched, missing = skill_gap(resume_skills, job_skills)

    coverage = len(matched) / len(job_skills) if job_skills else 0.0

    semantic = semantic_similarity(
        resume_text[:12000],
        job_text[:12000]
    )

    final_score = combined_match_score(
        semantic,
        coverage
    )

    return {
        "semantic_similarity": semantic,
        "skill_coverage": coverage,
        "match_score": final_score,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched,
        "missing_skills": missing,
    }

def build_interview_prompt(
    resume_text: str,
    job_text: str,
    analysis: dict
) -> str:

    matched = ", ".join(
        analysis.get("matched_skills", [])
    )

    missing = ", ".join(
        analysis.get("missing_skills", [])
    )

    return f"""
You are a technical interviewer for a fresher AI/ML role.

Candidate skills:
{matched}

Skill gaps:
{missing}

Create a short interview preparation pack.

Give exactly:
1. 3 Python/AI-ML technical questions with short answers.
2. 2 project questions with short answers.
3. 2 behavioral questions with short answers.
4. 2 preparation priorities.

Keep every answer under 3 sentences.
Do not repeat questions.
Do not explain your reasoning.
Be practical and concise.
"""


def fallback_interview(analysis: dict) -> str:

    gaps = (
        ", ".join(analysis["missing_skills"][:5])
        if analysis["missing_skills"]
        else "no major explicit skill gaps"
    )

    return (
        "Interview preparation plan\n\n"
        "1. Explain Python fundamentals, OOP, APIs, exceptions and data handling.\n"
        "2. Be ready to explain your AI/ML project architecture, data flow and evaluation.\n"
        "3. Prepare examples for debugging and API integration.\n"
        f"4. Review these detected job-skill gaps: {gaps}."
    )


def generate_interview_pack(
    resume_text: str,
    job_text: str,
    analysis: dict
):

    prompt = build_interview_prompt(
        resume_text,
        job_text,
        analysis
    )

    return safe_generate(
        prompt,
        fallback_interview(analysis)
    )


def rag_answer(
    question: str,
    resume_text: str,
    job_text: str
) -> tuple[str, bool]:

    retrieved = retrieve_context(
        question,
        [resume_text, job_text],
        top_k=5
    )

    context = "\n\n".join(
        f"- {chunk}"
        for chunk, _ in retrieved
    )

    prompt = f"""
Answer the user's question using ONLY the retrieved context.

Question:
{question}

Retrieved context:
{context}

If the answer is not present, say that the available documents
do not contain enough information.
"""

    fallback = (
        "I can only answer from the uploaded resume and job description. "
        "The local LLM is unavailable, so please start Ollama "
        "for document-grounded answers."
    )

    return safe_generate(
        prompt,
        fallback
    )


def generate_interview_questions(
    resume_text,
    job_text,
    missing_skills
):

    questions = []

    questions.append({
        "question": "Tell me about yourself and your technical background.",
        "answer": (
            "I am a B.Sc. ITM student with experience in Python, "
            "web development, REST APIs, MySQL and AI/ML concepts. "
            "I have worked on projects involving full-stack development "
            "and AI-based applications."
        )
    })

    questions.append({
        "question": "Explain your Employee Management System project.",
        "answer": (
            "It is a full-stack application built using Python, Flask, "
            "REST APIs and MySQL. It performs CRUD operations for "
            "employee data and provides API-based communication "
            "between the application and database."
        )
    })

    questions.append({
        "question": "What is Machine Learning?",
        "answer": (
            "Machine Learning is a branch of AI in which computers "
            "learn patterns from data and use those patterns to make "
            "predictions or decisions without being explicitly "
            "programmed for every case."
        )
    })

    questions.append({
        "question": "What is RAG?",
        "answer": (
            "RAG stands for Retrieval-Augmented Generation. "
            "It retrieves relevant information from a knowledge source "
            "and provides that information to a language model so that "
            "the generated response is more relevant and grounded."
        )
    })

    questions.append({
        "question": "What is a REST API?",
        "answer": (
            "A REST API is an application programming interface that "
            "follows REST principles and commonly uses HTTP methods "
            "such as GET, POST, PUT and DELETE to work with resources."
        )
    })

    questions.append({
        "question": "What is Prompt Engineering?",
        "answer": (
            "Prompt Engineering is the process of designing effective "
            "instructions or prompts for an AI model to obtain accurate, "
            "relevant and useful responses."
        )
    })

    questions.append({
        "question": "Why are Python and Machine Learning commonly used together?",
        "answer": (
            "Python provides simple syntax and has a large ecosystem "
            "of libraries such as NumPy, pandas, scikit-learn, PyTorch "
            "and TensorFlow, making it suitable for data processing "
            "and machine learning development."
        )
    })

    for skill in missing_skills:
        questions.append({
            "question": f"What do you know about {skill}?",
            "answer": (
                f"{skill} is one of the skills identified as relevant "
                f"to the target job. I am currently strengthening my "
                f"knowledge of {skill} through practical learning "
                f"and project work."
            )
        })

    return questions