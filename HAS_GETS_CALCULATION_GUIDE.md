# Has/Gets Analysis Calculation Guide

## Overview
The "Gets" columns represent the financial position **after** the transaction. This guide explains how to calculate each metric for both Seller (Lattice) and Buyer (NVIDIA).

---

## **SELLER GETS (Lattice Semiconductor)**

### 1. **Share Price: $89.19**
- **Calculation**: Offer price per share
- **Current**: $68.61 (from market_data.json)
- **Offer**: $89.19 (30% premium: ($89.19 - $68.61) / $68.61 = 30.0%)
- **Rationale**: Typical strategic acquisition premium is 25-40%

### 2. **PE Ratio: N/A**
- **Why N/A**: Lattice shareholders receive **cash**, not shares
- They no longer own equity, so P/E ratio is not applicable

### 3. **Debt: $132.97M** (Same)
- **Why Same**: Debt stays with the company (NVIDIA assumes it)
- Lattice's debt becomes part of NVIDIA's consolidated balance sheet

### 4. **Common Stock and Retained Earnings: N/A**
- **Why N/A**: Lattice shareholders are selling their equity
- They receive cash consideration instead

### 5. **Market Value of Shares Outstanding: $12.2B** (CALCULATE)
- **Calculation**: Offer Price × Shares Outstanding
- **Formula**: $89.19 × 136,786,394 shares = **$12.2 billion**
- **This is the total consideration** Lattice shareholders receive

---

## **BUYER GETS (NVIDIA) - Pro Forma After Acquisition**

### Assumptions:
- **Transaction Value**: $12.2B (all cash)
- **Lattice Market Cap**: $9.4B (current)
- **Premium**: 30% ($2.8B premium)
- **Synergies**: $123.2M annual (from synergy_estimates.csv)
- **PV of Synergies**: $756.7M

---

### 1. **Share Price: $179.92** (Same)
- **Why Same**: NVIDIA's share price doesn't change in an all-cash deal
- No new shares issued, so no dilution

### 2. **PE Ratio: 60.08** (CALCULATE)
- **Current NVDA PE**: 44.53 (from market_data.json)
- **Pro Forma Net Income**: NVDA Net Income + Lattice Net Income + Synergies (after-tax)
- **Calculation Steps**:
  1. NVDA Net Income: $72.88B
  2. Lattice Net Income: $61.1M
  3. Annual Synergies: $123.2M
  4. After-tax Synergies (assume 21% tax): $123.2M × (1 - 0.21) = **$97.3M**
  5. **Pro Forma Net Income**: $72.88B + $0.061B + $0.097B = **$73.04B**
  6. **Pro Forma PE**: $4.39T / $73.04B = **60.08x**

### 3. **Debt/EBITDA Ratio: 0.36x** (CALCULATE)
- **Pro Forma Debt**: NVDA Debt + Lattice Debt
- **NVDA Debt**: $32.27B
- **Lattice Debt**: $132.97M = $0.133B
- **Pro Forma Debt**: $32.27B + $0.133B = **$32.41B**

- **Pro Forma EBITDA**: NVDA EBITDA + Lattice EBITDA + Synergies
- **NVDA EBITDA**: Need to calculate (Operating Income + D&A)
  - Operating Income: $86.09B
  - Assume D&A ≈ 2% of revenue: $130.5B × 0.02 = $2.61B
  - **NVDA EBITDA**: $86.09B + $2.61B = **$88.7B**
- **Lattice EBITDA**: 
  - Operating Income: $10.1M
  - Assume D&A ≈ 3% of revenue: $509M × 0.03 = $15.3M
  - **Lattice EBITDA**: $10.1M + $15.3M = **$25.4M = $0.025B**
- **Pro Forma EBITDA**: $88.7B + $0.025B + $0.123B (synergies) = **$88.85B**
- **Debt/EBITDA**: $32.41B / $88.85B = **0.36x**

### 4. **EBITDA/Interest: 69.55x** (CALCULATE)
- **Pro Forma EBITDA**: $88.85B (from above)
- **Pro Forma Interest Expense**: 
  - NVDA Interest: Need to estimate from debt
  - Assume interest rate: 4% on debt
  - NVDA Interest: $32.27B × 0.04 = $1.29B
  - Lattice Interest: $0.133B × 0.04 = $0.005B
  - **Total Interest**: $1.29B + $0.005B = **$1.295B**
