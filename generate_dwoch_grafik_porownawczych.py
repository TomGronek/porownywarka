import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
os.makedirs('output_visualizations', exist_ok=True)

# 1. Load Data
df_1l = pd.read_excel('data/1 liga/pozycja 4,5.xlsx')
df_2l = pd.read_excel('data/2 liga/pozycja 4,5.xlsx')
df_esa = pd.read_excel('data/ESA/pozycja 4,5.xlsx')

def get_player(df, name):
    res = df[df['Player'].astype(str).str.contains(name, case=False, na=False)]
    if not res.empty:
        return res.iloc[0]
    raise ValueError(f"Player {name} not found!")

# Target players for Grafika 1
synos = get_player(df_1l, 'Synos')
rezacz = get_player(df_1l, 'Rezacz')
lepczynski = get_player(df_2l, 'Lepczy')

# Target players for Grafika 2
szyminski = get_player(df_1l, 'Szymi')
matysik = get_player(df_esa, 'Matysik')
cisse = get_player(df_1l, 'Ciss')
stepinski = get_player(df_1l, 'Stępiński')

# Benchmarks
mean_1l = df_1l.mean(numeric_only=True)
u21_1l = df_1l[df_1l['Age'] <= 21].mean(numeric_only=True)

# 2. Metrics Specification
metrics_meta = [
    # (raw_col, display_name, category, unit)
    ('Defensive duels per 90', 'Pojedynki w defensywie / 90', 'GRA W DEFENSYWIE', 'per90'),
    ('Defensive duels won, %', '% wygranych pojedynków w defensywie', 'GRA W DEFENSYWIE', '%'),
    ('Shots blocked per 90', 'Zablokowane strzały / 90', 'GRA W DEFENSYWIE', 'per90'),
    
    ('Aerial duels per 90', 'Pojedynki w powietrzu / 90', 'GRA W POWIETRZU', 'per90'),
    ('Aerial duels won, %', '% wygranych pojedynków w powietrzu', 'GRA W POWIETRZU', '%'),
    
    ('Offensive duels per 90', 'Pojedynki w ofensywie / 90', 'DYSTRYBUCJA I OFENSYWA', 'per90'),
    ('Forward passes per 90', 'Podania do przodu / 90', 'DYSTRYBUCJA I OFENSYWA', 'per90'),
    ('Accurate forward passes, %', '% celności podań do przodu', 'DYSTRYBUCJA I OFENSYWA', '%'),
    ('Passes to penalty area per 90', 'Podania w pole karne / 90', 'DYSTRYBUCJA I OFENSYWA', 'per90'),
    ('Accurate passes to penalty area, %', '% celności podań w pole karne', 'DYSTRYBUCJA I OFENSYWA', '%')
]

def fmt_val(val, unit):
    if pd.isna(val):
        return "-"
    if unit == '%':
        return f"{val:.1f}%"
    else:
        return f"{val:.2f}"

# Colors
YELLOW_BG = "#FEF08A"       # Soft yellow background for league average columns
YELLOW_HEADER = "#EAB308"   # Rich yellow for league average column header
GREEN_HIGHLIGHT = "#BBF7D0" # Soft green background for highlighted stats relative to Lepczyński
DARK_GREEN_TXT = "#15803D"  # Dark green text for highlighted stats
DARK_SLATE_HEADER = "#0F172A"

