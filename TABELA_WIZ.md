---
name: tabela-wiz
description: Uniwersalna specyfikacja i generator czytelnych grafik oraz dashboardów tabelarycznych dla statystyk piłkarskich (raw data). Obsługuje dowolnego zawodnika, pozycję, zbiór metryk z Wyscout/Excel/CSV oraz dowolne punkty odniesienia.
---

# TABELA_WIZ.md — Uniwersalny Standard Wizualizacji Tabel Statystycznych Zawodników

Niniejszy plik definiuje kompleksowy, uniwersalny standard tworzenia grafik tabelarycznych (PNG 300 DPI) oraz interaktywnych dashboardów HTML/CSS na podstawie surowych danych statystycznych (raw data) z dowolnych arkuszy Excel/CSV (np. Wyscout). 

Standard ten ma zastosowanie do **dowolnej pozycji** (obrońca, pomocnik, skrzydłowy, napastnik, bramkarz), **dowolnego zawodnika** oraz **dowolnego zestawu wskaźników statystycznych**.

---

## 1. Zasady Designu i Estetyki (Visual Design System)

Wizualizacja tabelaryczna służy szybkiemu, czytelnemu porównaniu liczbowemu. Należy bezwzględnie przestrzegać poniższych zasad:

1. **Brak "wniosków" i opisów**: Tabela przedstawia **czyste dane (raw data)**. Nie dodajemy słownych podsumowań dla zarządu na samej grafice.
2. **Minimalistyczny Light Theme**:
   - **Tło główne**: Czysta biel `#FFFFFF`.
   - **Wiersze z danymi**: Naprzemienny kolor `#F8FAFC` (bardzo jasna szarość/łupek) dla wierszy nieparzystych oraz `#FFFFFF` dla parzystych.
   - **Nagłówek główny tabeli (Header Bar)**: Ciemny łupek (`#1E293B`) z grubym, białym tekstem (`#FFFFFF`, bold).
   - **Sekcje / Kategorie metryk (Category Rows)**: Jasnoszary pas (`#F1F5F9`) z dolną obwódką (`#CBD5E1`), tekst pisany WIELKIMI LITERAMI (`#334155`, bold).
   - **Krawędzie komórek**: Subtelna dolna linia separatora (`#E2E8F0`, szerokość 0.8px).
3. **Ściśle kontrolowana paleta akcentów**:
   - **Dodatnia delta (`+`)**: Ciemna zieleń `#15803D` (bold).
   - **Ujemna delta (`-`)**: Czerwony `#B91C1C` (bold).
   - **Wyróżnienia najlepszych w zbiorze (Top 3)**:
     - **Top 1 (Najlepsza wartość w metryce)**: tło komórki `#BBF7D0` (nasycony seledyn), tekst zielony `#15803D` (bold).
     - **Top 2 i Top 3**: tło komórki `#DCFCE7` (jasny emerald), tekst zielony `#15803D` (bold).
   - **Komórki głównego zawodnika (Target Column)**: Tekst pogrubiony (`fontweight='bold'`), kolor `#111827`.
4. **ZAKAZANE elementy**:
   - Gradienty pod tekstem.
   - Fioletowe/różowe akcenty na ciemnym tle.
   - Kolorowe świecące obramowania (glowing borders).
   - Upychanie sztucznych wykresów kołowych lub pasków postępu wewnątrz komórek tabeli.

---

## 2. Architektura Danych i Słownik Metryk (`metric_meta`)

Każdy zbiór danych przed wygenerowaniem tabeli musi zostać zamapowany przy pomocy uniwersalnego słownika mapującego surowe kolumny pliku (np. z Wyscout) na polskie nazwy wyświetlane, przypisaną sekcję/kategorię oraz jednostkę.

### 2.1. Unifikacja Słownika `metric_meta`

