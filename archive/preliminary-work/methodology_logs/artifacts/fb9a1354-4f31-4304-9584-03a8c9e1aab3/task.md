# TRAP Data Extraction Task

## Setup
- [x] Initialize git repository
- [x] Create new work directory (`claude_extraction/`)
- [x] Set up Python virtual environment
- [x] Install dependencies (pandas, openpyxl, xlrd, python-docx, pdf2image, pytesseract, Pillow)

## Phase 1: Extract Team Leader & Composition
- [x] Examine KAZ09_SurveySummary.xls structure
- [x] Extract from SurveySummary Excel files (ELH09, Yam10, Kaz10, Kaz11)
- [ ] Extract team composition from PDF Daily Progress Forms (vision-based, fallback only)
- [x] Output Phase 1 CSV: Date, Team, Start Unit, End Unit, Leader, Walkers

## Phase 2: Extract Specific Roles
- [x] Extract from English diary Word documents (.doc, .docx)
- [x] Parse for: PDA operator, Paper recorder, Geospatial data editor, Digitiser
- [x] Merge with Phase 1 data
- [x] Output final CSV with all columns

## Verification
- [x] Validate date formats (ISO YYYY-MM-DD)
- [x] Validate unit numbers (5-digit format)
- [x] Check for duplicate entries
- [x] Review sample extractions

## Phase 3: Improvements (Name Cleaning & Context)
- [x] Update Phase 2 to capture context text for each extraction
- [x] Create Phase 3 script to clean noisy extractions using NLP cues
- [x] Use verb cues to assign roles (e.g., 'drew' → PDA operator)
- [x] Deduplicate names in walkers list
- [x] Add context columns to final output
- [x] Re-run extraction pipeline
- [x] Validate improved output

## Phase 2b: PDF Walker Extraction
- [x] Create test script for vision-based PDF extraction
- [x] Test Daily Progress Form extraction (B_2010Summary.pdf)
- [x] Test Survey Unit Form extraction (B_20100317.pdf)
- [x] Implement full Phase 2b script with recursive PDF search
- [ ] Extract walkers from Daily Progress Forms (3/page) - READY FOR CLAUDE CODE
- [ ] Extract walkers from Survey Unit Forms (bottom grid) - READY FOR CLAUDE CODE
- [ ] Handle rotation and multiple pages - READY FOR CLAUDE CODE
- [ ] Integrate Phase 2b into pipeline
- [ ] Re-run and validate
