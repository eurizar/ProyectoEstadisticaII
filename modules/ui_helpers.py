"""Helpers de UI compartidos entre todas las paginas."""

import streamlit as st
from pathlib import Path


def cargar_estilos(es_pagina: bool = True):
    """Inyecta Google Fonts, Tabler Icons, CSS y orbs animados."""
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.19.0/dist/tabler-icons.min.css">
    <div class="bg-orbs" aria-hidden="true">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
    </div>
    """, unsafe_allow_html=True)

    css_path = Path(__file__).parent.parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Loader lives outside Streamlit's React tree so navigation doesn't reset it.
    # The script creates the element once and appends to document.body of the
    # parent frame; subsequent calls from other pages find it already there.
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function(){
      var doc = (window.parent && window.parent.document) ? window.parent.document : document;
      var win = window.parent || window;

      function setup() {
        if (!doc.body) { setTimeout(setup, 50); return; }

        // No necesitamos buscar #unauth-marker aquí. auth.py inyecta su propio script.

        // Create loader element only once — persists across client-side navigations
        if (!doc.getElementById('appLoader')) {
          var bars = '';
          for (var i = 0; i < 12; i++) bars += '<div class="bar"></div>';
          var el = doc.createElement('div');
          el.id = 'appLoader';
          el.className = 'app-loader';
          el.setAttribute('aria-hidden', 'true');
          el.innerHTML = '<div class="loader-card">'
            + '<div class="apple-spinner">' + bars + '</div>'
            + '<div class="loader-label">Cargando</div>'
            + '</div>';
          doc.body.appendChild(el);

          win.hideAppLoader = function(){ 
            var l = doc.getElementById('appLoader');
            if(l) l.classList.remove('show'); 
          };
          win.showAppLoader = function(){ 
            var l = doc.getElementById('appLoader');
            if(l) l.classList.add('show'); 
          };

          // Show on sidebar nav-link click (capture phase)
          doc.addEventListener('click', function(e) {
            var link = e.target.closest(
              '[data-testid="stSidebar"] [data-testid="stPageLink"] a,' +
              '[data-testid="stSidebar"] a[href]'
            );
            if (link) {
              win.showAppLoader();
              win.clearTimeout(win._loaderSafety);
              // Use win.setTimeout so it survives iframe destruction!
              win._loaderSafety = win.setTimeout(win.hideAppLoader, 4000);
            }
          }, true);
        }

        // ALWAYS attempt to hide the loader when this script runs (page loaded)
        if (win.hideAppLoader) {
            win.hideAppLoader();
        }

        // Hide when stMain content updates (page finished rendering)
        function watchMain() {
          var main = doc.querySelector('[data-testid="stMain"]');
          if (!main) { setTimeout(watchMain, 150); return; }
          var obs = new MutationObserver(function() {
            var loader = doc.getElementById('appLoader');
            if (loader && loader.classList.contains('show') && win.hideAppLoader) {
              win.clearTimeout(win._loaderHideT);
              win._loaderHideT = win.setTimeout(win.hideAppLoader, 300);
            }
          });
          obs.observe(main, { childList: true, subtree: true });
        }
        watchMain();
      }

      setup();
    })();
    </script>
    """, height=1)


