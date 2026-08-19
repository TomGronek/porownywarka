import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
os.makedirs('output_visualizations', exist_ok=True)

# Load dataset
df_fb = pd.read_excel('data/1 liga - skrajny.xlsx')

players_meta = [
    {'name': 'Szymon Karasiński', 'pattern': 'Karasinski', 'team': 'Ruch Chorzów'},
    {'name': 'Oleksandr Azatsky', 'pattern': 'Azatsky', 'team': 'Polonia Bytom'},
    {'name': 'Paweł Tupaj', 'pattern': 'Tupaj', 'team': 'Chrobry Głogów'},
    {'name': 'Daniel Mikołajewski', 'pattern': 'Miko', 'team': 'Wieczysta Kraków'}
]

# Exactly 9 requested metrics
metrics_meta = [
    # (raw_col, display_name, category, unit)
    ('Defensive duels per 90', 'Pojedynki w defensywie / 90', 'Gra w Defensywie', 'per90'),
    ('Defensive duels won, %', 'Wygrane pojedynki w defensywie', 'Gra w Defensywie', '%'),
    ('Shots blocked per 90', 'Zablokowane strzały / 90', 'Gra w Defensywie', 'per90'),
    
    ('Aerial duels per 90', 'Pojedynki w powietrzu / 90', 'Gra w Powietrzu', 'per90'),
    ('Aerial duels won, %', 'Wygrane pojedynki w powietrzu', 'Gra w Powietrzu', '%'),
    
    ('Forward passes per 90', 'Podania do przodu / 90', 'Dystrybucja i Dośrodkowania', 'per90'),
    ('Accurate forward passes, %', 'Dokładność podań do przodu', 'Dystrybucja i Dośrodkowania', '%'),
    ('Crosses per 90', 'Dośrodkowania / 90', 'Dystrybucja i Dośrodkowania', 'per90'),
    ('Accurate crosses, %', 'Dokładność dośrodkowań', 'Dystrybucja i Dośrodkowania', '%')
]

player_data = {}
for p in players_meta:
    match = df_fb[df_fb['Player'].astype(str).str.contains(p['pattern'], case=False, na=False)]
    if len(match) > 0:
        player_data[p['name']] = match.iloc[0]

avg_1l = df_fb.mean(numeric_only=True)

def fmt_val(val, unit):
    if pd.isna(val):
        return "-"
    if unit == '%':
        return f"{val:.1f}%"
    else:
        return f"{val:.2f}"

