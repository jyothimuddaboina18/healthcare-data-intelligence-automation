# Healthcare Data Intelligence & Automation

A Streamlit portfolio prototype for clinic-directory data quality and intelligence.

## Features
- Upload a clinic CSV or use the included fictional sample dataset.
- Standardise text fields and identify duplicate clinics by name + city + state.
- Flag rows with missing phone or website details.
- Explore clinics by city, speciality and data-quality status.
- View interactive Plotly charts.
- Download cleaned CSV and Excel summary.
- Optional Gemini-powered AI summary using a user-provided API key.

## Important data and safety note
The included sample data is fictional. Do not treat its names, phone numbers or websites as real.
Do not upload patient records, medical histories, or sensitive personal information. This is a
directory-data demonstration, not a clinical decision-support tool. AI output can be wrong and
must be reviewed.

## Run locally (Windows)
1. Install Python 3.10+.
2. Open Command Prompt in this project folder.
3. Create and activate a virtual environment (optional but recommended):
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```cmd
   python -m pip install -r requirements.txt
   ```
5. Launch:
   ```cmd
   python -m streamlit run app.py
   ```
6. Open the local URL printed in the terminal (usually http://localhost:8501).

## CSV format
The app expects these columns (missing columns are added as blank):
`Clinic_Name, City, State, Phone, Website, Speciality`

## Optional AI feature
Create a Gemini API key from Google's AI developer platform and paste it into the password field
in the sidebar. The key is used for the current session only and is not saved in this project.
Do not commit API keys to GitHub. The AI prompt uses aggregate counts only, not uploaded row-level
contact details.

## Project structure
- `app.py`: Streamlit application
- `data/sample_clinics.csv`: fictional test data
- `prompts/prompt_documentation.md`: prompt and iteration record
- `requirements.txt`: Python dependencies
