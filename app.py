import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Assessment Blueprint Generator", layout="wide")

# Logo and Title
col1, col2 = st.columns([1, 10])
with col1:
    st.image("logo.jpg", width=80)
with col2:
    st.title("Blueprint Generator - MERIT India")

st.markdown("""
This app helps you build a subject-wise blueprint based on weightage distribution and domain-specific item allocation.
Fill in the data below and download your blueprint grid.
""")

# Input Section
total_marks = st.number_input("Enter Total Marks for Theory Paper", value=100)

st.subheader("Section-wise Distribution (MCQ, SAQ, LAQ)")
col1, col2, col3 = st.columns(3)
with col1:
    mcq_marks = st.number_input("MCQ Marks", value=30)
with col2:
    saq_marks = st.number_input("SAQ Marks", value=30)
with col3:
    laq_marks = st.number_input("LAQ Marks", value=40)

st.subheader("Cognitive Domain Distribution (%) for Each Question Type")
domain_labels = ["Recall (R)", "Understand (U)", "Apply (A)"]

col1, col2, col3 = st.columns(3)
with col1:
    r_mcq = st.number_input("Recall % in MCQ", value=30)
    r_saq = st.number_input("Recall % in SAQ", value=30)
    r_laq = st.number_input("Recall % in LAQ", value=10)
with col2:
    u_mcq = st.number_input("Understand % in MCQ", value=40)
    u_saq = st.number_input("Understand % in SAQ", value=30)
    u_laq = st.number_input("Understand % in LAQ", value=30)
with col3:
    a_mcq = st.number_input("Apply % in MCQ", value=30)
    a_saq = st.number_input("Apply % in SAQ", value=40)
    a_laq = st.number_input("Apply % in LAQ", value=60)

# Unit-wise data input
st.subheader("Unit-wise I x F Scores")
unit_data = st.text_area("Paste Unit-wise Data (Format: Unit Name, I x F Score)", 
"Gastrointestinal and Hepatobiliary, 143\nRenal and Genitourinary, 101\nEndocrine Disorders, 83\nRheumatology and Connective Tissue, 34")

# Parse input
unit_rows = [row.strip().split(',') for row in unit_data.strip().split('\n') if row.strip()]
unit_df = pd.DataFrame(unit_rows, columns=["Unit", "IxF"])
unit_df["IxF"] = unit_df["IxF"].astype(float)
unit_df["Weightage %"] = round((unit_df["IxF"] / unit_df["IxF"].sum()) * 100)
unit_df["Marks"] = round((unit_df["Weightage %"] / 100) * total_marks)

# Generate Grid
def distribute(marks, r, u, a):
    return [round(marks * r / 100), round(marks * u / 100), round(marks * a / 100)]

def build_grid():
    grid = []
    for _, row in unit_df.iterrows():
        mcq_row = distribute(row['Marks'] * mcq_marks / total_marks, r_mcq, u_mcq, a_mcq)
        saq_row = distribute(row['Marks'] * saq_marks / total_marks, r_saq, u_saq, a_saq)
        laq_row = distribute(row['Marks'] * laq_marks / total_marks, r_laq, u_laq, a_laq)
        grid.append(mcq_row + saq_row + laq_row)
    return pd.DataFrame(grid, columns=["MCQ-R", "MCQ-U", "MCQ-A", "SAQ-R", "SAQ-U", "SAQ-A", "LAQ-R", "LAQ-U", "LAQ-A"])

blueprint_df = pd.concat([unit_df, build_grid()], axis=1)

# Display
st.subheader("Generated Blueprint Table")
st.dataframe(blueprint_df, use_container_width=True)

# Export Section
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df(blueprint_df)
st.download_button("📥 Download as CSV", csv_data, "blueprint_grid.csv", "text/csv")

st.markdown("---")
st.markdown("Made by **MERIT India** | Logo © All rights reserved")
