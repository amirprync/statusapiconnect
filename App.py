import streamlit as st
import requests
import json

# Configuración de la página
st.set_page_config(page_title="Login API Cohen", layout="wide")

# URL base de la API
BASE_URL = "https://connect.cohen.com.ar"

def get_full_url(endpoint):
    """Función para construir la URL completa"""
    return f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

def login(username, password, validation_code=None):
    """Función para realizar el login"""
    url = get_full_url("Token")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "userName": username,
        "password": password,
        "rememberMe": False
    }

    # Agregar código de validación si está presente
    if validation_code:
        payload["code"] = validation_code
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        # Si el status es 200, el login fue exitoso
        if response.status_code == 200:
            st.session_state['token'] = response.text
            return True, "Login exitoso"
        
        # Si recibimos otro código, puede ser que necesite 2FA
        try:
            error_data = response.json()
            if "requiresToken" in error_data and error_data["requiresToken"]:
                return False, "2FA_REQUIRED"
        except:
            pass
            
        return False, f"Error en la respuesta: {response.status_code}"
        
    except requests.exceptions.RequestException as e:
        return False, f"Error en la conexión: {str(e)}"

def verify_token():
    """Función para verificar el token"""
    if 'token' not in st.session_state:
        return False, "No hay token"
        
    url = get_full_url("api/Authorize/UserInfo")
    
    headers = {
        "Authorization": f"Bearer {st.session_state['token']}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return data["isAuthenticated"], "Token verificado" if data["isAuthenticated"] else "Token inválido"
        
    except requests.exceptions.RequestException as e:
        return False, f"Error en la verificación: {str(e)}"

# Interfaz de usuario
st.title("Login API Cohen")

# Si no hay token, mostrar formulario de login
if 'token' not in st.session_state:
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        # Mostrar campo de código de validación si ya intentó login
        if 'awaiting_2fa' in st.session_state and st.session_state['awaiting_2fa']:
            validation_code = st.text_input("Código de Validación")
        else:
            validation_code = None
            
        submit = st.form_submit_button("Iniciar Sesión")
        
        if submit:
            # Guardar credenciales en sesión si es primer intento
            if not st.session_state.get('awaiting_2fa'):
                st.session_state['temp_username'] = username
                st.session_state['temp_password'] = password
            
            # Usar credenciales guardadas si es segundo intento
            if st.session_state.get('awaiting_2fa'):
                username = st.session_state['temp_username']
                password = st.session_state['temp_password']
            
            success, message = login(username, password, validation_code)
            
            if message == "2FA_REQUIRED":
                st.session_state['awaiting_2fa'] = True
                st.warning("Por favor, ingrese el código de validación")
                st.rerun()
            elif success:
                # Limpiar variables temporales
                if 'temp_username' in st.session_state:
                    del st.session_state['temp_username']
                if 'temp_password' in st.session_state:
                    del st.session_state['temp_password']
                if 'awaiting_2fa' in st.session_state:
                    del st.session_state['awaiting_2fa']
                    
                st.success("Login exitoso")
                st.rerun()
            else:
                st.error(message)

# Si hay token, mostrar información y opciones
else:
    success, message = verify_token()
    if success:
        st.success("Sesión activa")
        
        # Mostrar el token
        if st.checkbox("Mostrar Token"):
            st.code(st.session_state['token'], language="text")
        
        # Botón para cerrar sesión
        if st.button("Cerrar Sesión"):
            # Limpiar toda la sesión
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
    else:
        st.error(message)
        # Limpiar toda la sesión
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Footer con información
st.markdown("---")
st.markdown(f"Conectado a: {BASE_URL}")

# Mostrar información de la sesión para debugging
if st.checkbox("Mostrar información de debug"):
    st.write("Estado de la sesión:", st.session_state)
