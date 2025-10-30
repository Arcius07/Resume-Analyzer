import streamlit as st
from utils import (
    get_text_from_pdf,
    clean_text,
    get_gemini_keywords,
    calculate_similarity_score,
    calculate_semantic_keyword_score, # Use semantic keyword score
    calculate_format_score,
    get_gemini_advice
)

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# Sidebar for API key
with st.sidebar:
    st.header("🤖 AI Features")
    st.markdown("Uses Google Gemini for keywords & advice.")
    gemini_key = st.text_input("Enter Google AI Studio API Key", type="password", help="Get your free key from Google AI Studio")
    if not gemini_key:
        st.warning("Add Google API key for AI features.")
    st.markdown("[Get your free key here](https://makersuite.google.com/app/apikey)")

# Main app layout
st.title("🧠 AI Resume Match Analyzer")
st.caption("A project by Sarthak")

pdf_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_description_text = st.text_area("Paste Job Description")

# Only proceed if both inputs are available
if pdf_file and job_description_text:

    if st.button("Analyze My Resume"):
        if not gemini_key:
            st.error("Please enter your Google API Key in the sidebar first.")
        else:
            analysis_failed = False
            # Processing steps with Gemini keyword extraction first
            with st.spinner("Analyzing with Gemini... (Extracting keywords...)"):
                pdf_bytes = pdf_file.getvalue()
                resume_text = get_text_from_pdf(pdf_bytes)
                resume_text = clean_text(resume_text)
                jd_text = clean_text(job_description_text)

                # Get keywords using Gemini
                st.write("Extracting keywords via Gemini...") # Let user know
                resume_keywords = get_gemini_keywords(gemini_key, resume_text)
                jd_keywords = get_gemini_keywords(gemini_key, jd_text)
                st.write(f"Resume Keywords: {len(resume_keywords)}, JD Keywords: {len(jd_keywords)}")

                if not resume_keywords or not jd_keywords:
                     st.error("Keyword extraction failed. Check API key/status or content. Cannot score.")
                     analysis_failed = True

            # Calculate scores only if keywords were extracted
            if not analysis_failed:
                with st.spinner("Calculating scores..."):
                    similarity_score = calculate_similarity_score(resume_text, jd_text)
                    # Use semantic keyword score function
                    keyword_score, matched_keywords, missing_keywords = calculate_semantic_keyword_score(resume_keywords, jd_keywords)
                    format_score = calculate_format_score(resume_text)

                    # Calculate final weighted score
                    final_score = (keyword_score * 0.50) + (similarity_score * 0.30) + (format_score * 0.20)

                    # Save results to session state
                    st.session_state.missing_keywords = missing_keywords
                    st.session_state.jd_text = jd_text
                    st.session_state.show_results = True
                    st.session_state.scores = {
                        "final": round(final_score, 2),
                        "content": keyword_score,
                        "similarity": similarity_score,
                        "format": format_score
                    }
                    st.session_state.matched_keywords = matched_keywords # Save exact matches too
            else:
                 st.session_state.show_results = False # Don't show results if failed

# Display results if analysis was successful
if st.session_state.get('show_results', False):
    st.markdown("---") # Separator

    # Display final score and feedback
    st.subheader("📊 Final Weighted Score")
    final_score = st.session_state.scores['final']
    st.metric("Overall Match Score", f"{final_score}%")

    if final_score >= 85:
        st.success("🎉 Excellent Fit!")
    elif final_score >= 65:
        st.info(f"✅ Good Fit. Check breakdown/advice to improve.")
    else:
        st.error(f"❌ Poor Fit. See advice below.")

    # Display score breakdown
    st.subheader("Score Breakdown")
    col1, col2, col3 = st.columns(3)
    col1.metric("Content (Skills)", f"{st.session_state.scores['content']}%", help="50% weight (Semantic Keyword Match)")
    col2.metric("Similarity (Context)", f"{st.session_state.scores['similarity']}%", help="30% weight (Full Text Meaning Match)")
    col3.metric("Format (Sections)", f"{st.session_state.scores['format']}%", help="20% weight (Structure Check)")

    # Display keyword analysis (exact matches/misses are still useful)
    st.subheader("🧩 Keyword Analysis (via Gemini)")
    col1, col2 = st.columns(2)
    with col1:
        st.warning("**Keywords Missing (Exact Match):**")
        if st.session_state.missing_keywords:
            st.write(", ".join(st.session_state.missing_keywords))
        else:
            st.write("None (based on exact match).")
    with col2:
        st.success("**Keywords Found (Exact Match):**")
        if st.session_state.matched_keywords:
            st.write(", ".join(st.session_state.matched_keywords))
        else:
            st.write("No exact matches found.")

    # Display AI Advisor section
    st.markdown("---")
    st.subheader("🤖 AI Career Advisor")

    if st.button("Get Gemini's Advice"):
        if not gemini_key:
            st.error("Add your Google API Key in the sidebar.")
        else:
            with st.spinner("Gemini is generating advice..."):
                # Call Gemini for advice using the saved data
                advice = get_gemini_advice(gemini_key,
                                           st.session_state.missing_keywords,
                                           st.session_state.jd_text,
                                           st.session_state.scores)
                st.markdown(advice)

# Show initial message if inputs are missing and results aren't ready
elif not pdf_file or not job_description_text:
     if not st.session_state.get('show_results', False):
        st.info("Upload resume and paste job description to begin.")