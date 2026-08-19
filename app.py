"""
Aplikacja Streamlit: Piłkarska Platforma Analityczna & Generator Tabel Porównawczych
Zgodna ze standardem TABELA_WIZ.md (czyste tabele, brak ramek, zielone akcenty, żółte benchmarki).
"""

import streamlit as st
import pandas as pd
import numpy as np
import io

from src.metrics_config import METRICS_DICT, POSITION_PRESETS, get_metric_info, format_metric_value
from src.data_loader import load_all_datasets, filter_players_df, get_unique_players_summary, calculate_benchmark_average
from src.table_renderer import generate_comparison_table_html
from src.image_generator import generate_table_png_bytes
from src.components import inject_custom_css, render_metric_selector
from src.auth import check_password, render_auth_sidebar

# Konfiguracja strony Streamlit
st.set_page_config(
    page_title="Football Data Analytics & Table Builder",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

# Weryfikacja hasła dostępu
if not check_password():
    st.stop()

# Pasek boczny ze statusem i wylogowaniem
render_auth_sidebar()

# Wczytanie bazy danych
master_df = load_all_datasets()

# Nagłówek główny
st.markdown("""
<div class="main-header">
    <h1>⚽ Football Analytics & Comparison Studio</h1>
    <p>Interaktywne narzędzie do porównywania zawodników, analizy grupowej i generowania publikacyjnych tabel statystycznych (Light Theme / 300 DPI)</p>
</div>
""", unsafe_allow_html=True)

if master_df.empty:
    st.error("Nie znaleziono żadnych plików danych w folderze `data/` ani w katalogu głównym!")
    st.stop()

# Zakładki główne
tab_compare, tab_overview, tab_player, tab_data = st.tabs([
    "📊 Kreator Zestawień Porównawczych",
    "👥 Zestawienie Zbiorcze & Ranking",
    "🔍 Profil i Analiza Zawodnika",
    "📁 Baza Danych & Wgrywanie Plików"
])


# ==============================================================================
# TAB 1: KREATOR ZESTAWIEŃ PORÓWNAWCZYCH
# ==============================================================================
with tab_compare:
    st.markdown("### 📊 Kreator Tabeli Porównawczej")
    st.caption("Stwórz zestawienie dowolnych zawodników z wyróżnionymi średnimi ligowymi i wiekowymi (żółte kolumny) oraz zielonymi akcentami dla najlepszych wartości.")

    col_setup_left, col_setup_right = st.columns([1, 1], gap="large")

    with col_setup_left:
        st.markdown("##### 1. 👥 Wybór Zawodników do Porównania")
        
        # Filtry pomocnicze do zawężenia listy zawodników
        with st.expander("🔍 Filtry pomocnicze listy zawodników", expanded=False):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                available_leagues = sorted(list(master_df['League'].unique()))
                filter_l = st.multiselect("Filtruj po lidze:", available_leagues, default=available_leagues, key="comp_f_league")
            with f_col2:
                available_positions = sorted(list(master_df['Position_Group'].unique()))
                filter_p = st.multiselect("Filtruj po pozycji:", available_positions, default=available_positions, key="comp_f_pos")

        filtered_player_pool = filter_players_df(master_df, leagues=filter_l, positions=filter_p)
        
        # Domyślny zestaw zawodników (np. 3 zawodników z pozycji 10 lub obrońców)
        player_options = filtered_player_pool['Player_Display'].tolist()
        
        # Znajdź przykładowych zawodników do domyślnego wyboru
        default_selection = []
        for default_name in ['Kucharski', 'Wołczek', 'Kusztal']:
            matched = [p for p in player_options if default_name.lower() in p.lower()]
            if matched and matched[0] not in default_selection:
                default_selection.append(matched[0])
                
        if len(default_selection) < 3 and len(player_options) >= 3:
            default_selection = player_options[:3]

        selected_player_displays = st.multiselect(
            "Wybierz zawodników (możesz wpisać nazwisko lub klub w polu):",
            options=player_options,
            default=default_selection,
            key="comp_selected_players",
            help="Wpisz nazwisko, klub lub pozycję, aby wyszukać i dodać piłkarza do porównania."
        )

        if not selected_player_displays:
            st.info("👆 Wybierz co najmniej 1 zawodnika powyżej, aby wygenerować tabelę.")

    with col_setup_right:
        st.markdown("##### 2. 🟡 Konfiguracja Średnich i Odniesień (Żółte Kolumny)")
        
        # Benchmark 1: Średnia Ligi
        enable_league_bench = st.checkbox("Dodaj Średnią Ligi", value=True, key="bench_l_enable")
        bench_league_data = None
        bench_league_title = "Średnia 1 Liga"
        bench_league_sub = ""
        
        if enable_league_bench:
            b1_col1, b1_col2 = st.columns(2)
            with b1_col1:
                chosen_bench_league = st.selectbox("Wybierz ligę odniesienia:", available_leagues, index=0 if '1 Liga' not in available_leagues else available_leagues.index('1 Liga'), key="bench_l_choice")
            with b1_col2:
                bench_pos_filter = st.selectbox("Dla pozycji:", ["Wszystkie pozycje"] + available_positions, index=0, key="bench_l_pos")
                
            pos_crit = None if bench_pos_filter == "Wszystkie pozycje" else [bench_pos_filter]
            subset_league = filter_players_df(master_df, leagues=[chosen_bench_league], positions=pos_crit)
            bench_league_data = calculate_benchmark_average(subset_league)
            bench_league_title = f"Średnia {chosen_bench_league}"
            bench_league_sub = f"({bench_pos_filter})" if bench_pos_filter != "Wszystkie pozycje" else f"({len(subset_league)} zaw.)"

        # Benchmark 2: Średnia Wiekowa
        enable_age_bench = st.checkbox("Dodaj Średnią Wiekową (np. U21 / U17 / ur. 2008+)", value=True, key="bench_age_enable")
        bench_age_data = None
        bench_age_title = "Średnia U21"
        bench_age_sub = ""
        
        if enable_age_bench:
            b2_col1, b2_col2 = st.columns(2)
            with b2_col1:
                age_mode = st.selectbox("Kryterium wieku:", ["Maksymalny wiek (U-X)", "Rocznik (np. 2008+)", "Dowolny przedział wieku"], key="bench_age_mode")
            with b2_col2:
                if age_mode == "Maksymalny wiek (U-X)":
                    max_age_val = st.number_input("Maksymalny wiek (np. 21, 19, 17):", min_value=15, max_value=35, value=21, step=1, key="bench_u_age")
                    subset_age = master_df[master_df['Age'].fillna(99) <= max_age_val]
                    bench_age_title = f"Średnia U{max_age_val}"
                    bench_age_sub = f"(wiek ≤ {max_age_val}, {len(subset_age)} zaw.)"
                elif age_mode == "Rocznik (np. 2008+)":
                    birth_year = st.number_input("Rocznik (od danego roku w górę):", min_value=1980, max_value=2012, value=2008, step=1, key="bench_birth_year")
                    # 2026 - birth_year = max age
                    calc_max_age = 2026 - birth_year
                    subset_age = master_df[master_df['Age'].fillna(99) <= calc_max_age]
                    bench_age_title = f"Średnia ur. {birth_year}+"
                    bench_age_sub = f"({len(subset_age)} piłkarzy)"
                else:
                    age_range = st.slider("Przedział wieku:", min_value=15, max_value=40, value=(17, 21), key="bench_age_slider")
                    subset_age = master_df[(master_df['Age'].fillna(99) >= age_range[0]) & (master_df['Age'].fillna(0) <= age_range[1])]
                    bench_age_title = f"Średnia wiek {age_range[0]}-{age_range[1]}"
                    bench_age_sub = f"({len(subset_age)} zaw.)"
                    
            bench_age_data = calculate_benchmark_average(subset_age)

        # Benchmark 3: Średnia Klubu / Własna grupa (opcjonalnie)
        enable_club_bench = st.checkbox("Dodaj Średnią Klubu (opcjonalnie)", value=False, key="bench_club_enable")
        bench_club_data = None
        bench_club_title = "Średnia Klubu"
        bench_club_sub = ""
        
        if enable_club_bench:
            all_teams = sorted([t for t in master_df['Team'].unique() if t and t != '-'])
            chosen_team = st.selectbox("Wybierz klub:", all_teams, key="bench_club_choice")
            subset_club = master_df[master_df['Team'] == chosen_team]
            bench_club_data = calculate_benchmark_average(subset_club)
            bench_club_title = f"Średnia {chosen_team}"
            bench_club_sub = f"({len(subset_club)} zaw.)"

    st.markdown("---")

    # 3. Wybór Metryk
    selected_metrics = render_metric_selector(default_preset="Ofensywny Pomocnik / Skrzydłowy (10/7/11 - 6 metryk)", key_prefix="main_comp")

    # 4. Opcje Wyświetlania i Tytułu
    with st.expander("📝 Ustawienia Tytułu i Wyglądu Tabeli", expanded=False):
        c_title, c_sub = st.columns([1, 1])
        with c_title:
            default_t = "ZESTAWIENIE PORÓWNAWCZE ZAWODNIKÓW"
            user_title = st.text_input("Tytuł główny tabeli:", value=default_t, key="user_title_comp")
        with c_sub:
            default_s = "Porównanie surowych danych statystycznych vs średnie odniesienia ligowe i wiekowe"
            user_subtitle = st.text_input("Podtytuł tabeli:", value=default_s, key="user_sub_comp")
            
        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            hl_mode = st.radio("Wyróżnienie najlepszych wartości (Zielony kolor):", ["top1", "top3", "none"], format_func=lambda x: "Tylko najlepsza wartość (Top 1)" if x == "top1" else ("Top 3 wartości" if x == "top3" else "Brak wyróżnień"), horizontal=True)
        with c_opt2:
            show_deltas_opt = st.checkbox("Pokaż delty / różnice względem 1. zawodnika", value=False)

    # 5. Przygotowanie danych do wygenerowania tabeli
    if selected_player_displays and selected_metrics:
        player_cols_payload = []
        for p_disp in selected_player_displays:
            row = master_df[master_df['Player_Display'] == p_disp].iloc[0]
            player_cols_payload.append({
                'name': row['Player'],
                'club': row['Team'],
                'age': str(int(row['Age'])) if pd.notna(row.get('Age')) else '-',
                'data': row
            })

        bench_cols_payload = []
        if enable_league_bench and bench_league_data is not None:
            bench_cols_payload.append({
                'name': bench_league_title,
                'subtitle': bench_league_sub,
                'data': bench_league_data
            })
            
        if enable_age_bench and bench_age_data is not None:
            bench_cols_payload.append({
                'name': bench_age_title,
                'subtitle': bench_age_sub,
                'data': bench_age_data
            })
            
        if enable_club_bench and bench_club_data is not None:
            bench_cols_payload.append({
                'name': bench_club_title,
                'subtitle': bench_club_sub,
                'data': bench_club_data
            })

        # Generowanie HTML tabeli
        table_html = generate_comparison_table_html(
            title=user_title,
            subtitle=user_subtitle,
            player_columns=player_cols_payload,
            benchmark_columns=bench_cols_payload,
            selected_metrics=selected_metrics,
            highlight_mode=hl_mode,
            show_deltas=show_deltas_opt,
            reference_player_idx=0
        )

        st.markdown("---")
        st.markdown("#### 📋 Wygenerowana Tabela Statystyczna")
        
        # Wyświetlenie interaktywnej tabeli HTML
        st.components.v1.html(table_html, height=180 + len(selected_metrics) * 45 + 120, scrolling=True)

        # Przyciski Pobierania
        d_col1, d_col2, d_col3 = st.columns([1, 1, 2])
        
        with d_col1:
            # Generowanie PNG 300 DPI
            with st.spinner("Generowanie grafiki PNG (300 DPI)..."):
                png_bytes = generate_table_png_bytes(
                    title=user_title,
                    subtitle=user_subtitle,
                    player_columns=player_cols_payload,
                    benchmark_columns=bench_cols_payload,
                    selected_metrics=selected_metrics,
                    highlight_mode=hl_mode,
                    dpi=300
                )
                
            st.download_button(
                label="📥 Pobierz Grafikę PNG (300 DPI)",
                data=png_bytes,
                file_name="tabela_porownawcza.png",
                mime="image/png",
                use_container_width=True
            )
            
        with d_col2:
            st.download_button(
                label="🌐 Pobierz Kod HTML Tabeli",
                data=table_html,
                file_name="tabela_porownawcza.html",
                mime="text/html",
                use_container_width=True
            )
            
        with d_col3:
            # Eksport CSV / Excel
            export_rows = []
            for m in selected_metrics:
                disp_n, cat_n, unit_n, _ = get_metric_info(m)
                r_dict = {'Kategoria': cat_n, 'Metryka': disp_n}
                for p in player_cols_payload:
                    r_dict[f"{p['name']} ({p['club']})"] = p['data'].get(m, np.nan)
                for b in bench_cols_payload:
                    r_dict[b['name']] = b['data'].get(m, np.nan)
                export_rows.append(r_dict)
                
            df_export = pd.DataFrame(export_rows)
            csv_data = df_export.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📊 Pobierz Dane (CSV/Excel)",
                data=csv_data,
                file_name="dane_porownawcze.csv",
                mime="text/csv",
                use_container_width=True
            )