```python
metric_meta = {
    # Surowa nazwa z pliku : (Nazwa_Wyświetlana_PL, Nazwa_Kategorii_PL, Jednostka)
    # Jednostki: '%' dla wartości procentowych, 'per90' dla wskaźników na 90 minut, 'count' dla liczności
    
    # Przykłady Defensywa:
    'Defensive duels per 90': ('Pojedynki w defensywie / 90', 'Gra w Defensywie', 'per90'),
    'Defensive duels won, %': ('Wygrane pojedynki w defensywie', 'Gra w Defensywie', '%'),
    'Shots blocked per 90': ('Zablokowane strzały / 90', 'Gra w Defensywie', 'per90'),
    'Interceptions per 90': ('Przejęcia / 90', 'Gra w Defensywie', 'per90'),
    'PAdj Interceptions': ('Przejęcia (PAdj) / 90', 'Gra w Defensywie', 'per90'),
    
    # Przykłady Powietrze:
    'Aerial duels per 90': ('Pojedynki w powietrzu / 90', 'Gra w Powietrzu', 'per90'),
    'Aerial duels won, %': ('Wygrane pojedynki w powietrzu', 'Gra w Powietrzu', '%'),
    
    # Przykłady Dystrybucja i Rozgrywanie:
    'Forward passes per 90': ('Podania do przodu / 90', 'Dystrybucja i Rozgrywanie', 'per90'),
    'Accurate forward passes, %': ('Dokładność podań do przodu', 'Dystrybucja i Rozgrywanie', '%'),
    'Passes to final third per 90': ('Podania w 3. tercję / 90', 'Dystrybucja i Rozgrywanie', 'per90'),
    'Accurate passes to final third, %': ('Dokładność podań w 3. tercję', 'Dystrybucja i Rozgrywanie', '%'),
    'Crosses per 90': ('Dośrodkowania / 90', 'Dystrybucja i Rozgrywanie', 'per90'),
    'Accurate crosses, %': ('Dokładność dośrodkowań', 'Dystrybucja i Rozgrywanie', '%'),
    
    # Przykłady Ofensywa i Drybling:
    'Dribbles per 90': ('Dryblingi / 90', 'Gra 1v1 i Ofensywa', 'per90'),
    'Successful dribbles, %': ('Udane dryblingi', 'Gra 1v1 i Ofensywa', '%'),
    'Progressive runs per 90': ('Progresywne rajdy / 90', 'Gra 1v1 i Ofensywa', 'per90'),
    'Touches in box per 90': ('Kontakty z piłką w polu karnym / 90', 'Gra 1v1 i Ofensywa', 'per90'),
    'Shots per 90': ('Strzały / 90', 'Finalizacja i Ofensywa', 'per90'),
    'Shots on target, %': ('Celność strzałów', 'Finalizacja i Ofensywa', '%'),
    'Goal conversion, %': ('Konwersja strzałów na gole', 'Finalizacja i Ofensywa', '%'),
}
```

### 2.2. Standardowe Sekcje według Pozycji Zawodnika

W zależności od pozycji zawodnika, metryki powinny być podzielone na 3-4 logiczne sekcje:
- **Środkowy stoper / Obrońca**: `GRA W DEFENSYWIE`, `GRA W POWIETRZU`, `DYSTRYBUCJA I ROZGRYWANIE`.
- **Boczny obrońca / Wahadłowy**: `GRA W DEFENSYWIE`, `DYSTRYBUCJA I DOŚRODKOWANIA`, `GRA 1V1 I ROZGRYWANIE`.
- **Środkowy pomocnik (6/8)**: `POJEDYNKI I ODZYSKI`, `DYSTRYBUCJA I ROZGRYWANIE`, `KREACJA I PROGRESJA`.
- **Ofensywny pomocnik / Skrzydłowy (10/7/11)**: `KREACJA I DRYBLING`, `FINALIZACJA I STRZAŁY`, `PRACA W DEFENSYWIE`.
- **Środkowy napastnik (9)**: `FINALIZACJA I STRZAŁY`, `GRA W POWIETRZU I POJEDYNKI`, `GRA Z PIŁKĄ I PRESSING`.

---

## 3. Matematyka Formatowania i Delt (`fmt_val` oraz `calc_delta`)

Należy bezwzględnie stosować spójne reguły matematycznego formatowania liczb:

