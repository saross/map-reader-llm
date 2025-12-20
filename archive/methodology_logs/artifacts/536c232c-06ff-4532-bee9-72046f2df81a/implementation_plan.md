# TRAP Data Extraction Implementation Plan

## Goal
Extract team composition and roles from TRAP survey data files and output as CSV, organized within a dedicated workspace.

## Refinements (Round 2)
1.  **Separate Outputs**: Produce `phase1_summary.csv` and `phase2_diaries.csv` separately.
2.  **Context Column**: Add a `Context` column to the Diaries output containing the full paragraph/sentence.
3.  **PDF Extraction**: **SKIPPED**.
    *   *Reason*: `tesseract` is not installed. `view_file` does not support PDF. `pdfminer` only works on text-based PDFs, not scans.
    *   *Action*: I will focus on the text/Excel extraction.

## Proposed Changes

### 1. `extract_data.py` Updates

#### A. Output Separation
- Remove merging logic.
- Save `df_summary` to `phase1_summary.csv`.
- Save `df_diary` to `phase2_diaries.csv`.

#### B. Context Column
- In `parse_diary_text`, capture the full line/paragraph where a match is found.
- Store it in the `Context` field.

## Verification Plan
- Run updated `extract_data.py`.
- Verify `phase1_summary.csv` and `phase2_diaries.csv` are separate.
- Verify `Context` column in `phase2_diaries.csv`.
