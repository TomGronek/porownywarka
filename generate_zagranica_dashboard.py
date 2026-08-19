import os
import pandas as pd
import numpy as np

req_metrics = [
    'Defensive duels per 90',
    'Defensive duels won, %',
    'Shots blocked per 90',
    'Aerial duels per 90',
    'Aerial duels won, %',
    'Forward passes per 90',
    'Accurate forward passes, %',
    'Crosses per 90',
    'Accurate crosses, %'
]

metric_meta = {
    'Defensive duels per 90': ('Pojedynki w defensywie / 90', 'Gra w Defensywie', 'per90'),
    'Defensive duels won, %': ('Wygrane pojedynki w defensywie', 'Gra w Defensywie', '%'),
    'Shots blocked per 90': ('Zablokowane strzały / 90', 'Gra w Defensywie', 'per90'),
    'Aerial duels per 90': ('Pojedynki w powietrzu / 90', 'Gra w Powietrzu', 'per90'),
    'Aerial duels won, %': ('Wygrane pojedynki w powietrzu', 'Gra w Powietrzu', '%'),
    'Forward passes per 90': ('Podania do przodu / 90', 'Dystrybucja i Rozgrywanie', 'per90'),
    'Accurate forward passes, %': ('Dokładność podań do przodu', 'Dystrybucja i Rozgrywanie', '%'),
    'Crosses per 90': ('Dośrodkowania / 90', 'Dystrybucja i Rozgrywanie', 'per90'),
    'Accurate crosses, %': ('Dokładność dośrodkowań', 'Dystrybucja i Rozgrywanie', '%')
}

clean_names = [
    'W. Kooy', 'M. Šuver', 'S. Aigner', 'M. Rodin', 'T. Kok',
    'M. Untergrabner', 'A. Bol', 'B. Cipetić', 'M. Pourzitidis', 'A. Foah-Sam',
    'D. Balodis', 'K. Nowak', 'A. Jovičić', 'B. Kopacz', 'B. Batar',
    'N. Vujčić', 'D. Fišl', 'D. Stăiculescu', 'M. Sawicki'
]

df_zag = pd.read_excel('zagranica.xlsx')
df_1l_fb = pd.read_excel('data/1 liga - skrajny.xlsx')
df_2l_cb = pd.read_excel('data/2 liga - centralny.xlsx')
df_zal = pd.read_excel('data/zalewski.xlsx')

lep = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Lepczy')][req_metrics].iloc[0]
kwiat = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Kwiatkowski')][req_metrics].iloc[0]
zal = df_zal[df_zal['Player'].astype(str).str.contains('Zalewski')][req_metrics].iloc[0]

avg_zag = df_zag[req_metrics].mean()
avg_1l_fb = df_1l_fb[req_metrics].mean()
avg_warta_fb = pd.DataFrame([lep, kwiat, zal]).mean()

# Calculate top 3 dicts per metric
top3_dict = {}
top1_dict = {}
for m in req_metrics:
    top3_indices = df_zag[m].nlargest(3).index.tolist()
    top3_dict[m] = set(top3_indices)
    top1_dict[m] = top3_indices[0]

def fmt(m, val):
    if '%' in m:
        return f"{val:.1f}%"
    return f"{val:.2f}"

def fmt_delta(val, ref, is_pct):
    diff = val - ref
    if is_pct:
        cls = "pos" if diff >= 0 else "neg"
        return f'<span class="delta {cls}">{diff:+.1f} p.p.</span>'
    else:
        pct = (diff / ref * 100) if ref != 0 else 0
        cls = "pos" if diff >= 0 else "neg"
        return f'<span class="delta {cls}">{diff:+.2f} ({pct:+.1f}%)</span>'

def get_file_name(clean_name, idx):
    clean = clean_name.lower().replace(' ', '_').replace('.', '').replace('š', 's').replace('ć', 'c').replace('č', 'c').replace('ă', 'a')
    return f"zagranica/tabela_{idx+1:02d}_{clean}.png"

