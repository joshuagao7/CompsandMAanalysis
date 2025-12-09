#!/usr/bin/env python3
"""
CSV to LaTeX Table Converter

Converts CSV files to LaTeX table format for inclusion in the main document.
This script maintains the hybrid CSV + LaTeX workflow where CSV is the source of truth.

Usage:
    python csv_to_latex.py <csv_file> [caption]
    python csv_to_latex.py tables/csv/comps/market_cap_ev.csv "Market Capitalization and Enterprise Value"
    
    Or convert all tables (from tables/csv/ to tables/tex/):
    python csv_to_latex.py --all
"""

import csv
import sys
import os
import re
from pathlib import Path

# Caption mapping for known tables
CAPTIONS = {
    'market_cap_ev': 'Market Capitalization and Enterprise Value (as of [Date])',
    'revenue_profitability': 'Revenue and Profitability Analysis (LTM)',
    'valuation_multiples': 'Valuation Multiples',
    'growth_metrics': 'Growth Analysis',
    'operating_metrics': 'Operating Metrics',
    'target_valuation': 'Target Valuation Summary',
    'consideration_structure': 'Consideration Structure Analysis',
    'synergy_estimates': 'Synergy Estimates',
    'has_gets_analysis': 'Has Gets Analysis',
}

def escape_latex(text):
    """Escape special LaTeX characters in text."""
    if not text:
        return ''
    text = str(text)
    # Order matters: escape backslash first, then other special chars
    text = text.replace('\\', '\\textbackslash{}')
    text = text.replace('&', '\\&')
    text = text.replace('%', '\\%')
    text = text.replace('$', '\\$')
    text = text.replace('#', '\\#')
    text = text.replace('^', '\\textasciicircum{}')
    text = text.replace('_', '\\_')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    return text

def determine_column_alignment(headers):
    """Determine LaTeX column alignment based on header names."""
    alignment = ['l']  # First column is always left-aligned (usually labels)
    
    for header in headers[1:]:
        header_lower = header.lower()
        # If header suggests numeric data, use right alignment
        if any(keyword in header_lower for keyword in ['value', 'cap', 'revenue', 'ebitda', 
                                                        'income', 'margin', 'multiple', 'cagr', 
                                                        'growth', 'roe', 'roic', 'cash', 'debt',
                                                        'price', 'premium', 'synergy']):
            alignment.append('r')
        else:
            alignment.append('l')
    
    return ''.join(alignment)

