import pandas as pd
import os
import re
import sys

# --------- CONFIG ---------
INPUT_CSV = "PROTECTGestationalAgeObstetric_DataDictionary_2025-11-20.csv"          # <-- change to your file path
OUTPUT_DIR = "forms_split_ultrasound"       # folder to save per-form CSVs
# --------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

def safe_name(name: str) -> str:
    """Create a filesystem-safe filename from the form name."""
    name = str(name).strip()
    # replace slashes and dangerous chars with underscore
    name = re.sub(r'[\\/:"*?<>|]+', "_", name)
    # collapse whitespace
    name = re.sub(r"\s+", " ", name)
    return name or "unnamed_form"

# Try common UTF-8 variants first
read_encodings = ["utf-8-sig", "utf-8", "latin-1"]
last_err = None
for enc in read_encodings:
    try:
        df = pd.read_csv(INPUT_CSV, encoding=enc, dtype=str, keep_default_na=False)
        break
    except Exception as e:
        last_err = e
else:
    print(f"Could not read CSV ({INPUT_CSV}). Last error: {last_err}", file=sys.stderr)
    sys.exit(1)

# Normalize/standardize headers (trim only; keep original names)
df.columns = [c.strip() for c in df.columns]

# Column names expected from your layout (adjust if yours differ)
COL_FORM = "Form Name"
COL_VAR  = "Variable / Field Name"

if COL_FORM not in df.columns or COL_VAR not in df.columns:
    raise ValueError(
        f"CSV must contain '{COL_FORM}' and '{COL_VAR}' columns. "
        f"Found: {list(df.columns)}"
    )

# A canonical record_id row to clone if a form lacks one.
record_id_rows_all = df[df[COL_VAR].str.strip().eq("record_id")]
record_id_template = record_id_rows_all.iloc[0:1].copy() if not record_id_rows_all.empty else None

# Process each form
for form_name, form_df in df.groupby(COL_FORM, dropna=False):
    if (isinstance(form_name, float) and pd.isna(form_name)) or len(str(form_name).strip()) == 0:
        # Skip rows without a form name
        continue

    form_df = form_df.copy()

    # Ensure a record_id row exists for THIS form
    has_record_id = form_df[COL_VAR].str.strip().eq("record_id").any()

    if not has_record_id:
        if record_id_template is None:
            # If no global record_id exists, synthesize a minimal one with same columns
            new_row = {col: "" for col in form_df.columns}
            new_row[COL_VAR] = "record_id"
            new_row[COL_FORM] = form_name
            record_row_for_form = pd.DataFrame([new_row])
        else:
            # Clone template and set this form name
            record_row_for_form = record_id_template.copy()
            if COL_FORM in record_row_for_form.columns:
                record_row_for_form.loc[:, COL_FORM] = form_name
        # Prepend the record_id row
        form_df = pd.concat([record_row_for_form, form_df], ignore_index=True)

    # Save as UTF-8 CSV named after the form
    fname = safe_name(form_name) + ".csv"
    out_path = os.path.join(OUTPUT_DIR, fname)
    form_df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"Saved: {out_path}")

print("✅ Done.")
