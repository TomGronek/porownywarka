"""
Silnik renderowania tabel HTML/CSS w standardzie TABELA_WIZ.
Czyste linie, brak pionowych obramowań komórek, zielone akcenty dla Top wyników,
oraz jednolite żółte pasy dla kolumn średnich ligowych/wiekowych.
"""

from src.metrics_config import get_metric_info, format_metric_value, format_delta
import pandas as pd
import numpy as np

def generate_comparison_table_html(
    title: str,
    subtitle: str,
    player_columns: list, # [{'name': '...', 'club': '...', 'data': pd.Series/dict, 'meta': '...'}]
    benchmark_columns: list, # [{'name': '...', 'subtitle': '...', 'data': pd.Series/dict, 'highlight_yellow': True}]
    selected_metrics: list, # [raw_col1, raw_col2, ...]
    highlight_mode: str = 'top1', # 'top1', 'top3', 'none'
    show_deltas: bool = False,
    reference_player_idx: int = 0
) -> str:
    """
    Generuje kompletny kod HTML i CSS tabeli porównawczej.
    """
    # 1. Przygotuj kolumny nagłówka
    # Kolumna 0: Metryka
    all_cols_meta = [{'title': 'METRYKA STATYSTYCZNA', 'sub': '', 'type': 'metric'}]
    
    for p in player_columns:
        all_cols_meta.append({
            'title': p['name'],
            'sub': p.get('club', '') + (f"<br>Wiek: {p.get('age', '-')}" if p.get('age') else ''),
            'type': 'player',
            'data': p['data']
        })
        
    for b in benchmark_columns:
        sub = b.get('subtitle', '').strip()
        sub_formatted = f"({sub.strip('()')})" if sub else ''
        all_cols_meta.append({
            'title': b['name'],
            'sub': sub_formatted,
            'type': 'benchmark',
            'data': b['data']
        })

    # 2. Pogrupuj metryki wg kategorii
    metrics_by_cat = {}
    for m in selected_metrics:
        disp_name, cat, unit, higher_is_better = get_metric_info(m)
        if cat not in metrics_by_cat:
            metrics_by_cat[cat] = []
        metrics_by_cat[cat].append((m, disp_name, unit, higher_is_better))

    # 3. Zbuduj wiersze tabeli
    tbody_html = ""
    
    for cat_name, metrics_list in metrics_by_cat.items():
        # Wiersz nagłówkowy kategorii
        n_cols = len(all_cols_meta)
        tbody_html += f"""
        <tr class="category-row">
            <td colspan="{n_cols}">{cat_name.upper()}</td>
        </tr>
        """
        
        for raw_col, disp_name, unit, higher_is_better in metrics_list:
            tbody_html += "<tr>\n"
            # Kolumna 0: Nazwa metryki
            tbody_html += f'    <td class="metric-col"><strong>{disp_name}</strong></td>\n'
            
            # Pobierz wartości liczbowe graczy, aby wyznaczyć Top 1 / Top 3
            player_num_vals = []
            for p in player_columns:
                p_data = p['data']
                val = p_data.get(raw_col, np.nan) if isinstance(p_data, dict) else (p_data[raw_col] if raw_col in p_data else np.nan)
                try:
                    num_v = float(val) if pd.notna(val) else np.nan
                except (ValueError, TypeError):
                    num_v = np.nan
                player_num_vals.append(num_v)

            # Wyznacz najlepsze wartości (Top 1 / Top 3)
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

            # Renderuj komórki zawodników
            for idx, p in enumerate(player_columns):
                val_num = player_num_vals[idx]
                val_str = format_metric_value(val_num, unit)
                
                cell_class = ""
                badge_class = ""
                
                if highlight_mode != 'none' and not np.isnan(val_num):
                    if val_num == best_val and len(player_columns) > 1:
                        badge_class = "badge-top1"
                    elif highlight_mode == 'top3' and val_num in top3_vals and len(player_columns) > 2:
                        badge_class = "badge-top3"

                delta_html = ""
                if show_deltas and idx != reference_player_idx and len(player_columns) > 1:
                    ref_val = player_num_vals[reference_player_idx]
                    if not np.isnan(val_num) and not np.isnan(ref_val):
                        d_str = format_delta(val_num, ref_val, unit)
                        d_cls = "delta-pos" if (val_num > ref_val if higher_is_better else val_num < ref_val) else "delta-neg"
                        delta_html = f'<div class="{d_cls}">{d_str}</div>'

                if badge_class:
                    content = f'<span class="{badge_class}">{val_str}</span>{delta_html}'
                else:
                    content = f'<span>{val_str}</span>{delta_html}'
                    
                tbody_html += f'    <td class="player-cell">{content}</td>\n'

            # Renderuj komórki benchmarków (żółte tło)
            for b in benchmark_columns:
                b_data = b['data']
                val = b_data.get(raw_col, np.nan) if isinstance(b_data, dict) else (b_data[raw_col] if raw_col in b_data else np.nan)
                val_str = format_metric_value(val, unit)
                
                delta_bench_html = ""
                if show_deltas and len(player_columns) > 0:
                    ref_p_val = player_num_vals[reference_player_idx]
                    try:
                        b_num = float(val) if pd.notna(val) else np.nan
                        if not np.isnan(ref_p_val) and not np.isnan(b_num):
                            d_str = format_delta(ref_p_val, b_num, unit)
                            d_cls = "delta-pos" if (ref_p_val > b_num if higher_is_better else ref_p_val < b_num) else "delta-neg"
                            delta_bench_html = f'<div class="{d_cls}">vs {player_columns[reference_player_idx]["name"].split()[-1]}: {d_str}</div>'
                    except Exception:
                        pass

                tbody_html += f'    <td class="benchmark-cell"><strong>{val_str}</strong>{delta_bench_html}</td>\n'

            tbody_html += "</tr>\n"

    # 4. Zbuduj nagłówki <th>
    thead_html = "<tr>\n"
    for col in all_cols_meta:
        if col['type'] == 'metric':
            thead_html += f'    <th class="th-metric">{col["title"]}</th>\n'
        elif col['type'] == 'player':
            sub_text = f'<div class="th-sub">{col["sub"]}</div>' if col['sub'] else ''
            thead_html += f'    <th class="th-player">{col["title"]}{sub_text}</th>\n'
        elif col['type'] == 'benchmark':
            sub_text = f'<div class="th-sub-yellow">{col["sub"]}</div>' if col['sub'] else ''
            thead_html += f'    <th class="th-benchmark">{col["title"]}{sub_text}</th>\n'
    thead_html += "</tr>\n"

    # 5. Pełny kod HTML ze stylami zgodnymi z TABELA_WIZ
    full_html = f"""
    <div class="table-wiz-wrapper">
        <div class="table-wiz-card">
            <div class="table-wiz-header">
                <h2 class="table-wiz-title">{title}</h2>
                <p class="table-wiz-subtitle">{subtitle}</p>
            </div>
            <div class="table-wiz-scroll">
                <table class="table-wiz-table">
                    <thead>
                        {thead_html}
                    </thead>
                    <tbody>
                        {tbody_html}
                    </tbody>
                </table>
            </div>
            <div class="table-wiz-legend">
                <span class="legend-item"><span class="legend-box legend-top1"></span> <strong>Najlepszy wynik w grupie</strong></span>
                <span class="legend-item"><span class="legend-box legend-yellow"></span> <strong>Średnie odniesienia (Benchmarki)</strong></span>
            </div>
        </div>
    </div>

    <style>
        .table-wiz-wrapper {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            margin: 16px 0;
            width: 100%;
            box-sizing: border-box;
        }}
        .table-wiz-card {{
            background: #FFFFFF;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            border: 1px solid #E2E8F0;
            overflow: hidden;
        }}
        .table-wiz-header {{
            background-color: #1E293B;
            color: #FFFFFF;
            padding: 20px 24px;
        }}
        .table-wiz-title {{
            font-size: 18px;
            font-weight: 700;
            margin: 0;
            letter-spacing: 0.2px;
            color: #FFFFFF;
        }}
        .table-wiz-subtitle {{
            font-size: 12.5px;
            color: #94A3B8;
            margin: 6px 0 0 0;
        }}
        .table-wiz-scroll {{
            overflow-x: auto;
            width: 100%;
        }}
        .table-wiz-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
            color: #111827;
            border: none;
            table-layout: auto;
        }}
        .table-wiz-table th {{
            padding: 12px 16px;
            font-size: 12px;
            letter-spacing: 0.3px;
            border: none;
            vertical-align: middle;
        }}
        .th-metric {{
            background-color: #0F172A;
            color: #FFFFFF;
            font-weight: 700;
            text-align: left;
            min-width: 200px;
        }}
        .th-player {{
            background-color: #0F172A;
            color: #FFFFFF;
            font-weight: 700;
            text-align: center;
            min-width: 140px;
        }}
        .th-sub {{
            font-size: 10.5px;
            color: #94A3B8;
            font-weight: 400;
            margin-top: 3px;
            line-height: 1.2;
        }}
        .th-benchmark {{
            background-color: #EAB308;
            color: #0F172A;
            font-weight: 700;
            text-align: center;
            min-width: 140px;
        }}
        .th-sub-yellow {{
            font-size: 10.5px;
            color: #713F12;
            font-weight: 500;
            margin-top: 3px;
            line-height: 1.2;
        }}
        .category-row td {{
            background-color: #F1F5F9;
            color: #334155;
            font-weight: 700;
            font-size: 11.5px;
            letter-spacing: 0.5px;
            padding: 9px 16px;
            border-top: 1px solid #CBD5E1;
            border-bottom: 1px solid #CBD5E1;
            border-left: none;
            border-right: none;
            text-align: left !important;
        }}
        .table-wiz-table tbody tr:nth-child(even) {{
            background-color: #F8FAFC;
        }}
        .table-wiz-table td {{
            padding: 10px 16px;
            border-bottom: 1px solid #E2E8F0;
            border-left: none;
            border-right: none;
            vertical-align: middle;
        }}
        .metric-col {{
            text-align: left;
            color: #1E293B;
        }}
        .player-cell {{
            text-align: center;
            color: #0F172A;
        }}
        .benchmark-cell {{
            background-color: #FEF08A !important;
            color: #0F172A;
            text-align: center;
            font-weight: 700;
        }}
        .badge-top1 {{
            background-color: #BBF7D0;
            color: #15803D;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 4px;
            display: inline-block;
        }}
        .badge-top3 {{
            background-color: #DCFCE7;
            color: #15803D;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 4px;
            display: inline-block;
        }}
        .delta-pos {{
            font-size: 11px;
            font-weight: 700;
            color: #15803D;
            margin-top: 2px;
        }}
        .delta-neg {{
            font-size: 11px;
            font-weight: 700;
            color: #B91C1C;
            margin-top: 2px;
        }}
        .table-wiz-legend {{
            padding: 12px 20px;
            background: #FAFAFA;
            border-top: 1px solid #E2E8F0;
            font-size: 12px;
            color: #475569;
            display: flex;
            gap: 24px;
            align-items: center;
        }}
        .legend-item {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .legend-box {{
            width: 14px;
            height: 14px;
            border-radius: 3px;
            display: inline-block;
        }}
        .legend-top1 {{
            background-color: #BBF7D0;
            border: 1px solid #86EFAC;
        }}
        .legend-yellow {{
            background-color: #FEF08A;
            border: 1px solid #FDE047;
        }}
    </style>
    """
    return full_html
