import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directories exist
os.makedirs('output_visualizations/zagranica', exist_ok=True)

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

def fmt(m, val):
    if '%' in m:
        return f"{val:.1f}%"
    return f"{val:.2f}"

# Determine top 3 indices per metric
top3_dict = {}
top1_dict = {}
for m in req_metrics:
    top3_indices = df_zag[m].nlargest(3).index.tolist()
    top3_dict[m] = set(top3_indices)
    top1_dict[m] = top3_indices[0]

print("Generowanie wyznaczonej grafiki zbiorczej PNG z wyróżnieniem Top 3 w każdej statystyce...")
plt.rcParams['font.sans-serif'] = 'Segoe UI'
fig, ax = plt.subplots(figsize=(22, 14.5), dpi=300)
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')
ax.axis('off')

# Title & Subtitle
fig.text(0.02, 0.96, "ZESTAWIENIE ZBIORCZE ZAWODNIKÓW — TOP 3 ODCHYLONA POZYTYWNE W KAŻDEJ STATYSTYCE", fontsize=15, fontweight='bold', color='#111827', va='top')
fig.text(0.02, 0.93, "Wyróżnienie zielonym tłem 3 najlepszych wyników (najwyższe odchylenie in plus od średniej) w kontekście KAŻDEJ POJEDYNCZEJ statystyki", fontsize=9.5, color='#475569', va='top')

sum_cols = ["Zawodnik", "Klub", "Minuty", "Poj. Def /90", "Wygr. Def %", "Poj. Pow /90", "Wygr. Pow %", "Pod. przód /90", "Dokł. przód %", "Dośrodk. /90", "Dokł. dośr %"]
sum_widths = [0.12, 0.12, 0.06, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.07, 0.07]

top = 0.88
left = 0.02
total_w = sum(sum_widths)

col_starts = []
curr = left
for w in sum_widths:
    col_starts.append(curr)
    curr += w

# Header
h_box = patches.FancyBboxPatch((left, top - 0.035), total_w, 0.035, boxstyle="square,pad=0", facecolor="#1E293B", transform=fig.transFigure)
fig.patches.append(h_box)

for idx, c_name in enumerate(sum_cols):
    cx = col_starts[idx]
    cw = sum_widths[idx]
    ha = 'left' if idx < 2 else 'center'
    tx = cx + 0.008 if idx < 2 else cx + cw / 2.0
    fig.text(tx, top - 0.0175, c_name, fontsize=8.5, fontweight='bold', color='#FFFFFF', ha=ha, va='center')

curr_y = top - 0.035
row_h = 0.032

# Render 19 Players
for idx, clean_name in enumerate(clean_names):
    curr_y -= row_h
    p_row = df_zag.iloc[idx]
    team = str(p_row['Team']) if pd.notna(p_row['Team']) else '-'
    mins = str(p_row['Minutes played'])
    
    bg = "#F8FAFC" if idx % 2 == 1 else "#FFFFFF"
    r_box = patches.FancyBboxPatch((left, curr_y), total_w, row_h, boxstyle="square,pad=0", facecolor=bg, transform=fig.transFigure)
    fig.patches.append(r_box)
    
    vals = [
        clean_name, team[:18], mins,
        fmt('Defensive duels per 90', p_row['Defensive duels per 90']),
        fmt('Defensive duels won, %', p_row['Defensive duels won, %']),
        fmt('Aerial duels per 90', p_row['Aerial duels per 90']),
        fmt('Aerial duels won, %', p_row['Aerial duels won, %']),
        fmt('Forward passes per 90', p_row['Forward passes per 90']),
        fmt('Accurate forward passes, %', p_row['Accurate forward passes, %']),
        fmt('Crosses per 90', p_row['Crosses per 90']),
        fmt('Accurate crosses, %', p_row['Accurate crosses, %'])
    ]
    
    for c_idx, v_str in enumerate(vals):
        cx = col_starts[c_idx]
        cw = sum_widths[c_idx]
        ha = 'left' if c_idx < 2 else 'center'
        tx = cx + 0.008 if c_idx < 2 else cx + cw / 2.0
        fw = 'bold' if c_idx == 0 else 'normal'
        color = '#111827'
        
        # Check if cell is in Top 3 for metric
        if c_idx >= 3:
            m_key = req_metrics[c_idx - 3]
            if idx in top3_dict[m_key]:
                # Draw cell highlight box (Light Emerald / Green)
                cell_bg = "#DCFCE7" if idx != top1_dict[m_key] else "#BBF7D0" # Darker green for top 1
                c_box = patches.FancyBboxPatch((cx, curr_y), cw, row_h, boxstyle="square,pad=0", facecolor=cell_bg, transform=fig.transFigure)
                fig.patches.append(c_box)
                color = "#15803D" # Bold green text
                fw = "bold"
        
        fig.text(tx, curr_y + row_h / 2.0, v_str, fontsize=8.0, fontweight=fw, color=color, ha=ha, va='center')

# Render Benchmark Rows at Bottom
benchmarks = [
    ("ŚREDNIA GRUPA ZAGRANICA", "-", "-", avg_zag),
    ("ŚREDNIA 1 LIGA (SKRAJNY STOPER)", "-", "-", avg_1l_fb),
    ("ŚREDNIA WARTA POZNAŃ (SKRAJNY STOPER)", "-", "-", avg_warta_fb)
]

for b_name, b_team, b_mins, b_series in benchmarks:
    curr_y -= (row_h + 0.004)
    b_box = patches.FancyBboxPatch((left, curr_y), total_w, row_h, boxstyle="square,pad=0", facecolor="#E2E8F0", transform=fig.transFigure)
    fig.patches.append(b_box)
    
    vals = [
        b_name, b_team, b_mins,
        fmt('Defensive duels per 90', b_series['Defensive duels per 90']),
        fmt('Defensive duels won, %', b_series['Defensive duels won, %']),
        fmt('Aerial duels per 90', b_series['Aerial duels per 90']),
        fmt('Aerial duels won, %', b_series['Aerial duels won, %']),
        fmt('Forward passes per 90', b_series['Forward passes per 90']),
        fmt('Accurate forward passes, %', b_series['Accurate forward passes, %']),
        fmt('Crosses per 90', b_series['Crosses per 90']),
        fmt('Accurate crosses, %', b_series['Accurate crosses, %'])
    ]
    
    for c_idx, v_str in enumerate(vals):
        cx = col_starts[c_idx]
        cw = sum_widths[c_idx]
        ha = 'left' if c_idx < 2 else 'center'
        tx = cx + 0.008 if c_idx < 2 else cx + cw / 2.0
        fig.text(tx, curr_y + row_h / 2.0, v_str, fontsize=8.0, fontweight='bold', color='#0F172A', ha=ha, va='center')

# Legend at the bottom
fig.text(0.02, 0.03, "LEGENDA:  [ Ciemnozielone tło ] = 1. Miejsce w danej statystyce   |   [ Jasnozielone tło ] = 2. lub 3. Miejsce w danej statystyce", fontsize=8.5, fontweight='bold', color='#15803D', va='bottom')

out_path = 'output_visualizations/zagranica/tabela_zbiorcza_top3_odchylenie.png'
plt.savefig(out_path, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.15)
plt.close()

print(f"Pomyślnie wygenerowano nową grafikę zbiorczą z wyróżnieniem Top 3: {out_path}")
