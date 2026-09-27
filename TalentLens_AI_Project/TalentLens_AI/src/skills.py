import re
from typing import Iterable


# ============================================================
# SKILL TAXONOMY
# ============================================================

SKILL_TAXONOMY = [
    "Python",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "Java",
    "C++",
    "JavaScript",
    "TypeScript",
    "React",
    "Node.js",
    "REST API",
    "FastAPI",
    "Flask",
    "Git",
    "GitHub",
    "Docker",
    "Linux",
    "Jenkins",
    "HTML",
    "CSS",

    "Artificial Intelligence",
    "AI/ML",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Computer Vision",

    "scikit-learn",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "OpenCV",
    "YOLO",

    "LLM",
    "RAG",
    "LangChain",
    "Prompt Engineering",
    "Generative AI",
    "Ollama",
    "Embeddings",
    "Vector Database",
    "FAISS",

    "API Integration",
    "Automation",
    "Streamlit",
    "Data Analysis",
    "Statistics",
]


# ============================================================
# ALIASES
# ============================================================

ALIASES = {
    # AI / ML
    "artificial intelligence": "Artificial Intelligence",
    "ai": "Artificial Intelligence",
    "ai/ml": "AI/ML",
    "ai ml": "AI/ML",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",

    # LLM / Generative AI
    "large language model": "LLM",
    "large language models": "LLM",
    "llm": "LLM",
    "llms": "LLM",

    "generative ai": "Generative AI",
    "gen ai": "Generative AI",

    "prompt engineering": "Prompt Engineering",
    "prompt engineer": "Prompt Engineering",

    # APIs
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",

    "api integration": "API Integration",
    "api integrations": "API Integration",

    # JavaScript / Node
    "node": "Node.js",
    "nodejs": "Node.js",
    "node js": "Node.js",

    # Machine learning libraries
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",

    # Computer vision
    "computer vision": "Computer Vision",

    # Database
    "postgres": "PostgreSQL",

    # GenAI / RAG
    "retrieval augmented generation": "RAG",
    "retrieval-augmented generation": "RAG",

    # Data
    "data analytics": "Data Analysis",
    "data analysis": "Data Analysis",
}


# ============================================================
# RELATED SKILLS
# ============================================================

# These relationships prevent obvious terminology differences
# from creating unnecessary skill gaps.

RELATED_SKILLS = {
    "ai/ml": {
        "artificial intelligence",
        "machine learning",
        "ai/ml",
    },

    "artificial intelligence": {
        "artificial intelligence",
        "ai/ml",
        "machine learning",
    },

    "machine learning": {
        "machine learning",
        "ml",
        "ai/ml",
    },

    "rest api": {
        "rest api",
        "api integration",
    },

    "api integration": {
        "api integration",
        "rest api",
    },

    "llm": {
        "llm",
        "large language model",
        "large language models",
        "llms",
    },

    "rag": {
        "rag",
        "retrieval augmented generation",
        "retrieval-augmented generation",
    },

    "data analysis": {
        "data analysis",
        "data analytics",
    },
}


# ============================================================
# REGEX PATTERN
# ============================================================

def _pattern(term: str) -> str:
    return (
        r"(?<![A-Za-z0-9+#.])"
        + re.escape(term)
        + r"(?![A-Za-z0-9+#.])"
    )


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(
    text: str,
    taxonomy: Iterable[str] = SKILL_TAXONOMY
) -> list[str]:

    if not text:
        return []

    lowered = text.lower()

    found = []

    # Search official taxonomy
    for skill in taxonomy:
        if re.search(_pattern(skill.lower()), lowered):
            found.append(skill)

    # Search aliases
    for alias, canonical in ALIASES.items():

        if re.search(_pattern(alias.lower()), lowered):

            if canonical not in found:
                found.append(canonical)

    return sorted(set(found))


# ============================================================
# SKILL GAP ANALYSIS
# ============================================================

def skill_gap(
    resume_skills: list[str],
    job_skills: list[str]
) -> tuple[list[str], list[str]]:

    resume_lower = {
        skill.lower()
        for skill in resume_skills
    }

    matched = []
    missing = []

    for job_skill in job_skills:

        job_lower = job_skill.lower()

        # Exact match
        if job_lower in resume_lower:
            matched.append(job_skill)
            continue

        # Related skill match
        related = RELATED_SKILLS.get(job_lower, set())

        if related.intersection(resume_lower):
            matched.append(job_skill)
        else:
            missing.append(job_skill)

    return (
        sorted(set(matched)),
        sorted(set(missing))
    )