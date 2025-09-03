import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Blueprint Generator - MERIT India", layout="wide")

# Title and Logo
col1, col2 = st.columns([1, 8])
with col1:
    st.image("logo.jpg", width=100)
with col2:
    st.markdown("<h1 style='font-size:30px; color:#004466;'>Blueprint Generator - MERIT India</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:18px; color:#444;'>A tool to ensure balanced assessment design in medical education</p>", unsafe_allow_html=True)

# Support
st.markdown("<p style='font-size:14px; color:#666;'>For queries, contact: <a href='mailto:support@meritindia.org'>support@meritindia.org</a></p>", unsafe_allow_html=True)
st.markdown("---")

# ---------- Step 1: Total Marks ----------
st.markdown("<h2 style='font-size:26px;'>Step 1: Total Marks for Theory Paper</h2>", unsafe_allow_html=True)
total_marks = st.number_input("Enter Total Marks", min_value=1, value=100)

# ---------- Step 2: Question Type Distribution ----------
st.markdown("<h2 style='font-size:26px;'>Step 2: Question Type Distribution (%)</h2>", unsafe_allow_html=True)
section_input = st.text_area("Paste section data (e.g., MCQ, 30)", value="MCQ, 30\nSAQ, 30\nLAQ, 40")

try:
    section_lines = [line for line in section_input.splitlines() if line.strip()]
    section_data = [line.split(',') for line in section_lines]
    section_df = pd.DataFrame(section_data, columns=["Section", "% Weightage"])
    section_df["% Weightage"] = pd.to_numeric(section_df["% Weightage"], errors='coerce')
    section_df["Marks Allocated"] = (section_df["% Weightage"] * total_marks / 100).round(0).astype(int)
    st.dataframe(section_df, use_container_width=True)
except:
    st.warning("Please enter valid section-wise distribution data.")

# ---------- Step 3: Cognitive Domain Distribution ----------
st.markdown("<h2 style='font-size:26px;'>Step 3: Cognitive Domain Distribution (%) for Each Question Type</h2>", unsafe_allow_html=True)
cognitive_input = st.text_area("Paste cognitive distribution data (e.g., Recall in MCQ, 30)", 
    value="""Recall in MCQ, 30\nUnderstand in MCQ, 30\nApply in MCQ, 40\nRecall in SAQ, 30\nUnderstand in SAQ, 30\nApply in SAQ, 40\nRecall in LAQ, 30\nUnderstand in LAQ, 30\nApply in LAQ, 40""")

try:
    cog_lines = [line for line in cognitive_input.splitlines() if line.strip()]
    cog_data = [line.split(',') for line in cog_lines]
    cog_df = pd.DataFrame(cog_data, columns=["Domain", "% Weight"])
    cog_df["% Weight"] = pd.to_numeric(cog_df["% Weight"], errors='coerce')
    st.dataframe(cog_df, use_container_width=True)
except:
    st.warning("Please enter valid cognitive domain distribution data.")

# ---------- Step 4: Marks Distribution: Domain and Question Type Wise ----------
st.markdown("<h2 style='font-size:26px;'>Step 4: Marks Distribution: Domain and Question Type Wise</h2>", unsafe_allow_html=True)
try:
    cog_matrix = pd.DataFrame(index=['Recall', 'Understand', 'Apply'], columns=['MCQ', 'SAQ', 'LAQ'])
    section_marks_dict = dict(zip(section_df["Section"], section_df["Marks Allocated"]))
    for _, row in cog_df.iterrows():
        domain_entry = row["Domain"]
        percent = row["% Weight"]
        for level in cog_matrix.index:
            if level in domain_entry:
                for sec in cog_matrix.columns:
                    if sec in domain_entry:
                        cog_matrix.loc[level, sec] = round((percent / 100) * section_marks_dict.get(sec, 0))
    cog_matrix = cog_matrix.fillna(0).astype(int)
    st.dataframe(cog_matrix, use_container_width=True)
except:
    st.warning("Cognitive Matrix generation failed.")

# ---------- Step 5: Enter Units and IxF ----------
st.markdown("<h2 style='font-size:26px;'>Step 5: Enter Units and IxF Scores</h2>", unsafe_allow_html=True)
unit_input = st.text_area("Paste Units (e.g., Unit Name, I x F Score)", 
    value="""Gastrointestinal and Hepatobiliary, 143\nRenal and Genitourinary, 101\nEndocrine Disorders, 83\nRheumatology and Connective Tissue, 34""")

unit_lines = [line for line in unit_input.splitlines() if line.strip()]
unit_data = [line.split(',') for line in unit_lines if ',' in line]
unit_df = pd.DataFrame(unit_data, columns=["Unit", "IxF"])
unit_df["IxF"] = pd.to_numeric(unit_df["IxF"], errors='coerce')
unit_df = unit_df.dropna()
unit_df["IxF"] = unit_df["IxF"].astype(int)
total_ixf = unit_df["IxF"].sum()
unit_df["Weightage %"] = ((unit_df["IxF"] / total_ixf) * 100).round(0)
unit_df["Marks"] = ((unit_df["Weightage %"] * total_marks) / 100).round(0).astype(int)

# ---------- Step 6: Manual Grid Entry ----------
st.markdown("<h2 style='font-size:26px;'>Step 6: Manual Grid Entry</h2>", unsafe_allow_html=True)
grid_columns = ["MCQ-R", "MCQ-U", "MCQ-A", "SAQ-R", "SAQ-U", "SAQ-A", "LAQ-R", "LAQ-U", "LAQ-A"]
grid_template = pd.DataFrame(0, index=unit_df["Unit"], columns=grid_columns)
edited_grid = st.data_editor(grid_template.copy(), use_container_width=True, num_rows="dynamic")

# ---------- Step 7: Final Blueprint Generation ----------
st.markdown("## Generated Blueprint Table")
unit_totals = edited_grid.sum(axis=1)
final_df = pd.concat([unit_df.set_index("Unit"), edited_grid], axis=1)
final_df["Grid Total"] = unit_totals
st.dataframe(final_df.reset_index(), use_container_width=True)

# ---------- Step 8: CSV Export ----------
st.download_button(
    label="\U0001F4BE Download as CSV",
    data=final_df.reset_index().to_csv(index=False).encode('utf-8'),
    file_name="blueprint_grid.csv",
    mime='text/csv'
)

# ---------- Styling ----------
st.markdown("<style>div[data-testid=stDataFrame] td { font-size: 16px; }</style>", unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("---")
st.markdown(
    "<p style='font-size:16px; color:gray;'>© 2025 MERIT India. All rights reserved. | Reference: Kumar, P., Chaudhary, N., Kokane, A.M. et al. Designing a summative assessment blueprint in community medicine: an expert consensus approach at All India Institute of Medical Sciences. <i>BMC Med Educ</i> 24, 1539 (2024). <a href='https://doi.org/10.1186/s12909-024-06365-3' target='_blank'>https://doi.org/10.1186/s12909-024-06365-3</a></p>",
    unsafe_allow_html=True
)
