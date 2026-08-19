import os
import pandas as pd
import numpy as np

# 1. Load Datasets
df_1liga_pos10 = pd.read_excel('data/1 liga/pozycja 10.xlsx')
df_2liga_pos10 = pd.read_excel('data/2 liga/pozycja 10.xlsx')
df_combined = pd.concat([df_1liga_pos10, df_2liga_pos10], ignore_index=True)

# 2. Extract Players & Compute Averages
kucharski_row = df_1liga_pos10[df_1liga_pos10['Player'].str.contains('Kucharski', na=False)].iloc[0]
wolczek_row = df_2liga_pos10[df_2liga_pos10['Player'].str.contains('Wołczek|Wolczek', na=False)].iloc[0]
kusztal_row = df_2liga_pos10[df_2liga_pos10['Player'].str.contains('Kusztal', na=False)].iloc[0]

mean_1liga_pos10 = df_1liga_pos10.mean(numeric_only=True)
u17_df = df_combined[df_combined['Age'] <= 17]
mean_12liga_u17 = u17_df.mean(numeric_only=True)

metrics_spec = [
    ('Successful attacking actions per 90', 'Udane akcje ofensywne / 90', False, 'GRA W OFENSYWIE I DRYBLING'),
    ('Progressive runs per 90', 'Progresywne rajdy / 90', False, 'GRA W OFENSYWIE I DRYBLING'),
    ('Dribbles per 90', 'Dryblingi / 90', False, 'GRA W OFENSYWIE I DRYBLING'),
    ('Successful dribbles, %', 'Udane dryblingi, %', True, 'GRA W OFENSYWIE I DRYBLING'),
    
    ('Forward passes per 90', 'Podania do przodu / 90', False, 'KREACJA I DYSTRYBUCJA'),
    ('Accurate forward passes, %', 'Dokładność podań do przodu, %', True, 'KREACJA I DYSTRYBUCJA'),
    ('xA per 90', 'xA / 90', False, 'KREACJA I DYSTRYBUCJA'),
    ('Through passes per 90', 'Podania prostopadłe / 90', False, 'KREACJA I DYSTRYBUCJA'),
    
    ('Defensive duels per 90', 'Pojedynki w defensywie / 90', False, 'GRA W DEFENSYWIE'),
    ('Defensive duels won, %', 'Wygrane pojedynki w defensywie, %', True, 'GRA W DEFENSYWIE'),
    ('PAdj Interceptions', 'Przejęcia (PAdj) / 90', False, 'GRA W DEFENSYWIE')
]

def fmt_val(val, is_pct):
    if pd.isna(val):
        return "-"
    if is_pct:
        return f"{val:.1f}%"
    else:
        return f"{val:.2f}"

# Generate Table HTML Rows
table_rows_html = ""
curr_category = ""

for raw_col, display_label, is_pct, category in metrics_spec:
    if category != curr_category:
        curr_category = category
        table_rows_html += f'''
        <tr class="category-row">
            <td colspan="6">{category.upper()}</td>
        </tr>
        '''
    
    val_k = kucharski_row[raw_col]
    val_w = wolczek_row[raw_col]
    val_ku = kusztal_row[raw_col]
    val_l1 = mean_1liga_pos10[raw_col]
    val_u17 = mean_12liga_u17[raw_col]
    
    pvals = [val_k, val_w, val_ku]
    best_pval = max([v for v in pvals if not pd.isna(v)]) if any(not pd.isna(v) for v in pvals) else None
    
    def get_badge(v):
        if best_pval is not None and v == best_pval:
            return 'class="badge-top1"'
        return ''

    table_rows_html += f'''
    <tr>
        <td class="metric-name">{display_label}</td>
        <td><span {get_badge(val_k)}>{fmt_val(val_k, is_pct)}</span></td>
        <td><span {get_badge(val_w)}>{fmt_val(val_w, is_pct)}</span></td>
        <td><span {get_badge(val_ku)}>{fmt_val(val_ku, is_pct)}</span></td>
        <td class="benchmark-col">{fmt_val(val_l1, is_pct)}</td>
        <td class="benchmark-col">{fmt_val(val_u17, is_pct)}</td>
    </tr>
    '''