### 3.1. Formatowanie Wartości Bezwzględnej (`fmt_val`)
- **Dla metryk procentowych (`%`)**: 1 miejsce po przecinku + znak `%` (np. `64.2%`).
- **Dla metryk per 90 (`per90`)**: 2 miejsca po przecinku (np. `4.18`).
- **Dla liczności/minut/meczów**: Liczba całkowita bez miejsc po przecinku (np. `2450`).

```python
def fmt_val(metric_name, val):
    if pd.isna(val):
        return "-"
    if '%' in metric_name or 'won, %' in metric_name:
        return f"{val:.1f}%"
    else:
        return f"{val:.2f}"
```

### 3.2. Formatowanie Delt / Odchyleń (`calc_delta`)
Delta wskazuje różnicę pomiędzy wynikiem zawodnika ($V_{player}$) a wartością referencyjną ($V_{ref}$).

- **Dla metryk procentowych (`%`)**: Wyliczamy **punkty procentowe (`p.p.`)**:
  $$\Delta = V_{player} - V_{ref}$$
  Wykazywana jako: `+3.2 p.p.` (gdy $\Delta \ge 0$) lub `-1.5 p.p.` (gdy $\Delta < 0$).
- **Dla metryk per 90 (`per90`)**: Wyliczamy różnicę bezwzględną oraz różnicę względną procentową:
  $$\Delta_{abs} = V_{player} - V_{ref}, \quad \Delta_{rel} = \left(\frac{\Delta_{abs}}{V_{ref}}\right) \times 100$$
  Wykazywana jako: `+0.45 (+12.3%)` lub `-0.15 (-5.2%)`.

```python
def calc_delta(val, ref, is_pct):
    if pd.isna(val) or pd.isna(ref):
        return "-"
    diff = val - ref
    if is_pct:
        return f"{diff:+.1f} p.p."
    else:
        pct_diff = (diff / ref * 100) if ref != 0 else 0
        return f"{diff:+.2f} ({pct_diff:+.1f}%)"
```

---

## 4. Reguły Wyliczania Szerokości Kolumn (Auto-Layout System)

Aby teksty metryk i liczby **nigdy nie wychodziły poza ramki ani komórki tabeli**, stosuje się proporcjonalny podział szerokości w układzie współrzędnych `fig.transFigure`:

1. **Suma szerokości kolumn (`sum(col_widths)`)**: Zawsze z przedziału `0.88` – `0.94`, co pozostawia stały lewy margines `left = 0.035` (lub `0.02` dla tabel 11-kolumnowych).
2. **Podział szerokości pod liczbę kolumn ($N$)**:
   - **Kolumna 0 (Metryka / Zawodnik)**: Zawsze zajmuje **22% - 28%** całkowitej szerokości (np. `width = 0.24` do `0.28`), aby zmieścić najdłuższe nazwy polskich metryk.
   - **Pozostałe kolumny numeryczne ($1 \dots N-1$)**: Dzielą równomiernie pozostałe miejsce (np. `0.08` – `0.15` na komórkę).

### Przykładowe Standardowe Zestawy Szerokości:
- **Tabela 5-kolumnowa (Zestawienie bezpośrednie)**:
  `col_widths = [0.28, 0.15, 0.15, 0.18, 0.17]` (suma = 0.93)
  *Słupki: [Metryka Statystyczna, Zawodnik A, Zawodnik B, Średnia Liga, Średnia Klub]*
- **Tabela 8-kolumnowa (Profil Indywidualny Zawodnika vs 3 Benchmarki + 3 Delty)**:
  `col_widths = [0.24, 0.10, 0.10, 0.11, 0.10, 0.09, 0.09, 0.10]` (suma = 0.93)
  *Słupki: [Metryka, Zawodnik, Śr. Grupa, Śr. Liga, Śr. Klub, vs Grupa, vs Liga, vs Klub]*
- **Tabela 11-kolumnowa (Zbiorcze podsumowanie wielu zawodników)**:
  `sum_widths = [0.12, 0.12, 0.06, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.07, 0.07]` (suma = 0.87, `left = 0.02`)

---

## 5. Generator Python Matplotlib (Uniwersalny Silnik PNG)

Poniższa funkcja `render_table_image_white` stanowi **gotowy silnik produkcyjny** do wygenerowania grafiki w formacie PNG z dowolnymi danymi.