# ==============================================================================
# TAB 2: ZESTAWIENIE ZBIORCZE & RANKING
# ==============================================================================
with tab_overview:
    st.markdown("### 👥 Zestawienie Zbiorcze i Ranking Zawodników")
    st.caption("Przegląd wielu zawodników z automatycznym zielonym wyróżnieniem Top 3 odchyleń w każdej statystyce.")

    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    with r_col1:
        rank_leagues = st.multiselect("Wybierz ligi:", available_leagues, default=available_leagues[:1], key="rank_leagues")
    with r_col2:
        rank_positions = st.multiselect("Wybierz pozycje:", available_positions, default=available_positions[:1], key="rank_positions")
    with r_col3:
        rank_min_min = st.number_input("Minimalna liczba minut:", min_value=0, max_value=3500, value=500, step=100, key="rank_min_min")
    with r_col4:
        rank_max_players = st.slider("Maksymalna liczba zawodników:", min_value=5, max_value=50, value=15, key="rank_max_p")

    # Wybór metryk dla rankingu
    rank_metrics = render_metric_selector(default_preset="Środkowy Obrońca (5 kluczowych)", key_prefix="rank_preset")

    # Filtruj graczy
    rank_df = filter_players_df(master_df, leagues=rank_leagues, positions=rank_positions, min_minutes=rank_min_min)
    
    if rank_df.empty:
        st.warning("Brak zawodników spełniających podane kryteria filtrów.")
    else:
        st.info(f"Znaleziono **{len(rank_df)}** zawodników. Wyświetlam czołowych {min(rank_max_players, len(rank_df))}.")
        
        sample_df = rank_df.head(rank_max_players)
        
        # Przygotuj payload
        rank_player_payload = []
        for _, row in sample_df.iterrows():
            rank_player_payload.append({
                'name': row['Player'],
                'club': row['Team'],
                'age': str(int(row['Age'])) if pd.notna(row.get('Age')) else '-',
                'data': row
            })

        # Średnia grupy
        group_avg = calculate_benchmark_average(rank_df)
        rank_bench_payload = [{
            'name': 'Średnia Wybranej Grupy',
            'subtitle': f'({len(rank_df)} zawodników)',
            'data': group_avg
        }]

        rank_html = generate_comparison_table_html(
            title=f"ZESTAWIENIE ZBIORCZE — {', '.join(rank_positions)}",
            subtitle=f"Wyróżnienie Top wyników w grupie {len(sample_df)} zawodników (min. {rank_min_min} min)",
            player_columns=rank_player_payload,
            benchmark_columns=rank_bench_payload,
            selected_metrics=rank_metrics,
            highlight_mode='top3',
            show_deltas=False
        )

        st.components.v1.html(rank_html, height=180 + len(rank_metrics) * 45 + 120, scrolling=True)
        
        # Przycisk pobrania grafiki PNG dla zestawienia zbiorczego
        png_rank_bytes = generate_table_png_bytes(
            title=f"ZESTAWIENIE ZBIORCZE — {', '.join(rank_positions)}",
            subtitle=f"Wyróżnienie Top 3 wyników (min. {rank_min_min} min)",
            player_columns=rank_player_payload,
            benchmark_columns=rank_bench_payload,
            selected_metrics=rank_metrics,
            highlight_mode='top3',
            dpi=300
        )
        
        st.download_button(
            label="📥 Pobierz Grafikę Zestawienia Zbiorczego (PNG 300 DPI)",
            data=png_rank_bytes,
            file_name="zestawienie_zbiorcze_top3.png",
            mime="image/png",
            use_container_width=True
        )


