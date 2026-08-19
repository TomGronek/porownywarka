"""
Silnik generowania grafik tabelarycznych wysokiej rozdzielczości (PNG 300 DPI)
zgodny ze standardem wizualnym TABELA_WIZ.md.
"""

import io
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from src.metrics_config import get_metric_info, format_metric_value

def generate_table_png_bytes(
    title: str,
    subtitle: str,
    player_columns: list, # [{'name': '...', 'club': '...', 'data': ...}]
    benchmark_columns: list, # [{'name': '...', 'subtitle': '...', 'data': ...}]
    selected_metrics: list,
    highlight_mode: str = 'top1', # 'top1', 'top3', 'none'
    dpi: int = 300
) -> bytes:
    """
    Renderuje tabelę porównawczą do bufora bajtów PNG (300 DPI).
    """
    # 1. Zbuduj listę kolumn i typów
    columns_labels = ["Metryka Statystyczna"]
    col_types = ['metric']
    
    for p in player_columns:
        lbl = p['name']
        if p.get('club'):
            lbl += f"\n({p['club']})"
        columns_labels.append(lbl)
        col_types.append('player')

    yellow_indices = []
    for b in benchmark_columns:
        yellow_indices.append(len(columns_labels))
        lbl = b['name']
        sub = b.get('subtitle', '').strip()
        if sub:
            sub_clean = sub.strip('()')
            lbl += f"\n({sub_clean})"
        columns_labels.append(lbl)
        col_types.append('benchmark')

    n_cols = len(columns_labels)

    # 2. Oblicz szerokości kolumn (Auto-Layout)
    # Suma szerokości ~ 0.93, lewy margines 0.035
    metric_col_w = 0.28 if n_cols <= 5 else 0.24
    rem_w = 0.93 - metric_col_w
    other_col_w = rem_w / (n_cols - 1) if n_cols > 1 else 0.5
    col_widths = [metric_col_w] + [other_col_w] * (n_cols - 1)

    # 3. Pogrupuj metryki wg kategorii
    metrics_by_cat = {}
    for m in selected_metrics:
        disp_name, cat, unit, higher_is_better = get_metric_info(m)
        if cat not in metrics_by_cat:
            metrics_by_cat[cat] = []
        metrics_by_cat[cat].append((m, disp_name, unit, higher_is_better))

    # 4. Przygotuj dane wierszy i wyróżnienia
    rows_data = []
    for cat_name, metrics_list in metrics_by_cat.items():
        for raw_col, disp_name, unit, higher_is_better in metrics_list:
            player_num_vals = []
            for p in player_columns:
                p_data = p['data']
                val = p_data.get(raw_col, np.nan) if isinstance(p_data, dict) else (p_data[raw_col] if raw_col in p_data else np.nan)
                try:
                    num_v = float(val) if pd.notna(val) else np.nan
                except (ValueError, TypeError):
                    num_v = np.nan
                player_num_vals.append(num_v)

            # Wyznacz top
            valid_vals = [v for v in player_num_vals if not np.isnan(v)]
            best_val = None
            top3_vals = set()
            if valid_vals:
                sorted_vals = sorted(valid_vals, reverse=higher_is_better)
                best_val = sorted_vals[0]
                if len(sorted_vals) >= 3:
                    top3_vals = set(sorted_vals[:3])
                else:
                    top3_vals = set(sorted_vals)

            # Wartości wiersza
            row_vals = [disp_name]
            row_hls = [None] # Kolumna metryki

            # Gracze
            for idx, p in enumerate(player_columns):
                v_num = player_num_vals[idx]
                row_vals.append(format_metric_value(v_num, unit))
                
                hl_color = None
                if highlight_mode != 'none' and not np.isnan(v_num) and len(player_columns) > 1:
                    if v_num == best_val:
                        hl_color = "#BBF7D0" # Ciemniejszy seledyn
                    elif highlight_mode == 'top3' and v_num in top3_vals and len(player_columns) > 2:
                        hl_color = "#DCFCE7" # Jasny szmaragd
                row_hls.append(hl_color)

            # Benchmarki
            for b in benchmark_columns:
                b_data = b['data']
                val = b_data.get(raw_col, np.nan) if isinstance(b_data, dict) else (b_data[raw_col] if raw_col in b_data else np.nan)
                row_vals.append(format_metric_value(val, unit))
                row_hls.append(None)

            rows_data.append({
                'category': cat_name,
                'values': row_vals,
                'highlights': row_hls
            })

    # 5. Oblicz wymiary grafiki Matplotlib
    n_rows = len(rows_data)
    n_cats = len(metrics_by_cat)
    fig_height = max(6.0, 1.8 + n_rows * 0.45 + n_cats * 0.35)
    fig_width = max(14.0, n_cols * 2.6)

    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['axes.edgecolor'] = 'none'

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Nagłówek i Tytuł
    fig.text(0.035, 0.950, title, fontsize=14, fontweight='bold', color='#0F172A', va='top')
    fig.text(0.035, 0.910, subtitle, fontsize=9.0, color='#64748B', va='top')

    left, top = 0.035, 0.850
    col_x_starts = []
    curr = left
    for w in col_widths:
        col_x_starts.append(curr)
        curr += w

    header_height = 0.070
    row_h = 0.048
    cat_h = 0.036

    # Oblicz całkowitą wysokość pod żółte tło benchmarków
    total_table_h = header_height + n_rows * row_h + n_cats * cat_h

    # A. Żółte tło dla kolumn benchmarkowych
    YELLOW_BG = "#FEF08A"
    YELLOW_HEADER = "#EAB308"
    
    for b_idx in yellow_indices:
        bx = col_x_starts[b_idx]
        bw = col_widths[b_idx]
        y_box = patches.FancyBboxPatch(
            (bx, top - total_table_h), bw, total_table_h,
            boxstyle="square,pad=0",
            facecolor=YELLOW_BG,
            edgecolor="none",
            linewidth=0,
            transform=fig.transFigure,
            zorder=1
        )
        fig.patches.append(y_box)

    # B. Nagłówki kolumn
    for idx, col_lbl in enumerate(columns_labels):
        cx = col_x_starts[idx]
        cw = col_widths[idx]
        is_bench = idx in yellow_indices
        h_bg = YELLOW_HEADER if is_bench else "#0F172A"
        txt_color = "#0F172A" if is_bench else "#FFFFFF"

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
            tx, top - header_height / 2.0, col_lbl,
            fontsize=8.5, fontweight='bold', color=txt_color,
            ha=ha, va='center', zorder=4, linespacing=1.2
        )

    # C. Renderowanie wierszy i kategorii
    curr_y = top - header_height
    curr_cat = ""

    for row_idx, row in enumerate(rows_data):
        cat = row.get('category', '')
        
        # Pasek kategorii
        if cat and cat != curr_cat:
            curr_cat = cat
            curr_y -= cat_h
            
            for c_idx in range(n_cols):
                if c_idx in yellow_indices:
                    continue
                cx = col_x_starts[c_idx]
                cw = col_widths[c_idx]
                c_box = patches.FancyBboxPatch(
                    (cx, curr_y), cw, cat_h,
                    boxstyle="square,pad=0",
                    facecolor="#F1F5F9",
                    edgecolor="none",
                    linewidth=0,
                    transform=fig.transFigure,
                    zorder=2
                )
                fig.patches.append(c_box)

            fig.text(
                left + 0.012, curr_y + cat_h / 2.0, cat.upper(),
                fontsize=8.0, fontweight='bold', color='#334155',
                va='center', zorder=4
            )

        curr_y -= row_h
        bg_row = "#F8FAFC" if row_idx % 2 == 1 else "#FFFFFF"

        # Tło komórek wiersza
        for c_idx in range(n_cols):
            if c_idx in yellow_indices:
                continue
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            hl_color = row['highlights'][c_idx] if c_idx < len(row['highlights']) else None
            cell_bg = hl_color if hl_color else bg_row
            
            r_box = patches.FancyBboxPatch(
                (cx, curr_y), cw, row_h,
                boxstyle="square,pad=0",
                facecolor=cell_bg,
                edgecolor="none",
                linewidth=0,
                transform=fig.transFigure,
                zorder=2
            )
            fig.patches.append(r_box)

        # Wartości tekstowe
        for c_idx, val_str in enumerate(row['values']):
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            ha = 'left' if c_idx == 0 else 'center'
            tx = cx + 0.012 if c_idx == 0 else cx + cw / 2.0
            
            hl_color = row['highlights'][c_idx] if c_idx < len(row['highlights']) else None
            if hl_color:
                txt_color = "#15803D"
                fw = 'bold'
            elif c_idx in yellow_indices:
                txt_color = "#0F172A"
                fw = 'bold'
            elif c_idx == 0:
                txt_color = "#1E293B"
                fw = 'bold'
            else:
                txt_color = "#0F172A"
                fw = 'normal'

            fig.text(
                tx, curr_y + row_h / 2.0, val_str,
                fontsize=9.0, fontweight=fw, color=txt_color,
                ha=ha, va='center', zorder=4
            )

    # D. Stopka / Legenda
    fig.text(
        0.035, 0.030,
        "LEGENDA:  [ Zielone tło ] = Najlepsza wartość w porównaniu   |   [ Żółte kolumny ] = Średnie ligowe i wiekowe",
        fontsize=8.0, fontweight='bold', color='#475569', va='bottom'
    )

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor(), pad_inches=0.15)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