```python
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def render_table_image_white(title, subtitle, columns, col_widths, rows_data, filename, target_col_idx=1, fig_height=9.0, fig_width=16.5):
    """
    Uniwersalny silnik renderujący czystą tabelę statystyczną PNG (Light Theme 300 DPI).
    """
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['axes.edgecolor'] = 'none'

    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Nagłówek Tytułu i Podtytułu
    fig.text(0.035, 0.94, title, fontsize=14, fontweight='bold', color='#111827', va='top')
    fig.text(0.035, 0.90, subtitle, fontsize=9.0, color='#64748B', va='top')

    left, top = 0.035, 0.84
    total_width = sum(col_widths)
    
    col_x_starts = []
    curr = left
    for w in col_widths:
        col_x_starts.append(curr)
        curr += w

    # Górny Pas Nagłówkowy (Ciemny Łupek)
    header_height = 0.050
    th_box = patches.FancyBboxPatch((left, top - header_height), total_width, header_height,
                                     boxstyle="square,pad=0",
                                     facecolor="#1E293B", edgecolor="none",
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
        fig.text(tx, top - header_height / 2.0, col_name, fontsize=8.8, fontweight='bold', color='#FFFFFF', ha=ha, va='center')

    curr_y = top - header_height
    row_h = 0.044
    current_category = ""

    for row_idx, row in enumerate(rows_data):
        category = row.get('category', '')
        
        # Wiersz Rozdzielający Kategorię (Section Header)
        if category and category != current_category:
            current_category = category
            curr_y -= 0.032
            cat_box = patches.FancyBboxPatch((left, curr_y), total_width, 0.030,
                                             boxstyle="square,pad=0",
                                             facecolor="#F1F5F9", edgecolor="none",
                                             transform=fig.transFigure)
            fig.patches.append(cat_box)
            fig.text(left + 0.012, curr_y + 0.015, category.upper(), fontsize=8.5, fontweight='bold', color='#334155', va='center')
            
            line = patches.Rectangle((left, curr_y), total_width, 0.001, facecolor="#CBD5E1", transform=fig.transFigure)
            fig.patches.append(line)

        curr_y -= row_h

        # Alternujące tło wierszy
        bg_color = "#F8FAFC" if row_idx % 2 == 1 else "#FFFFFF"
        r_box = patches.FancyBboxPatch((left, curr_y), total_width, row_h,
                                        boxstyle="square,pad=0",
                                        facecolor=bg_color, edgecolor="none",
                                        transform=fig.transFigure)
        fig.patches.append(r_box)

        # Dolna linia komórki
        border_line = patches.Rectangle((left, curr_y), total_width, 0.0008, facecolor="#E2E8F0", transform=fig.transFigure)
        fig.patches.append(border_line)

        # Renderowanie Wartości w Komórkach
        vals = row['values']
        bg_highlights = row.get('highlights', [None] * len(vals))

        for c_idx, val_str in enumerate(vals):
            cx = col_x_starts[c_idx]
            cw = col_widths[c_idx]
            ha = 'left' if c_idx == 0 else 'center'
            tx = cx + 0.012 if c_idx == 0 else cx + cw / 2.0
            
            color = '#111827'
            fontweight = 'normal'

            # Pogrubienie kolumny docelowej
            if target_col_idx is not None and c_idx == target_col_idx:
                fontweight = 'bold'
            
            # Wyróżnienie tła komórki (np. Top 3)
            cell_hl = bg_highlights[c_idx] if c_idx < len(bg_highlights) else None
            if cell_hl:
                c_box = patches.FancyBboxPatch((cx, curr_y), cw, row_h, boxstyle="square,pad=0", facecolor=cell_hl, transform=fig.transFigure)
                fig.patches.append(c_box)
                color = '#15803D'
                fontweight = 'bold'

            # Formatowanie kolorów dla delt
            if val_str.startswith('+'):
                color = '#15803D' # Zielony delta
                fontweight = 'bold'
            elif val_str.startswith('-'):
                color = '#B91C1C' # Czerwony delta
                fontweight = 'bold'

            fig.text(tx, curr_y + row_h / 2.0, val_str, fontsize=8.8, fontweight=fontweight, color=color, ha=ha, va='center')

    # Zapis pliku
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.15)
    plt.close()
    print(f"Pomyślnie wygenerowano grafikę tabeli: {filename}")
```

