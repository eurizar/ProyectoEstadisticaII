"""Login principal — Sistema de Analisis Estadistico UMG."""

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Acceso · Análisis Estadístico UMG",
    page_icon="assets/favicon.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)


LOGIN_CSS = """
<style>
  /* ── Login page scope: form becomes the card ─────────────── */
  body:has(#login-pavilion) [data-testid="stAppViewContainer"]{
    background:
      radial-gradient(1200px 600px at 85% -10%, rgba(201,168,70,0.10), transparent 60%),
      radial-gradient(900px 600px at -10% 110%, rgba(0,48,135,0.14), transparent 55%),
      linear-gradient(180deg, #F5F1E8 0%, #F8F7F4 45%, #EEEAE0 100%) !important;
  }
  body:has(#login-pavilion) [data-testid="block-container"]{
    padding-top: 0 !important;
    padding-bottom: 1rem !important;
    max-width: 560px !important;
  }
  body:has(#login-pavilion) [data-testid="stMain"] > .main,
  body:has(#login-pavilion) section.main > div.block-container,
  body:has(#login-pavilion) [data-testid="stMainBlockContainer"]{
    padding-top: 0 !important;
  }
  body:has(#login-pavilion) [data-testid="stHeader"],
  body:has(#login-pavilion) header[data-testid="stHeader"]{
    display:none !important;
    height:0 !important;
  }
  body:has(#login-pavilion) [data-testid="stDecoration"]{ display:none !important; }
  body:has(#login-pavilion) [data-testid="stApp"]{ padding-top:0 !important; }
  body:has(#login-pavilion) [data-testid="stAppViewContainer"]::before{
    content:"";
    position:fixed; inset:0;
    background-image:
      linear-gradient(rgba(0,48,135,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,48,135,0.04) 1px, transparent 1px);
    background-size: 56px 56px;
    mask-image: radial-gradient(ellipse 70% 60% at 50% 35%, #000 30%, transparent 80%);
    -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 35%, #000 30%, transparent 80%);
    pointer-events:none;
    z-index:0;
  }

  /* Masthead */
  .pavilion-mast{
    text-align:center;
    margin: 1.5rem 0 1.4rem;
    position:relative;
    animation: fadeRise .7s cubic-bezier(.2,.7,.2,1) both;
  }
  .pavilion-mark{
    width:68px; height:68px;
    margin: 0 auto 1.1rem;
    border-radius:50%;
    background:
      radial-gradient(circle at 32% 32%, rgba(255,255,255,0.18), transparent 55%),
      linear-gradient(140deg, #001240 0%, #003087 55%, #1a4a9f 100%);
    display:flex; align-items:center; justify-content:center;
    box-shadow:
      0 0 0 1px rgba(255,255,255,0.5),
      0 0 0 8px rgba(0,48,135,0.06),
      0 22px 50px rgba(0,48,135,0.30),
      inset 0 1px 0 rgba(255,255,255,0.35);
    position:relative;
  }
  .pavilion-mark::after{
    content:"";
    position:absolute;
    inset:-6px;
    border-radius:50%;
    border:1px dashed rgba(201,168,70,0.55);
    animation: spinSlow 36s linear infinite;
  }
  .pavilion-mark i{
    font-size:1.75rem;
    color: #EDD99A;
    text-shadow: 0 2px 8px rgba(0,0,0,0.35);
  }
  .pavilion-title{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #0A0F1E;
    line-height: 1.05;
    margin: 0 0 .55rem;
    letter-spacing: -.015em;
  }
  .pavilion-title em{
    font-style: italic;
    color: #003087;
    font-weight: 400;
  }
  .pavilion-rule{
    display:flex; align-items:center; justify-content:center;
    gap: .85rem;
    margin: .9rem auto 1.1rem;
    max-width: 360px;
  }
  .pavilion-rule .line{
    flex:1;
    height:1px;
    background: linear-gradient(90deg, transparent, rgba(0,48,135,0.28), transparent);
  }
  .pavilion-rule .ornament{
    font-family: 'Playfair Display', serif;
    color: #C9A846;
    font-size: 1.05rem;
    line-height: 1;
  }
  .pavilion-sub{
    font-family: 'Source Sans 3', sans-serif;
    font-size: .86rem;
    color: rgba(10,15,30,0.55);
    letter-spacing: .04em;
    margin: 0;
  }
  .pavilion-sub b{ color:#003087; font-weight:600; }

  /* The Streamlit form IS the card */
  body:has(#login-pavilion) [data-testid="stForm"]{
    background:
      linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,255,255,0.78)) !important;
    backdrop-filter: blur(22px) saturate(1.1) !important;
    -webkit-backdrop-filter: blur(22px) saturate(1.1) !important;
    border: 1px solid rgba(255,255,255,0.9) !important;
    border-radius: 22px !important;
    padding: 2.4rem 2.2rem 2.1rem !important;
    box-shadow:
      0 1px 0 rgba(255,255,255,0.9) inset,
      0 30px 70px -20px rgba(0,48,135,0.25),
      0 10px 30px -10px rgba(0,48,135,0.15),
      0 0 0 1px rgba(0,48,135,0.04) !important;
    position: relative;
    overflow: hidden;
    animation: fadeRise .8s .15s cubic-bezier(.2,.7,.2,1) both;
  }
  body:has(#login-pavilion) [data-testid="stForm"]::before{
    content:"";
    position:absolute; left:0; right:0; top:0; height:3px;
    background: linear-gradient(90deg,
      transparent 0%,
      #C9A846 25%,
      #EDD99A 50%,
      #C9A846 75%,
      transparent 100%);
    opacity:.85;
  }
  body:has(#login-pavilion) [data-testid="stForm"]::after{
    content:"";
    position:absolute;
    right:-60px; bottom:-60px;
    width:220px; height:220px;
    border-radius:50%;
    background: radial-gradient(circle, rgba(201,168,70,0.10) 0%, transparent 70%);
    pointer-events:none;
  }

  /* Form heading */
  .form-eyebrow{
    font-family: 'JetBrains Mono', monospace;
    font-size: .65rem;
    letter-spacing: .28em;
    color: rgba(10,15,30,0.48);
    text-transform: uppercase;
    margin: 0 0 .35rem;
    display:flex; align-items:center; gap:.55rem;
    justify-content:center;
  }
  .form-eyebrow i{ font-size:.85rem; color:#003087; }
  .form-heading{
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: #003087;
    text-align: center;
    margin: 0 0 1.6rem;
    line-height: 1.2;
  }

  /* Inputs: editorial bottom-border style */
  body:has(#login-pavilion) [data-testid="stForm"] .stTextInput > label{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .64rem !important;
    letter-spacing: .22em !important;
    color: rgba(10,15,30,0.55) !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
    margin-bottom: .35rem !important;
  }
  body:has(#login-pavilion) [data-testid="stForm"] .stTextInput > div > div{
    background: transparent !important;
    border: none !important;
    border-bottom: 1.5px solid rgba(0,48,135,0.18) !important;
    border-radius: 0 !important;
    transition: border-color .25s ease, box-shadow .25s ease !important;
    padding: 0 !important;
  }
  body:has(#login-pavilion) [data-testid="stForm"] .stTextInput > div > div input{
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    backdrop-filter: none !important;
    padding: .65rem .15rem !important;
    font-size: 1.02rem !important;
    font-family: 'Source Sans 3', sans-serif !important;
    color: #0A0F1E !important;
    box-shadow: none !important;
  }
  body:has(#login-pavilion) [data-testid="stForm"] .stTextInput > div > div:focus-within{
    border-bottom-color: #003087 !important;
    box-shadow: 0 1px 0 0 #003087 !important;
  }
  body:has(#login-pavilion) [data-testid="stForm"] .stTextInput{
    margin-bottom: 1.1rem !important;
  }
  /* Password eye button */
  body:has(#login-pavilion) [data-testid="stForm"] [data-testid="stTextInputRootElement"] button,
  body:has(#login-pavilion) [data-testid="stForm"] .stTextInput button{
    background: transparent !important;
    border: none !important;
    color: rgba(10,15,30,0.45) !important;
    box-shadow: none !important;
  }

  /* Submit button — full-width navy with gold underline accent */
  body:has(#login-pavilion) [data-testid="stFormSubmitButton"]{
    margin-top: .85rem;
  }
  body:has(#login-pavilion) [data-testid="stFormSubmitButton"] > button{
    width: 100% !important;
    background: linear-gradient(180deg, #003087 0%, #001f5b 100%) !important;
    color: #FFFFFF !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: .82rem !important;
    font-weight: 700 !important;
    letter-spacing: .18em !important;
    text-transform: uppercase !important;
    padding: 1rem 1.2rem !important;
    border: none !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow:
      0 1px 0 rgba(255,255,255,0.20) inset,
      0 8px 24px rgba(0,48,135,0.35),
      0 2px 6px rgba(0,48,135,0.18) !important;
    transition: transform .22s ease, box-shadow .22s ease, background .22s ease !important;
  }
  body:has(#login-pavilion) [data-testid="stFormSubmitButton"] > button::after{
    content:"";
    position:absolute;
    left: 50%; bottom: 10px;
    width: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #EDD99A, transparent);
    transition: width .35s ease, left .35s ease;
  }
  body:has(#login-pavilion) [data-testid="stFormSubmitButton"] > button:hover{
    background: linear-gradient(180deg, #1a4a9f 0%, #003087 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow:
      0 1px 0 rgba(255,255,255,0.22) inset,
      0 14px 32px rgba(0,48,135,0.40),
      0 4px 10px rgba(0,48,135,0.22) !important;
  }
  body:has(#login-pavilion) [data-testid="stFormSubmitButton"] > button:hover::after{
    width: 60%; left: 20%;
  }
  body:has(#login-pavilion) [data-testid="stFormSubmitButton"] > button:active{
    transform: translateY(0) !important;
  }

  /* Custom alerts */
  .login-alert{
    margin-top: 1.2rem;
    border-radius: 12px;
    padding: .85rem 1rem;
    display: flex; align-items: flex-start; gap: .65rem;
    font-size: .87rem;
    font-family: 'Source Sans 3', sans-serif;
    line-height: 1.5;
    animation: shake .4s ease, fadeRise .35s ease both;
  }
  .login-alert.error{
    background: linear-gradient(180deg, rgba(155,28,28,0.06), rgba(155,28,28,0.10));
    border: 1px solid rgba(155,28,28,0.20);
    color: #7B1818;
  }
  .login-alert.info{
    background: linear-gradient(180deg, rgba(0,48,135,0.05), rgba(0,48,135,0.08));
    border: 1px solid rgba(0,48,135,0.18);
    color: #1A3A7A;
  }
  .login-alert.success{
    background: linear-gradient(180deg, rgba(13,110,62,0.06), rgba(13,110,62,0.10));
    border: 1px solid rgba(13,110,62,0.20);
    color: #0D6E3E;
  }
  .login-alert i{
    flex-shrink: 0;
    font-size: 1.05rem;
    margin-top: 1px;
  }
  .login-alert b{ font-weight: 700; }

  /* Footer */
  .pavilion-footer{
    text-align: center;
    margin-top: 1.8rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: .62rem;
    letter-spacing: .22em;
    color: rgba(10,15,30,0.35);
    text-transform: uppercase;
    animation: fadeRise .9s .3s ease both;
  }
  .pavilion-footer span{
    display:inline-flex; align-items:center; gap:.5rem;
  }
  .pavilion-footer i{ color: #C9A846; font-size:.8rem; }

  /* Animations */
  @keyframes fadeRise{
    from{ opacity:0; transform: translateY(18px); }
    to  { opacity:1; transform: translateY(0); }
  }
  @keyframes spinSlow{
    to { transform: rotate(360deg); }
  }
  @keyframes shake{
    0%,100%{ transform: translateX(0); }
    25%    { transform: translateX(-4px); }
    75%    { transform: translateX(4px); }
  }

  /* Hide spinner default styling — let inline handle */
  body:has(#login-pavilion) [data-testid="stSpinner"]{
    display:flex; justify-content:center;
    margin-top: 1.2rem;
  }

  /* ── Visitor / public mode section ──────────────────── */
  .visitor-divider{
    display:flex; align-items:center; gap:.8rem;
    margin: 1.5rem 0 1rem;
    color: rgba(10,15,30,0.30);
    font-family: 'JetBrains Mono', monospace;
    font-size: .60rem;
    letter-spacing: .20em;
    text-transform: uppercase;
  }
  .visitor-divider::before,.visitor-divider::after{
    content:""; flex:1; height:1px;
    background: rgba(0,48,135,0.12);
  }
  /* Style the checkbox for visitor mode */
  body:has(#login-pavilion) .stCheckbox{
    display:flex; justify-content:center;
    margin-bottom: .85rem !important;
  }
  body:has(#login-pavilion) .stCheckbox label{
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: .85rem !important;
    color: rgba(10,15,30,0.55) !important;
    cursor: pointer !important;
    gap: .55rem !important;
  }
  body:has(#login-pavilion) .stCheckbox label:hover{
    color: rgba(10,15,30,0.80) !important;
  }
  /* Visitor enter button — outlined secondary style */
  .visitor-btn-wrap [data-testid="stBaseButton-secondary"],
  .visitor-btn-wrap button{
    width: 100% !important;
    background: transparent !important;
    color: #003087 !important;
    border: 1.5px solid rgba(0,48,135,0.30) !important;
    border-radius: 12px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: .80rem !important;
    font-weight: 600 !important;
    letter-spacing: .14em !important;
    text-transform: uppercase !important;
    padding: .85rem 1.2rem !important;
    transition: all .22s ease !important;
    box-shadow: none !important;
  }
  .visitor-btn-wrap [data-testid="stBaseButton-secondary"]:hover,
  .visitor-btn-wrap button:hover{
    background: rgba(0,48,135,0.05) !important;
    border-color: #003087 !important;
    box-shadow: 0 4px 14px rgba(0,48,135,0.12) !important;
    transform: translateY(-1px) !important;
  }
</style>
"""