def render_table_png(title, subtitle, columns, col_widths, rows_data, filename):
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['axes.edgecolor'] = 'none'

    fig_height = 8.5
    fig_width = 17.5
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Title & Subtitle
    fig.text(0.035, 0.945, title, fontsize=15, fontweight='bold', color='#111827', va='top')
    fig.text(0.035, 0.905, subtitle, fontsize=9.5, color='#64748B', va='top')

    left, top = 0.035, 0.850
    avg_col_idx = len(columns) - 1

    col_x_starts = []
    curr = left
    for w in col_widths:
        col_x_starts.append(curr)
        curr += w

    header_height = 0.052
    row_h = 0.046
    
    # Calculate total height of table to draw solid background column for yellow benchmark
    # Count total rows including categories
    categories_seen = set()
    total_y_height = header_height
    for row in rows_data:
        cat = row.get('category', '')
        if cat and cat not in categories_seen:
            categories_seen.add(cat)
            total_y_height += 0.032 # category height
        total_y_height += row_h

    # 1. DRAW SOLID YELLOW BACKGROUND FOR THE ENTIRE 1 LIGA COLUMN
    yellow_col_x = col_x_starts[avg_col_idx]
    yellow_col_w = col_widths[avg_col_idx]
    yellow_solid_box = patches.FancyBboxPatch(
        (yellow_col_x, top - total_y_height), yellow_col_w, total_y_height,
        boxstyle="square,pad=0",
        facecolor="#FDE047", # Solid vibrant yellow
        edgecolor="none",
        transform=fig.transFigure,
        zorder=1
    )
    fig.patches.append(yellow_solid_box)

    # 2. DRAW HEADER BAR FOR PLAYER COLUMNS (0..N-2)
    main_header_width = sum(col_widths[:avg_col_idx])
    th_box = patches.FancyBboxPatch((left, top - header_height), main_header_width, header_height,
                                     boxstyle="square,pad=0",
                                     facecolor="#1E293B", edgecolor="none",
                                     transform=fig.transFigure,
                                     zorder=2)
    fig.patches.append(th_box)

    # Render Header Texts
    for idx, col_name in enumerate(columns):
        cx = col_x_starts[idx]
        cw = col_widths[idx]
        if idx == 0:
            tx = cx + 0.015
            ha = 'left'
            txt_color = '#FFFFFF'
        elif idx == avg_col_idx:
            tx = cx + cw / 2.0
            ha = 'center'
            txt_color = '#1E293B' # Dark slate text on solid yellow header
        else:
            tx = cx + cw / 2.0
            ha = 'center'
            txt_color = '#FFFFFF'
        
        fig.text(tx, top - header_height / 2.0, col_name.replace('<br>', '\n'), 
                 fontsize=9.2, fontweight='bold', color=txt_color, ha=ha, va='center', zorder=5)

    curr_y = top - header_height
    current_category = ""

    for row_idx, row in enumerate(rows_data):
        category = row.get('category', '')

        # Category section header (player columns only, yellow column remains solid yellow)
        if category and category != current_category:
            current_category = category
            curr_y -= 0.032
            
            cat_box = patches.FancyBboxPatch((left, curr_y), main_header_width, 0.030,
                                             boxstyle="square,pad=0",
                                             facecolor="#F1F5F9", edgecolor="none",
                                             transform=fig.transFigure,
                                             zorder=2)
            fig.patches.append(cat_box)
            fig.text(left + 0.015, curr_y + 0.015, category.upper(), fontsize=9.0, fontweight='bold', color='#334155', va='center', zorder=5)

        curr_y -= row_h

        # Alternating row background for player columns ONLY (NO BORDERS)
        bg_color = "#F8FAFC" if row_idx % 2 == 1 else "#FFFFFF"
        r_box = patches.FancyBboxPatch((left, curr_y), main_header_width, row_h,
                                        boxstyle="square,pad=0",
                                        facecolor=bg_color, edgecolor="none",
                                        transform=fig.transFigure,
                                        zorder=2)
        fig.patches.append(r_box)

        # Render cell values
        vals = row['values']
        highlights = row.get('highlights', [None] * len(vals))

        for c_idx, val_str in enumerate(vals):
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            ha = 'left' if c_idx == 0 else 'center'
            tx = cx + 0.015 if c_idx == 0 else cx + cw / 2.0

            color = '#111827'
            fontweight = 'normal'

            if c_idx == avg_col_idx:
                color = '#1E293B' # Solid dark slate text for yellow column
                fontweight = 'bold'

            cell_hl = highlights[c_idx] if c_idx < len(highlights) else None
            if cell_hl and c_idx != avg_col_idx:
                c_box = patches.FancyBboxPatch((cx, curr_y), cw, row_h, 
                                                boxstyle="square,pad=0", 
                                                facecolor=cell_hl, 
                                                edgecolor="none", # NO BORDERS
                                                transform=fig.transFigure,
                                                zorder=3)
                fig.patches.append(c_box)
                color = '#15803D'
                fontweight = 'bold'

            fig.text(tx, curr_y + row_h / 2.0, val_str, fontsize=9.2, fontweight=fontweight, color=color, ha=ha, va='center', zorder=5)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.15)
    plt.close()
    print(f"Wygenerowano grafikę PNG (bez czarnych ramek, stały żółty pasek): {filename}")

