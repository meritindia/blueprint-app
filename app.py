# Updated version for environments without Streamlit
import pandas as pd
from io import BytesIO
from fpdf import FPDF

# Simulated Data
unit_data = """Gastrointestinal and Hepatobiliary, 143
Renal and Genitourinary, 101
Endocrine Disorders, 83
Rheumatology and Connective Tissue, 34"""

total_marks = 100
mcq_pct, saq_pct, laq_pct = 30, 30, 40
mcq_marks = round(mcq_pct * total_marks / 100)
saq_marks = round(saq_pct * total_marks / 100)
laq_marks = round(laq_pct * total_marks / 100)

cd_perc = {
    "MCQ": [30, 30, 40],
    "SAQ": [30, 30, 40],
    "LAQ": [30, 30, 40],
}
cd_marks = {
    sec: [round(p * marks / 100) for p in perc]
    for sec, perc, marks in zip(cd_perc.keys(), cd_perc.values(), [mcq_marks, saq_marks, laq_marks])
}
cdm_df = pd.DataFrame(cd_marks, index=["Recall", "Understand", "Apply"])

unit_rows = [row.strip().split(',') for row in unit_data.strip().split('\n') if row.strip()]
unit_df = pd.DataFrame(unit_rows, columns=["Unit", "IxF"])
unit_df["IxF"] = unit_df["IxF"].astype(float)
unit_df["Weightage %"] = round((unit_df["IxF"] / unit_df["IxF"].sum()) * 100)
unit_df["Marks"] = round((unit_df["Weightage %"] / 100) * total_marks)

# Dummy blueprint grid for local demonstration
grid_template = pd.DataFrame(index=unit_df["Unit"], columns=[
    "MCQ-R", "MCQ-U", "MCQ-A",
    "SAQ-R", "SAQ-U", "SAQ-A",
    "LAQ-R", "LAQ-U", "LAQ-A"])
grid_template = grid_template.fillna(0).astype(int)
grid_template.loc["Gastrointestinal and Hepatobiliary"] = [2, 3, 4, 1, 2, 2, 2, 1, 1]
grid_template.loc["Renal and Genitourinary"] = [1, 1, 1, 1, 1, 1, 1, 1, 1]
unit_totals = grid_template.sum(axis=1)
blueprint_df = pd.concat([unit_df, grid_template], axis=1)
blueprint_df["Grid Total"] = unit_totals.values

# PDF Export Function
def export_to_pdf(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", size=8)
    cell_widths = [40] + [18] * (len(df.columns) - 1)
    row_height = 8

    for i, col in enumerate(df.columns):
        pdf.cell(cell_widths[i], row_height, str(col)[:15], border=1, align='C')
    pdf.ln(row_height)

    for _, row in df.iterrows():
        for i, val in enumerate(row):
            pdf.cell(cell_widths[i], row_height, str(val), border=1, align='C')
        pdf.ln(row_height)

    output_path = "blueprint_grid.pdf"
    pdf.output(output_path)
    print(f"PDF exported to: {output_path}")

# Save CSV and PDF
blueprint_df.to_csv("blueprint_grid.csv", index=False)
export_to_pdf(blueprint_df)
print("CSV and PDF exported successfully.")