def cargar_estilos():
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
    <style>
      [data-testid="stSidebarNav"]{display:none!important;}
      [data-testid="stSidebar"]{display:none!important;}
    </style>
    """, unsafe_allow_html=True)
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)


def mostrar_login():
    cargar_estilos()

    # Ensure token is cleared if the user is here (logged out or expired)
    from modules.auth import _js_limpiar_token
    _js_limpiar_token()

    # Sentinel marker scopes the login-only CSS
    st.markdown('<div id="login-pavilion"></div>', unsafe_allow_html=True)

    # Masthead
    st.markdown("""
    <div class="pavilion-mast">
      <div class="pavilion-mark">
        <i class="ti ti-chart-histogram"></i>
      </div>
      <h1 class="pavilion-title">Análisis <em>Estadístico</em></h1>
      <div class="pavilion-rule">
        <span class="line"></span>
        <span class="ornament">❦</span>
        <span class="line"></span>
      </div>
      <p class="pavilion-sub">
        <b>Universidad Mariano Gálvez</b> · Hábitos de pago y pruebas inferenciales
      </p>
    </div>
    """, unsafe_allow_html=True)

    # The form IS the card — no wrapper div
    with st.form("form_login", clear_on_submit=False):
        st.markdown("""
        <p class="form-eyebrow">
          <i class="ti ti-shield-lock"></i> Acceso al sistema
        </p>
        <h2 class="form-heading">Inicia tu sesión</h2>
        """, unsafe_allow_html=True)

        email = st.text_input(
            "Correo institucional",
            placeholder="usuario@umg.edu.gt",
        )
        contrasena = st.text_input(
            "Contraseña",
            type="password",
            placeholder="••••••••",
        )
        enviar = st.form_submit_button("Ingresar al sistema", use_container_width=True)

    # Result rendering (outside form so st.switch_page works)
    if enviar:
        if not email or not contrasena:
            st.markdown("""
            <div class="login-alert error">
              <i class="ti ti-alert-triangle"></i>
              <div><b>Campos incompletos.</b> Ingresa tu correo y contraseña para continuar.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("Verificando credenciales…"):
                try:
                    from modules.auth import iniciar_sesion
                    exito, mensaje = iniciar_sesion(email, contrasena)
                except Exception:
                    exito, mensaje = False, "No se pudo conectar al servicio. Intenta de nuevo más tarde."

            if exito:
                st.markdown(f"""
                <div class="login-alert success">
                  <i class="ti ti-circle-check"></i>
                  <div>{mensaje}. Redirigiendo…</div>
                </div>
                """, unsafe_allow_html=True)
                st.switch_page("pages/1_Dashboard.py")
            else:
                st.markdown(f"""
                <div class="login-alert error">
                  <i class="ti ti-lock-exclamation"></i>
                  <div><b>No fue posible iniciar sesión.</b><br/>{mensaje}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Visitor / public access ─────────────────────────────────
    st.markdown("""
    <div class="visitor-divider">Acceso público</div>
    """, unsafe_allow_html=True)

    modo_visitante = st.checkbox(
        "Acceder como visitante · solo visualización de resultados",
        key="chk_visitante",
    )
    if modo_visitante:
        st.markdown('<div class="visitor-btn-wrap">', unsafe_allow_html=True)
        if st.button(
            "Ver resultados como visitante →",
            key="btn_visitante",
            use_container_width=True,
        ):
            from modules.auth import iniciar_modo_publico
            iniciar_modo_publico()
            st.switch_page("pages/4_Resultados.py")
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="pavilion-footer">
      <span>
        <i class="ti ti-building-community"></i>
        Ingeniería en Sistemas · Campus Cobán
      </span>
    </div>
    """, unsafe_allow_html=True)


def main():
    if st.session_state.get("autenticado"):
        st.switch_page("pages/1_Dashboard.py")
    elif st.session_state.get("modo_publico"):
        st.switch_page("pages/4_Resultados.py")
    else:
        mostrar_login()


main()