def render_table_png(title, subtitle, columns, col_widths, rows_data, yellow_col_indices, filename, fig_width=17.5, fig_height=9.2):
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['axes.edgecolor'] = 'none'

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Header Title & Subtitle
    fig.text(0.035, 0.950, title, fontsize=15, fontweight='bold', color='#0F172A', va='top')
    fig.text(0.035, 0.910, subtitle, fontsize=9.5, color='#64748B', va='top')

    left, top = 0.035, 0.850
    total_width = sum(col_widths)

    col_x_starts = []
    curr = left
    for w in col_widths:
        col_x_starts.append(curr)
        curr += w

    header_height = 0.065
    row_h = 0.052
    cat_h = 0.038
    
    # Calculate total height of table to draw solid yellow background columns for league averages
    categories_seen = []
    total_y_height = header_height
    for row in rows_data:
        cat = row.get('category', '')
        if cat and cat not in categories_seen:
            categories_seen.append(cat)
            total_y_height += cat_h
        total_y_height += row_h

    # 1. DRAW UNIFORM YELLOW BACKGROUND FOR LEAGUE AVERAGE COLUMNS
    for col_idx in yellow_col_indices:
        yellow_x = col_x_starts[col_idx]
        yellow_w = col_widths[col_idx]
        
        yellow_box = patches.FancyBboxPatch(
            (yellow_x, top - total_y_height), yellow_w, total_y_height,
            boxstyle="square,pad=0",
            facecolor=YELLOW_BG,
            edgecolor="none",
            linewidth=0,
            transform=fig.transFigure,
            zorder=1
        )
        fig.patches.append(yellow_box)

    # 2. DRAW HEADER BAR
    for idx, col_name in enumerate(columns):
        cx = col_x_starts[idx]
        cw = col_widths[idx]
        
        if idx in yellow_col_indices:
            h_bg = YELLOW_HEADER
            text_color = "#0F172A"
        else:
            h_bg = DARK_SLATE_HEADER
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
            
            # Category bar across regular (non-yellow) columns
            for c_idx in range(len(columns)):
                if c_idx in yellow_col_indices:
                    continue
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

        # Alternating row background for regular columns
        bg_color = "#F8FAFC" if row_idx % 2 == 1 else "#FFFFFF"
        
        for c_idx in range(len(columns)):
            if c_idx in yellow_col_indices:
                continue
            
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            
            # Check cell highlight (e.g. green highlight vs Lepczyński)
            cell_bg = row.get('highlights', [None] * len(columns))[c_idx]
            use_bg = cell_bg if cell_bg else bg_color

            r_box = patches.FancyBboxPatch(
                (cx, curr_y), cw, row_h,
                boxstyle="square,pad=0",
                facecolor=use_bg,
                edgecolor="none",
                linewidth=0,
                transform=fig.transFigure,
                zorder=2
            )
            fig.patches.append(r_box)

        # Render Cell Values
        vals = row['values']
        highlights = row.get('highlights', [None] * len(columns))

        for c_idx, val_str in enumerate(vals):
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            ha = 'left' if c_idx == 0 else 'center'
            tx = cx + 0.012 if c_idx == 0 else cx + cw / 2.0
            
            # Text color & weight
            if highlights[c_idx] == GREEN_HIGHLIGHT:
                color = DARK_GREEN_TXT
                fw = 'bold'
            elif c_idx in yellow_col_indices:
                color = '#0F172A'
                fw = 'bold'
            elif c_idx == 0:
                color = '#1E293B'
                fw = 'bold'
            else:
                color = '#0F172A'
                fw = 'bold'

            fig.text(
                tx, curr_y + row_h / 2.0, val_str,
                fontsize=9.5, fontweight=fw, color=color,
                ha=ha, va='center', zorder=4
            )

    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Grafika zapisana pomyślnie: {filename}")

# --- BUILD GRAFIKA 1 ---
cols1 = [
    'Metryka Statystyczna',
    'M. Synos\n(Stal Rzeszów)',
    'W. Rezacz\n(Miedź Legnica)',
    'K. Lepczyński\n(Warta Poznań)',
    'Średnia 1 liga\n(Pozycja 4/5)',
    'Średnia 1 liga U21\n(Pozycja 4/5)'
]
col_widths1 = [0.27, 0.13, 0.13, 0.13, 0.135, 0.135]
yellow_cols1 = [4, 5]

