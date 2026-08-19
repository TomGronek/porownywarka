"""
Moduł wczytywania, normalizacji i filtrowania danych piłkarskich.
Obsługuje wszystkie 24 arkusze Excel oraz dynamiczne wgrywanie nowych plików.
"""

import os
import glob
import pandas as pd
import numpy as np
import streamlit as st

POS_FILE_MAP = {
    'pozycja 2,3.xlsx': ('Boczny obrońca / Wahadłowy', '2, 3'),
    'pozycja 4,5.xlsx': ('Środkowy obrońca', '4, 5'),
    'pozycja 6.xlsx': ('Defensywny pomocnik', '6'),
    'pozycja 8.xlsx': ('Środkowy pomocnik', '8'),
    'pozycja 10.xlsx': ('Ofensywny pomocnik / Skrzydłowy', '10'),
    'pozycja 9.xlsx': ('Środkowy napastnik', '9'),
    '1 liga - centralny.xlsx': ('Środkowy obrońca', '4, 5'),
    '1 liga - skrajny.xlsx': ('Boczny obrońca / Wahadłowy', '2, 3'),
    '2 liga - centralny.xlsx': ('Środkowy obrońca', '4, 5'),
    '2 liga - skrajny.xlsx': ('Boczny obrońca / Wahadłowy', '2, 3'),
    'zalewski.xlsx': ('Boczny obrońca / Skrzydłowy', 'Inne'),
    'zagranica.xlsx': ('Środkowy obrońca', '4, 5'),
}

@st.cache_data(show_spinner=False)
def load_all_datasets(data_dir='data'):
    """
    Wczytuje i integruje wszystkie pliki Excel z bazy.
    Zwraca ujednolicony DataFrame z oznaczeniami lig i pozycji.
    """
    all_dfs = []
    
    # 1. Przeszukaj podkatalogi ligowe (ESA, 1 liga, 2 liga)
    leagues_dirs = [
        ('ESA', 'Ekstraklasa'),
        ('1 liga', '1 Liga'),
        ('2 liga', '2 Liga')
    ]
    
    for folder_name, league_display in leagues_dirs:
        folder_path = os.path.join(data_dir, folder_name)
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                    file_path = os.path.join(folder_path, file_name)
                    try:
                        df = pd.read_excel(file_path)
                        pos_group, pos_code = POS_FILE_MAP.get(file_name, ('Inna pozycja', 'Inne'))
                        df['League'] = league_display
                        df['Position_Group'] = pos_group
                        df['Position_Code'] = pos_code
                        df['Source_File'] = f"{folder_name}/{file_name}"
                        all_dfs.append(df)
                    except Exception as e:
                        print(f"Błąd odczytu {file_path}: {e}")

    # 2. Przeszukaj pliki w katalogu data bezpośrednio
    if os.path.exists(data_dir):
        for file_name in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file_name)
            if os.path.isfile(file_path) and (file_name.endswith('.xlsx') or file_name.endswith('.xls')):
                league = '1 Liga' if '1 liga' in file_name else ('2 Liga' if '2 liga' in file_name else 'Inna Liga')
                pos_group, pos_code = POS_FILE_MAP.get(file_name, ('Inna pozycja', 'Inne'))
                try:
                    df = pd.read_excel(file_path)
                    df['League'] = league
                    df['Position_Group'] = pos_group
                    df['Position_Code'] = pos_code
                    df['Source_File'] = file_name
                    all_dfs.append(df)
                except Exception as e:
                    print(f"Błąd odczytu {file_path}: {e}")

    # 3. Sprawdź plik zagranica.xlsx w katalogu głównym
    if os.path.exists('zagranica.xlsx'):
        try:
            df = pd.read_excel('zagranica.xlsx')
            df['League'] = 'Zagranica'
            df['Position_Group'] = 'Środkowy obrońca'
            df['Position_Code'] = '4, 5'
            df['Source_File'] = 'zagranica.xlsx'
            all_dfs.append(df)
        except Exception as e:
            print(f"Błąd odczytu zagranica.xlsx: {e}")

    if not all_dfs:
        return pd.DataFrame()

    master_df = pd.concat(all_dfs, ignore_index=True)
    
    # Czyszczenie i standaryzacja
    master_df['Player'] = master_df['Player'].astype(str).str.strip()
    if 'Team' in master_df.columns:
        master_df['Team'] = master_df['Team'].fillna('-').astype(str).str.strip()
    else:
        master_df['Team'] = '-'
        
    if 'Position' in master_df.columns:
        master_df['Position'] = master_df['Position'].fillna('-').astype(str).str.strip()
        
    # Konwersja kolumn numerycznych
    num_candidate_cols = master_df.columns.drop(['Player', 'Team', 'Position', 'League', 'Position_Group', 'Position_Code', 'Source_File'], errors='ignore')
    for col in num_candidate_cols:
        if master_df[col].dtype == 'object':
            # Zamień przecinki na kropki jeśli występują stringi liczbowe
            try:
                master_df[col] = pd.to_numeric(master_df[col].astype(str).str.replace(',', '.').str.replace('%', '').str.strip(), errors='coerce')
            except Exception:
                pass

    # Usuń ewentualne puste wiersze
    master_df = master_df[master_df['Player'].notna() & (master_df['Player'] != '') & (master_df['Player'] != 'nan')]
    
    # Tworzenie etykiety unikalnej wyświetlanej dla każdego wiersza
    master_df['Player_Display'] = master_df.apply(
        lambda r: f"{r['Player']} ({r['Team']} | {r['League']} | {r['Position_Group']})", axis=1
    )
    
    return master_df


def filter_players_df(df, leagues=None, positions=None, teams=None, min_minutes=0, min_age=None, max_age=None, search_text=None):
    """Filtruje zbiór danych na podstawie przekazanych kryteriów."""
    if df.empty:
        return df

    filtered = df.copy()

    if leagues:
        filtered = filtered[filtered['League'].isin(leagues)]

    if positions:
        filtered = filtered[filtered['Position_Group'].isin(positions)]

    if teams:
        filtered = filtered[filtered['Team'].isin(teams)]

    if min_minutes and 'Minutes played' in filtered.columns:
        filtered = filtered[filtered['Minutes played'].fillna(0) >= min_minutes]

    if min_age is not None and 'Age' in filtered.columns:
        filtered = filtered[filtered['Age'].fillna(99) >= min_age]

    if max_age is not None and 'Age' in filtered.columns:
        filtered = filtered[filtered['Age'].fillna(0) <= max_age]

    if search_text:
        query = search_text.strip().lower()
        filtered = filtered[
            filtered['Player'].str.lower().str.contains(query, na=False) |
            filtered['Team'].str.lower().str.contains(query, na=False) |
            filtered['Position'].str.lower().str.contains(query, na=False)
        ]

    return filtered


def get_unique_players_summary(df):
    """Zwraca unikalną listę zawodników z metadanymi."""
    if df.empty:
        return []
    
    return df[['Player', 'Team', 'League', 'Position_Group', 'Position', 'Age', 'Minutes played', 'Player_Display']].to_dict('records')


def calculate_benchmark_average(df, condition_func=None, label="Średnia grupy"):
    """
    Oblicza średnią arytmetyczną numerycznych metryk dla wybranego podzbioru.
    Zwraca Series z wartościami średnimi i przypisaną etykietą.
    """
    if condition_func:
        subset = condition_func(df)
    else:
        subset = df

    if subset.empty:
        return None

    numeric_cols = subset.select_dtypes(include=[np.number]).columns
    avg_series = subset[numeric_cols].mean()
    avg_series.name = label
    return avg_series
