import os
import streamlit as st
import requests
import json
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Sistema de Búsqueda de Documentos", layout="wide")

# Título principal
st.title("Sistema de Búsqueda de Documentos")

# Configuración del servidor (permite override por variable de entorno SERVER_URL)
default_server_url = os.getenv("SERVER_URL", "http://localhost:8000")
server_url = st.sidebar.text_input("URL del Servidor", value=default_server_url)


# Función para verificar la salud del servidor
def check_health():
    try:
        response = requests.get(f"{server_url}/health")
        return response.status_code == 200
    except:
        return False


# Mostrar estado del servidor
if check_health():
    st.sidebar.success("Servidor conectado")
else:
    st.sidebar.error("Servidor no disponible")

# Tabs para diferentes funcionalidades
tab1, tab2 = st.tabs(["Búsqueda", "Gestión de Archivos"])

# Tab de Búsqueda
with tab1:
    st.header("Búsqueda de Documentos")

    # Campo de búsqueda
    search_query = st.text_input("Buscar documentos por nombre:")
    limit = st.slider("Número máximo de resultados", 1, 200, 20)

    if st.button("Buscar"):
        try:
            response = requests.get(
                f"{server_url}/search", params={"q": search_query, "limit": limit}
            )
            results = response.json()

            if results["count"] > 0:
                for item in results["items"]:
                    with st.expander(f"📄 {item['name']}"):
                        st.text(f"ID: {item['file_id']}")
                        st.text(f"Ruta: {item['path']}")
                        if item["mime_type"]:
                            st.text(f"Tipo MIME: {item['mime_type']}")
                        if item["size"]:
                            st.text(f"Tamaño: {item['size']} bytes")
                        if item["last_modified"]:
                            date = datetime.fromtimestamp(item["last_modified"])
                            st.text(f"Última modificación: {date}")
            else:
                st.info("No se encontraron resultados")
        except Exception as e:
            st.error(f"Error al buscar: {str(e)}")

# Tab de Gestión de Archivos
with tab2:
    st.header("Gestión de Archivos")

    # Formulario para agregar/actualizar archivo
    with st.form("file_form"):
        file_id = st.text_input("ID del Archivo")
        name = st.text_input("Nombre del Archivo")
        path = st.text_input("Ruta del Archivo")
        mime_type = st.text_input("Tipo MIME (opcional)")
        size = st.number_input("Tamaño en bytes (opcional)", min_value=0)

        submitted = st.form_submit_button("Guardar Archivo")

        if submitted:
            try:
                data = {
                    "file_id": file_id,
                    "name": name,
                    "path": path,
                    "mime_type": mime_type or None,
                    "size": size or None,
                    "last_modified": int(datetime.now().timestamp()),
                    "indexed_at": int(datetime.now().timestamp()),
                }

                response = requests.post(f"{server_url}/files", json=data)

                if response.status_code == 200:
                    st.success("Archivo guardado exitosamente")
                else:
                    st.error("Error al guardar el archivo")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Eliminar archivo
    st.subheader("Eliminar Archivo")
    delete_id = st.text_input("ID del archivo a eliminar")
    if st.button("Eliminar"):
        try:
            response = requests.delete(f"{server_url}/files/{delete_id}")
            if response.status_code == 200:
                st.success("Archivo eliminado exitosamente")
            else:
                st.error("Error al eliminar el archivo")
        except Exception as e:
            st.error(f"Error: {str(e)}")
