import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import base64

# -- Page Config --
st.set_page_config(page_title="Assessment Blueprint Generator - MERIT India", layout="wide")

# -- Logo and Title --
col1, col2 = st.columns([1, 10])
with col1:
    st.image("logo.jpg", width=80)
with col2:
    st.markdown("""
        # 🎯 Blueprint Generator – MERIT India
        _A tool to systematically design assessments in alignment with medical education objectives._
    """)

# -- Step 1: Total Marks --
st.markdown("## 🧮 Step 1: Total Marks for Theory Paper")
total_marks = st.number_input("Enter Total Marks", value=100)

# -- Step 2: Section-wise Distribution Input (via text) --
st.markdown("## 🧩 Step 2: Section-wise Distribution (%)")
section_input = st.text_input("Enter section breakdown (e.g., MCQ,30;SAQ,40;LAQ,30)", "MCQ,30;SAQ,40;LAQ,30")

section_rows = [s.strip().split(',') for s in section_input.split(';') if s.strip() and ',' in s]
section_df = pd.DataFrame(section_rows, columns=["Section", "% Weightage"])
section_df["% Weightage"] = section_df["% Weightage"].astype(float)
section_df["Marks Allocated"] = round((section_df["% Weightage"] / 100) * total_marks)
st.dataframe(section_df, use_container_width=True)

# -- Step 3: Cognitive Domain (%) Input --
st.markdown("## 🧠 Step 3: Cognitive Domain Distribution (%) for Each Question Type")
cognitive_input = st.text_area("Paste Cognitive %s for each section like below",
"""MCQ,Recall,30;MCQ,Understand,40;MCQ,Apply,30;
SAQ,Recall,30;SAQ,Understand,30;SAQ,Apply,40;
LAQ,Recall,30;LAQ,Understand,30;LAQ,Apply,40""")

cog_rows = [row.strip().split(',') for row in cognitive_input.split(';') if row.strip() and len(row.strip().split(',')) == 3]
cog_df = pd.DataFrame(cog_rows, columns=["Section", "Domain", "%"])
cog_df["%"] = cog_df["%"].astype(float)

# Calculate marks for each domain
merged = pd.merge(cog_df, section_df, on="Section")
merged["Marks"] = round((merged["Marks Allocated"] * merged["%"]) / 100)
st.markdown("## 🧾 Step 4: Cognitive Domain Marks (Auto-calculated)")
st.dataframe(merged, use_container_width=True)

# -- Step 5: Unit Input --
st.markdown("## 📚 Step 5: Enter Units and I x F Scores")
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

# -- Step 6: Combined Manual Grid Entry --
st.markdown("## 🧾 Step 6: Enter Distribution per Unit")
grid_columns = ["MCQ-R", "MCQ-U", "MCQ-A", "SAQ-R", "SAQ-U", "SAQ-A", "LAQ-R", "LAQ-U", "LAQ-A"]
grid_template = pd.DataFrame(index=unit_df["Unit"], columns=grid_columns).fillna(0).astype(int)

combined_grid = st.data_editor(grid_template, use_container_width=True, key="final_grid")
combined_grid["Grid Total"] = combined_grid.sum(axis=1)
final_df = pd.concat([unit_df.set_index("Unit"), combined_grid], axis=1)

# -- Display Final Blueprint Table --
st.markdown("## 📊 Final Blueprint Table")
try:
    st.dataframe(final_df, use_container_width=True)
except:
    st.write("Unable to render styled dataframe, fallback to plain table.")
    st.write(final_df)

# -- PDF Export --
def export_to_pdf(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", size=8)
    col_widths = [40] + [20] * (len(df.columns) - 1)
    row_height = 8

    for i, col in enumerate(df.reset_index().columns):
        pdf.cell(col_widths[i], row_height, str(col), border=1, align='C')
    pdf.ln(row_height)

    for _, row in df.reset_index().iterrows():
        for i, val in enumerate(row):
            pdf.cell(col_widths[i], row_height, str(val), border=1, align='C')
        pdf.ln(row_height)

    output = BytesIO()
    pdf.output(output)
    b64 = base64.b64encode(output.getvalue()).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="blueprint_grid.pdf">📥 Download as PDF</a>'

st.markdown("## 📤 Export Report")
st.markdown(export_to_pdf(final_df), unsafe_allow_html=True)

# -- Footer --
st.markdown("---")
st.markdown("📬 Support: support@meritindia.org")
st.markdown("© 2025 MERIT India. All rights reserved.")
