# ⚡ Quick Reference Guide

**Fast commands for common tasks**

---

## 🔄 Data Extraction

```bash
# Extract fresh EDGAR data for all 4 companies
/Users/joshuagao/.local/pipx/venvs/edgartools/bin/python scripts/extract_data.py
```

**Outputs:**
- `data/master_financials.json` ← **Use this!**
- `data/master_comps.csv` ← **Use this!**
- `data/processed/IB_*.csv/json` (timestamped copies)

---

## 📊 Ratio Calculation

```bash
# Calculate all financial ratios
python3 comprehensive_ratios_analysis.py
```

**Outputs:**
- `tables/csv/comprehensive_core_ratios.csv`
- `tables/csv/comprehensive_size_metrics.csv`
- `tables/csv/comprehensive_leverage_ratios.csv`
- `tables/csv/master_comprehensive_ratios.csv`

---

## 📝 Table Conversion

```bash
# Convert all CSV tables to LaTeX
python3 scripts/csv_to_latex.py --all

# Convert specific table
python3 scripts/csv_to_latex.py tables/csv/comps/revenue_profitability.csv
```

**Outputs:** LaTeX files in `tables/tex/`

---

## 📄 LaTeX Compilation

```bash
cd writeup/
pdflatex main.tex
```

**Output:** `writeup/main.pdf`

---

## 📁 Key File Locations

| What You Need | Where It Is |
|---------------|-------------|
| **Master financial data** | `data/master_financials.json` |
| **Master comps table** | `data/master_comps.csv` |
| **Edit comps tables** | `tables/csv/comps/*.csv` |
| **Edit M&A tables** | `tables/csv/ma/*.csv` |
| **Part 1 writeup** | `writeup/comps/comps_analysis.tex` |
| **Part 2 writeup** | `writeup/ma/ma_analysis.tex` |

---

## 🎯 Common Workflows

### Extract Fresh Data → Calculate Ratios → Update Tables
```bash
# 1. Extract
/Users/joshuagao/.local/pipx/venvs/edgartools/bin/python scripts/extract_data.py

# 2. Calculate ratios
python3 comprehensive_ratios_analysis.py

# 3. Edit tables in Excel/Sheets
open tables/csv/comps/revenue_profitability.csv

# 4. Convert to LaTeX
python3 scripts/csv_to_latex.py --all
```

### Update Writeup → Compile PDF
```bash
# 1. Edit LaTeX files
code writeup/ma/ma_analysis.tex

# 2. Compile
cd writeup && pdflatex main.tex
```

---

## 💡 Pro Tips

1. **Always check `data/master_financials.json`** first - it's the single source of truth
2. **Edit CSV files, not LaTeX** - LaTeX files are auto-generated
3. **Use timestamped files in `data/processed/`** for historical reference
4. **Archive folder** can be ignored - it's just old development files

---

**Need more details?** See `README.md` for comprehensive documentation.

