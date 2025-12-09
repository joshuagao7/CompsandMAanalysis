# 📁 Current File Structure (CLEAN)

**Last Updated**: December 1, 2025  
**Status**: ✅ Cleaned and Organized

---

## 🎯 **ESSENTIAL FILES (WORK WITH THESE)**

```
CompsandMAanalysis/
├── README.md                          # ⭐ Project overview & quick start
├── Prompt.txt                         # Assignment requirements
├── CURSOR_HANDOFF.md                  # Project handoff documentation
├── requirements.txt                   # Python dependencies
│
├── data/                              # ⭐ ALL FINANCIAL DATA
│   ├── master_financials.json        # ⭐ MASTER DATA - Single source of truth
│   ├── master_comps.csv              # ⭐ MASTER TABLE - Summary comps
│   ├── processed/                    # Timestamped extraction outputs
│   ├── raw/                          # Raw EDGAR extractions (historical)
│   └── [nvda|amd|mchp|lattice]/      # Company HTML files (10-K filings)
│
├── scripts/                           # ⭐ ESSENTIAL SCRIPTS ONLY
│   ├── extract_data.py               # ⭐ EDGAR data extractor (WORKING)
│   ├── csv_to_latex.py               # CSV → LaTeX converter
│   └── populate_comparison_tables.py # Table generator
│
├── tables/                           # ⭐ ASSIGNMENT DELIVERABLES
│   ├── csv/                          # Source CSV files (EDIT HERE!)
│   │   ├── comps/                    # Comparable companies tables
│   │   │   ├── revenue_profitability.csv
│   │   │   ├── operating_metrics.csv
│   │   │   ├── growth_metrics.csv
│   │   │   ├── market_cap_ev.csv
│   │   │   └── valuation_multiples.csv
│   │   ├── ma/                       # M&A analysis tables
│   │   │   ├── target_valuation.csv
│   │   │   ├── consideration_structure.csv
│   │   │   └── synergy_estimates.csv
│   │   ├── comprehensive_core_ratios.csv
│   │   ├── comprehensive_size_metrics.csv
│   │   ├── comprehensive_leverage_ratios.csv
│   │   └── master_comprehensive_ratios.csv
│   └── tex/                          # LaTeX formatted tables (AUTO-GENERATED)
│       ├── comps/
│       └── ma/
│
├── writeup/                          # ⭐ ASSIGNMENT WRITEUP
│   ├── main.tex                      # Main LaTeX document
│   ├── comps/
│   │   └── comps_analysis.tex        # ✅ Part 1: Comps Analysis (COMPLETE)
│   └── ma/
│       └── ma_analysis.tex           # 🚧 Part 2: M&A Analysis (TODO)
│
├── comprehensive_ratios_analysis.py  # Ratio calculator script
│
└── archive/                          # Development history (IGNORE)
    └── [old scripts and test files]
```

---

## 📊 **DATA FLOW**

### 1. Data Extraction
```
scripts/extract_data.py
    ↓
data/master_financials.json  (MASTER DATA)
data/master_comps.csv        (MASTER TABLE)
data/processed/IB_*.csv/json  (Timestamped copies)
```

### 2. Ratio Calculation
```
comprehensive_ratios_analysis.py
    ↓
data/master_financials.json  (INPUT)
    ↓
tables/csv/comprehensive_*.csv  (OUTPUT)
```

### 3. Table Editing
```
tables/csv/*.csv  (EDIT HERE)
    ↓
scripts/csv_to_latex.py
    ↓
tables/tex/*.tex  (AUTO-GENERATED)
```

### 4. Writeup
```
writeup/comps/comps_analysis.tex  ✅ COMPLETE
writeup/ma/ma_analysis.tex        🚧 TODO
    ↓
pdflatex main.tex
    ↓
main.pdf  (FINAL DELIVERABLE)
```

---

## 🔑 **KEY FILES (SINGLE SOURCE OF TRUTH)**

| File | Purpose | Updated By |
|------|---------|------------|
| `data/master_financials.json` | **Master financial data** | `scripts/extract_data.py` |
| `data/master_comps.csv` | **Master comps table** | `scripts/extract_data.py` |
| `tables/csv/comps/*.csv` | **Comps tables** | Manual editing |
| `tables/csv/ma/*.csv` | **M&A tables** | Manual editing |
| `writeup/comps/comps_analysis.tex` | **Part 1 writeup** | Manual editing |
| `writeup/ma/ma_analysis.tex` | **Part 2 writeup** | Manual editing |

---

## 🚀 **QUICK COMMANDS**

```bash
# Extract fresh EDGAR data
/Users/joshuagao/.local/pipx/venvs/edgartools/bin/python scripts/extract_data.py

# Calculate comprehensive ratios
python3 comprehensive_ratios_analysis.py

# Convert CSV to LaTeX
python3 scripts/csv_to_latex.py --all

# Compile LaTeX document
cd writeup && pdflatex main.tex
```

---

## 📝 **WORKFLOW RULES**

1. **Always use `data/master_financials.json`** as single source of truth
2. **Edit CSV files in `tables/csv/`**, not LaTeX files in `tables/tex/`
3. **Script outputs go to `data/processed/`** with timestamps
4. **Master files updated automatically** by extraction script
5. **Archive folder** contains old files - can be ignored

---

## ✅ **CLEANUP COMPLETED**

- ✅ Removed temporary files from root directory
- ✅ Consolidated master data files
- ✅ Organized data directory structure
- ✅ Updated extraction script to output correctly
- ✅ Created comprehensive README
- ✅ Added .gitignore for clean version control
- ✅ Updated documentation

**Repository is now clean and ready for fast data processing!** 🚀
