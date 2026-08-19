import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directories exist
os.makedirs('output_visualizations/zagranica', exist_ok=True)

# 9 metrics (xA per 90 removed as in previous project scripts)
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

# Load Warta FB benchmark players
lep = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Lepczy')][req_metrics].iloc[0]
kwiat = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Kwiatkowski')][req_metrics].iloc[0]
zal = df_zal[df_zal['Player'].astype(str).str.contains('Zalewski')][req_metrics].iloc[0]

# Calculate averages
avg_zag = df_zag[req_metrics].mean()
avg_1l_fb = df_1l_fb[req_metrics].mean()
avg_warta_fb = pd.DataFrame([lep, kwiat, zal]).mean()

def fmt_val(m, val):
    if '%' in m:
        return f"{val:.1f}%"
    else:
        return f"{val:.2f}"

def calc_delta(val, ref, is_pct):
    diff = val - ref
    if is_pct:
        return f"{diff:+.1f} p.p."
    else:
        pct_diff = (diff / ref * 100) if ref != 0 else 0
        return f"{diff:+.2f} ({pct_diff:+.1f}%)"

def render_table_image_white(title, subtitle, columns, col_widths, rows_data, filename, target_col_idx=1):
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['axes.edgecolor'] = 'none'

    fig_height = 9.0
    fig, ax = plt.subplots(figsize=(16.5, fig_height), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Title & Subtitle block
    fig.text(0.035, 0.94, title, fontsize=14, fontweight='bold', color='#111827', va='top')
    fig.text(0.035, 0.90, subtitle, fontsize=9.0, color='#64748B', va='top')

    left, top = 0.035, 0.84
    total_width = sum(col_widths)
    
    col_x_starts = []
    curr = left
    for w in col_widths:
        col_x_starts.append(curr)
        curr += w

    # Top Header Bar (Dark Slate)
    header_height = 0.050
    th_box = patches.FancyBboxPatch((left, top - header_height), total_width, header_height,
                                     boxstyle="square,pad=0",
                                     facecolor="#1E293B", edgecolor="none",
                                     transform=fig.transFigure)
    fig.patches.append(th_box)

    for idx, col_name in enumerate(columns):
        cx = col_x_starts[idx]
        cw = col_widths[idx]
        if idx == 0:
            tx = cx + 0.012
            ha = 'left'
        else:
            tx = cx + cw / 2.0
            ha = 'center'
        fig.text(tx, top - header_height / 2.0, col_name, fontsize=8.8, fontweight='bold', color='#FFFFFF', ha=ha, va='center')

    curr_y = top - header_height
    row_h = 0.044
    current_category = ""

    for row_idx, row in enumerate(rows_data):
        category = row.get('category', '')
        
        # Category Section Header Row
        if category and category != current_category:
            current_category = category
            curr_y -= 0.032
            cat_box = patches.FancyBboxPatch((left, curr_y), total_width, 0.030,
                                             boxstyle="square,pad=0",
                                             facecolor="#F1F5F9", edgecolor="none",
                                             transform=fig.transFigure)
            fig.patches.append(cat_box)
            fig.text(left + 0.012, curr_y + 0.015, category.upper(), fontsize=8.5, fontweight='bold', color='#334155', va='center')
            
            line = patches.Rectangle((left, curr_y), total_width, 0.001, facecolor="#CBD5E1", transform=fig.transFigure)
            fig.patches.append(line)

        curr_y -= row_h

        # Alternating row background color
        bg_color = "#F8FAFC" if row_idx % 2 == 1 else "#FFFFFF"
        r_box = patches.FancyBboxPatch((left, curr_y), total_width, row_h,
                                        boxstyle="square,pad=0",
                                        facecolor=bg_color, edgecolor="none",
                                        transform=fig.transFigure)
        fig.patches.append(r_box)

        # Bottom row border line
        border_line = patches.Rectangle((left, curr_y), total_width, 0.0008, facecolor="#E2E8F0", transform=fig.transFigure)
        fig.patches.append(border_line)

        # Render Cell Values
        vals = row['values']
        for c_idx, val_str in enumerate(vals):
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            if c_idx == 0:
                tx = cx + 0.012
                ha = 'left'
            else:
                tx = cx + cw / 2.0
                ha = 'center'
            
            color = '#111827'
            fontweight = 'normal'

            if target_col_idx is not None and c_idx == target_col_idx:
                fontweight = 'bold'
            
            if val_str.startswith('+'):
                color = '#15803D' # Green delta
                fontweight = 'bold'
            elif val_str.startswith('-'):
                color = '#B91C1C' # Red delta
                fontweight = 'bold'

            fig.text(tx, curr_y + row_h / 2.0, val_str, fontsize=8.8, fontweight=fontweight, color=color, ha=ha, va='center')

    plt.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.15)
    plt.close()

# Width configuration for 8-column player tables (sum = 0.93)
widths_8col = [0.24, 0.10, 0.10, 0.11, 0.10, 0.09, 0.09, 0.10]

# Render individual PNG table for each of the 19 players
print("Generowanie grafik PNG dla 19 zawodników...")
for idx, clean_name in enumerate(clean_names):
    p_row = df_zag.iloc[idx]
    team = str(p_row['Team']) if pd.notna(p_row['Team']) else 'Wolny zawodnik / Inny klub'
    mins = p_row['Minutes played']
    
    rows_data = []
    for m in req_metrics:
        disp_name, cat, unit = metric_meta[m]
        v_p = p_row[m]
        v_g = avg_zag[m]
        v_l = avg_1l_fb[m]
        v_w = avg_warta_fb[m]
        is_pct = (unit == '%')
        
        rows_data.append({
            'category': cat,
            'values': [
                disp_name,
                fmt_val(m, v_p),
                fmt_val(m, v_g),
                fmt_val(m, v_l),
                fmt_val(m, v_w),
                calc_delta(v_p, v_g, is_pct),
                calc_delta(v_p, v_l, is_pct),
                calc_delta(v_p, v_w, is_pct)
            ]
        })

    fname = f"output_visualizations/zagranica/tabela_{idx+1:02d}_{clean_name.lower().replace(' ', '_').replace('.', '').replace('š', 's').replace('ć', 'c').replace('č', 'c').replace('ă', 'a')}.png"
    
    render_table_image_white(
        title=f"{clean_name.upper()} — PORÓWNANIE POZYCYJNE (SKRAJNY STOPER)",
        subtitle=f"Klub: {team} | Minuty: {mins} | Analiza surowych danych statystycznych vs Grupa Zagranica, 1. Liga (Skrajny stoper) i Warta Poznań",
        columns=["Metryka Statystyczna", clean_name, "Średnia Grupa", "Średnia 1 Liga", "Średnia Warta", "vs Grupa", "vs 1 Liga", "vs Warta Poznań"],
        col_widths=widths_8col,
        rows_data=rows_data,
        filename=fname,
        target_col_idx=1
    )

print("Wygenerowano wszystkie 19 grafik indywidualnych PNG w folderze output_visualizations/zagranica/")