# Inline SVG icons — Lucide/Tabler style, stroke-based, 24x24 viewBox.
_NAV_ICONS = {
    "dashboard": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M3 13a9 9 0 1 1 18 0"/><path d="M12 13l4-5"/><circle cx="12" cy="13" r="1.5"/></svg>""",
    "upload": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>""",
    "flask": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6"/><path d="M10 3v6L4.5 18a2 2 0 0 0 1.7 3h11.6a2 2 0 0 0 1.7-3L14 9V3"/><line x1="7.5" y1="14" x2="16.5" y2="14"/><circle cx="10" cy="17" r=".8" fill="currentColor"/><circle cx="14" cy="18.5" r=".8" fill="currentColor"/></svg>""",
    "chart": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="20" x2="20" y2="20"/><rect x="6" y="12" width="3" height="6" rx="1"/><rect x="11" y="8" width="3" height="10" rx="1"/><rect x="16" y="4" width="3" height="14" rx="1"/></svg>""",
    "history": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7"/><polyline points="3 4 3 9 8 9"/><polyline points="12 7 12 12 15 14"/></svg>""",
    "pdf": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><polyline points="14 3 14 8 19 8"/><path d="M9 14h.5a1.5 1.5 0 0 1 0 3H9zM13 14v3M13 14h1.5M13 15.5h1"/></svg>""",
}


def sidebar_usuario(pagina_actual: str = ""):
    """Renderiza el sidebar con navegacion y datos del usuario."""
    from modules.auth import es_modo_publico
    es_publico = es_modo_publico()

    with st.sidebar:
        if es_publico:
            st.html("""
            <div class="sb-user slide-in">
                <div class="sb-avatar" style="background:linear-gradient(140deg,#5a6a8a,#8896A5);font-size:1.1rem">
                    &#128065;
                </div>
                <div>
                    <span class="sb-label" style="color:rgba(255,255,255,0.45)">Modo visitante</span>
                    <div class="sb-email" style="color:rgba(255,255,255,0.60);font-size:.75rem">
                        Solo visualización
                    </div>
                </div>
            </div>
            <div class="sb-divider"></div>
            <p class="umg-nav-title">Navegación</p>
            """)
        else:
            email = st.session_state.get("user_email", "usuario@umg.edu.gt")
            inicial = email[0].upper()
            st.html(f"""
            <div class="sb-user slide-in">
                <div class="sb-avatar">{inicial}</div>
                <div>
                    <span class="sb-label">Usuario activo</span>
                    <div class="sb-email">{email}</div>
                </div>
            </div>
            <div class="sb-divider"></div>
            <p class="umg-nav-title">Navegación</p>
            """)

        # Nav items — public mode: Dashboard y Resultados activos, resto deshabilitado
        nav_items = [
            ("pages/1_Dashboard.py",      "Dashboard",      ":material/space_dashboard:",  True),
            ("pages/2_Cargar_Datos.py",   "Cargar Datos",   ":material/cloud_upload:",     False),
            ("pages/3_Nuevo_Analisis.py", "Nuevo Análisis", ":material/science:",          False),
            ("pages/4_Resultados.py",     "Resultados",     ":material/bar_chart:",        True),
            ("pages/5_Historico.py",      "Histórico",      ":material/history:",          False),
            ("pages/6_Exportar.py",       "Exportar PDF",   ":material/picture_as_pdf:",   False),
        ]

        _DISABLED_ICONS = {
            ":material/space_dashboard:": "ti ti-layout-dashboard",
            ":material/cloud_upload:":    "ti ti-cloud-upload",
            ":material/science:":         "ti ti-flask",
            ":material/bar_chart:":       "ti ti-chart-bar",
            ":material/history:":         "ti ti-history",
            ":material/picture_as_pdf:":  "ti ti-file-type-pdf",
        }

        _TOOLTIP = "Requiere inicio de sesión · Esta sección está disponible solo para usuarios registrados de UMG"

        for page_path, label, icon, publico_ok in nav_items:
            if es_publico and not publico_ok:
                ti = _DISABLED_ICONS.get(icon, "ti ti-lock")
                st.html(f"""
                <div title="{_TOOLTIP}" style="
                    display:flex;align-items:center;gap:10px;
                    padding:10px 14px;border-radius:10px;
                    color:rgba(255,255,255,0.22);
                    font-size:.85rem;font-family:sans-serif;
                    cursor:not-allowed;user-select:none;
                    margin-bottom:2px;
                    position:relative;
                ">
                    <i class="{ti}" style="font-size:.95rem;width:18px;text-align:center"></i>
                    <span>{label}</span>
                    <i class="ti ti-lock" style="font-size:.7rem;margin-left:auto;opacity:.6"></i>
                </div>
                """)
            else:
                st.page_link(page_path, label=label, icon=icon, use_container_width=True)

        st.html('<div class="sb-divider"></div>')

        if es_publico:
            if st.button("Salir del modo visitante", use_container_width=True, key="btn_salir_visitante"):
                from modules.auth import cerrar_modo_publico
                cerrar_modo_publico()
                st.switch_page("app.py")
        else:
            if st.button("Cerrar sesión", use_container_width=True, key="btn_logout_sidebar"):
                from modules.auth import cerrar_sesion
                cerrar_sesion()
                st.switch_page("app.py")

        st.html('<div class="sb-footer">Estadística II · UMG Cobán · 2026</div>')

def lanzar_confeti():
    """Inyecta y ejecuta canvas-confetti en la ventana principal de la aplicación."""
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
            var win = window.parent || window;
            if (!win.confetti) {
                var script = win.document.createElement('script');
                script.src = "https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js";
                script.onload = function() {
                    win.confetti({
                        particleCount: 150,
                        spread: 80,
                        origin: { y: 0.6 },
                        colors: ['#003087', '#C8102E', '#C9A846', '#4FC3F7']
                    });
                };
                win.document.head.appendChild(script);
            } else {
                win.confetti({
                    particleCount: 150,
                    spread: 80,
                    origin: { y: 0.6 },
                    colors: ['#003087', '#C8102E', '#C9A846', '#4FC3F7']
                });
            }
        </script>
        """,
        height=0,
    )