---

## 6. Generator Dashboardu HTML/CSS (Interaktywny Pulpit WWW)

Poniższy szablon stylów CSS oraz struktury HTML zapewnia idealne odwzorowanie estetyki grafik PNG w formie interaktywnej strony internetowej z przełączaniem zawodników/tabel w zakładkach.

```html
<style>
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: #F8FAFC;
        color: #111827;
        padding: 32px;
    }
    .card {
        background: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
        overflow: hidden;
        margin-bottom: 32px;
    }
    .card-header {
        background-color: #1E293B;
        color: #FFFFFF;
        padding: 20px 24px;
    }
    .card-title {
        font-size: 18px;
        font-weight: 700;
    }
    .card-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
    }
    .table-container {
        overflow-x: auto;
    }
    .data-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
        font-size: 13.5px;
    }
    .data-table th {
        background-color: #0F172A;
        color: #FFFFFF;
        padding: 12px 16px;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 0.5px;
    }
    .data-table th:not(:first-child), .data-table td:not(:first-child) {
        text-align: center;
    }
    .category-row td {
        background-color: #F1F5F9;
        color: #334155;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.5px;
        padding: 10px 16px;
        border-top: 1px solid #CBD5E1;
        border-bottom: 1px solid #CBD5E1;
    }
    .data-table tbody tr:nth-child(even) {
        background-color: #F8FAFC;
    }
    .data-table td {
        padding: 12px 16px;
        border-bottom: 1px solid #E2E8F0;
    }
    .target-col {
        font-weight: 700;
        color: #0F172A;
    }
    .delta.pos {
        color: #15803D;
        font-weight: 700;
    }
    .delta.neg {
        color: #B91C1C;
        font-weight: 700;
    }
    .badge-top1 {
        background-color: #BBF7D0;
        color: #15803D;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .badge-top3 {
        background-color: #DCFCE7;
        color: #15803D;
        font-weight: 600;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .btn-download {
        display: inline-block;
        background-color: #2563EB;
        color: #FFFFFF;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
        font-size: 13px;
        transition: background 0.2s;
    }
    .btn-download:hover {
        background-color: #1D4ED8;
    }
</style>
```

---

## 7. Instrukcja Postępowania dla Agenta AI (Checklista Krok po Kroku)

Gdy użytkownik prosi o wygenerowanie tabeli wizualizacyjnej w nowym projekcie lub dla dowolnego pliku danych, wykonaj następujące kroki:

1. **Wczytaj dane**: Odczytaj plik `.xlsx` / `.csv` przy użyciu Pandas.
2. **Zdefiniuj `metric_meta`**: Przetłumacz nagłówki kolumn z pliku źródłowego na polskie czytelne nazwy, przypisz je do 3-4 logicznych kategorii odpowiednich dla pozycji i podaj ich jednostkę (`%` lub `per90`).
3. **Oblicz średnie odniesienia (Benchmarki)**: Wylicz średnią dla całego zbioru (`avg_group`), średnią dla danej ligi/pozycji (`avg_league`) oraz ewentualne średnie wybranego klubu (`avg_club`).
4. **Wylicz delty**: Dla każdego zawodnika z wyliczonego wiersza wywołaj `calc_delta(val, ref, is_pct)`.
5. **Wybierz układ kolumn i oblicz `col_widths`**:
   - Dla pojedynczego profilu: użyj 8-kolumnowego układu porównawczego.
   - Dla zestawienia bezpośredniego 2 zawodników: użyj 5-kolumnowego układu.
   - Dla tabeli zbiorczej całego zespołu: użyj układu wielokolumnowego z podświetleniem Top 3 w każdej metryce (`badge-top1` i `badge-top3`).
6. **Wygeneruj pliki PNG**: Wywołaj funkcję `render_table_image_white` i zapisz pliki w folderze `output_visualizations/`.
7. **Wygeneruj Dashboard HTML**: Wygeneruj plik `index.html` integrujący wszystkie tabele w interaktywnym podglądzie.
