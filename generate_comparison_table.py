import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
os.makedirs('output_visualizations', exist_ok=True)

# 1. Load Datasets
df_1liga_pos10 = pd.read_excel('data/1 liga/pozycja 10.xlsx')
df_2liga_pos10 = pd.read_excel('data/2 liga/pozycja 10.xlsx')

# Combine for 1+2 liga u17 benchmark
df_combined = pd.concat([df_1liga_pos10, df_2liga_pos10], ignore_index=True)

# 2. Extract Specific Players
kucharski_row = df_1liga_pos10[df_1liga_pos10['Player'].str.contains('Kucharski', na=False)].iloc[0]
wolczek_row = df_2liga_pos10[df_2liga_pos10['Player'].str.contains('Wołczek|Wolczek', na=False)].iloc[0]
kusztal_row = df_2liga_pos10[df_2liga_pos10['Player'].str.contains('Kusztal', na=False)].iloc[0]

# 3. Compute Averages
mean_1liga_pos10 = df_1liga_pos10.mean(numeric_only=True)
u17_df = df_combined[df_combined['Age'] <= 17]
mean_12liga_u17 = u17_df.mean(numeric_only=True)

# 4. Metrics Definition
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

# Prepare rows data for rendering
rows_data = []

# Colors
YELLOW_BG = "#FEF08A" # Warm light yellow for benchmark columns
GREEN_TOP = "#BBF7D0"  # Soft green for top player highlight

for raw_col, display_label, is_pct, category in metrics_spec:
    val_k = kucharski_row[raw_col]
    val_w = wolczek_row[raw_col]
    val_ku = kusztal_row[raw_col]
    val_l1 = mean_1liga_pos10[raw_col]
    val_u17 = mean_12liga_u17[raw_col]
    
    # Determine best among the 3 players for highlighting
    player_vals = [val_k, val_w, val_ku]
    valid_pvals = [v for v in player_vals if not pd.isna(v)]
    best_pval = max(valid_pvals) if valid_pvals else None
    
    highlights = [None] * 6
    
    # Highlight best player in green
    if best_pval is not None:
        if val_k == best_pval:
            highlights[1] = GREEN_TOP
        if val_w == best_pval:
            highlights[2] = GREEN_TOP
        if val_ku == best_pval:
            highlights[3] = GREEN_TOP
            
    # Uniform Yellow background for both benchmark columns (col 4 & col 5)
    highlights[4] = YELLOW_BG
    highlights[5] = YELLOW_BG
            
    val_strs = [
        display_label,
        fmt_val(val_k, is_pct),
        fmt_val(val_w, is_pct),
        fmt_val(val_ku, is_pct),
        fmt_val(val_l1, is_pct),
        fmt_val(val_u17, is_pct)
    ]
    
    rows_data.append({
        'category': category,
        'values': val_strs,
        'highlights': highlights
    })

