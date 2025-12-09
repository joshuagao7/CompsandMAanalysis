# CSV Tables Directory

**This is the source of truth - only edit files in this directory!**

## Structure

- `comps/` - Comparable companies tables (5 tables)
- `ma/` - M&A analysis tables (3 tables)

## Workflow

1. **Edit CSV files here** - Use Excel, Google Sheets, or any text editor
2. **AI can read these directly** - Lightweight, easy to parse
3. **Convert to LaTeX at the end** - Run `python scripts/csv_to_latex.py --all` when ready for final compilation

## Files

### Comparable Companies (`comps/`)
- `market_cap_ev.csv` - Market capitalization and enterprise value
- `revenue_profitability.csv` - Revenue and profitability metrics (LTM)
- `valuation_multiples.csv` - Valuation multiples (EV/Revenue, EV/EBITDA, P/E, etc.)
- `growth_metrics.csv` - Growth analysis (CAGR, YoY growth)
- `operating_metrics.csv` - Operating metrics (R&D/Revenue, margins, ROE, ROIC)

### M&A Analysis (`ma/`)
- `target_valuation.csv` - Target valuation summary
- `consideration_structure.csv` - Consideration structure analysis
- `synergy_estimates.csv` - Synergy estimates and breakdown

## Notes

- **Do NOT edit files in `tables/tex/`** - they are auto-generated
- CSV format: First row is headers, subsequent rows are data
- Empty cells are fine - leave blank for values not yet populated
- Special characters will be automatically escaped when converting to LaTeX