# ==============================================================================
# TAB 3: PROFIL I ANALIZA ZAWODNIKA
# ==============================================================================
with tab_player:
    st.markdown("### 🔍 Profil Indywidualny Zawodnika")
    st.caption("Szczegółowa karta zawodnika z porównaniem do średnich ligowych i percentyli.")

    scout_p_col1, scout_p_col2 = st.columns([2, 1])
    with scout_p_col1:
        scout_search = st.selectbox(
            "Wybierz zawodnika z bazy:",
            options=master_df['Player_Display'].unique(),
            key="scout_player_select"
        )
        
    p_record = master_df[master_df['Player_Display'] == scout_search].iloc[0]
    
    # Metadane zawodnika
    meta_c1, meta_c2, meta_c3, meta_c4, meta_c5 = st.columns(5)
    with meta_c1:
        st.metric("Klub", p_record.get('Team', '-'))
    with meta_c2:
        st.metric("Liga", p_record.get('League', '-'))
    with meta_c3:
        st.metric("Pozycja", p_record.get('Position', '-'))
    with meta_c4:
        st.metric("Wiek", int(p_record.get('Age')) if pd.notna(p_record.get('Age')) else '-')
    with meta_c5:
        st.metric("Rozegrane Minuty", int(p_record.get('Minutes played')) if pd.notna(p_record.get('Minutes played')) else '-')

    st.markdown("---")
    
    # Wybór metryk do karty
    scout_metrics = render_metric_selector(default_preset="Uniwersalny Zestaw 5 Metryk", key_prefix="scout_preset")
    
    # Średnia ligi dla tej pozycji
    league_peers = master_df[(master_df['League'] == p_record['League']) & (master_df['Position_Group'] == p_record['Position_Group'])]
    peer_avg = calculate_benchmark_average(league_peers)
    
    scout_player_payload = [{
        'name': p_record['Player'],
        'club': p_record['Team'],
        'age': str(int(p_record['Age'])) if pd.notna(p_record.get('Age')) else '-',
        'data': p_record
    }]
    
    scout_bench_payload = [{
        'name': f"Średnia {p_record['League']}",
        'subtitle': f"({p_record['Position_Group']})",
        'data': peer_avg
    }]
    
    scout_html = generate_comparison_table_html(
        title=f"PROFIL ZAWODNIKA: {p_record['Player'].upper()}",
        subtitle=f"{p_record['Team']} | {p_record['League']} | {p_record['Position_Group']} vs Średnia Pozycyjna",
        player_columns=scout_player_payload,
        benchmark_columns=scout_bench_payload,
        selected_metrics=scout_metrics,
        highlight_mode='none',
        show_deltas=True
    )
    
    st.components.v1.html(scout_html, height=180 + len(scout_metrics) * 45 + 120, scrolling=True)


