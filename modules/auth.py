"""Autenticacion de usuarios con Supabase Auth."""

import json
import streamlit as st
import streamlit.components.v1 as components
from modules.db import obtener_cliente


# ── Helpers de localStorage ────────────────────────────────────────────────

def _js_guardar_token(token: str) -> None:
    """Persiste el refresh_token en localStorage y Cookies para sobrevivir recargas sin parpadeos."""
    components.html(
        f"""<script>
        try {{
            var win = window.parent || window;
            win.localStorage.setItem('umg_rt', '{token}');
            // Guardar en cookie para lectura sincrona en Python
            var script = win.document.createElement('script');
            script.type = 'text/javascript';
            script.innerHTML = "document.cookie = 'umg_rt={token}; path=/; max-age=2592000; SameSite=Lax';";
            win.document.body.appendChild(script);
        }} catch(e) {{
            console.error('[Auth] Error al guardar token:', e);
        }}
        </script>""",
        height=0,
    )


def _js_limpiar_token() -> None:
    """Elimina el refresh_token del localStorage y Cookies (logout)."""
    components.html(
        """<script>
        try {
            var win = window.parent || window;
            win.localStorage.removeItem('umg_rt');
            var script = win.document.createElement('script');
            script.type = 'text/javascript';
            script.innerHTML = "document.cookie = 'umg_rt=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';";
            win.document.body.appendChild(script);
        } catch(e) {}
        </script>""",
        height=0,
    )


def _js_guardar_publico() -> None:
    """Persiste el flag de modo publico en localStorage y Cookie para sobrevivir recargas."""
    components.html(
        """<script>
        try {
            var win = window.parent || window;
            win.localStorage.setItem('umg_pub', '1');
            var script = win.document.createElement('script');
            script.type = 'text/javascript';
            script.innerHTML = "document.cookie = 'umg_pub=1; path=/; max-age=86400; SameSite=Lax';";
            win.document.body.appendChild(script);
        } catch(e) {}
        </script>""",
        height=0,
    )


def _js_limpiar_publico() -> None:
    """Elimina el flag de modo publico del localStorage y Cookie."""
    components.html(
        """<script>
        try {
            var win = window.parent || window;
            win.localStorage.removeItem('umg_pub');
            var script = win.document.createElement('script');
            script.type = 'text/javascript';
            script.innerHTML = "document.cookie = 'umg_pub=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';";
            win.document.body.appendChild(script);
        } catch(e) {}
        </script>""",
        height=0,
    )


# ── Autenticacion ──────────────────────────────────────────────────────────

def iniciar_sesion(email: str, contrasena: str) -> tuple[bool, str]:
    """Autentica con Supabase y persiste la sesion en session_state."""
    try:
        cliente = obtener_cliente()
        respuesta = cliente.auth.sign_in_with_password({
            "email": email,
            "password": contrasena,
        })
        usuario = respuesta.user
        sesion  = respuesta.session
        if usuario and sesion:
            st.session_state["autenticado"]   = True
            st.session_state["user_id"]       = usuario.id
            st.session_state["user_email"]    = usuario.email
            st.session_state["access_token"]  = sesion.access_token
            st.session_state["refresh_token"] = sesion.refresh_token
            st.session_state.pop("modo_publico", None)
            _js_limpiar_publico()
            return True, f"Bienvenido, {usuario.email}"
        return False, "Credenciales incorrectas."
    except Exception as e:
        msg = str(e)
        if "Invalid login credentials" in msg:
            return False, "Email o contrasena incorrectos."
        if "Email not confirmed" in msg:
            return False, "Debes confirmar tu email antes de ingresar."
        return False, f"Error de autenticacion: {msg}"


def cerrar_sesion() -> None:
    """Cierra sesion en Supabase y limpia session_state."""
    try:
        obtener_cliente().auth.sign_out()
    except Exception:
        pass
    for clave in ["autenticado", "user_id", "user_email",
                  "access_token", "refresh_token",
                  "df_encuestas", "ultimo_analisis"]:
        st.session_state.pop(clave, None)
    # The localStorage cleanup will happen in app.py or the unauth marker.

def verificar_sesion() -> bool:
    return st.session_state.get("autenticado", False)

