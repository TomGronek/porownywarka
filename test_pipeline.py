import os
import sys
import pandas as pd
import numpy as np

from src.data_loader import load_all_datasets, calculate_benchmark_average
from src.table_renderer import generate_comparison_table_html
from src.image_generator import generate_table_png_bytes
from src.metrics_config import POSITION_PRESETS

def test_full_pipeline():
    print("--- Test 1: Loading Datasets ---")
    df = load_all_datasets()
    print(f"Total rows loaded: {len(df)}")
    assert len(df) > 2000, "Expected > 2000 rows"

    print("--- Test 2: Extracting 3 Players ---")
    p1 = df[df['Player'].str.contains('Kucharski', na=False)].iloc[0]
    p2 = df[df['Player'].str.contains('Wołczek|Wolczek', na=False)].iloc[0]
    p3 = df[df['Player'].str.contains('Kusztal', na=False)].iloc[0]
    print("P1:", p1['Player'], f"({p1['Team']})")
    print("P2:", p2['Player'], f"({p2['Team']})")
    print("P3:", p3['Player'], f"({p3['Team']})")

    print("--- Test 3: Calculating Benchmarks (League + Age) ---")
    l1_df = df[df['League'] == '1 Liga']
    avg_1l = calculate_benchmark_average(l1_df)

    u17_df = df[df['Age'] <= 17]
    avg_u17 = calculate_benchmark_average(u17_df)

    players_payload = [
        {'name': p1['Player'], 'club': p1['Team'], 'age': '17', 'data': p1},
        {'name': p2['Player'], 'club': p2['Team'], 'age': '21', 'data': p2},
        {'name': p3['Player'], 'club': p3['Team'], 'age': '23', 'data': p3},
    ]
    bench_payload = [
        {'name': 'Średnia 1 Liga', 'subtitle': f'({len(l1_df)} zaw.)', 'data': avg_1l},
        {'name': 'Średnia U17', 'subtitle': f'({len(u17_df)} zaw.)', 'data': avg_u17},
    ]

    metrics = [
        'Successful attacking actions per 90',
        'Progressive runs per 90',
        'Dribbles per 90',
        'Accurate forward passes, %',
        'Defensive duels won, %'
    ]

    print("--- Test 4: Generating HTML Table ---")
    html_out = generate_comparison_table_html(
        title='ANALIZA PORÓWNAWCZA 3 ZAWODNIKÓW — 5 METRYK',
        subtitle='Kucharski vs Wołczek vs Kusztal na tle średniej 1. ligi oraz średniej U17',
        player_columns=players_payload,
        benchmark_columns=bench_payload,
        selected_metrics=metrics,
        highlight_mode='top1'
    )
    assert 'table-wiz-table' in html_out
    assert 'badge-top1' in html_out
    assert 'benchmark-cell' in html_out
    print(f"HTML generated successfully! Length: {len(html_out)} characters.")

    print("--- Test 5: Generating PNG 300 DPI ---")
    png_bytes = generate_table_png_bytes(
        title='ANALIZA PORÓWNAWCZA 3 ZAWODNIKÓW — 5 METRYK',
        subtitle='Kucharski vs Wołczek vs Kusztal na tle średniej 1. ligi oraz średniej U17',
        player_columns=players_payload,
        benchmark_columns=bench_payload,
        selected_metrics=metrics,
        highlight_mode='top1',
        dpi=300
    )
    assert len(png_bytes) > 10000
    print(f"PNG generated successfully! Size: {len(png_bytes)} bytes.")

    os.makedirs('output_visualizations', exist_ok=True)
    with open('output_visualizations/test_streamlit_output.png', 'wb') as f:
        f.write(png_bytes)
    print("Saved test image to output_visualizations/test_streamlit_output.png")
    print("ALL TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == '__main__':
    test_full_pipeline()