html_content = f'''<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analiza Porównawcza Statystyk — Pozycja 10</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #F8FAFC;
            color: #111827;
            padding: 32px;
            margin: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .card {{
            background: #FFFFFF;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid #E2E8F0;
            overflow: hidden;
            margin-bottom: 32px;
        }}
        .card-header {{
            background-color: #1E293B;
            color: #FFFFFF;
            padding: 24px 28px;
        }}
        .card-title {{
            font-size: 20px;
            font-weight: 700;
            margin: 0;
        }}
        .card-subtitle {{
            font-size: 13px;
            color: #94A3B8;
            margin-top: 6px;
        }}
        .table-container {{
            overflow-x: auto;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13.5px;
        }}
        .data-table th {{
            background-color: #0F172A;
            color: #FFFFFF;
            padding: 14px 18px;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            border: none;
        }}
        .data-table th:not(:first-child), .data-table td:not(:first-child) {{
            text-align: center;
        }}
        .category-row td {{
            background-color: #F1F5F9;
            color: #334155;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
            padding: 10px 18px;
            border-top: 1px solid #CBD5E1;
            border-bottom: 1px solid #CBD5E1;
            text-align: left !important;
        }}
        .data-table tbody tr:nth-child(even) {{
            background-color: #F8FAFC;
        }}
        .data-table td {{
            padding: 12px 18px;
            border-bottom: 1px solid #E2E8F0;
            border-left: none;
            border-right: none;
        }}
        .metric-name {{
            font-weight: 600;
            color: #1E293B;
        }}
        .benchmark-col {{
            background-color: #FEF08A !important;
            color: #713F12;
            font-weight: 700;
        }}
        .badge-top1 {{
            background-color: #BBF7D0;
            color: #15803D;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
            border: none;
        }}
        .preview-section {{
            margin-top: 24px;
            text-align: center;
        }}
        .preview-image {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid #CBD5E1;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .meta-info {{
            display: flex;
            gap: 16px;
            margin-bottom: 20px;
            font-size: 13px;
        }}
        .meta-card {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 12px 16px;
            flex: 1;
        }}
        .meta-card strong {{
            display: block;
            color: #1E293B;
            margin-bottom: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h1 class="card-title">ANALIZA PORÓWNAWCZA STATYSTYK — POZYCJA 10</h1>
                <div class="card-subtitle">Jakub Kucharski vs Aleksander Wołczek vs Patryk Kusztal na tle średnich 1. i 2. ligi</div>
            </div>
            
            <div style="padding: 24px;">
                <div class="meta-info">
                    <div class="meta-card">
                        <strong>J. Kucharski (Stal Rzeszów)</strong>
                        1 Liga | Wiek: 17 (ur. 2008) | 689 min
                    </div>
                    <div class="meta-card">
                        <strong>A. Wołczek (Sandecja Nowy Sącz)</strong>
                        2 Liga | Wiek: 21 | 2671 min
                    </div>
                    <div class="meta-card">
                        <strong>P. Kusztal (Warta Poznań)</strong>
                        2 Liga | Wiek: 23 | 952 min
                    </div>
                    <div class="meta-card">
                        <strong>Średnie Odniesienia (Żółte Kolumny)</strong>
                        1 Liga Poz. 10 (210 piłk.) | 1+2 Liga ur. 2008+ (15 piłk.)
                    </div>
                </div>

                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Metryka Statystyczna</th>
                                <th>Jakub Kucharski</th>
                                <th>Aleksander Wołczek</th>
                                <th>Patryk Kusztal</th>
                                <th style="background-color: #EAB308; color: #FFFFFF;">Średnia 1 Liga</th>
                                <th style="background-color: #CA8A04; color: #FFFFFF;">Średnia 1+2L (ur. 2008+)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="card" style="padding: 24px;">
            <h2 style="font-size: 16px; font-weight: 700; margin-top: 0; color: #1E293B;">Podgląd Wygenerowanej Grafiki PNG (300 DPI)</h2>
            <div class="preview-section">
                <img src="output_visualizations/tabela_porownawcza_pozycja10.png" alt="Tabela Porównawcza Pozycja 10" class="preview-image">
            </div>
        </div>
    </div>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Pomyślnie wygenerowano plik HTML: index.html")