# BUILD HTML DASHBOARD
html_content = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zestawienie Statystyczne Zawodników Zagranicznych — Skrajny Stoper</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #F8FAFC;
            color: #111827;
            padding: 32px;
            line-height: 1.5;
        }}

        .container {{
            max-width: 1420px;
            margin: 0 auto;
        }}

        .page-header {{
            margin-bottom: 24px;
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 16px;
        }}

        .page-header h1 {{
            font-size: 22px;
            font-weight: 700;
            color: #0F172A;
            letter-spacing: -0.3px;
        }}

        .page-header p {{
            font-size: 13px;
            color: #64748B;
            margin-top: 4px;
        }}

        .benchmark-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .bench-card {{
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        .bench-card h3 {{
            font-size: 14px;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 8px;
            border-bottom: 1px solid #F1F5F9;
            padding-bottom: 6px;
        }}

        .bench-metric {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            padding: 3px 0;
            color: #475569;
        }}

        .bench-metric strong {{
            color: #0F172A;
        }}

        .nav-tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }}

        .tab-btn {{
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            color: #475569;
            padding: 8px 14px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .tab-btn:hover {{
            background-color: #F1F5F9;
            color: #0F172A;
        }}

        .tab-btn.active {{
            background-color: #1E293B;
            color: #FFFFFF;
            border-color: #1E293B;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .table-card {{
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            margin-bottom: 24px;
        }}

        .table-title-bar {{
            padding: 16px 20px;
            background-color: #FFFFFF;
            border-bottom: 1px solid #E2E8F0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .table-title-bar h2 {{
            font-size: 16px;
            font-weight: 700;
            color: #0F172A;
        }}

        .table-title-bar p {{
            font-size: 12px;
            color: #64748B;
            margin-top: 2px;
        }}

        .data-table {{
            width: 100%;
            table-layout: fixed;
            border-collapse: collapse;
            text-align: center;
            font-size: 12.5px;
        }}

        .data-table th {{
            background-color: #1E293B;
            color: #FFFFFF;
            font-weight: 600;
            padding: 11px 12px;
            font-size: 11.5px;
            letter-spacing: 0.2px;
            white-space: nowrap;
        }}

        .data-table th:first-child {{
            text-align: left;
            padding-left: 20px;
            width: 26%;
        }}

        .data-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #E2E8F0;
            color: #111827;
            word-wrap: break-word;
        }}

        .data-table td:first-child {{
            text-align: left;
            padding-left: 20px;
            font-weight: 500;
        }}

        .data-table tr:nth-child(even) {{
            background-color: #F8FAFC;
        }}

        .category-row td {{
            background-color: #F1F5F9 !important;
            color: #334155;
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 0.5px;
            text-align: left;
            padding: 8px 20px;
            border-bottom: 1px solid #CBD5E1;
        }}

        .benchmark-row td {{
            background-color: #E2E8F0 !important;
            font-weight: 700;
            color: #0F172A;
        }}

        .top3-highlight {{
            background-color: #DCFCE7 !important;
            color: #15803D !important;
            font-weight: 700 !important;
        }}

        .top1-highlight {{
            background-color: #BBF7D0 !important;
            color: #166534 !important;
            font-weight: 700 !important;
        }}

        .delta {{
            font-weight: 600;
        }}

        .delta.pos {{
            color: #15803D;
        }}

        .delta.neg {{
            color: #B91C1C;
        }}

        .target-val {{
            font-weight: 700;
        }}

        .download-bar {{
            padding: 12px 20px;
            background-color: #F8FAFC;
            border-top: 1px solid #E2E8F0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: #64748B;
        }}

        .btn-download {{
            display: inline-block;
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            color: #1E293B;
            padding: 6px 12px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.15s ease;
        }}

        .btn-download:hover {{
            background-color: #1E293B;
            color: #FFFFFF;
        }}
    </style>