def csv_to_latex(csv_path, caption=None, output_path=None, transpose=False):
    """
    Convert a CSV file to LaTeX table format.
    
    Args:
        csv_path: Path to input CSV file
        caption: Table caption (if None, will try to infer from filename)
        output_path: Path to output LaTeX file (if None, converts csv/ to tex/ automatically)
        transpose: If True, transpose the table (rows become columns, columns become rows)
    """
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}", file=sys.stderr)
        return False
    
    # Determine output path - convert csv/ to tex/ automatically
    if output_path is None:
        # If CSV is in tables/csv/, output to tables/tex/ with same structure
        csv_str = str(csv_path)
        if 'tables/csv/' in csv_str:
            output_path = Path(str(csv_path).replace('tables/csv/', 'tables/tex/')).with_suffix('.tex')
        else:
            # Fallback: same directory, different extension
            output_path = csv_path.with_suffix('.tex')
    else:
        output_path = Path(output_path)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine caption
    if caption is None:
        table_name = csv_path.stem
        caption = CAPTIONS.get(table_name, f"{table_name.replace('_', ' ').title()}")
    
    # Read CSV
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV file: {e}", file=sys.stderr)
        return False
    
    # Filter out completely empty rows
    rows = [row for row in rows if any(cell.strip() for cell in row)]
    
    # Transpose if requested
    if transpose:
        # First column is company names, rest are metrics
        # After transpose: first row is company names, rest rows are metrics
        company_col = [row[0] for row in rows]  # Extract company names
        metric_names = headers[1:]  # Metric names become row labels
        
        # Build transposed data: each metric becomes a row
        transposed_rows = []
        for i, metric_name in enumerate(metric_names):
            metric_row = [metric_name]  # First column is metric name
            for row in rows:
                # Get the value for this metric from each company
                if i + 1 < len(row):
                    metric_row.append(row[i + 1])
                else:
                    metric_row.append('')
            transposed_rows.append(metric_row)
        
        # New headers: "Metric" + company names
        headers = ['Metric'] + company_col
        rows = transposed_rows
        
        # For transposed tables: first column (Metric) is left-aligned, rest are right-aligned (numeric)
        col_align = 'l' + 'r' * (len(headers) - 1)
    else:
        # Determine column alignment for non-transposed tables
        col_align = determine_column_alignment(headers)
    
    # Write LaTeX table
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\\begin{table}[h]\n")
            f.write("\\centering\n")
            f.write(f"\\caption{{{escape_latex(caption)}}}\n")
            f.write(f"\\begin{{tabular}}{{{col_align}}}\n")
            f.write("\\toprule\n")
            
            # Write headers
            header_row = " & ".join([escape_latex(h) for h in headers]) + " \\\\\n"
            f.write(header_row)
            f.write("\\midrule\n")
            
            # Write data rows
            for i, row in enumerate(rows):
                # Skip completely empty rows
                if not any(cell.strip() for cell in row):
                    continue
                # Pad row if necessary
                while len(row) < len(headers):
                    row.append('')
                # Truncate if too long
                row = row[:len(headers)]
                
                # Check if this is a subheading row (first cell has content, rest are empty)
                first_cell = row[0].strip() if row[0] else ''
                rest_cells = [cell.strip() for cell in row[1:]]
                is_subheading = first_cell and not any(rest_cells)
                
                if is_subheading:
                    # Write subheading with midrule above
                    f.write("\\midrule\n")
                    subheading_row = "\\multicolumn{" + str(len(headers)) + "}{l}{\\textit{" + escape_latex(first_cell) + "}} \\\\\n"
                    f.write(subheading_row)
                else:
                    # Regular data row
                    data_row = " & ".join([escape_latex(cell.strip()) if cell.strip() else '' for cell in row]) + " \\\\\n"
                    f.write(data_row)
            
            f.write("\\bottomrule\n")
            f.write("\\end{tabular}\n")
            f.write("\\end{table}\n")
            f.write("\n")
        
        print(f"✓ Converted {csv_path} → {output_path}" + (" (transposed)" if transpose else ""))
        return True
        
    except Exception as e:
        print(f"Error writing LaTeX file: {e}", file=sys.stderr)
        return False

def convert_all_tables(base_dir='tables/csv', transpose_comps=False):
    """Convert all CSV files in the tables/csv directory to LaTeX in tables/tex."""
    base_path = Path(base_dir)
    
    if not base_path.exists():
        print(f"Error: CSV directory not found: {base_dir}/", file=sys.stderr)
        return
    
    csv_files = list(base_path.rglob('*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in {base_dir}/")
        return
    
    print(f"Converting {len(csv_files)} CSV files from {base_dir}/ to tables/tex/...\n")
    success_count = 0
    
    for csv_file in csv_files:
        # Transpose comps tables if requested
        should_transpose = transpose_comps and 'comps' in str(csv_file)
        if csv_to_latex(csv_file, transpose=should_transpose):
            success_count += 1
    
    print(f"\n✓ Successfully converted {success_count}/{len(csv_files)} files")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        transpose_comps = '--transpose-comps' in sys.argv
        convert_all_tables(transpose_comps=transpose_comps)
    elif sys.argv[1] == '--transpose-comps':
        # Convert all comps tables with transpose
        convert_all_tables(transpose_comps=True)
    elif len(sys.argv) == 2:
        csv_path = sys.argv[1]
        csv_to_latex(csv_path)
    elif len(sys.argv) == 3:
        csv_path = sys.argv[1]
        caption = sys.argv[2]
        csv_to_latex(csv_path, caption)
    elif len(sys.argv) == 4 and sys.argv[3] == '--transpose':
        csv_path = sys.argv[1]
        caption = sys.argv[2]
        csv_to_latex(csv_path, caption, transpose=True)
    else:
        print("Usage: python csv_to_latex.py <csv_file> [caption] [--transpose]")
        print("       python csv_to_latex.py --all [--transpose-comps]")
        print("       python csv_to_latex.py --transpose-comps")
        sys.exit(1)

if __name__ == '__main__':
    main()

