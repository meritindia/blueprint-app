import streamlit as st
import pandas as pd
import base64
from io import BytesIO

# -------------------- PAGE CONFIG -------------------- #
st.set_page_config(layout="wide", page_title="Blueprint Generator | MERIT INDIA")

# -------------------- HEADER -------------------- #
st.markdown("""
    <div style='display: flex; align-items: center;'>
        <img src='https://i.imgur.com/tzQx4nC.png' width='80'>
        <h1 style='margin-left: 20px;'>Medical Blueprint Generator</h1>
    </div>
    <h4 style='margin-top: -10px;'>A scientifically designed tool to map curriculum outcomes and assessment strategies</h4>
    <p style='color: gray; font-size: 15px;'>Blueprints help ensure fair, valid, and structured assessment in medical education.</p>
    <p style='color: gray; font-size: 13px;'>Support: support@meritindia.org</p>
""", unsafe_allow_html=True)

st.markdown("---")

# -------------------- STEP 1 -------------------- #
st.subheader("Step 1: Total Marks for Theory Paper")
total_marks = st.number_input("Enter Total Marks", min_value=1, value=100, step=1)

# -------------------- STEP 2 -------------------- #
st.subheader("Step 2: Section-wise Distribution (%)")
section_input = st.text_area("Paste section data (e.g., MCQ, 30)", "MCQ, 30\nSAQ, 30\nLAQ, 40")
section_data = []
for line in section_input.strip().split("\n"):
    try:
        sec, wt = line.split(',')
        section_data.append((sec.strip(), float(wt.strip())))
    except:
        pass

section_df = pd.DataFrame(section_data, columns=["Section", "% Weightage"])
section_df["Marks Allocated"] = (section_df["% Weightage"] / 100 * total_marks).round().astype(int)
st.dataframe(section_df, use_container_width=True)

# -------------------- STEP 3 -------------------- #
st.subheader("Step 3: Cognitive Domain Distribution (%) for Each Question Type")
cognitive_input = st.text_area("Paste cognitive distribution (e.g., Recall in MCQ, 30)",
    "Recall in MCQ, 30\nUnderstand in MCQ, 30\nApply in MCQ, 40\n"
    "Recall in SAQ, 30\nUnderstand in SAQ, 30\nApply in SAQ, 40\n"
    "Recall in LAQ, 30\nUnderstand in LAQ, 30\nApply in LAQ, 40")

cog_data = []
for line in cognitive_input.strip().split("\n"):
    try:
        cog, val = line.split(',')
        cog_data.append((cog.strip(), float(val.strip())))
    except:
        pass

cog_df = pd.DataFrame(cog_data, columns=["Distribution", "%"])
st.dataframe(cog_df, use_container_width=True)

# -------------------- STEP 4 -------------------- #
st.subheader("Step 4: Weightage Calculation Table")
st.dataframe(section_df, use_container_width=True)

# -------------------- STEP 5 -------------------- #
st.subheader("Step 5: Enter Units and I x F Scores")
unit_input = st.text_area("Paste unit data (e.g., Unit Name, I x F Score)",
    "Gastrointestinal and Hepatobiliary, 143\nRenal and Genitourinary, 101\nEndocrine Disorders, 83\nRheumatology and Connective Tissue, 34")

unit_data = []
for line in unit_input.strip().split("\n"):
    try:
        name, score = line.split(',')
        unit_data.append((name.strip(), int(score.strip())))
    except:
        pass

unit_df = pd.DataFrame(unit_data, columns=["Unit", "IxF"])
unit_df["Weightage %"] = round(unit_df["IxF"] / unit_df["IxF"].sum() * 100)
unit_df["Marks"] = round(unit_df["Weightage %"] / 100 * total_marks).astype(int)

# -------------------- STEP 6 -------------------- #
st.subheader("Step 6: Manual Grid Entry")

columns = ["MCQ-R", "MCQ-U", "MCQ-A", "SAQ-R", "SAQ-U", "SAQ-A", "LAQ-R", "LAQ-U", "LAQ-A"]
grid_template = pd.DataFrame(0, index=unit_df["Unit"], columns=columns)

edited_grid = st.data_editor(grid_template.reset_index().rename(columns={"index": "Unit"}), use_container_width=True)
edited_grid.set_index("Unit", inplace=True)
edited_grid = edited_grid[columns]  # ensure column order
edited_grid = edited_grid.fillna(0).astype(int)
unit_totals = edited_grid.sum(axis=1)
unit_df["Grid Total"] = unit_totals.values

# -------------------- FINAL BLUEPRINT -------------------- #
st.subheader("Generated Blueprint Table")
blueprint_df = pd.concat([unit_df, edited_grid], axis=1)
st.dataframe(blueprint_df.style.format("{:.0f}"), use_container_width=True)

# -------------------- DOWNLOAD -------------------- #
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(blueprint_df)
st.download_button("\U0001F4BE Download as CSV", csv, "blueprint_table.csv", "text/csv", key='download-csv')

# -------------------- FOOTER -------------------- #
st.markdown("""
---
<p style='font-size: 13px; color: gray;'>
© 2025 MERIT INDIA. All rights reserved. | Designed to support competency-based medical education.
</p>
<p style='font-size: 13px; color: gray;'>Source logic based on MCI/NMC blueprinting guidelines and curriculum planning recommendations.</p>
""", unsafe_allow_html=True)