</head>
<body>

    <div class="container">
        <div class="page-header">
            <h1>ZESTAWIENIE STATYSTYCZNE ZAWODNIKÓW ZAGRANICZNYCH — SKRAJNY STOPER</h1>
            <p>Porównanie surowych danych 19 zawodników z pliku zagranica.xlsx vs Średnia Grupy, Średnia 1. Ligi (Skrajny stoper) oraz Średnia Warta Poznań</p>
        </div>

        <div class="benchmark-summary">
            <div class="bench-card">
                <h3>ŚREDNIA GRUPA ZAGRANICA (19 ZAW.)</h3>
                <div class="bench-metric"><span>Pojedynki defensywne / 90:</span> <strong>5.75 (68.6%)</strong></div>
                <div class="bench-metric"><span>Pojedynki w powietrzu / 90:</span> <strong>4.17 (54.2%)</strong></div>
                <div class="bench-metric"><span>Podania do przodu / 90:</span> <strong>16.98 (70.3%)</strong></div>
                <div class="bench-metric"><span>Dośrodkowania / 90:</span> <strong>0.46 (27.4%)</strong></div>
            </div>
            <div class="bench-card">
                <h3>ŚREDNIA 1 LIGA (SKRAJNY STOPER)</h3>
                <div class="bench-metric"><span>Pojedynki defensywne / 90:</span> <strong>5.32 (62.5%)</strong></div>
                <div class="bench-metric"><span>Pojedynki w powietrzu / 90:</span> <strong>3.61 (50.7%)</strong></div>
                <div class="bench-metric"><span>Podania do przodu / 90:</span> <strong>15.13 (70.9%)</strong></div>
                <div class="bench-metric"><span>Dośrodkowania / 90:</span> <strong>1.50 (31.6%)</strong></div>
            </div>
            <div class="bench-card">
                <h3>ŚREDNIA WARTA POZNAŃ (SKRAJNY STOPER)</h3>
                <div class="bench-metric"><span>Pojedynki defensywne / 90:</span> <strong>7.63 (63.0%)</strong></div>
                <div class="bench-metric"><span>Pojedynki w powietrzu / 90:</span> <strong>4.68 (51.0%)</strong></div>
                <div class="bench-metric"><span>Podania do przodu / 90:</span> <strong>14.86 (67.0%)</strong></div>
                <div class="bench-metric"><span>Dośrodkowania / 90:</span> <strong>1.19 (54.9%)</strong></div>
            </div>
        </div>

        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab(0)">0A. ZESTAWIENIE ZBIORCZE</button>
            <button class="tab-btn" onclick="switchTab(99)">0B. ZESTAWIENIE (TOP 3 PER STATYSTYKA)</button>
"""

for idx, clean_name in enumerate(clean_names):
    html_content += f'<button class="tab-btn" onclick="switchTab({idx+1})">{idx+1}. {clean_name}</button>\n'

html_content += """
        </div>

        <!-- TAB 0A: SUMMARY TABLE -->
        <div id="tab-0" class="tab-content active">
            <div class="table-card">
                <div class="table-title-bar">
                    <div>
                        <h2>ZESTAWIENIE ZBIORCZE ALL 19 ZAWODNIKÓW — SKRAJNY STOPER</h2>
                        <p>Zestawienie surowych parametrów statystycznych na tle benchmarków</p>
                    </div>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th style="width: 14%;">Zawodnik</th>
                            <th style="width: 12%;">Klub</th>
                            <th style="width: 6%;">Minuty</th>
                            <th>Poj. Def /90</th>
                            <th>Wygr. Def %</th>
                            <th>Poj. Pow /90</th>
                            <th>Wygr. Pow %</th>
                            <th>Pod. przód /90</th>
                            <th>Dokł. przód %</th>
                            <th>Dośrodk. /90</th>
                            <th>Dokł. dośr %</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Render rows in Summary Tab 0A
for idx, clean_name in enumerate(clean_names):
    p_row = df_zag.iloc[idx]
    team = str(p_row['Team']) if pd.notna(p_row['Team']) else '-'
    mins = p_row['Minutes played']
    
    html_content += f"""
    <tr>
        <td class="target-val">{clean_name}</td>
        <td>{team}</td>
        <td>{mins}</td>
        <td>{fmt('Defensive duels per 90', p_row['Defensive duels per 90'])}</td>
        <td>{fmt('Defensive duels won, %', p_row['Defensive duels won, %'])}</td>
        <td>{fmt('Aerial duels per 90', p_row['Aerial duels per 90'])}</td>
        <td>{fmt('Aerial duels won, %', p_row['Aerial duels won, %'])}</td>
        <td>{fmt('Forward passes per 90', p_row['Forward passes per 90'])}</td>
        <td>{fmt('Accurate forward passes, %', p_row['Accurate forward passes, %'])}</td>
        <td>{fmt('Crosses per 90', p_row['Crosses per 90'])}</td>
        <td>{fmt('Accurate crosses, %', p_row['Accurate crosses, %'])}</td>
    </tr>"""

