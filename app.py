import tempfile
import streamlit as st

from src.parser import extract_pdf_text, clean_text
from src.pipeline import (
    analyze_resume_job,
    generate_interview_pack,
    rag_answer,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TalentLens AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "analysis": None,
    "resume_text": "",
    "job_text": "",
    "interview_result": "",
    "rag_result": "",
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HEADER
# ============================================================

st.title("🤖 TalentLens AI")

st.subheader(
    "AI Resume Intelligence & Career Copilot"
)

st.write(
    "Analyze your resume against a target job, "
    "identify skill gaps, calculate semantic similarity, "
    "generate interview questions and ask "
    "document-grounded career questions."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("👤 Candidate Profile")

    resume_file = st.file_uploader(
        "Upload Resume",
        type=["pdf"],
    )

    st.divider()

    st.header("🎯 Target Job")

    job_text = st.text_area(
        "Paste Job Description",
        height=300,
        placeholder=(
            "Paste the complete job description here..."
        ),
    )

    st.divider()

    st.caption(
        "TalentLens AI\n"
        "Python • ML • RAG • Ollama"
    )


# ============================================================
# MAIN ANALYZE BUTTON
# ============================================================

st.header("🚀 Resume Analysis")

st.write(
    "Upload your resume and paste the target job description "
    "from the sidebar."
)

analyze_button = st.button(
    "🚀 Analyze My Resume",
    type="primary",
    use_container_width=True,
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze_button:

    # --------------------------------------------
    # Validate resume
    # --------------------------------------------

    if resume_file is None:

        st.error(
            "Please upload your resume PDF first."
        )

        st.stop()


    # --------------------------------------------
    # Validate JD
    # --------------------------------------------

    if not job_text.strip():

        st.error(
            "Please paste the target job description."
        )

        st.stop()


    try:

        # ----------------------------------------
        # Save PDF temporarily
        # ----------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:

            temp_file.write(
                resume_file.getbuffer()
            )

            pdf_path = temp_file.name


        # ----------------------------------------
        # Extract resume
        # ----------------------------------------

        with st.spinner(
            "📄 Reading your resume..."
        ):

            resume_text = clean_text(
                extract_pdf_text(pdf_path)
            )


        if not resume_text or len(resume_text) < 100:

            st.error(
                "Could not extract enough text "
                "from this PDF."
            )

            st.info(
                "Please use a normal text-based PDF "
                "instead of a scanned image."
            )

            st.stop()


        # ----------------------------------------
        # Run ML analysis
        # ----------------------------------------

        with st.spinner(
            "🧠 Running AI/ML resume analysis..."
        ):

            analysis = analyze_resume_job(
                resume_text,
                job_text,
            )


        # ----------------------------------------
        # Save results
        # ----------------------------------------

        st.session_state.resume_text = resume_text

        st.session_state.job_text = job_text

        st.session_state.analysis = analysis

        st.session_state.interview_result = ""

        st.session_state.rag_result = ""


        st.success(
            "✅ Resume analysis completed!"
        )


    except Exception as error:

        st.error(
            "❌ Resume analysis failed."
        )

        st.exception(error)


# ============================================================
# GET CURRENT ANALYSIS
# ============================================================

analysis = st.session_state.analysis


# ============================================================
# DASHBOARD
# ============================================================

if analysis:

    st.divider()

    st.header("📊 Match Overview")


    # --------------------------------------------------------
    # Scores
    # --------------------------------------------------------

    semantic_score = float(
        analysis.get(
            "semantic_similarity",
            0,
        )
    )

    skill_coverage = float(
        analysis.get(
            "skill_coverage",
            0,
        )
    )

    match_score = float(
        analysis.get(
            "match_score",
            0,
        )
    )


    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "🎯 Overall Match",
            f"{match_score * 100:.1f}%",
        )


    with col2:

        st.metric(
            "🧠 Semantic Similarity",
            f"{semantic_score * 100:.1f}%",
        )


    with col3:

        st.metric(
            "🛠 Skill Coverage",
            f"{skill_coverage * 100:.1f}%",
        )


    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    st.write("Overall Match")

    st.progress(
        max(
            0.0,
            min(
                match_score,
                1.0,
            ),
        )
    )


    # ========================================================
    # SKILL ANALYSIS
    # ========================================================

    st.divider()

    st.header("🧩 Skill Analysis")


    matched_skills = analysis.get(
        "matched_skills",
        [],
    ) or []


    missing_skills = analysis.get(
        "missing_skills",
        [],
    ) or []


    resume_skills = analysis.get(
        "resume_skills",
        [],
    ) or []


    job_skills = analysis.get(
        "job_skills",
        [],
    ) or []


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # Matched
    # --------------------------------------------------------

    with col1:

        st.subheader("✅ Matched Skills")

        if matched_skills:

            for skill in matched_skills:

                st.success(
                    skill
                )

        else:

            st.info(
                "No matched skills detected."
            )


    # --------------------------------------------------------
    # Missing
    # --------------------------------------------------------

    with col2:

        st.subheader("⚠️ Skill Gaps")

        if missing_skills:

            for skill in missing_skills:

                st.warning(
                    skill
                )

        else:

            st.success(
                "No major skill gaps detected."
            )


    # --------------------------------------------------------
    # All detected skills
    # --------------------------------------------------------

    with st.expander(
        "🔍 View All Detected Skills"
    ):

        st.write(
            "**Resume Skills**"
        )

        st.write(
            ", ".join(resume_skills)
            if resume_skills
            else "None detected"
        )


        st.write(
            "**Job Skills**"
        )

        st.write(
            ", ".join(job_skills)
            if job_skills
            else "None detected"
        )


    # ========================================================
    # INTERVIEW COPILOT
    # ========================================================

    st.divider()

    st.header(
        "🧠 LLM Interview Copilot"
    )

    st.write(
        "Generate technical, project and behavioral "
        "interview questions based on the resume "
        "and target job."
    )


    interview_button = st.button(
        "🎤 Generate Interview Pack",
        type="primary",
        key="interview_button",
    )


    if interview_button:

        try:

            with st.spinner(
                "🤖 Ollama is generating your interview pack..."
            ):

                generated = generate_interview_pack(
                    st.session_state.resume_text,
                    st.session_state.job_text,
                    st.session_state.analysis,
                )


            # ------------------------------------------------
            # Handle string / tuple safely
            # ------------------------------------------------

            if isinstance(
                generated,
                tuple,
            ):

                if len(generated) >= 1:

                    result = generated[0]

                else:

                    result = ""

            else:

                result = generated


            st.session_state.interview_result = (
                str(result)
                if result
                else ""
            )


            if st.session_state.interview_result:

                st.success(
                    "✅ Interview pack generated!"
                )

            else:

                st.warning(
                    "Ollama returned an empty response."
                )


        except Exception as error:

            st.error(
                "❌ Interview generation failed."
            )

            st.exception(error)


    # --------------------------------------------------------
    # Display interview
    # --------------------------------------------------------

    if st.session_state.interview_result:

        st.subheader(
            "📋 Personalized Interview Pack"
        )

        st.markdown(
            st.session_state.interview_result
        )


    # ========================================================
    # RAG CAREER Q&A
    # ========================================================

    st.divider()

    st.header(
        "🔎 RAG Career Q&A"
    )

    st.write(
        "Ask questions using information from "
        "your resume and target job."
    )


    question = st.text_input(
        "Your question",
        placeholder=(
            "What AI skills should I strengthen?"
        ),
    )


    ask_button = st.button(
        "💬 Ask Career Copilot",
        key="rag_button",
    )


    if ask_button:

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            try:

                with st.spinner(
                    "🔎 Retrieving relevant context..."
                ):

                    rag_response = rag_answer(
                        question,
                        st.session_state.resume_text,
                        st.session_state.job_text,
                    )


                # --------------------------------------------
                # Handle tuple/string
                # --------------------------------------------

                if isinstance(
                    rag_response,
                    tuple,
                ):

                    if len(rag_response) >= 1:

                        answer = rag_response[0]

                    else:

                        answer = ""

                else:

                    answer = rag_response


                st.session_state.rag_result = (
                    str(answer)
                    if answer
                    else ""
                )


            except Exception as error:

                st.error(
                    "❌ RAG processing failed."
                )

                st.exception(error)


    if st.session_state.rag_result:

        st.subheader(
            "💡 Career Copilot Answer"
        )

        st.info(
            st.session_state.rag_result
        )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.divider()

    st.info(
        "👈 Upload your resume and paste a job description "
        "from the sidebar, then click **Analyze My Resume**."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "TalentLens AI • "
    "Python • Machine Learning • "
    "Sentence Transformers • RAG • Ollama"
)