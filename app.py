import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import base64

st.set_page_config(page_title="Assessment Blueprint Generator", layout="wide")

# Title and Logo
col1, col2 = st.columns([1, 10])
with col1:
    st.image("logo.jpg", width=80)
with col2:
    st.title("Blueprint Generator - MERIT India")

st.markdown("""
This app helps you build a subject-wise assessment blueprint. Define section-wise weightage, cognitive domain splits, and manually enter distribution.
""")

# Step 1: Total Marks
st.subheader("Step 1: Total Marks for Theory Paper")
total_marks = st.number_input("Enter Total Marks", value=100)

# Step 2: Section-wise Distribution (%)
st.subheader("Step 2: Section-wise Distribution (%)")
col1, col2, col3 = st.columns(3)
with col1:
    mcq_pct = st.number_input("MCQ %", value=30)
with col2:
    saq_pct = st.number_input("SAQ %", value=30)
with col3:
    laq_pct = st.number_input("LAQ %", value=40)

mcq_marks = round(mcq_pct * total_marks / 100)
saq_marks = round(saq_pct * total_marks / 100)
laq_marks = round(laq_pct * total_marks / 100)

section_df = pd.DataFrame({
    "Section": ["MCQ", "SAQ", "LAQ"],
    "% Weightage": [mcq_pct, saq_pct, laq_pct],
    "Marks Allocated": [mcq_marks, saq_marks, laq_marks]
})
st.dataframe(section_df, use_container_width=True)

# Step 3: Unit Data Input
st.subheader("Step 3: Enter Units and I x F Scores")
unit_data = st.text_area("Paste unit data (e.g., Unit Name, I x F Score)",
"""Gastrointestinal and Hepatobiliary, 143
Renal and Genitourinary, 101
Endocrine Disorders, 83
Rheumatology and Connective Tissue, 34""")

unit_rows = [row.strip().split(',') for row in unit_data.strip().split('\n') if row.strip() and len(row.strip().split(',')) == 2]
unit_df = pd.DataFrame(unit_rows, columns=["Unit", "IxF"])
unit_df["IxF"] = unit_df["IxF"].astype(float)
unit_df["Weightage %"] = round((unit_df["IxF"] / unit_df["IxF"].sum()) * 100)
unit_df["Marks"] = round((unit_df["Weightage %"] / 100) * total_marks)

# Step 4: Cognitive Domain Distribution Grid
st.subheader("Step 4: Enter Grid Values")
cog_cols = ["MCQ-R", "MCQ-U", "MCQ-A", "SAQ-R", "SAQ-U", "SAQ-A", "LAQ-R", "LAQ-U", "LAQ-A"]
combined_df = unit_df.copy()
for col in cog_cols:
    combined_df[col] = 0

edited_df = st.data_editor(combined_df, use_container_width=True, key="merged_grid")

# Add Grid Total
edited_df["Grid Total"] = edited_df[cog_cols].sum(axis=1)

# Display Final Table
st.subheader("Generated Blueprint Table")
st.dataframe(edited_df, use_container_width=True)

# CSV Download
def convert_df_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_csv(edited_df)
st.download_button("📥 Download as CSV", csv_data, "blueprint_grid.csv", "text/csv")

# PDF Download
st.subheader("📄 Export to PDF")
def export_to_pdf(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", size=7)

    col_widths = []
    max_col_width = 30
    for col in df.columns:
        max_len = max(df[col].astype(str).apply(len).max(), len(str(col)))
        col_widths.append(min(max_col_width, max_len * 2.5))

    row_height = 8
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], row_height, str(col), border=1, align='C')
    pdf.ln(row_height)

    for _, row in df.iterrows():
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], row_height, str(val), border=1, align='C')
        pdf.ln(row_height)

    output = BytesIO()
    pdf.output(output, dest='F')
    pdf_bytes = output.getvalue()
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="blueprint_grid.pdf">📥 Download as PDF</a>'
    return href

st.markdown(export_to_pdf(edited_df), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Made by **MERIT India** | Logo © All rights reserved")