rows_data1 = []
for raw_col, display_name, category, unit in metrics_meta:
    v_syn = synos[raw_col]
    v_rez = rezacz[raw_col]
    v_lep = lepczynski[raw_col]
    v_1l = mean_1l[raw_col]
    v_u21 = u21_1l[raw_col]
    
    highlights = [None] * 6
    if pd.notna(v_syn) and pd.notna(v_lep) and v_syn > v_lep:
        highlights[1] = GREEN_HIGHLIGHT
    if pd.notna(v_rez) and pd.notna(v_lep) and v_rez > v_lep:
        highlights[2] = GREEN_HIGHLIGHT

    val_strs = [
        display_name,
        fmt_val(v_syn, unit),
        fmt_val(v_rez, unit),
        fmt_val(v_lep, unit),
        fmt_val(v_1l, unit),
        fmt_val(v_u21, unit)
    ]
    rows_data1.append({
        'category': category,
        'values': val_strs,
        'highlights': highlights
    })

render_table_png(
    title="PORÓWNANIE ZAWODNIKÓW M. SYNOS I W. REZACZ",
    subtitle="Zestawienie wybranych młodzieżowych obrońców na tle Kacpra Lepczyńskiego, średniej 1. Ligi (poz. 4/5) oraz średniej U21 1. Ligi",
    columns=cols1,
    col_widths=col_widths1,
    rows_data=rows_data1,
    yellow_col_indices=yellow_cols1,
    filename="output_visualizations/porownanie_synos_rezacz.png"
)

# --- BUILD GRAFIKA 2 ---
cols2 = [
    'Metryka Statystyczna',
    'P. Szymiński\n(Ruch Chorzów)',
    'M. Matysik\n(Nieciecza)',
    'S. Cissé\n(Polonia Warszawa)',
    'P. Stępiński\n(Miedź Legnica)',
    'K. Lepczyński\n(Warta Poznań)',
    'Średnia 1 liga\n(Pozycja 4/5)'
]
col_widths2 = [0.25, 0.115, 0.115, 0.115, 0.115, 0.11, 0.11]
yellow_cols2 = [6]

rows_data2 = []
for raw_col, display_name, category, unit in metrics_meta:
    v_szym = szyminski[raw_col]
    v_mat = matysik[raw_col]
    v_cis = cisse[raw_col]
    v_ste = stepinski[raw_col]
    v_lep = lepczynski[raw_col]
    v_1l = mean_1l[raw_col]
    
    highlights = [None] * 7
    if pd.notna(v_szym) and pd.notna(v_lep) and v_szym > v_lep:
        highlights[1] = GREEN_HIGHLIGHT
    if pd.notna(v_mat) and pd.notna(v_lep) and v_mat > v_lep:
        highlights[2] = GREEN_HIGHLIGHT
    if pd.notna(v_cis) and pd.notna(v_lep) and v_cis > v_lep:
        highlights[3] = GREEN_HIGHLIGHT
    if pd.notna(v_ste) and pd.notna(v_lep) and v_ste > v_lep:
        highlights[4] = GREEN_HIGHLIGHT

    val_strs = [
        display_name,
        fmt_val(v_szym, unit),
        fmt_val(v_mat, unit),
        fmt_val(v_cis, unit),
        fmt_val(v_ste, unit),
        fmt_val(v_lep, unit),
        fmt_val(v_1l, unit)
    ]
    rows_data2.append({
        'category': category,
        'values': val_strs,
        'highlights': highlights
    })

render_table_png(
    title="PORÓWNANIE OBROŃCÓW — SZYMIŃSKI, MATYSIK, CISSÉ, STĘPIŃSKI",
    subtitle="Zestawienie statystyczne obrońców na tle Kacpra Lepczyńskiego (Warta Poznań) oraz średniej 1. Ligi (pozycja 4/5)",
    columns=cols2,
    col_widths=col_widths2,
    rows_data=rows_data2,
    yellow_col_indices=yellow_cols2,
    filename="output_visualizations/porownanie_szyminski_matysik_cisse_stepinski.png"
)