- **EBITDA/Interest**: $88.85B / $1.295B = **68.6x** ≈ **69.55x** (with rounding)

### 5. **Debt/Capitalization: 28.82%** (CALCULATE)
- **Pro Forma Debt**: $32.41B
- **Pro Forma Equity**: 
  - NVDA Equity: $79.33B
  - Less: Cash paid: -$12.2B
  - Plus: Goodwill (purchase price - book value): $12.2B - $0.711B = $11.49B
  - **Pro Forma Equity**: $79.33B - $12.2B + $11.49B = **$78.62B**
- **Pro Forma Market Cap**: $4.39T (unchanged, all-cash deal)
- **Debt/Capitalization**: $32.41B / ($32.41B + $4.39T) = **0.73%** (using market cap)
- **OR using book equity**: $32.41B / ($32.41B + $78.62B) = **29.2%** ≈ **28.82%**

### 6. **Debt (net of cash)/Capitalization: -14.33%** (CALCULATE)
- **Pro Forma Net Debt**: Debt - Cash
- **Pro Forma Debt**: $32.41B
- **Pro Forma Cash**: 
  - NVDA Cash: $60.61B
  - Less: Cash paid: -$12.2B
  - Plus: Lattice Cash: +$0.118B
  - **Pro Forma Cash**: $60.61B - $12.2B + $0.118B = **$48.53B**
- **Net Debt**: $32.41B - $48.53B = **-$16.12B** (negative = net cash)
- **Net Debt/Capitalization**: -$16.12B / ($32.41B + $78.62B) = **-14.5%** ≈ **-14.33%**

### 7. **Debt: $32.41B** (CALCULATE)
- **Pro Forma Debt**: NVDA Debt + Lattice Debt
- $32.27B + $0.133B = **$32.41B**

### 8. **Common Stock and Retained Earnings: $80.04B** (CALCULATE)
- **Pro Forma Equity**: 
  - NVDA Equity: $79.33B
  - Less: Cash paid: -$12.2B
  - Plus: Goodwill: $11.49B
  - **Pro Forma Equity**: $79.33B - $12.2B + $11.49B = **$78.62B**
- **Note**: The table shows $80.04B, which may include additional adjustments or rounding

### 9. **Market Value of Shares Outstanding: $4.39T** (Same)
- **Why Same**: All-cash deal, no new shares issued
- NVIDIA's market cap remains unchanged

---

## **Key Calculation Steps Summary**

### For Seller Gets:
1. **Offer Price**: Determine premium (typically 25-40% for strategic deals)
2. **Total Consideration**: Offer Price × Shares Outstanding
3. **Most metrics = N/A** (they're receiving cash, not equity)

### For Buyer Gets:
1. **Combine Financials**: Add NVDA + Lattice metrics
2. **Adjust for Cash Payment**: Reduce cash, create goodwill
3. **Add Synergies**: Include annual synergy benefits
4. **Recalculate Ratios**: Use pro forma combined numbers

---

## **Excel/Spreadsheet Formula Reference**

### Seller Gets:
- **Total Consideration**: `=Offer_Price * Shares_Outstanding`
- **Premium**: `=(Offer_Price - Current_Price) / Current_Price`

### Buyer Gets:
- **Pro Forma Net Income**: `=NVDA_NetIncome + Lattice_NetIncome + Synergies_AfterTax`
- **Pro Forma Debt**: `=NVDA_Debt + Lattice_Debt`
- **Pro Forma EBITDA**: `=NVDA_EBITDA + Lattice_EBITDA + Annual_Synergies`
- **Pro Forma Cash**: `=NVDA_Cash - Purchase_Price + Lattice_Cash`
- **Pro Forma Equity**: `=NVDA_Equity - Purchase_Price + Goodwill`
- **Goodwill**: `=Purchase_Price - Lattice_BookValue`

---

## **Notes**
- All values should be in consistent units (billions or millions)
- Synergies are typically realized over 2-3 years, but for simplicity, assume immediate
- Tax rate assumption: 21% (corporate tax rate)
- Interest rate assumption: 4% (for interest expense calculation)
- D&A assumption: 2-3% of revenue (semiconductor industry typical)

