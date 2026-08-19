import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
os.makedirs('output_visualizations', exist_ok=True)

# 9 metrics (xA per 90 removed)
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

metric_display_names = {
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

df_1l_cb = pd.read_excel('data/1 liga - centralny.xlsx')
df_1l_fb = pd.read_excel('data/1 liga - skrajny.xlsx')
df_2l_cb = pd.read_excel('data/2 liga - centralny.xlsx')
df_zal = pd.read_excel('data/zalewski.xlsx')

kupczak = df_1l_cb[df_1l_cb['Player'].astype(str).str.contains('Kupczak')][req_metrics].iloc[0]
muszynski = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Muszy')][req_metrics].iloc[0]

wojc = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Wojcinowicz')][req_metrics].iloc[0]
azat = df_1l_cb[df_1l_cb['Player'].astype(str).str.contains('Azatsky')][req_metrics].iloc[0]
jaku = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Jakubowski')][req_metrics].iloc[0]

lep = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Lepczy')][req_metrics].iloc[0]
kwiat_2l = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Kwiatkowski')][req_metrics].iloc[0]
zal = df_zal[df_zal['Player'].astype(str).str.contains('Zalewski')][req_metrics].iloc[0]

avg_1l_cb = df_1l_cb[req_metrics].mean()
avg_1l_fb = df_1l_fb[req_metrics].mean()

avg_warta_cb = pd.DataFrame([wojc, azat, jaku]).mean()
avg_warta_fb = pd.DataFrame([lep, kwiat_2l, zal]).mean()

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

    fig_height = 8.5
    fig, ax = plt.subplots(figsize=(15.5, fig_height), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Title & Subtitle block
    fig.text(0.035, 0.94, title, fontsize=15, fontweight='bold', color='#111827', va='top')
    fig.text(0.035, 0.90, subtitle, fontsize=9.5, color='#64748B', va='top')

    left, top = 0.035, 0.84
    total_width = sum(col_widths)
    
    col_x_starts = []
    curr = left
    for w in col_widths:
        col_x_starts.append(curr)
        curr += w

    # Top Header Bar (Dark Slate)
    header_height = 0.052
    th_box = patches.FancyBboxPatch((left, top - header_height), total_width, header_height,
                                     boxstyle="square,pad=0",
                                     facecolor="#1E293B", edgecolor="none",
                                     transform=fig.transFigure)
    fig.patches.append(th_box)

    for idx, col_name in enumerate(columns):
        cx = col_x_starts[idx]
        cw = col_widths[idx]
        if idx == 0:
            tx = cx + 0.015
            ha = 'left'
        else:
            tx = cx + cw / 2.0
            ha = 'center'
        fig.text(tx, top - header_height / 2.0, col_name, fontsize=9.5, fontweight='bold', color='#FFFFFF', ha=ha, va='center')

    curr_y = top - header_height
    row_h = 0.046
    current_category = ""

    for row_idx, row in enumerate(rows_data):
        category = row.get('category', '')
        
        # Category Section Header Row
        if category and category != current_category:
            current_category = category
            curr_y -= 0.034
            cat_box = patches.FancyBboxPatch((left, curr_y), total_width, 0.032,
                                             boxstyle="square,pad=0",
                                             facecolor="#F1F5F9", edgecolor="none",
                                             transform=fig.transFigure)
            fig.patches.append(cat_box)
            fig.text(left + 0.015, curr_y + 0.016, category.upper(), fontsize=9, fontweight='bold', color='#334155', va='center')
            
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
                tx = cx + 0.015
                ha = 'left'
            else:
                tx = cx + cw / 2.0
                ha = 'center'
            
            color = '#111827'
            fontweight = 'normal'

            if c_idx == target_col_idx:
                fontweight = 'bold'
            
            if val_str.startswith('+'):
                color = '#15803D' # Green delta
                fontweight = 'bold'
            elif val_str.startswith('-'):
                color = '#B91C1C' # Red delta
                fontweight = 'bold'

            fig.text(tx, curr_y + row_h / 2.0, val_str, fontsize=9.5, fontweight=fontweight, color=color, ha=ha, va='center')

    plt.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.15)
    plt.close()
    print(f"Wygenerowano czytelną czystą grafikę: {filename}")


ordered_metrics = [
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

# Width configuration for 6-column tables (sum = 0.93)
widths_6col = [0.28, 0.13, 0.18, 0.14, 0.10, 0.10]

# Width configuration for 5-column tables (sum = 0.93)
widths_5col = [0.31, 0.14, 0.14, 0.18, 0.16]

# TABLE 1: Mateusz Kupczak vs Centralny stoper
t1_rows = []
for m in ordered_metrics:
    disp_name, cat, unit = metric_display_names[m]
    v_p = kupczak[m]
    v_l = avg_1l_cb[m]
    v_b = avg_warta_cb[m]
    is_pct = (unit == '%')
    t1_rows.append({
        'category': cat,
        'values': [
            disp_name,
            fmt_val(m, v_p),
            fmt_val(m, v_l),
            fmt_val(m, v_b),
            calc_delta(v_p, v_l, is_pct),
            calc_delta(v_p, v_b, is_pct)
        ]
    })

render_table_image_white(
    title="MATEUSZ KUPCZAK — PORÓWNANIE POZYCYJNE (CENTRALNY STOPER)",
    subtitle="Analiza porównawcza surowych danych statystycznych vs Średnia 1. Ligi (Centralny stoper) oraz Średnia Warta Poznań",
    columns=["Metryka Statystyczna", "Mateusz Kupczak", "Średnia 1 Liga (Centralny stoper)", "Średnia Warta Poznań", "vs 1 Liga", "vs Warta Poznań"],
    col_widths=widths_6col,
    rows_data=t1_rows,
    filename="output_visualizations/tabela_1_kupczak_cb.png",
    target_col_idx=1
)

# TABLE 2: Mateusz Kupczak vs Skrajny stoper
t2_rows = []
for m in ordered_metrics:
    disp_name, cat, unit = metric_display_names[m]
    v_p = kupczak[m]
    v_l = avg_1l_fb[m]
    v_b = avg_warta_fb[m]
    is_pct = (unit == '%')
    t2_rows.append({
        'category': cat,
        'values': [
            disp_name,
            fmt_val(m, v_p),
            fmt_val(m, v_l),
            fmt_val(m, v_b),
            calc_delta(v_p, v_l, is_pct),
            calc_delta(v_p, v_b, is_pct)
        ]
    })

render_table_image_white(
    title="MATEUSZ KUPCZAK — PORÓWNANIE POZYCYJNE (SKRAJNY STOPER)",
    subtitle="Analiza porównawcza surowych danych statystycznych vs Średnia 1. Ligi (Skrajny stoper) oraz Średnia Warta Poznań",
    columns=["Metryka Statystyczna", "Mateusz Kupczak", "Średnia 1 Liga (Skrajny stoper)", "Średnia Warta Poznań", "vs 1 Liga", "vs Warta Poznań"],
    col_widths=widths_6col,
    rows_data=t2_rows,
    filename="output_visualizations/tabela_2_kupczak_fb.png",
    target_col_idx=1
)

# TABLE 3: Hubert Muszyński vs Centralny stoper
t3_rows = []
for m in ordered_metrics:
    disp_name, cat, unit = metric_display_names[m]
    v_p = muszynski[m]
    v_l = avg_1l_cb[m]
    v_b = avg_warta_cb[m]
    is_pct = (unit == '%')
    t3_rows.append({
        'category': cat,
        'values': [
            disp_name,
            fmt_val(m, v_p),
            fmt_val(m, v_l),
            fmt_val(m, v_b),
            calc_delta(v_p, v_l, is_pct),
            calc_delta(v_p, v_b, is_pct)
        ]
    })

render_table_image_white(
    title="HUBERT MUSZYŃSKI — PORÓWNANIE POZYCYJNE (CENTRALNY STOPER)",
    subtitle="Analiza porównawcza surowych danych statystycznych vs Średnia 1. Ligi (Centralny stoper) oraz Średnia Warta Poznań",
    columns=["Metryka Statystyczna", "Hubert Muszyński", "Średnia 1 Liga (Centralny stoper)", "Średnia Warta Poznań", "vs 1 Liga", "vs Warta Poznań"],
    col_widths=widths_6col,
    rows_data=t3_rows,
    filename="output_visualizations/tabela_3_muszynski_cb.png",
    target_col_idx=1
)

# TABLE 4: Hubert Muszyński vs Skrajny stoper
t4_rows = []
for m in ordered_metrics:
    disp_name, cat, unit = metric_display_names[m]
    v_p = muszynski[m]
    v_l = avg_1l_fb[m]
    v_b = avg_warta_fb[m]
    is_pct = (unit == '%')
    t4_rows.append({
        'category': cat,
        'values': [
            disp_name,
            fmt_val(m, v_p),
            fmt_val(m, v_l),
            fmt_val(m, v_b),
            calc_delta(v_p, v_l, is_pct),
            calc_delta(v_p, v_b, is_pct)
        ]
    })

render_table_image_white(
    title="HUBERT MUSZYŃSKI — PORÓWNANIE POZYCYJNE (SKRAJNY STOPER)",
    subtitle="Analiza porównawcza surowych danych statystycznych vs Średnia 1. Ligi (Skrajny stoper) oraz Średnia Warta Poznań",
    columns=["Metryka Statystyczna", "Hubert Muszyński", "Średnia 1 Liga (Skrajny stoper)", "Średnia Warta Poznań", "vs 1 Liga", "vs Warta Poznań"],
    col_widths=widths_6col,
    rows_data=t4_rows,
    filename="output_visualizations/tabela_4_muszynski_fb.png",
    target_col_idx=1
)

# TABLE 5: Zestawienie Centralny stoper
t5_rows = []
for m in ordered_metrics:
    disp_name, cat, unit = metric_display_names[m]
    v_k = kupczak[m]
    v_m = muszynski[m]
    v_l = avg_1l_cb[m]
    v_b = avg_warta_cb[m]
    t5_rows.append({
        'category': cat,
        'values': [
            disp_name,
            fmt_val(m, v_k),
            fmt_val(m, v_m),
            fmt_val(m, v_l),
            fmt_val(m, v_b)
        ]
    })

render_table_image_white(
    title="ZESTAWIENIE PORÓWNAWCZE — CENTRALNY STOPER",
    subtitle="Zestawienie bezpośrednie: Mateusz Kupczak vs Hubert Muszyński vs Średnia 1. Ligi (Centralny stoper) vs Średnia Warta Poznań",
    columns=["Metryka Statystyczna", "Mateusz Kupczak", "Hubert Muszyński", "Średnia 1 Liga (Centralny stoper)", "Średnia Warta Poznań"],
    col_widths=widths_5col,
    rows_data=t5_rows,
    filename="output_visualizations/tabela_5_zestawienie_cb.png",
    target_col_idx=None
)

# TABLE 6: Zestawienie Skrajny stoper
t6_rows = []
for m in ordered_metrics:
    disp_name, cat, unit = metric_display_names[m]
    v_k = kupczak[m]
    v_m = muszynski[m]
    v_l = avg_1l_fb[m]
    v_b = avg_warta_fb[m]
    t6_rows.append({
        'category': cat,
        'values': [
            disp_name,
            fmt_val(m, v_k),
            fmt_val(m, v_m),
            fmt_val(m, v_l),
            fmt_val(m, v_b)
        ]
    })

render_table_image_white(
    title="ZESTAWIENIE PORÓWNAWCZE — SKRAJNY STOPER",
    subtitle="Zestawienie bezpośrednie: Mateusz Kupczak vs Hubert Muszyński vs Średnia 1. Ligi (Skrajny stoper) vs Średnia Warta Poznań",
    columns=["Metryka Statystyczna", "Mateusz Kupczak", "Hubert Muszyński", "Średnia 1 Liga (Skrajny stoper)", "Średnia Warta Poznań"],
    col_widths=widths_5col,
    rows_data=t6_rows,
    filename="output_visualizations/tabela_6_zestawienie_fb.png",
    target_col_idx=None
)
