from src.skills import extract_skills, skill_gap

def test_extract_skills():
    text = "Python, machine learning, REST APIs and Prompt Engineering"
    skills = extract_skills(text)
    assert "Python" in skills
    assert "Machine Learning" in skills
    assert "REST API" in skills
    assert "Prompt Engineering" in skills

def test_skill_gap():
    matched, missing = skill_gap(["Python", "LLM"], ["Python", "LLM", "RAG"])
    assert matched == ["Python", "LLM"]
    assert missing == ["RAG"]
