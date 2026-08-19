# ⚽ Football Analytics & Comparison Studio (Streamlit)

Kompleksowa aplikacja analityczna w technologii **Streamlit** do porównywania statystyk piłkarskich, analizy grupowej oraz automatycznego generowania publikacyjnych tabel w standardzie `TABELA_WIZ.md`.

---

## 🌟 Główne Funkcjonalności

- **📊 Kreator Tabel Porównawczych**:
  - Porównanie dowolnej liczby zawodników (np. 3 piłkarzy) z bazy ponad 3000 wierszy (Ekstraklasa, 1 Liga, 2 Liga, Zagranica).
  - Wzbogacenie o **Średnią Ligi** (np. 1 Liga, Ekstraklasa) oraz **Średnią Wiekową** (np. U21, U19, U17, ur. 2008+).
  - Wybór dowolnych 5, 8 lub N statystyk z gotowymi presetami pozycji (Środkowy obrońca, Wahadłowy, Pomocnik 6/8, Skrzydłowy/10, Napastnik) oraz pełną listą 100+ metryk Wyscout.
- **🎨 Unikalny Standard Wizualny**:
  - **Brak obramowań komórek** (Light Theme).
  - **Zielone wyróżnienia** (`#BBF7D0` / `#DCFCE7`) dla najlepszych wartości w grupie.
  - **Jednolite żółte kolumny** (`#FEF08A` / `#EAB308`) dla średnich odniesienia i benchmarków.
- **📥 Publikacyjny Eksport**:
  - Pobieranie grafiki **PNG w wysokiej rozdzielczości (300 DPI)** gotowej do raportów i social media.
  - Pobieranie kodu **HTML** tabeli.
  - Eksport do formatu **CSV/Excel**.
- **👥 Zestawienie Zbiorcze & Ranking**:
  - Analiza grupowa zawodników z automatycznym podświetleniem Top 3 wyników w każdej statystyce.
- **🔍 Profil i Analiza Zawodnika**:
  - Karta zawodnika z automatycznym porównaniem do średnich ligowych i pozycji.
- **📁 Zarządzanie Danymi**:
  - Obsługa wszystkich wgranych arkuszy oraz moduł dodawania nowych raportów Excel/CSV bezpośrednio z poziomu aplikacji.

---

## 🚀 Szybki Start Lokalnie

1. **Sklonuj repozytorium lub przejdź do folderu projektu**:
   ```bash
   cd similarity
   ```

2. **Zainstaluj zależności**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Uruchom aplikację**:
   ```bash
   streamlit run app.py
   ```

Aplikacja otworzy się automatycznie w przeglądarce pod adresem `http://localhost:8501`.

---

## ☁️ Wdrożenie na GitHub i Streamlit Community Cloud (Darmowy Hosting)

Aplikacja jest w 100% gotowa do 1-kliknięciowego wdrożenia w chmurze Streamlit:

1. **Zainicjalizuj repozytorium Git i wypchnij na GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Football Analytics Streamlit App"
   git branch -M main
   git remote add origin https://github.com/TWOJA_NAZWA_UZYTKOWNIKA/TWOJE_REPOZYTORIUM.git
   git push -u origin main
   ```

2. **Wdrożenie na Streamlit Cloud**:
   - Wejdź na [share.streamlit.io](https://share.streamlit.io/) i zaloguj się kontem GitHub.
   - Kliknij **"New app"**.
   - Wskaż swoje repozytorium, gałąź `main` oraz plik główny `app.py`.
   - Kliknij **"Deploy!"**.

Aplikacja będzie publicznie dostępna pod dedykowanym adresem URL!

---

## 📁 Struktura Projektu

```
similarity/
├── app.py                     # Główny punkt wejściowy aplikacji Streamlit
├── requirements.txt           # Biblioteki (streamlit, pandas, matplotlib, openpyxl itp.)
├── README.md                  # Dokumentacja projektu
├── .gitignore                 # Pliki ignorowane przez Git
│
├── src/
│   ├── data_loader.py         # Ładowanie, normalizacja i cache'owanie bazy danych
│   ├── metrics_config.py      # Słownik metryk (PL nazwy, kategorie, jednostki, presety)
│   ├── table_renderer.py      # Silnik generowania czystego HTML/CSS (brak ramek, akcenty)
│   ├── image_generator.py     # Silnik eksportu grafiki PNG 300 DPI (Matplotlib)
│   └── components.py          # Elementy UI, filtry, selektory
│
└── data/                      # Wszystkie bazy danych zawodników (ESA, 1 Liga, 2 Liga)
```
