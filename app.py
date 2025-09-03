import streamlit as st
import pandas as pd
import base64

st.set_page_config(layout="wide")

# Logo and Title
col1, col2 = st.columns([1, 15])
with col1:
    st.image("logo.jpg", width=80)
with col2:
    st.markdown("""
        <h2 style='font-size: 30px; margin-bottom: 0;'>AI-Enabled Blueprint Generator</h2>
        <p style='margin-top: 0; font-size: 16px;'>A vital tool for systematic question paper design in medical education</p>
        <p style='font-size: 12px; color: gray;'>Support: support@meritindia.org</p>
    """, unsafe_allow_html=True)

# Step 1
st.markdown("""<h4 style='margin-top: 30px;'>Step 1: Total Marks for Theory Paper</h4>""", unsafe_allow_html=True)
total_marks = st.number_input("Enter Total Marks", min_value=1, value=100)

# Step 2
st.markdown("""<h4 style='margin-top: 30px;'>Step 2: Section-wise Distribution (%)</h4>""", unsafe_allow_html=True)
section_input = st.text_area("Paste section data (e.g., MCQ,30\nSAQ,30\nLAQ,40)", height=100)
section_data = []
if section_input:
    for line in section_input.split("\n"):
        parts = line.split(",")
        if len(parts) == 2:
            section_data.append({"Section": parts[0].strip(), "% Weightage": float(parts[1].strip())})
section_df = pd.DataFrame(section_data)
if not section_df.empty:
    section_df["Marks Allocated"] = section_df["% Weightage"] * total_marks / 100
    st.dataframe(section_df, use_container_width=True)

# Step 3
st.markdown("""<h4 style='margin-top: 30px;'>Step 3: Cognitive Domain Distribution (%)</h4>""", unsafe_allow_html=True)
cognitive_input = st.text_area("Paste cognitive distribution per section (e.g., MCQ,30,30,40\nSAQ,30,30,40\nLAQ,30,30,40)", height=100)
cognitive_data = []
if cognitive_input:
    for line in cognitive_input.split("\n"):
        parts = line.split(",")
        if len(parts) == 4:
            cognitive_data.append({"Section": parts[0].strip(), "Recall %": float(parts[1]), "Understand %": float(parts[2]), "Apply %": float(parts[3])})
cognitive_df = pd.DataFrame(cognitive_data)
if not cognitive_df.empty:
    st.dataframe(cognitive_df, use_container_width=True)

# Step 4
st.markdown("""<h4 style='margin-top: 30px;'>Step 4: Difficulty Level Distribution (%)</h4>""", unsafe_allow_html=True)
difficulty_input = st.text_area("Paste difficulty levels per section (e.g., MCQ,30,40,30\nSAQ,30,40,30\nLAQ,30,40,30)", height=100)
difficulty_data = []
if difficulty_input:
    for line in difficulty_input.split("\n"):
        parts = line.split(",")
        if len(parts) == 4:
            difficulty_data.append({"Section": parts[0].strip(), "Easy %": float(parts[1]), "Moderate %": float(parts[2]), "Difficult %": float(parts[3])})
difficulty_df = pd.DataFrame(difficulty_data)
if not difficulty_df.empty:
    st.dataframe(difficulty_df, use_container_width=True)

# Step 5
st.markdown("""<h4 style='margin-top: 30px;'>Step 5: Enter Units and I x F Scores</h4>""", unsafe_allow_html=True)
unit_input = st.text_area("Paste unit data (e.g., Unit Name, I x F Score)", height=150)
unit_data = []
if unit_input:
    for line in unit_input.split("\n"):
        parts = line.split(",")
        if len(parts) == 2:
            unit_data.append((parts[0].strip(), float(parts[1].strip())))
unit_df = pd.DataFrame(unit_data, columns=["Unit", "IxF"])

# Calculate weights
if not unit_df.empty:
    unit_df["Weightage %"] = unit_df["IxF"] / unit_df["IxF"].sum() * 100
    unit_df["Marks"] = (unit_df["Weightage %"] * total_marks / 100).round(0)

# Step 6: Combined Grid Entry
st.markdown("""<h4 style='margin-top: 30px;'>Step 6: Manual Grid Entry (Combined)</h4>""", unsafe_allow_html=True)
question_types = ["MCQ-R", "MCQ-U", "MCQ-A", "SAQ-R", "SAQ-U", "SAQ-A", "LAQ-R", "LAQ-U", "LAQ-A"]
empty_data = {"Unit": unit_df["Unit"]}
for q in question_types:
    empty_data[q] = [0] * len(unit_df)
grid_df = pd.DataFrame(empty_data)

edited_df = st.data_editor(grid_df, use_container_width=True, key="manual_grid")

# Final Blueprint Table
st.markdown("""<h4 style='margin-top: 30px;'>Generated Blueprint Table</h4>""", unsafe_allow_html=True)
blueprint_df = unit_df.merge(edited_df, on="Unit")
blueprint_df["Grid Total"] = blueprint_df[question_types].sum(axis=1)

try:
    st.dataframe(blueprint_df, use_container_width=True)

    # CSV download
    csv = blueprint_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download as CSV", csv, "blueprint_table.csv", "text/csv")
except Exception as e:
    st.error(f"Error rendering table: {e}")

# Footer
st.markdown("""
---
<p style='text-align: center; font-size: 12px;'>
    © 2025 MERIT INDIA. All rights reserved. | Support: support@meritindia.org
</p>
""", unsafe_allow_html=True)