def render_html_dashboard(title, subtitle, columns, rows_data, filename):
    avg_col_idx = len(columns) - 1
    html_content = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
            max-width: 1280px;
            margin: 0 auto;
        }}
        .card {{
            background: #FFFFFF;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: none;
            overflow: hidden;
        }}
        .card-header {{
            background-color: #1E293B;
            color: #FFFFFF;
            padding: 24px;
        }}
        .card-title {{
            font-size: 20px;
            font-weight: 700;
        }}
        .card-subtitle {{
            font-size: 13.5px;
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
            padding: 14px 16px;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.5px;
            line-height: 1.4;
            border: none;
        }}
        .data-table th.solid-yellow-col {{
            background-color: #FDE047;
            color: #1E293B;
            font-weight: 700;
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
            padding: 10px 16px;
            border: none;
        }}
        .category-row td.solid-yellow-col {{
            background-color: #FDE047;
        }}
        .data-table tbody tr:nth-child(even) {{
            background-color: #F8FAFC;
        }}
        .data-table td {{
            padding: 12px 16px;
            border: none;
        }}
        .top1-cell {{
            background-color: #BBF7D0 !important;
            color: #15803D !important;
            font-weight: 700 !important;
        }}
        .solid-yellow-col {{
            background-color: #FDE047 !important;
            font-weight: 700 !important;
            color: #1E293B !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h1 class="card-title">{title}</h1>
                <p class="card-subtitle">{subtitle}</p>
            </div>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
"""
    for idx, col in enumerate(columns):
        cls = ' class="solid-yellow-col"' if idx == avg_col_idx else ''
        html_content += f"                            <th{cls}>{col}</th>\n"

    html_content += """                        </tr>
                    </thead>
                    <tbody>
"""
    current_cat = ""
    for row in rows_data:
        cat = row.get('category', '')
        if cat and cat != current_cat:
            current_cat = cat
            html_content += f"""
                        <tr class="category-row">
                            <td colspan="{avg_col_idx}">{cat.upper()}</td>
                            <td class="solid-yellow-col"></td>
                        </tr>
"""
        html_content += "                        <tr>\n"
        vals = row['values']
        hls = row.get('highlights', [None] * len(vals))
        for idx, val in enumerate(vals):
            td_cls = ""
            if idx == avg_col_idx:
                td_cls = ' class="solid-yellow-col"'
            elif hls[idx]:
                td_cls = ' class="top1-cell"'
            
            html_content += f"                            <td{td_cls}>{val}</td>\n"
        html_content += "                        </tr>\n"

    html_content += """                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Wygenerowano dashboard HTML: {filename}")

# Prepare data for rows
rows_data = []
for raw_col, disp_name, cat, unit in metrics_meta:
    vals_num = [player_data[p['name']][raw_col] for p in players_meta]
    avg_num = avg_1l[raw_col]

    vals_formatted = [fmt_val(v, unit) for v in vals_num]
    avg_formatted = fmt_val(avg_num, unit)

    # Find top 1 among the 4 players
    top1_idx = int(np.argmax(vals_num))
    
    highlights = [None] * (len(players_meta) + 2) # [Metric, P1, P2, P3, P4, Avg]
    highlights[top1_idx + 1] = "#BBF7D0"

    rows_data.append({
        'category': cat,
        'values': [disp_name] + vals_formatted + [avg_formatted],
        'highlights': highlights
    })

columns = [
    "Metryka Statystyczna",
    "Szymon Karasiński<br>(Ruch Chorzów)",
    "Oleksandr Azatsky<br>(Polonia Bytom)",
    "Paweł Tupaj<br>(Chrobry Głogów)",
    "Daniel Mikołajewski<br>(Wieczysta Kraków)",
    "Średnia 1 Ligi<br>(Skrajny obrońca)"
]

col_widths = [0.26, 0.13, 0.13, 0.13, 0.14, 0.14]

png_file = "output_visualizations/tabela_skrajni_obroncy_porownanie.png"
html_file = "output_visualizations/tabela_skrajni_obroncy_porownanie.html"

render_table_png(
    title="ZESTAWIENIE PORÓWNAWCZE SKRAJNYCH OBROŃCÓW — 9 METRYK (1. LIGA)",
    subtitle="Surowe dane statystyczne zawodników vs wyróżniony benchmark Średnia 1. Ligi dla skrajnego obrońcy",
    columns=columns,
    col_widths=col_widths,
    rows_data=rows_data,
    filename=png_file
)

render_html_dashboard(
    title="Zestawienie Porównawcze Skrajnych Obrońców — 9 Metryk",
    subtitle="Surowe dane statystyczne zawodników na pozycji skrajnego obrońcy / wahadłowego vs Średnia 1. Ligi",
    columns=columns,
    rows_data=rows_data,
    filename=html_file
)
