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

# Step 3: Cognitive Domain Distribution (%)
st.subheader("Step 3: Cognitive Domain Distribution (%) for Each Question Type")
cd_perc = {}
cd_marks = {}

for sec, sec_marks in zip(["MCQ", "SAQ", "LAQ"], [mcq_marks, saq_marks, laq_marks]):
    st.markdown(f"**{sec} Distribution**")
    col1, col2, col3 = st.columns(3)
    with col1:
        r = st.number_input(f"Recall % in {sec}", value=30, key=f"r_{sec}")
    with col2:
        u = st.number_input(f"Understand % in {sec}", value=30, key=f"u_{sec}")
    with col3:
        a = st.number_input(f"Apply % in {sec}", value=40, key=f"a_{sec}")
    cd_perc[sec] = [r, u, a]
    cd_marks[sec] = [round(r * sec_marks / 100), round(u * sec_marks / 100), round(a * sec_marks / 100)]

cdm_df = pd.DataFrame(cd_marks, index=["Recall", "Understand", "Apply"])
st.subheader("Step 4: Cognitive Domain Marks (Auto-calculated)")
st.dataframe(cdm_df, use_container_width=True)

# Step 5: Unit Data Input
st.subheader("Step 5: Enter Units and I x F Scores")
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

# Step 6: Combined Grid Entry (Unit + Grid)
st.subheader("Step 6: Combined Grid Entry")
combined_grid = pd.DataFrame(unit_df)

for col in ["MCQ-R", "MCQ-U", "MCQ-A", "SAQ-R", "SAQ-U", "SAQ-A", "LAQ-R", "LAQ-U", "LAQ-A"]:
    combined_grid[col] = 0

editable_grid = st.data_editor(combined_grid, use_container_width=True, key="combined_editor")

# Compute Totals
grid_columns = ["MCQ-R", "MCQ-U", "MCQ-A", "SAQ-R", "SAQ-U", "SAQ-A", "LAQ-R", "LAQ-U", "LAQ-A"]
editable_grid["Grid Total"] = editable_grid[grid_columns].sum(axis=1)

total_row = editable_grid[grid_columns + ["Grid Total"]].sum().to_frame().T
final_df = pd.concat([editable_grid, total_row.rename(index={0: "Total"})], ignore_index=False)

# Display Final Table
st.subheader("Generated Blueprint Table (Combined View)")
st.dataframe(final_df, use_container_width=True)

# CSV Download
def convert_df_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_csv(editable_grid)
st.download_button("📥 Download as CSV", csv_data, "blueprint_grid.csv", "text/csv")

# PDF Export
def export_to_pdf(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=7)

    col_widths = [max(len(str(cell)) for cell in df[col].astype(str)) * 2.5 for col in df.columns]
    row_height = 8

    # Header
    for i, col in enumerate(df.columns):
        width = col_widths[i] if col_widths[i] < 35 else 35
        pdf.cell(width, row_height, str(col), border=1, align='C')
    pdf.ln(row_height)

    # Data Rows
    for _, row in df.iterrows():
        for i, val in enumerate(row):
            width = col_widths[i] if col_widths[i] < 35 else 35
            pdf.cell(width, row_height, str(val), border=1, align='C')
        pdf.ln(row_height)

    output = BytesIO()
    pdf.output(output, dest='F')
    pdf_bytes = output.getvalue()
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="blueprint_grid.pdf">📄 Download as PDF</a>'
    return href

st.markdown(export_to_pdf(editable_grid), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Made by **MERIT India** | Logo © All rights reserved")