def _restaurar_sesion(refresh_token: str) -> bool:
    """Llama a Supabase refresh_session con el token guardado. True = ok."""
    try:
        from modules.db import obtener_cliente_base
        cliente = obtener_cliente_base()
        resp = cliente.auth.refresh_session(refresh_token)
        if resp and resp.session:
            st.session_state["autenticado"]   = True
            st.session_state["user_id"]       = resp.user.id
            st.session_state["user_email"]    = resp.user.email
            st.session_state["access_token"]  = resp.session.access_token
            st.session_state["refresh_token"] = resp.session.refresh_token
            _js_guardar_token(resp.session.refresh_token)
            return True
    except Exception:
        pass
    return False


def es_modo_publico() -> bool:
    return st.session_state.get("modo_publico", False)


def iniciar_modo_publico() -> None:
    for clave in ["autenticado", "user_id", "user_email", "access_token", "refresh_token"]:
        st.session_state.pop(clave, None)
    st.session_state["modo_publico"] = True
    _js_guardar_publico()


def cerrar_modo_publico() -> None:
    st.session_state.pop("modo_publico", None)
    _js_limpiar_publico()


def requerir_autenticacion(permitir_publico: bool = False) -> None:
    """
    Llama al inicio de cada pagina protegida.
    Flujo de restauracion (orden de prioridad):
      1. session_state ya tiene sesion autenticada → ok (ignora visitor cookie)
      2. Cookie umg_rt valida → restaura sesion → ok
      3. URL ?_rt=TOKEN → restaura sesion → ok
      4. session_state modo_publico activo → visitor mode
      5. Cookie umg_pub=1 → visitor mode (solo si no hay sesion auth)
      6. Nada → JS fallback via localStorage → stop
    """
    # ── Autenticacion: mayor prioridad, ignora cookies de visitante ────────
    if verificar_sesion():
        rt = st.session_state.get("refresh_token")
        if rt:
            _js_guardar_token(rt)
        return

    # Restauracion via cookie de auth
    if hasattr(st, "context") and hasattr(st.context, "cookies"):
        cookie_rt = st.context.cookies.get("umg_rt")
        if cookie_rt:
            if _restaurar_sesion(cookie_rt):
                return
            _js_limpiar_token()

    # Restauracion via parametro URL
    rt = st.query_params.get("_rt", "")
    if rt:
        if _restaurar_sesion(rt):
            try:
                del st.query_params["_rt"]
            except Exception:
                pass
            return
        _js_limpiar_token()
        try:
            del st.query_params["_rt"]
        except Exception:
            pass

    # ── Visitor mode: solo si no hay sesion autenticada ────────────────────
    if es_modo_publico():
        if permitir_publico:
            _js_guardar_publico()
            return
        st.switch_page("pages/4_Resultados.py")

    if hasattr(st, "context") and hasattr(st.context, "cookies"):
        if st.context.cookies.get("umg_pub") == "1":
            st.session_state["modo_publico"] = True
            if permitir_publico:
                return
            st.switch_page("pages/4_Resultados.py")

    # Componente que intenta restaurar la sesión sorteando el sandbox del iframe
    components.html("""
    <script>
      console.log('[Auth] Iniciando script de recuperacion...');
      var win = window.parent || window;
      var doc = win.document;
      var rt = '';
      try { 
          rt = win.localStorage.getItem('umg_rt') || ''; 
          console.log('[Auth] Token recuperado:', rt ? 'Si (longitud ' + rt.length + ')' : 'No (vacio)');
      } catch(e) {
          console.error('[Auth] Error al recuperar token:', e);
      }
      
      if (rt) {
        console.log('[Auth] Inyectando script en el padre para restaurar sesion...');
        var url = new URL(win.location.href);
        url.searchParams.set('_rt', rt);
        
        // Inyectar el script directamente en el body del parent para evadir el iframe sandbox (SecurityError)
        var script = doc.createElement('script');
        script.type = 'text/javascript';
        script.innerHTML = "window.location.replace('" + url.toString() + "');";
        doc.body.appendChild(script);
      } else {
        console.log('[Auth] No hay token para recuperar.');
      }
    </script>
    """, height=0)

    st.warning("Verificando sesión... Si no eres redirigido, por favor inicia sesión de nuevo.")
    if st.button("Ir al inicio de sesion", type="primary"):
        st.switch_page("app.py")
    st.stop()


# ── Getters ────────────────────────────────────────────────────────────────

def obtener_user_id() -> str | None:
    return st.session_state.get("user_id")


def obtener_user_email() -> str | None:
    return st.session_state.get("user_email")
