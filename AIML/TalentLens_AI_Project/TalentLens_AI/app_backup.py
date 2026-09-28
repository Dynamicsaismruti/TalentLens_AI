import tempfile
from pathlib import Path
import streamlit as st

from src.parser import extract_pdf_text, clean_text
from src.pipeline import analyze_resume_job, generate_interview_pack, rag_answer


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TalentLens AI",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🤖 TalentLens AI")

st.caption(
    "AI/ML Resume–Job Matching & Interview Copilot"
)

st.write(
    "A portfolio project demonstrating semantic matching, "
    "skill-gap analysis, RAG, prompt engineering, and local LLM integration."
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "job_text" not in st.session_state:
    st.session_state.job_text = ""

if "interview_result" not in st.session_state:
    st.session_state.interview_result = None

if "interview_used_llm" not in st.session_state:
    st.session_state.interview_used_llm = False


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("1. Upload Resume")

    resume_file = st.file_uploader(
        "PDF resume",
        type=["pdf"]
    )

    st.header("2. Add Job Description")

    job_text = st.text_area(
        "Paste the target JD here",
        height=260
    )


# --------------------------------------------------
# ANALYZE CANDIDATE
# --------------------------------------------------

if st.button("Analyze Candidate", type="primary"):

    # Check resume
    if not resume_file:
        st.error("Please upload a PDF resume.")
        st.stop()

    # Check job description
    if not job_text.strip():
        st.error("Please paste the job description.")
        st.stop()

    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp:

        tmp.write(resume_file.getbuffer())
        pdf_path = tmp.name

    try:

        # Extract resume text
        resume_text = clean_text(
            extract_pdf_text(pdf_path)
        )

    except Exception as e:

        st.error(f"Error reading the PDF: {e}")
        st.stop()

    # Check extracted text
    if len(resume_text) < 100:

        st.error(
            "Could not extract enough text from the PDF. "
            "Please use a text-based PDF rather than a scanned image."
        )

        st.stop()

    # Analyze resume and JD
    with st.spinner(
        "Loading embedding model and analyzing..."
    ):

        try:

            analysis = analyze_resume_job(
                resume_text,
                job_text
            )

        except Exception as e:

            st.error(
                f"Error during resume analysis: {e}"
            )

            st.stop()

    # Save results
    st.session_state.resume_text = resume_text

    st.session_state.job_text = job_text

    st.session_state.analysis = analysis

    # Reset interview result when a new analysis is performed
    st.session_state.interview_result = None

    st.session_state.interview_used_llm = False

    st.success("Resume analysis completed successfully!")


# --------------------------------------------------
# DISPLAY ANALYSIS
# --------------------------------------------------

analysis = st.session_state.analysis


if analysis:

    st.subheader("📊 Match Overview")

    c1, c2, c3 = st.columns(3)

    # Overall Match
    c1.metric(
        "Overall Match",
        f"{analysis['match_score'] * 100:.1f}%"
    )

    # Semantic Similarity
    c2.metric(
        "Semantic Similarity",
        f"{analysis['semantic_similarity'] * 100:.1f}%"
    )

    # Skill Coverage
    c3.metric(
        "Skill Coverage",
        f"{analysis['skill_coverage'] * 100:.1f}%"
    )


    # Progress bar
    st.progress(
        float(analysis["match_score"])
    )


    # --------------------------------------------------
    # MATCHED + MISSING SKILLS
    # --------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.subheader("✅ Matched Skills")

        matched_skills = analysis.get(
            "matched_skills",
            []
        )

        if matched_skills:

            st.write(
                ", ".join(matched_skills)
            )

        else:

            st.write("None detected")


    with right:

        st.subheader("⚠️ Skill Gaps")

        missing_skills = analysis.get(
            "missing_skills",
            []
        )

        if missing_skills:

            st.write(
                ", ".join(missing_skills)
            )

        else:

            st.write("None detected")


    # --------------------------------------------------
    # DETECTED SKILLS
    # --------------------------------------------------

    st.subheader("🔍 Detected Skills")

    resume_skills = analysis.get(
        "resume_skills",
        []
    )

    job_skills = analysis.get(
        "job_skills",
        []
    )

    st.write(
        "**Resume:**",
        ", ".join(resume_skills)
        if resume_skills
        else "None"
    )

    st.write(
        "**Job:**",
        ", ".join(job_skills)
        if job_skills
        else "None"
    )


    # --------------------------------------------------
    # INTERVIEW COPILOT
    # --------------------------------------------------

    st.divider()

    st.subheader("🧠 LLM Interview Copilot")

    st.write(
        "Generate interview questions based on "
        "the candidate's resume and target job description."
    )


    if st.button(
        "Generate Interview Pack"
    ):

        with st.spinner(
            "Generating interview questions..."
        ):

            try:

                output = generate_interview_pack(
                    st.session_state.resume_text,
                    st.session_state.job_text,
                    st.session_state.analysis
                )

                # ------------------------------------------
                # HANDLE DIFFERENT RETURN FORMATS
                # ------------------------------------------

                if isinstance(output, tuple):

                    # First value = generated result
                    result = output[0]

                    # Second value = whether Ollama was used
                    if len(output) > 1:

                        used_llm = output[1]

                    else:

                        used_llm = False

                else:

                    result = output

                    used_llm = False


                # Save result
                st.session_state.interview_result = result

                st.session_state.interview_used_llm = used_llm


            except Exception as e:

                st.error(
                    f"Error generating interview pack: {e}"
                )

                st.stop()


    # --------------------------------------------------
    # SHOW INTERVIEW RESULT
    # --------------------------------------------------

    if st.session_state.interview_result:

        if st.session_state.interview_used_llm:

            st.caption(
                "Generated with local Ollama LLM."
            )

        else:

            st.caption(
                "Fallback mode: Ollama not detected."
            )

        st.markdown(
            st.session_state.interview_result
        )


    # --------------------------------------------------
    # RAG CAREER Q&A
    # --------------------------------------------------

    st.divider()

    st.subheader("🔎 RAG Career Q&A")

    question = st.text_input(
        "Ask something about the resume/JD",
        placeholder=(
            "What AI skills does the candidate "
            "need to strengthen?"
        )
    )


    if st.button("Ask"):

        if not question.strip():

            st.warning(
                "Enter a question."
            )

        else:

            with st.spinner(
                "Retrieving relevant document context..."
            ):

                try:

                    rag_output = rag_answer(
                        question,
                        st.session_state.resume_text,
                        st.session_state.job_text
                    )


                    # --------------------------------------
                    # HANDLE RAG RETURN FORMAT
                    # --------------------------------------

                    if isinstance(
                        rag_output,
                        tuple
                    ):

                        answer = rag_output[0]

                        if len(rag_output) > 1:

                            used_llm = rag_output[1]

                        else:

                            used_llm = False

                    else:

                        answer = rag_output

                        used_llm = False


                    # --------------------------------------
                    # DISPLAY ANSWER
                    # --------------------------------------

                    if used_llm:

                        st.caption(
                            "Answer generated from retrieved context."
                        )

                    else:

                        st.caption(
                            "RAG retrieval worked; "
                            "local LLM is unavailable."
                        )

                    st.write(answer)


                except Exception as e:

                    st.error(
                        f"Error while answering the question: {e}"
                    )


# --------------------------------------------------
# INITIAL MESSAGE
# --------------------------------------------------

else:

    st.info(
        "Upload a resume PDF, paste a job description, "
        "then click Analyze Candidate."
    )