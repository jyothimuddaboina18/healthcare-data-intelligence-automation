import io
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Healthcare Data Intelligence", page_icon="🏥", layout="wide")

BASE_DIR = Path(__file__).parent
DEFAULT_DATA = BASE_DIR / "data" / "sample_clinics.csv"

REQUIRED_COLUMNS = ["Clinic_Name", "City", "State", "Phone", "Website", "Speciality"]

def clean_healthcare_data(raw_df):
    df = raw_df.copy()
    # Standardise column names and retain only expected fields where available.
    df.columns = [str(c).strip() for c in df.columns]
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    for col in missing_cols:
        df[col] = pd.NA
    df = df[REQUIRED_COLUMNS]
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    before = len(df)
    duplicate_mask = df.duplicated(subset=["Clinic_Name", "City", "State"], keep="first")
    duplicate_count = int(duplicate_mask.sum())
    df = df.loc[~duplicate_mask].copy()
    df["Data_Quality"] = df.apply(
        lambda r: "Needs Review" if pd.isna(r["Phone"]) or pd.isna(r["Website"]) else "Complete",
        axis=1
    )
    return df, duplicate_count, before

def build_summary(df):
    lines = [
        f"Number of unique clinic records: {len(df)}",
        "Clinics by city:\n" + df["City"].fillna("Unknown").value_counts().to_string(),
        "Clinics by state:\n" + df["State"].fillna("Unknown").value_counts().to_string(),
        "Speciality distribution:\n" + df["Speciality"].fillna("Unknown").value_counts().to_string(),
        "Data quality:\n" + df["Data_Quality"].value_counts().to_string(),
        f"Records missing phone: {int(df['Phone'].isna().sum())}",
        f"Records missing website: {int(df['Website'].isna().sum())}",
    ]
    return "\n\n".join(lines)

def ask_gemini(api_key, prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    response = requests.post(
        url,
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=45
    )
    response.raise_for_status()
    payload = response.json()
    return payload["candidates"][0]["content"]["parts"][0]["text"]

st.title("🏥 Healthcare Data Intelligence & Automation")
st.caption("A portfolio prototype for cleaning clinic-directory data, reviewing data quality, exploring trends and generating AI-assisted summaries.")
st.info("Demo data is fictional. Do not upload patient records or sensitive personal/medical information.")

with st.sidebar:
    st.header("Data source")
    uploaded = st.file_uploader("Upload a clinic CSV", type=["csv"])
    st.caption("Expected columns: Clinic_Name, City, State, Phone, Website, Speciality")
    st.divider()
    st.header("Optional AI analysis")
    gemini_key = st.text_input("Gemini API key", type="password", help="Optional. Enter your own key; it is used only for this session.")
    st.caption("Without an API key, all cleaning, charts and exports still work.")

if uploaded is not None:
    raw = pd.read_csv(uploaded)
else:
    raw = pd.read_csv(DEFAULT_DATA)

cleaned, duplicate_count, original_count = clean_healthcare_data(raw)
st.sidebar.success(f"Loaded {original_count} source rows")

st.subheader("Data overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Source records", f"{original_count:,}")
m2.metric("Unique clinics", f"{len(cleaned):,}")
m3.metric("Duplicates removed", f"{duplicate_count:,}")
m4.metric("Needs review", f"{int((cleaned['Data_Quality'] == 'Needs Review').sum()):,}")

st.divider()
left, right = st.columns(2)
with left:
    city_data = cleaned["City"].fillna("Unknown").value_counts().rename_axis("City").reset_index(name="Clinics")
    st.plotly_chart(px.bar(city_data, x="City", y="Clinics", title="Clinics by city", text="Clinics"), use_container_width=True)
with right:
    spec_data = cleaned["Speciality"].fillna("Unknown").value_counts().rename_axis("Speciality").reset_index(name="Clinics")
    st.plotly_chart(px.pie(spec_data, names="Speciality", values="Clinics", title="Speciality mix"), use_container_width=True)

st.subheader("Explore clinic records")
filter_col1, filter_col2, filter_col3 = st.columns(3)
city_options = ["All"] + sorted(cleaned["City"].dropna().astype(str).unique().tolist())
spec_options = ["All"] + sorted(cleaned["Speciality"].dropna().astype(str).unique().tolist())
quality_options = ["All"] + sorted(cleaned["Data_Quality"].unique().tolist())
city_choice = filter_col1.selectbox("City", city_options)
spec_choice = filter_col2.selectbox("Speciality", spec_options)
quality_choice = filter_col3.selectbox("Data quality", quality_options)
search = st.text_input("Search clinic name")
view = cleaned.copy()
if city_choice != "All": view = view[view["City"] == city_choice]
if spec_choice != "All": view = view[view["Speciality"] == spec_choice]
if quality_choice != "All": view = view[view["Data_Quality"] == quality_choice]
if search: view = view[view["Clinic_Name"].str.contains(search, case=False, na=False)]
st.dataframe(view, use_container_width=True, hide_index=True)

st.subheader("Download outputs")
csv_bytes = cleaned.to_csv(index=False).encode("utf-8")
st.download_button("Download cleaned clinic data (CSV)", csv_bytes, "cleaned_clinics.csv", "text/csv")
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    cleaned.to_excel(writer, index=False, sheet_name="Cleaned Clinics")
    pd.DataFrame({"Metric":["Source records","Unique clinics","Duplicates removed","Needs review"],
                  "Value":[original_count,len(cleaned),duplicate_count,int((cleaned["Data_Quality"]=="Needs Review").sum())]}).to_excel(writer,index=False,sheet_name="Summary")
st.download_button("Download report (Excel)", excel_buffer.getvalue(), "healthcare_intelligence_report.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.subheader("AI-assisted insight generation")
summary = build_summary(cleaned)
with st.expander("Preview data summary used for AI analysis"):
    st.text(summary)
if st.button("Generate AI insights", type="primary", disabled=not bool(gemini_key.strip())):
    prompt = f"""You are a careful data analyst. Analyse this aggregate clinic-directory dataset summary.
Do not invent facts, clinic contact details, medical advice, or patient outcomes.
Clearly distinguish observed patterns from recommendations. Mention that the dataset is a small demo
and that records are not verified. Give: (1) 3 concise observations, (2) data quality risks,
(3) 3 practical next steps. Keep the answer under 250 words.

DATA SUMMARY:
{summary}"""
    try:
        with st.spinner("Generating insights..."):
            answer = ask_gemini(gemini_key.strip(), prompt)
        st.markdown(answer)
        st.caption("AI-generated text; review before using. No patient data should be entered.")
    except Exception as exc:
        st.error(f"AI request failed: {exc}")
elif not gemini_key.strip():
    st.caption("Add a Gemini API key in the sidebar to enable the optional AI insight button. The rest of the dashboard works without it.")

with st.expander("About this prototype"):
    st.write("This project demonstrates CSV ingestion, data standardisation, duplicate detection, missing-field checks, interactive analytics, report exports and optional LLM-based summarisation.")
    st.write("The supplied sample clinic names and contact details are fictional placeholders and must not be represented as real providers.")