html_content += f"""
    <tr class="benchmark-row">
        <td colspan="3">ŚREDNIA GRUPA ZAGRANICA (19 ZAW.)</td>
        <td>{fmt('Defensive duels per 90', avg_zag['Defensive duels per 90'])}</td>
        <td>{fmt('Defensive duels won, %', avg_zag['Defensive duels won, %'])}</td>
        <td>{fmt('Aerial duels per 90', avg_zag['Aerial duels per 90'])}</td>
        <td>{fmt('Aerial duels won, %', avg_zag['Aerial duels won, %'])}</td>
        <td>{fmt('Forward passes per 90', avg_zag['Forward passes per 90'])}</td>
        <td>{fmt('Accurate forward passes, %', avg_zag['Accurate forward passes, %'])}</td>
        <td>{fmt('Crosses per 90', avg_zag['Crosses per 90'])}</td>
        <td>{fmt('Accurate crosses, %', avg_zag['Accurate crosses, %'])}</td>
    </tr>
    <tr class="benchmark-row">
        <td colspan="3">ŚREDNIA 1 LIGA (SKRAJNY STOPER)</td>
        <td>{fmt('Defensive duels per 90', avg_1l_fb['Defensive duels per 90'])}</td>
        <td>{fmt('Defensive duels won, %', avg_1l_fb['Defensive duels won, %'])}</td>
        <td>{fmt('Aerial duels per 90', avg_1l_fb['Aerial duels per 90'])}</td>
        <td>{fmt('Aerial duels won, %', avg_1l_fb['Aerial duels won, %'])}</td>
        <td>{fmt('Forward passes per 90', avg_1l_fb['Forward passes per 90'])}</td>
        <td>{fmt('Accurate forward passes, %', avg_1l_fb['Accurate forward passes, %'])}</td>
        <td>{fmt('Crosses per 90', avg_1l_fb['Crosses per 90'])}</td>
        <td>{fmt('Accurate crosses, %', avg_1l_fb['Accurate crosses, %'])}</td>
    </tr>
    <tr class="benchmark-row">
        <td colspan="3">ŚREDNIA WARTA POZNAŃ (SKRAJNY STOPER)</td>
        <td>{fmt('Defensive duels per 90', avg_warta_fb['Defensive duels per 90'])}</td>
        <td>{fmt('Defensive duels won, %', avg_warta_fb['Defensive duels won, %'])}</td>
        <td>{fmt('Aerial duels per 90', avg_warta_fb['Aerial duels per 90'])}</td>
        <td>{fmt('Aerial duels won, %', avg_warta_fb['Aerial duels won, %'])}</td>
        <td>{fmt('Forward passes per 90', avg_warta_fb['Forward passes per 90'])}</td>
        <td>{fmt('Accurate forward passes, %', avg_warta_fb['Accurate forward passes, %'])}</td>
        <td>{fmt('Crosses per 90', avg_warta_fb['Crosses per 90'])}</td>
        <td>{fmt('Accurate crosses, %', avg_warta_fb['Accurate crosses, %'])}</td>
    </tr>
"""

