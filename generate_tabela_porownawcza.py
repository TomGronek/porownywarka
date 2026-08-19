import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
os.makedirs('output_visualizations', exist_ok=True)

# 1. Load Data
df_1l_cb = pd.read_excel('data/1 liga - centralny.xlsx')
df_2l_cb = pd.read_excel('data/2 liga - centralny.xlsx')
df_esa_cb = pd.read_excel('data/ESA/pozycja 4,5.xlsx')
df_1l_pos45 = pd.read_excel('data/1 liga/pozycja 4,5.xlsx')

# Extract players
janiszewski = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Janiszewski', case=False)].iloc[0]
karasinski = df_1l_pos45[df_1l_pos45['Player'].astype(str).str.contains('Karasinski', case=False)].iloc[0]

azatsky = df_1l_pos45[df_1l_pos45['Player'].astype(str).str.contains('Azatsky', case=False)].iloc[0]
najemski = df_esa_cb[df_esa_cb['Player'].astype(str).str.contains('Najemski', case=False)].iloc[0]
wojcin = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Wojcin', case=False)].iloc[0]
lepczyn = df_2l_cb[df_2l_cb['Player'].astype(str).str.contains('Lepczy', case=False)].iloc[0]

warta_df = pd.DataFrame([azatsky, najemski, wojcin, lepczyn])
mean_warta = warta_df.mean(numeric_only=True)

mean_1l = df_1l_cb.mean(numeric_only=True)
mean_2l = df_2l_cb.mean(numeric_only=True)

# 2. Metrics Specification
metrics_meta = [
    # (raw_col, display_name, category, unit)
    ('Defensive duels per 90', 'Pojedynki w defensywie / 90', 'GRA W DEFENSYWIE', 'per90'),
    ('Defensive duels won, %', '% wygranych pojedynków w defensywie', 'GRA W DEFENSYWIE', '%'),
    ('Shots blocked per 90', 'Zablokowane strzały / 90', 'GRA W DEFENSYWIE', 'per90'),
    
    ('Aerial duels per 90', 'Pojedynki w powietrzu / 90', 'GRA W POWIETRZU', 'per90'),
    ('Aerial duels won, %', '% wygranych pojedynków w powietrzu', 'GRA W POWIETRZU', '%'),
    
    ('Forward passes per 90', 'Podania do przodu / 90', 'DYSTRYBUCJA I PODANIA', 'per90'),
    ('Accurate forward passes, %', '% celności podań do przodu', 'DYSTRYBUCJA I PODANIA', '%')
]

def fmt_val(val, unit):
    if pd.isna(val):
        return "-"
    if unit == '%':
        return f"{val:.1f}%"
    else:
        return f"{val:.2f}"

# 3. Columns definition
columns = [
    'Metryka Statystyczna',
    'G. Janiszewski\n(Zagłębie Sosnowiec)',
    'Karasiński\n(Ruch Chorzów)',
    'Średnia 2 liga\n(Środkowi obrońcy)',
    'Średnia 1 liga\n(Środkowi obrońcy)',
    'Średnia Warta\n(Azatsky, Najemski, Wojcinowicz, Lepczyński)'
]

col_widths = [0.26, 0.14, 0.14, 0.14, 0.14, 0.17]

rows_data = []
for raw_col, display_name, category, unit in metrics_meta:
    v_jan = janiszewski[raw_col]
    v_kar = karasinski[raw_col]
    v_2l = mean_2l[raw_col]
    v_1l = mean_1l[raw_col]
    v_war = mean_warta[raw_col]
    
    val_strs = [
        display_name,
        fmt_val(v_jan, unit),
        fmt_val(v_kar, unit),
        fmt_val(v_2l, unit),
        fmt_val(v_1l, unit),
        fmt_val(v_war, unit)
    ]
    
    rows_data.append({
        'category': category,
        'values': val_strs
    })

