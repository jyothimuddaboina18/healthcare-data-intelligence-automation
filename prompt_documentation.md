# Prompt Documentation

## Prompt 1 — Project planning
**Initial prompt:** Build a beginner-friendly healthcare data intelligence project using Python, Pandas and Streamlit.

**Iteration:** Keep the scope to clinic-directory data, not patient data. Include cleaning, duplicate detection, missing-field checks, dashboard, exports and an optional AI summary.

## Prompt 2 — Data cleaning
**Prompt:** Write a reusable Pandas function that standardises text columns, removes duplicate clinic rows using Clinic_Name + City + State, preserves missing values, and flags records missing phone or website.

**Iteration:** Add counts for original records and duplicates removed; avoid filling missing contact details with guesses.

## Prompt 3 — Dashboard
**Prompt:** Create a Streamlit dashboard with CSV upload, KPI metrics, city and speciality charts, filters, search and CSV/Excel downloads.

**Iteration:** Make uploaded CSV handling robust when optional columns are missing. Clearly identify the sample data as fictional.

## Prompt 4 — AI insight generation
**Prompt:** Act as a careful data analyst. Analyse aggregate clinic-directory metrics. Do not invent facts or contact information. Separate observations from recommendations, mention limitations and keep the response concise.

**Iteration:** Use an optional Gemini API key entered at runtime; do not hardcode credentials or send patient data. Keep core dashboard functionality available without the key.

## Responsible-use notes
- The sample records are fictional placeholders.
- No patient or medical data is included.
- AI output is not guaranteed to be correct and requires human review.
- Do not claim the app verifies real clinic details.