html_content += """
                    </tbody>
                </table>
                <div class="download-bar">
                    <span>Grafika zbiorcza do prezentacji:</span>
                    <a href="zagranica/tabela_zbiorcza_skrajny_stoper.png" target="_blank" class="btn-download">Pobierz Grafika Tabela Zbiorcza (PNG)</a>
                </div>
            </div>
        </div>

        <!-- TAB 0B: TOP 3 PER METRIC HIGHLIGHTED TABLE -->
        <div id="tab-99" class="tab-content">
            <div class="table-card">
                <div class="table-title-bar">
                    <div>
                        <h2>ZESTAWIENIE ZBIORCZE — TOP 3 W KAŻDEJ POJEDYNCZEJ STATYSTYCE</h2>
                        <p>Wyróżnienie na zielono 3 zawodników z najwyższym odchyleniem in plus od średniej w kontekście każdej poszczególnej metryki</p>
                    </div>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th style="width: 14%;">Zawodnik</th>
                            <th style="width: 12%;">Klub</th>
                            <th style="width: 6%;">Minuty</th>
                            <th>Poj. Def /90</th>
                            <th>Wygr. Def %</th>
                            <th>Poj. Pow /90</th>
                            <th>Wygr. Pow %</th>
                            <th>Pod. przód /90</th>
                            <th>Dokł. przód %</th>
                            <th>Dośrodk. /90</th>
                            <th>Dokł. dośr %</th>
                        </tr>
                    </thead>
                    <tbody>
"""

# Render Tab 0B rows with Top 3 Highlights
for idx, clean_name in enumerate(clean_names):
    p_row = df_zag.iloc[idx]
    team = str(p_row['Team']) if pd.notna(p_row['Team']) else '-'
    mins = p_row['Minutes played']
    
    html_content += f"""
    <tr>
        <td class="target-val">{clean_name}</td>
        <td>{team}</td>
        <td>{mins}</td>"""
        
    for m in req_metrics:
        val = p_row[m]
        v_str = fmt(m, val)
        cls = ""
        if idx == top1_dict[m]:
            cls = 'class="top1-highlight"'
        elif idx in top3_dict[m]:
            cls = 'class="top3-highlight"'
        html_content += f'<td {cls}>{v_str}</td>'

    html_content += "</tr>"

html_content += f"""
    <tr class="benchmark-row">
        <td colspan="3">ŚREDNIA GRUPA ZAGRANICA (19 ZAW.)</td>
        <td>{fmt('Defensive duels per 90', avg_zag['Defensive duels per 90'])}</td>
        <td>{fmt('Defensive duels won, %', avg_zag['Defensive duels won, %'])}</td>
        <td>{fmt('Aerial duels per 90', avg_zag['Aerial duels per 90'])}</td>
        <td>{fmt('Aerial duels won, %', avg_zag['Aerial duels won, %'])}</td>
        <td>{fmt('Forward passes per 90', avg_zag['Forward passes per 90'])}</td>
        <td>{fmt('Accurate forward passes, %', avg_zag['Accurate forward passes, %'])}</td>
        <td>{fmt('Crosses per 90', avg_zag['Crosses per 90'])}</td>
        <td>{fmt('Accurate crosses, %', avg_zag['Accurate crosses, %'])}</td>
    </tr>
    <tr class="benchmark-row">
        <td colspan="3">ŚREDNIA 1 LIGA (SKRAJNY STOPER)</td>
        <td>{fmt('Defensive duels per 90', avg_1l_fb['Defensive duels per 90'])}</td>
        <td>{fmt('Defensive duels won, %', avg_1l_fb['Defensive duels won, %'])}</td>
        <td>{fmt('Aerial duels per 90', avg_1l_fb['Aerial duels per 90'])}</td>
        <td>{fmt('Aerial duels won, %', avg_1l_fb['Aerial duels won, %'])}</td>
        <td>{fmt('Forward passes per 90', avg_1l_fb['Forward passes per 90'])}</td>
        <td>{fmt('Accurate forward passes, %', avg_1l_fb['Accurate forward passes, %'])}</td>
        <td>{fmt('Crosses per 90', avg_1l_fb['Crosses per 90'])}</td>
        <td>{fmt('Accurate crosses, %', avg_1l_fb['Accurate crosses, %'])}</td>
    </tr>
    <tr class="benchmark-row">
        <td colspan="3">ŚREDNIA WARTA POZNAŃ (SKRAJNY STOPER)</td>
        <td>{fmt('Defensive duels per 90', avg_warta_fb['Defensive duels per 90'])}</td>
        <td>{fmt('Defensive duels won, %', avg_warta_fb['Defensive duels won, %'])}</td>
        <td>{fmt('Aerial duels per 90', avg_warta_fb['Aerial duels per 90'])}</td>
        <td>{fmt('Aerial duels won, %', avg_warta_fb['Aerial duels won, %'])}</td>
        <td>{fmt('Forward passes per 90', avg_warta_fb['Forward passes per 90'])}</td>
        <td>{fmt('Accurate forward passes, %', avg_warta_fb['Accurate forward passes, %'])}</td>
        <td>{fmt('Crosses per 90', avg_warta_fb['Crosses per 90'])}</td>
        <td>{fmt('Accurate crosses, %', avg_warta_fb['Accurate crosses, %'])}</td>
    </tr>
"""

