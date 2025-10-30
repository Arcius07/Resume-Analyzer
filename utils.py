import re
import PyPDF2
from sentence_transformers import SentenceTransformer, util
import streamlit as st
import io
import google.generativeai as genai

# --- Load Models (Cached) ---

@st.cache_resource(show_spinner=False)
def load_sbert():
    # Load the sentence transformer model
    print("Loading SentenceTransformer model...") # Keep for first run
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("SentenceTransformer model loaded.")
    return model

# Load the model needed for similarity calculations
model = load_sbert()

# --- PDF & Text Functions ---

@st.cache_data(show_spinner=False)
def get_text_from_pdf(pdf_bytes):
    # Reads text from the uploaded PDF
    text = ""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text

@st.cache_data(show_spinner=False)
def clean_text(text):
    # Simple text cleaning (whitespace)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# --- Scoring Functions ---

# **Keyword Extraction via Gemini**
def get_gemini_keywords(api_key, text_to_analyze):
    # Uses Gemini API to extract relevant keywords
    if not api_key:
        raise ValueError("API Key is needed for Gemini keywords.")

    try:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('gemini-flash-latest')
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return []

    # Prompt asking Gemini to act like a keyword extractor
    prompt = f"""
    Task: Extract the most important keywords and skills from the following text.
    Prioritize: Specific technical skills, Software/Tools, Key job titles, Methodologies, Action verbs for accomplishments.
    Exclude: Generic terms, Locations, company names, people's names, dates, numbers, contact info, general soft skills.
    Format: Return ONLY a comma-separated list of the top 30-40 keywords/skills, all in lowercase. Normalize similar terms. No intro text.
    Text to Analyze: "{text_to_analyze[:3500]}"
    Keywords:
    """
    try:
        response = gemini_model.generate_content(prompt)
        if not response.parts:
            st.warning("Keyword extraction blocked. Returning empty list.")
            return []
        # Process the response string into a list
        raw_keywords = response.text.split(',')
        keywords = [kw.strip().lower() for kw in raw_keywords if kw.strip()]
        keywords = [kw for kw in keywords if kw] # Remove empty strings
        return keywords
    except Exception as e:
        st.error(f"Error calling Gemini for keywords: {e}")
        return []

# **Semantic Keyword Score Calculation**
def calculate_semantic_keyword_score(resume_keywords, jd_keywords):
    # Calculates keyword score based on MEANING similarity
    if not resume_keywords or not jd_keywords:
        return 0.0, [], []

    # Join keywords into strings for encoding
    resume_kw_string = " ".join(resume_keywords)
    jd_kw_string = " ".join(jd_keywords)

    # Encode the keyword strings using SBERT
    vec_resume_kw = model.encode(resume_kw_string, convert_to_tensor=True)
    vec_jd_kw = model.encode(jd_kw_string, convert_to_tensor=True)

    # Calculate Cosine Similarity
    score = util.pytorch_cos_sim(vec_resume_kw, vec_jd_kw).item()

    # Normalize score to 0-100
    final_score = max(0, score) * 100

    # Calculate exact overlap for display purposes
    jd_set = set(jd_keywords)
    res_set = set(resume_keywords)
    matched = list(jd_set.intersection(res_set))
    missing = list(jd_set.difference(res_set))

    return round(final_score, 2), matched, missing

# **Full Text Similarity Score Calculation**
@st.cache_data(show_spinner=False)
def calculate_similarity_score(resume_text, jd_text):
    # Calculates semantic similarity of the full texts
    res_vec = model.encode(resume_text, convert_to_tensor=True)
    jd_vec = model.encode(jd_text, convert_to_tensor=True)
    score = util.pytorch_cos_sim(res_vec, jd_vec).item()
    final_score = max(0, score) * 100
    return round(final_score, 2)

# **Format Score Calculation**
@st.cache_data(show_spinner=False)
def calculate_format_score(resume_text):
    # Simple check for basic resume sections and length
    text = resume_text.lower()
    score = 0.0
    # Add points for common section headers
    if re.search(r'\b(experience|employment|work history)\b', text): score += 35
    if re.search(r'\b(education|academic)\b', text): score += 25
    if re.search(r'\b(skills|abilities|technologies|competencies)\b', text): score += 25
    # Bonus for reasonable length
    word_count = len(resume_text.split())
    if 250 < word_count < 1200: score += 15
    return min(score, 100.0) # Cap score at 100

# --- AI Advisor (Gemini) ---
def get_gemini_advice(api_key, missing_keywords, jd_text, scores):
    # Calls Gemini API to get resume advice
    if not api_key:
        return "Error: Add your Google AI Studio API Key in the sidebar."
    try:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('gemini-flash-latest')
    except Exception as e:
        return f"Error configuring Gemini: {e}. Check API key."

    # Prompt for the AI coach
    prompt = f"""
    You are an expert career coach. A user analyzed their resume against a job description.
    Data:
    Job Description: "{jd_text[:1000]}"
    Score Breakdown:
    - Final Score: {scores['final']}%
    - Content Match: {scores['content']}% (Semantic keyword match)
    - Context Match: {scores['similarity']}% (Full text meaning match)
    - Format Score: {scores['format']}%
    Missing Skills (Exact Match): "{', '.join(missing_keywords[:20])}"

    Task: Provide friendly, actionable advice using markdown.
    1. Summarize their overall score encouragingly.
    2. Explain the score breakdown (good/bad parts).
    3. Identify 3-5 critical missing skills and explain why they matter for this job.
    4. Suggest 1-2 simple projects/courses to learn these.
    5. Give a resume-ready bullet point example.
    """
    try:
        response = gemini_model.generate_content(prompt)
        if not response.parts:
             return "AI response blocked (maybe safety settings?)."
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {e}"