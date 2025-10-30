# 🧠 AI Resume Match Analyzer

An intelligent web app that scores your resume against a job description using a hybrid AI model. It provides a detailed breakdown and personalized, AI-powered advice from Google's Gemini.

---

## ✨ Features

* **Weighted Scoring System:** Calculates a final match score based on three components:
    * **Content (Skills):** 50%
    * **Similarity (Context):** 30%
    * **Format (Structure):** 20%
* **AI-Powered Keyword Extraction:** Uses the **Google Gemini API** to analyze both the resume and job description, extracting the most relevant keywords, skills, and technologies like an expert recruiter.
* **Semantic Content Matching:** Instead of simple keyword counting, it uses a **SentenceTransformer** model to compare the *meaning* of the extracted keyword lists, giving credit for semantically similar skills (e.g., "ML" vs. "Machine Learning").
* **Contextual Similarity Matching:** Reads the *full text* of both documents to understand the overall "vibe" and contextual match, ensuring the resume's story aligns with the job's role.
* **🤖 AI Career Advisor:** Leverages the **Google Gemini API** to provide custom, actionable advice based on your specific score breakdown and missing skills.

---

## ⚙️ How It Works (The "Brain")

This project uses a sophisticated hybrid approach to provide the most accurate analysis:

1.  **Input:** User uploads a resume (PDF) and pastes a job description.
2.  **Text Extraction:** `PyPDF2` reads and cleans the text from the PDF.
3.  **AI Keyword Extraction:** The app sends *both* texts to the **Gemini API** with a custom prompt, asking it to extract the top 30-40 most important keywords, skills, and tools.
4.  **Score Calculation:**
    * **Content Score (50%):** The `SentenceTransformer` model encodes the two *lists of Gemini-keywords* into vectors and calculates their cosine similarity. This measures how well the *core skills* match.
    * **Similarity Score (30%):** The `SentenceTransformer` model encodes the *full text* of the resume and JD into vectors and calculates their cosine similarity. This measures the *overall contextual* match.
    * **Format Score (20%):** A simple heuristic check (`re.search`) looks for key headers (e.g., "Experience", "Education", "Skills") and checks the document's length.
5.  **Final Report:** The three scores are combined using their weights to produce the final percentage.
6.  **AI Advice:** If requested, all this data (scores, missing keywords) is sent to the **Gemini API** for personalized improvement tips.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| Web Framework | **Streamlit** | Building the interactive user interface. |
| PDF Reading | **PyPDF2** | Extracting text from the uploaded resume. |
| Semantic AI | **Sentence-Transformers** | Calculating similarity scores (for full text & keywords). |
| Generative AI | **Google Gemini (google-gen-ai)** | AI Keyword Extraction & AI Career Advice. |
| Core | **Python 3.9+** | Base language. |
| Other | **NumPy, re** | Numerical operations and text cleaning. |

---

## 🚀 Setup & Run

### 1. Clone the repository
```bash
git clone [https://github.com/Arcius07/resume-analyzer.git](https://github.com/Arcius07/resume-analyzer.git)
cd resume-analyzer

### 2. Create and activate a virtual environment
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run the Streamlit app

streamlit run app.py

🔑 Configuration
This app requires a Google Gemini API key to function.

Get your free API key from Google AI Studio.

Run the Streamlit app.

Paste your API key into the input box in the sidebar. The app is now ready to use!

👨‍💻 Author
Sarthak Thakur

LinkedIn: https://www.linkedin.com/in/sarthak-thakur-2b9788360/

GitHub: https://github.com/Arcius07

🪶 License
This project is licensed under the MIT License.