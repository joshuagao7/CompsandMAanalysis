# 📊 Enhanced EDGAR Data Extraction

## 🎯 Additional Metrics Now Extracted

The `scripts/extract_data.py` script has been enhanced to extract additional financial metrics needed for comprehensive investment banking comps analysis.

### ✅ **New Metrics Added:**

#### **Income Statement:**
1. **Gross Profit** - `get_gross_profit()`
   - Used for: Gross Margin calculation
   - Formula: Gross Margin = (Gross Profit / Revenue) × 100

2. **Operating Income / EBIT** - `get_operating_income()` or `get_ebit()`
   - Used for: Operating Margin, EV/EBIT multiples
   - Formula: Operating Margin = (Operating Income / Revenue) × 100

3. **EBITDA** - `get_ebitda()` or calculated
   - Used for: EV/EBITDA multiples (key valuation metric)
   - Formula: EBITDA = Operating Income + Depreciation + Amortization

4. **R&D Expenses** - `get_research_and_development()`
   - Used for: R&D as % of Revenue (important for tech companies)
   - Formula: R&D % = (R&D Expenses / Revenue) × 100

#### **Balance Sheet:**
5. **Total Debt** - `get_total_debt()` or calculated
   - Used for: Leverage ratios, Net Debt calculation
   - Fallback: Assets - Equity (approximation)

6. **Cash & Equivalents** - `get_cash()`
   - Used for: Net Debt, liquidity analysis
   - Formula: Net Debt = Total Debt - Cash

7. **Shares Outstanding** - `get_shares_outstanding()` or via facts
   - Used for: Per-share metrics (EPS, Book Value/Share)
   - Formula: EPS = Net Income / Shares Outstanding

#### **Calculated Ratios:**
8. **Gross Margin** - (Gross Profit / Revenue) × 100
9. **Operating Margin** - (Operating Income / Revenue) × 100
10. **EBITDA Margin** - (EBITDA / Revenue) × 100
11. **Debt/Equity** - (Total Debt / Equity) × 100
12. **Debt/Assets** - (Total Debt / Assets) × 100
13. **Net Debt** - Total Debt - Cash
14. **EPS** - Net Income / Shares Outstanding
15. **Book Value/Share** - Equity / Shares Outstanding

---

## 📋 **Comps Table Coverage**

### **Revenue & Profitability Table** ✅
- Revenue
- Net Income
- Net Margin
- **Gross Margin** ⭐ NEW
- **Operating Margin** ⭐ NEW
- ROE, ROA

### **Operating Metrics Table** ✅
- Total Assets, Equity
- Current Ratio
- Asset Turnover
- **R&D as % of Revenue** ⭐ NEW
- **EBITDA Margin** ⭐ NEW

### **Valuation Multiples Table** 🚧
- **EV/Revenue** (needs Market Cap)
- **EV/EBITDA** ⭐ NEW (needs Market Cap)
- **EV/EBIT** ⭐ NEW (needs Market Cap)
- P/E (needs Market Cap)
- P/B (needs Market Cap)

### **Market Cap & EV Table** 🚧
- **Market Cap** (needs stock price data)
- **Enterprise Value** (Market Cap + Debt - Cash) ⭐ NEW
- **Cash & Equivalents** ⭐ NEW
- **Net Debt** ⭐ NEW

### **Growth Metrics Table** 🚧
- Revenue CAGR (needs historical data)
- **EBITDA CAGR** ⭐ NEW (needs historical data)
- Revenue Growth YoY (needs historical data)

---

## 🚀 **Usage**

Run the enhanced extraction script:

```bash
/Users/joshuagao/.local/pipx/venvs/edgartools/bin/python scripts/extract_data.py
```

**Output:**
- `data/master_financials.json` - Updated with all new metrics
- `data/master_comps.csv` - Updated summary table
- `data/processed/IB_*.json/csv` - Timestamped copies

---

## 📊 **What's Still Missing (Requires External Data)**

1. **Market Cap** - Requires current stock price × shares outstanding
   - Can get from: Yahoo Finance API, Alpha Vantage, or manual lookup

2. **Enterprise Value** - Can calculate once we have Market Cap
   - Formula: EV = Market Cap + Total Debt - Cash

3. **Historical Data** - For growth metrics (CAGR, YoY growth)
   - Would need: Multiple periods of financial data
   - Can extract: Historical filings from EDGAR

4. **Stock Price** - For P/E, P/B, Market Cap calculations
   - External API needed: Yahoo Finance, Alpha Vantage, etc.

---

## 💡 **Next Steps**

1. ✅ **Extract enhanced metrics** - Run updated script
2. 🚧 **Add stock price data** - Integrate Yahoo Finance API for Market Cap
3. 🚧 **Extract historical data** - Build time series for growth metrics
4. ✅ **Update comps tables** - Populate with new metrics

---

**Last Updated**: December 1, 2025

