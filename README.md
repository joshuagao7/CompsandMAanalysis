# 🏦 Investment Banking Financial Analysis

**Semiconductor Sector: Comps & M&A Analysis**

Comprehensive financial analysis project comparing NVIDIA, AMD, Microchip Technology, and Lattice Semiconductor, with detailed M&A transaction analysis.

---

## 📋 Project Overview

**Assignment**: 2-part financial analysis
- **Part 1**: Comparable Companies Analysis (~1000 words) ✅ **COMPLETE**
- **Part 2**: M&A Analysis (~1250 words) 🚧 **IN PROGRESS**

**Companies Analyzed**: NVIDIA (NVDA), AMD, Microchip Technology (MCHP), Lattice Semiconductor (LSCC)

---

## 🚀 Quick Start

### 1. Extract Financial Data
```bash
# Run EDGAR data extraction (uses pipx edgartools)
/Users/joshuagao/.local/pipx/venvs/edgartools/bin/python scripts/extract_data.py
```

This will:
- Extract financial data from SEC EDGAR for all 4 companies
- Save to `data/master_financials.json` (master data)
- Generate `data/master_comps.csv` (summary table)
- Create timestamped files in `data/processed/`

### 2. Calculate Financial Ratios
```bash
python3 comprehensive_ratios_analysis.py
```

Generates comprehensive ratio tables in `tables/csv/`:
- `comprehensive_core_ratios.csv` - Core investment banking ratios
- `comprehensive_size_metrics.csv` - Scale comparison
- `comprehensive_leverage_ratios.csv` - Capital structure
- `master_comprehensive_ratios.csv` - All ratios combined

### 3. Convert Tables to LaTeX
```bash
python3 scripts/csv_to_latex.py --all
```

Converts CSV tables to LaTeX format in `tables/tex/`

### 4. Compile LaTeX Document
```bash
cd writeup/
pdflatex main.tex
```

---

## 📁 Repository Structure

```
CompsandMAanalysis/
├── README.md                          # This file
├── Prompt.txt                         # Assignment requirements
├── CURSOR_HANDOFF.md                  # Project handoff documentation
├── requirements.txt                   # Python dependencies
│
├── data/                              # All financial data
│   ├── master_financials.json        # ⭐ MASTER DATA - Single source of truth
│   ├── master_comps.csv              # ⭐ MASTER TABLE - Summary comps
│   ├── processed/                    # Timestamped extraction outputs
│   ├── raw/                          # Raw EDGAR extractions
│   └── [nvda|amd|mchp|lattice]/     # Company-specific HTML files
│
├── scripts/                           # Essential scripts only
│   ├── extract_data.py               # ⭐ EDGAR data extractor (WORKING)
│   ├── csv_to_latex.py               # CSV → LaTeX converter
│   └── populate_comparison_tables.py # Table generator
│
├── tables/                           # Assignment deliverables
│   ├── csv/                          # Source CSV files (edit here!)
│   │   ├── comps/                    # Comparable companies tables
│   │   ├── ma/                       # M&A analysis tables
│   │   └── comprehensive_*.csv      # Ratio analysis tables
│   └── tex/                          # LaTeX formatted tables (auto-generated)
│
├── writeup/                          # LaTeX report
│   ├── main.tex                      # Main document
│   ├── comps/
│   │   └── comps_analysis.tex        # ✅ Part 1: Comps Analysis (COMPLETE)
│   └── ma/
│       └── ma_analysis.tex           # 🚧 Part 2: M&A Analysis (TODO)
│
├── comprehensive_ratios_analysis.py  # Ratio calculator script
│
└── archive/                          # Development history (ignore)
```

---

## 📊 Current Financial Data Summary

| Company | Revenue ($M) | Net Margin | ROE | ROA | Current Ratio |
|---------|-------------|------------|-----|-----|---------------|
| **NVIDIA** | 130,497 | 55.8% | 91.9% | 65.3% | 4.44x |
| **AMD** | 25,785 | 6.4% | 2.9% | 2.4% | 2.62x |
| **MCHP** | 4,402 | -0.0% | -0.0% | -0.0% | 2.59x |
| **LSCC** | 509 | 12.0% | 8.6% | 7.2% | 3.66x |

**Key Insight**: Perfect setup for **NVIDIA acquiring Lattice Semiconductor** M&A analysis

---

## 🛠️ Technical Setup

### Dependencies
- `pandas` - Data manipulation
- `edgartools` - SEC EDGAR API access (installed via pipx)

### EDGAR API Configuration
```python
from edgar import Company, set_identity
set_identity("Investment Banking Analysis joshua.gao@yale.edu")
company = Company("NVDA")  # Works for all 4 companies
```

### Key Commands Reference
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

## 📈 Workflow

1. **Data Extraction** → `scripts/extract_data.py` → `data/master_financials.json`
2. **Ratio Calculation** → `comprehensive_ratios_analysis.py` → `tables/csv/comprehensive_*.csv`
3. **Table Editing** → Edit CSV files in `tables/csv/` (use Excel/Sheets)
4. **LaTeX Conversion** → `scripts/csv_to_latex.py` → `tables/tex/*.tex`
5. **Writeup** → Edit LaTeX files in `writeup/`
6. **Compilation** → `pdflatex main.tex` → Final PDF

---

## 🎯 Assignment Status

- [x] Part 1: Comps Analysis (~1000 words) ✅ **COMPLETE**
- [ ] Part 2: M&A Analysis (~1250 words) 🚧 **IN PROGRESS**
- [ ] Final LaTeX compilation ⏳ **PENDING**
- [ ] Wednesday submission ⏰ **DEADLINE**

**Current Progress**: ~60% complete

---

## 📝 Notes

- **Master Data**: Always use `data/master_financials.json` as single source of truth
- **Table Editing**: Edit CSV files in `tables/csv/`, not LaTeX files in `tables/tex/`
- **Script Outputs**: Latest extractions saved to `data/processed/` with timestamps
- **Archive**: Old development files stored in `archive/` (can be ignored)

---

## 🔗 Key Files

- `data/master_financials.json` - **Master financial data** (use this!)
- `writeup/comps/comps_analysis.tex` - Part 1 writeup (complete)
- `writeup/ma/ma_analysis.tex` - Part 2 writeup (to be written)
- `scripts/extract_data.py` - Working EDGAR extractor
- `comprehensive_ratios_analysis.py` - Ratio calculator

---

**Last Updated**: December 1, 2025  
**Status**: Repository cleaned and organized ✅
