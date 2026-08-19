"""
Komponenty interfejsu użytkownika i widgety pomocnicze dla aplikacji Streamlit.
"""

import streamlit as st
from src.metrics_config import METRICS_DICT, POSITION_PRESETS

def inject_custom_css():
    """Wstrzykuje niestandardowe style CSS do aplikacji Streamlit."""
    st.markdown("""
    <style>
        /* Modern Clean Header */
        .main-header {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            padding: 24px 32px;
            border-radius: 12px;
            color: #FFFFFF;
            margin-bottom: 24px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
        }
        .main-header h1 {
            font-size: 26px;
            font-weight: 800;
            margin: 0;
            color: #FFFFFF;
        }
        .main-header p {
            font-size: 14px;
            color: #94A3B8;
            margin: 6px 0 0 0;
        }
        
        /* Metric stat badge */
        .stat-badge {
            background-color: #F1F5F9;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
            color: #334155;
            display: inline-block;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        
        /* Section Title */
        .section-header {
            font-size: 18px;
            font-weight: 700;
            color: #0F172A;
            margin-top: 16px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
        }
        
        /* Clean card container */
        .ui-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
        }
    </style>
    """, unsafe_allow_html=True)


def render_metric_selector(default_preset="Środkowy Obrońca (5 kluczowych)", key_prefix="comp"):
    """
    Renderuje komponent wyboru szablonu oraz metryk z podziałem na kategorie.
    Zwraca listę wybranych metryk (raw column names).
    """
    st.markdown("##### ⚙️ Wybór Metryk i Szablonu")
    col_preset, col_custom = st.columns([1, 2])
    
    preset_names = list(POSITION_PRESETS.keys())
    default_idx = preset_names.index(default_preset) if default_preset in preset_names else 0
    
    with col_preset:
        selected_preset = st.selectbox(
            "Wybierz gotowy szablon pozycji:",
            preset_names,
            index=default_idx,
            key=f"{key_prefix}_preset"
        )
    
    preset_metrics = POSITION_PRESETS.get(selected_preset, [])
    
    all_available_metrics = list(METRICS_DICT.keys())
    
    with col_custom:
        selected_metrics = st.multiselect(
            "Dostosuj lub wybierz dowolne metryki:",
            options=all_available_metrics,
            default=preset_metrics,
            format_func=lambda x: f"{METRICS_DICT[x][0]} ({METRICS_DICT[x][1]})" if x in METRICS_DICT else x,
            key=f"{key_prefix}_metrics"
        )

    if not selected_metrics:
        st.warning("Wybierz przynajmniej 1 metrykę do zestawienia.")
        return preset_metrics

    return selected_metrics
