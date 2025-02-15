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

def login(username, password):
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
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Guardar el token en la sesión
        if response.status_code == 200:
            st.session_state['token'] = response.text
            return True, "Login exitoso"
        
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
        submit = st.form_submit_button("Iniciar Sesión")
        
        if submit:
            success, message = login(username, password)
            if success:
                st.success(message)
                st.experimental_rerun()
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
            del st.session_state['token']
            st.experimental_rerun()
            
    else:
        st.error(message)
        del st.session_state['token']
        st.experimental_rerun()

# Footer con información
st.markdown("---")
st.markdown(f"Conectado a: {BASE_URL}")
