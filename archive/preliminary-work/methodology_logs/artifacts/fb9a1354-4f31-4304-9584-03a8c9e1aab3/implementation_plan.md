# TRAP Data Extraction Implementation Plan

## Goal

Extract team composition and role attribution data from TRAP survey records (2009-2011) to support data creation attribution for the AKB (Bulgarian national archaeological database). The extraction will process Excel SurveySummary files, Word diary documents, and PDF scanned forms (as fallback) to produce a consolidated CSV with team leaders, members, and specific roles.

## User Review Required

> [!IMPORTANT]
> **KAZ09_SurveySummary.xls Status**: Initial examination shows this file contains data but is poorly structured. The script will attempt to extract from it, but we should verify the results carefully.

> [!NOTE]
> **PDF Extraction**: Vision-based PDF extraction will only be used as a fallback when information is missing from Excel/Word sources. This is slower and may require manual review.

## Proposed Changes

### Component 1: Core Extraction Infrastructure

#### [NEW] [extract_phase1.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/extract_phase1.py)

Phase 1 extraction script that processes SurveySummary Excel files to extract:
- Date (normalized to ISO YYYY-MM-DD format)
- Team (letter designation: A, B, C, D, E)
- Start Unit (5-digit survey unit number)
- End Unit (5-digit survey unit number)
- Leader (name/initials as recorded)
- Source file reference

**Key features:**
- Flexible column matching to handle variations in Excel headers
- Date normalization from various formats (datetime objects, strings)
- Robust error handling with detailed logging
- Processes files: ELH09 SurveySummary.xls, Yam10_SurveySummary.xls, Kaz10_SurveySummary.xls, Kaz11_SurveySummary.xlsx, KAZ09_SurveySummary.xls (if usable)

---

#### [NEW] [extract_phase2.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/extract_phase2.py)

Phase 2 extraction script that processes diary Word documents (.doc, .docx) to extract:
- Team composition (Walkers)
- PDA operator
- Paper recorder
- Geospatial data editor
- Digitiser

**Key features:**
- NLP/regex-based name extraction to filter out descriptive text
- Handles both .doc (using `strings` command) and .docx (using python-docx) formats
- Prioritizes English diaries (files ending with `_En.doc` or `_En.docx`)
- Date and team matching for merging with Phase 1 data
- Extracts role information from context clues (e.g., "PDA", "forms", "GIS", "digitizing")

---

#### [NEW] [extract_pdf_fallback.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/extract_pdf_fallback.py)

PDF fallback extraction script using vision capabilities (pdf2image + pytesseract) to extract team composition from scanned Daily Progress Forms when data is missing from other sources.

**Key features:**
- Converts PDF pages to images
- OCR text extraction
- Pattern matching for walker initials (typically at bottom of forms)
- Only runs for date/team combinations missing walker data after Phase 1 & 2

---

#### [NEW] [consolidate.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/consolidate.py)

Consolidation script that merges Phase 1 and Phase 2 data, applies PDF fallback where needed, and produces final CSV output.

**Key features:**
- Merges on Date + Team combination
- Handles duplicate entries intelligently (prefers most complete records)
- Validates data quality (date formats, unit numbers, name extraction)
- Outputs final CSV with columns: `Date, Team, Start Unit, End Unit, Leader, Walkers, PDA operator, Paper recorder, Data editor, Digitiser, Notes`
- Adds notes for interpolation suggestions and data quality concerns

---

#### [NEW] [utils.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/utils.py)

Shared utility functions:
- `extract_names(text)`: NLP/regex-based name extraction that filters out common words and retains only names/initials
- `normalize_date(date_str)`: Converts various date formats to ISO YYYY-MM-DD
- `normalize_team(team_str)`: Standardizes team letter designations
- `validate_unit(unit_str)`: Ensures unit numbers are 5-digit format
- `setup_logging(log_file)`: Configures logging to both file and console

---

#### [NEW] [run_extraction.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/run_extraction.py)

Main orchestration script that runs all phases in sequence:
1. Phase 1: Extract from Excel files
2. Phase 2: Extract from Word diaries
3. Identify gaps in walker data
4. Phase 3 (optional): PDF fallback for gaps
5. Consolidate and output final CSV

---

#### [NEW] [README.md](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/README.md)

Documentation covering:
- Project overview
- Installation instructions
- Usage instructions
- Output format description
- Known limitations
- Troubleshooting

## Verification Plan

### Automated Tests

1. **Unit number validation test**
   ```bash
   cd /media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction
   ./venv/bin/python3 -c "
   import pandas as pd
   df = pd.read_csv('outputs/final_attribution.csv')
   # Check all Start/End Units are 5 digits or empty
   for col in ['Start Unit', 'End Unit']:
       if col in df.columns:
           invalid = df[df[col].notna()][~df[df[col].notna()][col].astype(str).str.match(r'^\d{5}$')]
           print(f'{col} validation: {len(invalid)} invalid entries')
           if len(invalid) > 0:
               print(invalid[[col]].head())
   "
   ```

2. **Date format validation test**
   ```bash
   cd /media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction
   ./venv/bin/python3 -c "
   import pandas as pd
   df = pd.read_csv('outputs/final_attribution.csv')
   # Check all dates are YYYY-MM-DD format and in 2009-2011 range
   df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
   invalid_dates = df[df['Date'].isna()]
   print(f'Invalid dates: {len(invalid_dates)}')
   valid_years = df[df['Date'].notna()]['Date'].dt.year.isin([2009, 2010, 2011])
   print(f'Dates in 2009-2011: {valid_years.sum()} / {len(df[df[\"Date\"].notna()])}')
   "
   ```

3. **Name extraction quality test**
   ```bash
   cd /media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction
   ./venv/bin/python3 -c "
   import pandas as pd
   import re
   df = pd.read_csv('outputs/final_attribution.csv')
   # Check that name fields don't contain common noise words
   noise_words = ['team', 'date', 'unit', 'forms', 'gis', 'pda', 'the', 'and', 'with']
   for col in ['Leader', 'Walkers', 'PDA operator', 'Paper recorder', 'Data editor', 'Digitiser']:
       if col in df.columns:
           noisy = df[df[col].notna()][df[df[col].notna()][col].str.lower().str.contains('|'.join(noise_words), na=False)]
           print(f'{col} noise check: {len(noisy)} potentially noisy entries')
   "
   ```

4. **Run full extraction pipeline**
   ```bash
   cd /media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction
   ./venv/bin/python3 scripts/run_extraction.py
   ```

### Manual Verification

1. **Sample data review**: User should review a sample of 10-20 rows from the final CSV to verify:
   - Names are extracted correctly (not full sentences)
   - Dates match expected field season dates
   - Team letters are correct
   - Unit ranges are plausible

2. **Completeness check**: User should check coverage:
   - Are all expected field seasons represented? (Kazanlak 2009, 2010, 2011; Elhovo 2009; Yambol 2010)
   - Are there major gaps in the data that need PDF fallback?

3. **Cross-reference spot check**: User should manually verify 2-3 entries by checking the original source files to ensure extraction accuracy