# 4. Render Engine
def render_table_png(title, subtitle, columns, col_widths, rows_data, filename):
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['axes.edgecolor'] = 'none'

    fig_height = 7.0
    fig_width = 16.5
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Header Title & Subtitle
    fig.text(0.035, 0.940, title, fontsize=16, fontweight='bold', color='#0F172A', va='top')
    fig.text(0.035, 0.890, subtitle, fontsize=9.5, color='#64748B', va='top')

    left, top = 0.035, 0.820
    total_width = sum(col_widths)

    col_x_starts = []
    curr = left
    for w in col_widths:
        col_x_starts.append(curr)
        curr += w

    header_height = 0.080
    row_h = 0.062
    cat_h = 0.045
    
    # Calculate total height of table to draw solid background columns for yellow league averages
    categories_seen = []
    total_y_height = header_height
    for row in rows_data:
        cat = row.get('category', '')
        if cat and cat not in categories_seen:
            categories_seen.append(cat)
            total_y_height += cat_h # category header height
        total_y_height += row_h

    # 1. DRAW UNIFORM YELLOW BACKGROUND FOR LEAGUE AVERAGE COLUMNS (Col 3 & Col 4: Średnia 2 liga & Średnia 1 liga)
    YELLOW_LEAGUE_BG = "#FEF08A" # Soft elegant yellow background
    YELLOW_HEADER_BG = "#EAB308" # Rich yellow for column header title

    # Draw solid yellow box from top of header to bottom of table for columns 3 & 4
    for col_idx in [3, 4]:
        yellow_x = col_x_starts[col_idx]
        yellow_w = col_widths[col_idx]
        
        yellow_box = patches.FancyBboxPatch(
            (yellow_x, top - total_y_height), yellow_w, total_y_height,
            boxstyle="square,pad=0",
            facecolor=YELLOW_LEAGUE_BG,
            edgecolor="none",
            linewidth=0,
            transform=fig.transFigure,
            zorder=1
        )
        fig.patches.append(yellow_box)

    # 2. DRAW HEADER BAR (Dark Slate for regular, yellow accent for league columns)
    for idx, col_name in enumerate(columns):
        cx = col_x_starts[idx]
        cw = col_widths[idx]
        
        if idx in [3, 4]:
            h_bg = YELLOW_HEADER_BG
            text_color = "#0F172A"
        else:
            h_bg = "#0F172A"
            text_color = "#FFFFFF"

        th_box = patches.FancyBboxPatch(
            (cx, top - header_height), cw, header_height,
            boxstyle="square,pad=0",
            facecolor=h_bg,
            edgecolor="none",
            linewidth=0,
            transform=fig.transFigure,
            zorder=2
        )
        fig.patches.append(th_box)

        tx = cx + 0.012 if idx == 0 else cx + cw / 2.0
        ha = 'left' if idx == 0 else 'center'
        
        fig.text(
            tx, top - header_height / 2.0, col_name,
            fontsize=9.0, fontweight='bold', color=text_color,
            ha=ha, va='center', zorder=3, linespacing=1.2
        )

    curr_y = top - header_height
    current_category = ""

    # 3. DRAW ROWS (No cell borders!)
    for row_idx, row in enumerate(rows_data):
        category = row.get('category', '')
        
        # Category Section Row
        if category and category != current_category:
            current_category = category
            curr_y -= cat_h
            
            # Category bar across regular columns (0, 1, 2, 5)
            for c_idx in [0, 1, 2, 5]:
                cx = col_x_starts[c_idx]
                cw = col_widths[c_idx]
                cat_box = patches.FancyBboxPatch(
                    (cx, curr_y), cw, cat_h,
                    boxstyle="square,pad=0",
                    facecolor="#F1F5F9",
                    edgecolor="none",
                    linewidth=0,
                    transform=fig.transFigure,
                    zorder=2
                )
                fig.patches.append(cat_box)

            # Text for category title
            fig.text(
                left + 0.012, curr_y + cat_h / 2.0, category.upper(),
                fontsize=8.5, fontweight='bold', color='#334155',
                va='center', zorder=4
            )

        curr_y -= row_h

        # Alternating row background for regular columns (0, 1, 2, 5)
        bg_color = "#F8FAFC" if row_idx % 2 == 1 else "#FFFFFF"
        
        for c_idx in [0, 1, 2, 5]:
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            r_box = patches.FancyBboxPatch(
                (cx, curr_y), cw, row_h,
                boxstyle="square,pad=0",
                facecolor=bg_color,
                edgecolor="none",
                linewidth=0,
                transform=fig.transFigure,
                zorder=2
            )
            fig.patches.append(r_box)

        # Render Cell Values
        vals = row['values']
        for c_idx, val_str in enumerate(vals):
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            ha = 'left' if c_idx == 0 else 'center'
            tx = cx + 0.012 if c_idx == 0 else cx + cw / 2.0
            
            # Text formatting
            if c_idx == 0:
                color = '#1E293B'
                fw = 'bold'
            elif c_idx in [1, 2]:
                color = '#0F172A'
                fw = 'bold'
            elif c_idx in [3, 4]:
                color = '#0F172A'
                fw = 'bold'
            else:
                color = '#334155'
                fw = 'bold'

            fig.text(
                tx, curr_y + row_h / 2.0, val_str,
                fontsize=10.0, fontweight=fw, color=color,
                ha=ha, va='center', zorder=4
            )

    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Grafika zapisana pomyślnie: {filename}")

if __name__ == '__main__':
    render_table_png(
        title="TABELA PORÓWNAWCZA OBROŃCÓW — 1 I 2 LIGA",
        subtitle="Zestawienie wybranych obrońców na tle średnich ligowych oraz średniej bloku obronnego Warty Poznań",
        columns=columns,
        col_widths=col_widths,
        rows_data=rows_data,
        filename="output_visualizations/tabela_porownawcza_obroncy.png"
    )