# ==============================================================================
# TAB 4: BAZA DANYCH & WGRYWANIE PLIKÓW
# ==============================================================================
with tab_data:
    st.markdown("### 📁 Baza Danych i Wgrywanie Nowych Arkuszy")
    st.caption("Podgląd wszystkich załadowanych plików oraz możliwość wgrania dodatkowych raportów Excel / CSV.")

    st.markdown("##### 1. 📊 Statystyki Aktywnej Bazy")
    d_stat1, d_stat2, d_stat3, d_stat4 = st.columns(4)
    with d_stat1:
        st.metric("Łączna Liczba Wierszy", len(master_df))
    with d_stat2:
        st.metric("Unikalni Zawodnicy", master_df['Player'].nunique())
    with d_stat3:
        st.metric("Dostępne Ligi", master_df['League'].nunique())
    with d_stat4:
        st.metric("Kluby", master_df['Team'].nunique())

    st.markdown("---")
    
    st.markdown("##### 2. 📤 Wgraj Nowy Plik Raportu (Wyscout / Excel / CSV)")
    upload_col1, upload_col2, upload_col3 = st.columns([2, 1, 1])
    
    with upload_col1:
        uploaded_file = st.file_uploader("Wybierz plik .xlsx lub .csv:", type=['xlsx', 'xls', 'csv'])
    with upload_col2:
        up_league = st.selectbox("Przypisz do ligi:", ["Ekstraklasa", "1 Liga", "2 Liga", "Zagranica", "Inna Liga"])
    with upload_col3:
        up_pos = st.selectbox("Przypisz do grupy pozycji:", [
            "Środkowy obrońca",
            "Boczny obrońca / Wahadłowy",
            "Defensywny pomocnik",
            "Środkowy pomocnik",
            "Ofensywny pomocnik / Skrzydłowy",
            "Środkowy napastnik",
            "Inna pozycja"
        ])
        
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                new_df = pd.read_csv(uploaded_file)
            else:
                new_df = pd.read_excel(uploaded_file)
                
            st.success(f"Pomyślnie odczytano plik: **{uploaded_file.name}** ({len(new_df)} wierszy, {len(new_df.columns)} kolumn).")
            st.dataframe(new_df.head(5))
        except Exception as e:
            st.error(f"Błąd odczytu pliku: {e}")

    st.markdown("---")
    st.markdown("##### 3. 📑 Tabela Przeglądowa Bazy")
    st.dataframe(
        master_df[['Player', 'Team', 'League', 'Position_Group', 'Position', 'Age', 'Matches played', 'Minutes played', 'Source_File']],
        use_container_width=True,
        height=400
    )
