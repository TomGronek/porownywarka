"""
Moduł zabezpieczenia aplikacji hasłem (Authentication & Access Control).
Hasło pobierane jest wyłącznie w bezpieczny sposób ze Streamlit Secrets (APP_PASSWORD).
W kodzie nie ma żadnych haseł domyślnych ani fallbacków.
"""

import streamlit as st

def check_password() -> bool:
    """
    Sprawdza, czy użytkownik jest zalogowany.
    Weryfikuje hasło wprowadzone przez użytkownika względem st.secrets["APP_PASSWORD"].
    Jeśli nie jest zalogowany, wyświetla formularz i zatrzymuje aplikację.
    """
    # 1. Sprawdź czy użytkownik jest już uwierzytelniony w sesji
    if st.session_state.get("authenticated", False):
        return True

    # 2. Pobierz hasło wyłącznie ze Streamlit Secrets
    try:
        correct_password = st.secrets["APP_PASSWORD"]
    except (KeyError, FileNotFoundError, AttributeError):
        st.error("⚠️ Błąd konfiguracji bezpieczeństwa: brak zdefiniowanego klucza `APP_PASSWORD` w Streamlit Secrets. Skonfiguruj hasło w panelu Streamlit Cloud (Settings -> Secrets).")
        return False

    def verify_password():
        user_pass = st.session_state.get("login_password_input", "")
        if user_pass == correct_password:
            st.session_state["authenticated"] = True
            st.session_state["auth_error"] = False
        else:
            st.session_state["authenticated"] = False
            st.session_state["auth_error"] = True

    # 3. Formularz logowania
    st.markdown("""
    <div style="max-width: 480px; margin: 40px auto 20px auto; padding: 28px; background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08); text-align: center;">
        <div style="font-size: 40px; margin-bottom: 8px;">🔒</div>
        <h2 style="color: #0F172A; margin: 0 0 6px 0; font-size: 22px; font-weight: 700;">Dostęp Zabezpieczony Hasłem</h2>
        <p style="color: #64748B; font-size: 13.5px; margin: 0; line-height: 1.5;">
            Wpisz hasło dostępu, aby odblokować bazę danych oraz narzędzia analityczne.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.text_input(
                "Hasło:",
                type="password",
                placeholder="Wpisz hasło dostępu...",
                key="login_password_input"
            )
            submit_btn = st.form_submit_button("Odblokuj Dostęp 🚀", use_container_width=True, type="primary")
            
            if submit_btn:
                verify_password()
                if st.session_state.get("authenticated", False):
                    st.rerun()

        if st.session_state.get("auth_error", False):
            st.error("❌ Niepoprawne hasło. Spróbuj ponownie.")

    st.markdown("""
    <div style="text-align: center; margin-top: 32px; color: #94A3B8; font-size: 12px;">
        Football Analytics & Comparison Studio • Dostęp chroniony
    </div>
    """, unsafe_allow_html=True)

    return False


def render_auth_sidebar():
    """Renderuje status logowania oraz przycisk wylogowania w panelu bocznym."""
    with st.sidebar:
        st.markdown("---")
        st.caption("🔒 Status: **Zalogowano pomyślnie**")
        if st.button("Wyloguj się", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()
