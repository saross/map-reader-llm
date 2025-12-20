# TRAP Data Extraction Walkthrough (Updated with Phase 3)

## Overview

Successfully implemented and executed a 3-phase data extraction pipeline for TRAP (Tundzha Regional Archaeology Project) survey records from 2009-2011. The pipeline extracts team composition and role attribution data from Excel and Word sources, with intelligent name cleaning using NLP cues.

## Work Directory

All work is located in: `/media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/`

## Implementation Summary

### Scripts Created

1. **[utils.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/utils.py)** - Shared utility functions

2. **[extract_phase1.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/extract_phase1.py)** - Excel extraction

3. **[extract_phase2.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/extract_phase2.py)** - Diary extraction with context capture
   - **NEW**: Captures context text (first 200 chars) for each extraction
   - Stores context in separate columns for verification

4. **[extract_phase3.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/extract_phase3.py)** - **NEW** NLP-based name cleaning
   - Uses verb cues to assign roles (e.g., "Nadja drew" → PDA operator)
   - Deduplicates names in walkers list
   - Removes noise like "One mound was registered"
   - Verb patterns for role detection:
     - PDA: drew, operated, used, ran
     - Paper recorder: wrote, filled, recorded, kept
     - Data editor: edited, fixed, corrected, updated
     - Digitiser: digitised, entered, typed

5. **[consolidate.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/consolidate.py)** - Data merging (updated)
   - Now uses Phase 3 cleaned data
   - Includes context columns in final output

6. **[run_extraction.py](file:///media/shawn/191c3b96-5fa5-4d0d-8805-0cf05d3d8468/synology/Adela/TRAP-WD-2020-04/claude_extraction/scripts/run_extraction.py)** - Main orchestration (updated)
   - Now runs Phase 3 between Phase 2 and consolidation

## Execution Results

### Phase 1: Excel Extraction
- **Files Processed:** ELH09, Yam10, Kaz10, Kaz11 SurveySummary files
- **Total:** 192 records extracted

### Phase 2: Diary Extraction (with Context)
- **Files Processed:** 9 English diary files
- **Total:** 68 entries extracted
- **NEW**: Context captured for each extraction

### Phase 3: Name Cleaning (NEW)
- **Input:** 68 records from Phase 2
- **Output:** 68 cleaned records
- **Noise Reduction:** 6 → 2 noisy entries (67% reduction)
- **Improvements:**
  - Removed phrases like "One mound was registered"
  - Cleaned "Nadja drew huge polygons" → extracted "Nadja" as PDA operator
  - Deduplicated names in walker lists

### Consolidation
- **Final Output:** 208 records (after merging and deduplication)
- **Improvement:** Walker data increased from 17 → 29 records

## Data Quality Validation

### ✓ Noise Reduction
- **Before Phase 3:** 6 noisy entries
- **After Phase 3:** 2 noisy entries
- **Reduction:** 67%

### ✓ Improved Coverage
- **Total records:** 208
- **Records with Leader:** 191 (92%)
- **Records with Walkers:** 29 (14%, up from 8%)
- **Records with PDA operator:** 7
- **Records with Paper recorder:** 6
- **Records with Data editor:** 10
- **Records with Digitiser:** 0

### Context Columns Added
The final output now includes context columns for verification:
- `Context_Walkers`: Source text for walker extraction
- `Context_PDA`: Source text for PDA operator extraction
- `Context_Paper`: Source text for paper recorder extraction
- `Context_Editor`: Source text for data editor extraction
- `Context_Digitiser`: Source text for digitiser extraction

## Output Files

All outputs saved to `claude_extraction/outputs/`:

1. **phase1_summary.csv** - Excel extraction results (193 lines)
2. **phase2_roles.csv** - Diary extraction with context (69 lines)
3. **phase3_cleaned.csv** - **NEW** Cleaned data (69 lines)
4. **final_attribution.csv** - **MAIN OUTPUT** (209 lines)

### Final CSV Columns
```
Date, Team, Start Unit, End Unit, Leader, Walkers,
PDA operator, Paper recorder, Data editor, Digitiser,
Notes, SurveySummary_Source, Diary_Source,
Context_Walkers, Context_PDA, Context_Paper, Context_Editor, Context_Digitiser
```

## Known Issues & Remaining Work

1. **Minor Noise Remaining**: 2 entries still have some noise (e.g., "More" as a name). These can be manually reviewed using the context columns.

2. **Missing Walker Data**: 179 records (86%) still missing walker data - candidates for PDF fallback extraction.

3. **Digitiser Role**: Still no digitiser information extracted from any diary.

4. **Context Column Usage**: Users can now review the `Context_*` columns to verify name extractions and identify any remaining issues.

## Version Control

Two commits made:
1. Initial implementation (Phase 1 & 2)
2. Phase 3 improvements (name cleaning + context columns)

## Next Steps

1. **Manual Review**: Use context columns to verify extractions, especially the 2 remaining noisy entries

2. **PDF Fallback** (Optional): Implement vision-based extraction for the 179 records missing walker data

3. **Fine-tune Phase 3**: Add more noise patterns if additional issues are found during review

4. **Name Normalization**: Match extracted names/initials against participant rosters