html_content += """
                    </tbody>
                </table>
                <div class="download-bar">
                    <span>Grafika do prezentacji (Wyróżnienie Top 3 per Statystyka):</span>
                    <a href="zagranica/tabela_zbiorcza_top3_odchylenie.png" target="_blank" class="btn-download">Pobierz Grafika Tabela Top 3 (PNG)</a>
                </div>
            </div>
        </div>
"""

# Render individual player tabs (1-19)
for idx, clean_name in enumerate(clean_names):
    p_row = df_zag.iloc[idx]
    team = str(p_row['Team']) if pd.notna(p_row['Team']) else 'Wolny zawodnik / Inny klub'
    mins = p_row['Minutes played']
    img_file = get_file_name(clean_name, idx)
    
    html_content += f"""
        <!-- TAB {idx+1} -->
        <div id="tab-{idx+1}" class="tab-content">
            <div class="table-card">
                <div class="table-title-bar">
                    <div>
                        <h2>{clean_name.upper()} — PORÓWNANIE POZYCYJNE (SKRAJNY STOPER)</h2>
                        <p>Klub: {team} | Minuty na boisku: {mins} | Raw Data vs Benchmarki</p>
                    </div>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Metryka Statystyczna</th>
                            <th>{clean_name}</th>
                            <th>Średnia Grupa</th>
                            <th>Średnia 1 Liga</th>
                            <th>Średnia Warta</th>
                            <th>vs Grupa</th>
                            <th>vs 1 Liga</th>
                            <th>vs Warta Poznań</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    curr_cat = ""
    for m in req_metrics:
        disp, cat, unit = metric_meta[m]
        if cat != curr_cat:
            curr_cat = cat
            html_content += f'<tr class="category-row"><td colspan="8">{curr_cat.upper()}</td></tr>'
        
        v_p = p_row[m]
        v_g = avg_zag[m]
        v_l = avg_1l_fb[m]
        v_w = avg_warta_fb[m]
        is_pct = (unit == '%')
        
        html_content += f"""
        <tr>
            <td>{disp}</td>
            <td class="target-val">{fmt(m, v_p)}</td>
            <td>{fmt(m, v_g)}</td>
            <td>{fmt(m, v_l)}</td>
            <td>{fmt(m, v_w)}</td>
            <td>{fmt_delta(v_p, v_g, is_pct)}</td>
            <td>{fmt_delta(v_p, v_l, is_pct)}</td>
            <td>{fmt_delta(v_p, v_w, is_pct)}</td>
        </tr>"""

    html_content += f"""
                    </tbody>
                </table>
                <div class="download-bar">
                    <span>Grafika indywidualna do prezentacji:</span>
                    <a href="{img_file}" target="_blank" class="btn-download">Pobierz Grafika {clean_name} (PNG)</a>
                </div>
            </div>
        </div>
"""

html_content += """
    </div>

    <script>
        function switchTab(tabNum) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            if (tabNum === 0) {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('tab-0').classList.add('active');
            } else if (tabNum === 99) {
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('tab-99').classList.add('active');
            } else {
                document.querySelectorAll('.tab-btn')[tabNum + 1].classList.add('active');
                document.getElementById('tab-' + tabNum).classList.add('active');
            }
        }
    </script>
</body>
</html>
"""

with open('output_visualizations/zagranica_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

with open('output_visualizations/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Pomyślnie zaktualizowano zagranica_dashboard.html oraz index.html z dodatkową zakładką Top 3 per Statystyka!")