# 5. Render Matplotlib Table Image
def render_table(title, subtitle, columns, col_widths, rows_data, filename, fig_height=9.5, fig_width=16.5):
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['axes.edgecolor'] = 'none'

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Header Title & Subtitle
    fig.text(0.035, 0.95, title, fontsize=15, fontweight='bold', color='#111827', va='top')
    fig.text(0.035, 0.915, subtitle, fontsize=9.5, color='#64748B', va='top')

    left, top = 0.035, 0.86
    total_width = sum(col_widths)
    
    col_x_starts = []
    curr = left
    for w in col_widths:
        col_x_starts.append(curr)
        curr += w

    # Header Bar (Dark Slate)
    header_height = 0.048
    th_box = patches.FancyBboxPatch((left, top - header_height), total_width, header_height,
                                     boxstyle="square,pad=0",
                                     facecolor="#1E293B", edgecolor="none", linewidth=0,
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
        fig.text(tx, top - header_height / 2.0, col_name, fontsize=9.0, fontweight='bold', color='#FFFFFF', ha=ha, va='center')

    curr_y = top - header_height
    row_h = 0.042
    current_category = ""

    for row_idx, row in enumerate(rows_data):
        category = row.get('category', '')
        
        # Section Header Row
        if category and category != current_category:
            current_category = category
            curr_y -= 0.030
            cat_box = patches.FancyBboxPatch((left, curr_y), total_width, 0.028,
                                             boxstyle="square,pad=0",
                                             facecolor="#F1F5F9", edgecolor="none", linewidth=0,
                                             transform=fig.transFigure)
            fig.patches.append(cat_box)
            fig.text(left + 0.012, curr_y + 0.014, category.upper(), fontsize=8.5, fontweight='bold', color='#334155', va='center')
            
            line = patches.Rectangle((left, curr_y), total_width, 0.001, facecolor="#CBD5E1", edgecolor="none", linewidth=0, transform=fig.transFigure)
            fig.patches.append(line)

        curr_y -= row_h

        # Alternating Row Background
        bg_color = "#F8FAFC" if row_idx % 2 == 1 else "#FFFFFF"
        r_box = patches.FancyBboxPatch((left, curr_y), total_width, row_h,
                                        boxstyle="square,pad=0",
                                        facecolor=bg_color, edgecolor="none", linewidth=0,
                                        transform=fig.transFigure)
        fig.patches.append(r_box)

        # Bottom Cell Border (Subtle line separator)
        border_line = patches.Rectangle((left, curr_y), total_width, 0.0008, facecolor="#E2E8F0", edgecolor="none", linewidth=0, transform=fig.transFigure)
        fig.patches.append(border_line)

        # Render Cell Values
        vals = row['values']
        bg_highlights = row.get('highlights', [None] * len(vals))

        for c_idx, val_str in enumerate(vals):
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            ha = 'left' if c_idx == 0 else 'center'
            tx = cx + 0.012 if c_idx == 0 else cx + cw / 2.0
            
            color = '#111827'
            fontweight = 'normal'

            # Cell Highlight with NO EDGE BORDER (edgecolor="none", linewidth=0)
            cell_hl = bg_highlights[c_idx] if c_idx < len(bg_highlights) else None
            if cell_hl:
                c_box = patches.FancyBboxPatch((cx, curr_y), cw, row_h,
                                               boxstyle="square,pad=0",
                                               facecolor=cell_hl, edgecolor="none", linewidth=0,
                                               transform=fig.transFigure)
                fig.patches.append(c_box)
                
                # Text formatting depending on highlight type
                if cell_hl == GREEN_TOP:
                    color = '#15803D'
                    fontweight = 'bold'
                elif cell_hl == YELLOW_BG:
                    color = '#713F12'
                    fontweight = 'bold'

            fig.text(tx, curr_y + row_h / 2.0, val_str, fontsize=8.8, fontweight=fontweight, color=color, ha=ha, va='center')

    # Save PNG Image
    plt.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.15)
    plt.close()
    print(f"Pomyślnie zaktualizowano plik graficzny: {filename}")

# Run Table Generation
columns = [
    'METRYKA STATYSTYCZNA',
    'JAKUB KUCHARSKI\n(Stal Rzeszów)',
    'ALEKSANDER WOŁCZEK\n(Sandecja Nowy Sącz)',
    'PATRYK KUSZTAL\n(Warta Poznań)',
    'ŚREDNIA 1 LIGA\n(Pozycja 10)',
    'ŚREDNIA 1+2 LIGA\n(Poz. 10, ur. 2008+)'
]
col_widths = [0.28, 0.13, 0.13, 0.13, 0.13, 0.13]

output_filename = 'output_visualizations/tabela_porownawcza_pozycja10.png'
render_table(
    title="ANALIZA PORÓWNAWCZA STATYSTYK — POZYCJA 10",
    subtitle="Zestawienie indywidualne: Jakub Kucharski, Aleksander Wołczek, Patryk Kusztal vs średnie ligowe pozycji 10",
    columns=columns,
    col_widths=col_widths,
    rows_data=rows_data,
    filename=output_filename
)
