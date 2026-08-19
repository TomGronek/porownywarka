"""
Słownik metryk statystycznych i konfiguracja pozycji piłkarskich.
Odwzorowuje standard TABELA_WIZ.md z polskimi nazwami, kategoriami i regułami formatowania.
"""

# Słownik: raw_col -> (display_name_pl, category_pl, unit, higher_is_better)
# unit: '%' (procent), 'per90' (wskaźnik na 90 min), 'count' (liczba całkowita), 'meters' (metry)
METRICS_DICT = {
    # --- GRA W DEFENSYWIE ---
    'Defensive duels per 90': ('Pojedynki w defensywie / 90', 'GRA W DEFENSYWIE', 'per90', True),
    'Defensive duels won, %': ('Wygrane pojedynki w defensywie', 'GRA W DEFENSYWIE', '%', True),
    'Successful defensive actions per 90': ('Udane akcje w defensywie / 90', 'GRA W DEFENSYWIE', 'per90', True),
    'Shots blocked per 90': ('Zablokowane strzały / 90', 'GRA W DEFENSYWIE', 'per90', True),
    'Interceptions per 90': ('Przejęcia / 90', 'GRA W DEFENSYWIE', 'per90', True),
    'PAdj Interceptions': ('Przejęcia (PAdj) / 90', 'GRA W DEFENSYWIE', 'per90', True),
    'Sliding tackles per 90': ('Wślizgi / 90', 'GRA W DEFENSYWIE', 'per90', True),
    'PAdj Sliding tackles': ('Wślizgi (PAdj) / 90', 'GRA W DEFENSYWIE', 'per90', True),
    'Fouls per 90': ('Faule / 90', 'GRA W DEFENSYWIE', 'per90', False),
    'Yellow cards per 90': ('Żółte kartki / 90', 'GRA W DEFENSYWIE', 'per90', False),
    'Red cards per 90': ('Czerwone kartki / 90', 'GRA W DEFENSYWIE', 'per90', False),

    # --- GRA W POWIETRZU ---
    'Aerial duels per 90': ('Pojedynki w powietrzu / 90', 'GRA W POWIETRZU', 'per90', True),
    'Aerial duels per 90.1': ('Pojedynki w powietrzu / 90', 'GRA W POWIETRZU', 'per90', True),
    'Aerial duels won, %': ('Wygrane pojedynki w powietrzu', 'GRA W POWIETRZU', '%', True),
    'Head goals': ('Gole głową', 'GRA W POWIETRZU', 'count', True),
    'Head goals per 90': ('Gole głową / 90', 'GRA W POWIETRZU', 'per90', True),

    # --- DYSTRYBUCJA I ROZGRYWANIE ---
    'Passes per 90': ('Podania ogółem / 90', 'DYSTRYBUCJA I ROZGRYWANIE', 'per90', True),
    'Accurate passes, %': ('Dokładność podań ogółem', 'DYSTRYBUCJA I ROZGRYWANIE', '%', True),
    'Forward passes per 90': ('Podania do przodu / 90', 'DYSTRYBUCJA I ROZGRYWANIE', 'per90', True),
    'Accurate forward passes, %': ('Dokładność podań do przodu', 'DYSTRYBUCJA I ROZGRYWANIE', '%', True),
    'Back passes per 90': ('Podania do tyłu / 90', 'DYSTRYBUCJA I ROZGRYWANIE', 'per90', False),
    'Accurate back passes, %': ('Dokładność podań do tyłu', 'DYSTRYBUCJA I ROZGRYWANIE', '%', True),
    'Lateral passes per 90': ('Podania boczne / 90', 'DYSTRYBUCJA I ROZGRYWANIE', 'per90', True),
    'Accurate lateral passes, %': ('Dokładność podań bocznych', 'DYSTRYBUCJA I ROZGRYWANIE', '%', True),
    'Short / medium passes per 90': ('Podania krótkie/średnie / 90', 'DYSTRYBUCJA I ROZGRYWANIE', 'per90', True),
    'Accurate short / medium passes, %': ('Dokładność podań krótkich/średnich', 'DYSTRYBUCJA I ROZGRYWANIE', '%', True),
    'Long passes per 90': ('Długie podania / 90', 'DYSTRYBUCJA I ROZGRYWANIE', 'per90', True),
    'Accurate long passes, %': ('Dokładność długich podań', 'DYSTRYBUCJA I ROZGRYWANIE', '%', True),
    'Average pass length, m': ('Średnia długość podania (m)', 'DYSTRYBUCJA I ROZGRYWANIE', 'meters', True),
    'Average long pass length, m': ('Średnia długość długiego podania (m)', 'DYSTRYBUCJA I ROZGRYWANIE', 'meters', True),
    'Received passes per 90': ('Przyjęte podania / 90', 'DYSTRYBUCJA I ROZGRYWANIE', 'per90', True),

    # --- KREACJA I PROGRESJA ---
    'Passes to final third per 90': ('Podania w 3. tercję / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Accurate passes to final third, %': ('Dokładność podań w 3. tercję', 'KREACJA I PROGRESJA', '%', True),
    'Passes to penalty area per 90': ('Podania w pole karne / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Accurate passes to penalty area, %': ('Dokładność podań w pole karne', 'KREACJA I PROGRESJA', '%', True),
    'Through passes per 90': ('Podania prostopadłe / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Accurate through passes, %': ('Dokładność podań prostopadłych', 'KREACJA I PROGRESJA', '%', True),
    'Progressive passes per 90': ('Podania progresywne / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Accurate progressive passes, %': ('Dokładność podań progresywnych', 'KREACJA I PROGRESJA', '%', True),
    'Smart passes per 90': ('Podania otwierające (smart) / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Accurate smart passes, %': ('Dokładność podań otwierających', 'KREACJA I PROGRESJA', '%', True),
    'Key passes per 90': ('Kluczowe podania / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Shot assists per 90': ('Asysty przy strzałach / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Second assists per 90': ('Asysty drugiego stopnia / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Third assists per 90': ('Asysty trzeciego stopnia / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Deep completions per 90': ('Zagrania penetrujące / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Deep completed crosses per 90': ('Głębokie dośrodkowania / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Crosses per 90': ('Dośrodkowania / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Accurate crosses, %': ('Dokładność dośrodkowań', 'KREACJA I PROGRESJA', '%', True),
    'Crosses from left flank per 90': ('Dośrodkowania z lewej strony / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Accurate crosses from left flank, %': ('Dokładność dośrodkowań z lewej', 'KREACJA I PROGRESJA', '%', True),
    'Crosses from right flank per 90': ('Dośrodkowania z prawej strony / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Accurate crosses from right flank, %': ('Dokładność dośrodkowań z prawej', 'KREACJA I PROGRESJA', '%', True),
    'Crosses to goalie box per 90': ('Dośrodkowania w pole bramkowe / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Corners per 90': ('Rzuty rożne / 90', 'KREACJA I PROGRESJA', 'per90', True),
    'Free kicks per 90': ('Rzuty wolne / 90', 'KREACJA I PROGRESJA', 'per90', True),

    # --- GRA 1V1, DRYBLING I OFENSYWA ---
    'Successful attacking actions per 90': ('Udane akcje ofensywne / 90', 'GRA 1V1 I OFENSYWA', 'per90', True),
    'Dribbles per 90': ('Dryblingi / 90', 'GRA 1V1 I OFENSYWA', 'per90', True),
    'Successful dribbles, %': ('Udane dryblingi, %', 'GRA 1V1 I OFENSYWA', '%', True),
    'Offensive duels per 90': ('Pojedynki w ofensywie / 90', 'GRA 1V1 I OFENSYWA', 'per90', True),
    'Offensive duels won, %': ('Wygrane pojedynki w ofensywie', 'GRA 1V1 I OFENSYWA', '%', True),
    'Progressive runs per 90': ('Progresywne rajdy / 90', 'GRA 1V1 I OFENSYWA', 'per90', True),
    'Accelerations per 90': ('Przyspieszenia / 90', 'GRA 1V1 I OFENSYWA', 'per90', True),
    'Touches in box per 90': ('Kontakty z piłką w polu karnym / 90', 'GRA 1V1 I OFENSYWA', 'per90', True),
    'Fouls suffered per 90': ('Wywalczone faule / 90', 'GRA 1V1 I OFENSYWA', 'per90', True),
    'Duels per 90': ('Pojedynki ogółem / 90', 'GRA 1V1 I OFENSYWA', 'per90', True),
    'Duels won, %': ('Wygrane pojedynki ogółem', 'GRA 1V1 I OFENSYWA', '%', True),

    # --- FINALIZACJA, BRAMKI I KREACJA ---
    'Goals': ('Gole ogółem', 'FINALIZACJA I STRZAŁY', 'count', True),
    'Goals per 90': ('Gole / 90', 'FINALIZACJA I STRZAŁY', 'per90', True),
    'Non-penalty goals': ('Gole bez rzutów karnych', 'FINALIZACJA I STRZAŁY', 'count', True),
    'Non-penalty goals per 90': ('Gole bez karnych / 90', 'FINALIZACJA I STRZAŁY', 'per90', True),
    'xG': ('xG (Gole oczekiwane)', 'FINALIZACJA I STRZAŁY', 'per90', True),
    'xG per 90': ('xG / 90', 'FINALIZACJA I STRZAŁY', 'per90', True),
    'Shots': ('Strzały ogółem', 'FINALIZACJA I STRZAŁY', 'count', True),
    'Shots per 90': ('Strzały / 90', 'FINALIZACJA I STRZAŁY', 'per90', True),
    'Shots on target, %': ('Celność strzałów, %', 'FINALIZACJA I STRZAŁY', '%', True),
    'Goal conversion, %': ('Konwersja strzałów na gole', 'FINALIZACJA I STRZAŁY', '%', True),
    'Assists': ('Asysty ogółem', 'FINALIZACJA I STRZAŁY', 'count', True),
    'Assists per 90': ('Asysty / 90', 'FINALIZACJA I STRZAŁY', 'per90', True),
    'xA': ('xA (Asysty oczekiwane)', 'FINALIZACJA I STRZAŁY', 'per90', True),
    'xA per 90': ('xA / 90', 'FINALIZACJA I STRZAŁY', 'per90', True),
    'Penalties taken': ('Wykonane rzuty karne', 'FINALIZACJA I STRZAŁY', 'count', True),
    'Penalty conversion, %': ('Skuteczność rzutów karnych', 'FINALIZACJA I STRZAŁY', '%', True),
    'Direct free kicks per 90': ('Bezpośrednie rzuty wolne / 90', 'FINALIZACJA I STRZAŁY', 'per90', True),
    'Direct free kicks on target, %': ('Celność rzutów wolnych', 'FINALIZACJA I STRZAŁY', '%', True),

    # --- BRAMKARZE (Opcjonalnie) ---
    'Save rate, %': ('Obronione strzały, %', 'GRA BRAMKARSKA', '%', True),
    'Conceded goals': ('Stracone bramki', 'GRA BRAMKARSKA', 'count', False),
    'Conceded goals per 90': ('Stracone bramki / 90', 'GRA BRAMKARSKA', 'per90', False),
    'Clean sheets': ('Czyste konta', 'GRA BRAMKARSKA', 'count', True),
    'Prevented goals': ('Uratowane gole (Prevented)', 'GRA BRAMKARSKA', 'per90', True),
    'Prevented goals per 90': ('Uratowane gole / 90', 'GRA BRAMKARSKA', 'per90', True),
    'Exits per 90': ('Wyjścia z bramki / 90', 'GRA BRAMKARSKA', 'per90', True),
    'Shots against': ('Strzały na bramkę', 'GRA BRAMKARSKA', 'count', False),
    'Shots against per 90': ('Strzały na bramkę / 90', 'GRA BRAMKARSKA', 'per90', False),
    'xG against': ('xG rywali', 'GRA BRAMKARSKA', 'per90', False),
    'xG against per 90': ('xG rywali / 90', 'GRA BRAMKARSKA', 'per90', False),
    'Back passes received as GK per 90': ('Podania odebrane jako GK / 90', 'GRA BRAMKARSKA', 'per90', True),
}

# Gotowe presety dla poszczególnych pozycji
POSITION_PRESETS = {
    'Środkowy Obrońca (5 kluczowych)': [
        'Defensive duels per 90',
        'Defensive duels won, %',
        'Aerial duels won, %',
        'Shots blocked per 90',
        'Accurate forward passes, %'
    ],
    'Środkowy Obrońca (Kompletny - 7 metryk)': [
        'Defensive duels per 90',
        'Defensive duels won, %',
        'Shots blocked per 90',
        'Aerial duels per 90',
        'Aerial duels won, %',
        'Forward passes per 90',
        'Accurate forward passes, %'
    ],
    'Boczny Obrońca / Wahadłowy (5 kluczowych)': [
        'Defensive duels won, %',
        'Crosses per 90',
        'Accurate crosses, %',
        'Progressive runs per 90',
        'Accurate forward passes, %'
    ],
    'Boczny Obrońca / Wahadłowy (Kompletny - 9 metryk)': [
        'Defensive duels per 90',
        'Defensive duels won, %',
        'Shots blocked per 90',
        'Aerial duels per 90',
        'Aerial duels won, %',
        'Forward passes per 90',
        'Accurate forward passes, %',
        'Crosses per 90',
        'Accurate crosses, %'
    ],
    'Środkowy Pomocnik (6/8 - 6 metryk)': [
        'Defensive duels won, %',
        'PAdj Interceptions',
        'Accurate passes, %',
        'Accurate forward passes, %',
        'Passes to final third per 90',
        'Progressive passes per 90'
    ],
    'Ofensywny Pomocnik / Skrzydłowy (10/7/11 - 6 metryk)': [
        'Successful attacking actions per 90',
        'Progressive runs per 90',
        'Dribbles per 90',
        'Successful dribbles, %',
        'xA per 90',
        'Passes to penalty area per 90'
    ],
    'Środkowy Napastnik (9 - 6 metryk)': [
        'Goals per 90',
        'xG per 90',
        'Shots per 90',
        'Shots on target, %',
        'Touches in box per 90',
        'Aerial duels won, %'
    ],
    'Uniwersalny Zestaw 5 Metryk': [
        'Defensive duels won, %',
        'Aerial duels won, %',
        'Accurate forward passes, %',
        'Progressive runs per 90',
        'Successful attacking actions per 90'
    ]
}


def get_metric_info(raw_col):
    """Zwraca (display_name, category, unit, higher_is_better) dla kolumny."""
    if raw_col in METRICS_DICT:
        return METRICS_DICT[raw_col]
    
    # Auto-detekcja jeśli metryka nie jest w słowniku
    unit = '%' if '%' in raw_col else ('count' if any(w in raw_col.lower() for w in ['goals', 'matches', 'minutes', 'cards']) else 'per90')
    category = 'INNE METRYKI'
    display_name = raw_col
    higher_is_better = True
    return (display_name, category, unit, higher_is_better)


def format_metric_value(val, unit):
    """Formatowanie wartości do wyświetlenia."""
    import pandas as pd
    if pd.isna(val) or val is None:
        return "-"
    try:
        fval = float(val)
        if unit == '%':
            return f"{fval:.1f}%"
        elif unit == 'count':
            return f"{int(round(fval))}"
        elif unit == 'meters':
            return f"{fval:.1f} m"
        else: # per90 or float
            return f"{fval:.2f}"
    except (ValueError, TypeError):
        return str(val)


def format_delta(val, ref, unit):
    """Formatowanie delty pomiędzy zawodnikiem a benchmarkiem."""
    import pandas as pd
    if pd.isna(val) or pd.isna(ref) or val is None or ref is None:
        return "-"
    try:
        v = float(val)
        r = float(ref)
        diff = v - r
        if unit == '%':
            return f"{diff:+.1f} p.p."
        else:
            pct = (diff / r * 100) if r != 0 else 0
            return f"{diff:+.2f} ({pct:+.1f}%)"
    except (ValueError, TypeError):
        return "-"
