
import streamlit as st
from google import genai
import json
import urllib.request

# Configuración de la página web
st.set_page_config(page_title="IA Espacial Revolucionaria", page_icon="🚀", layout="centered")

st.title("🚀 Mi Primera IA en la Web")
st.write("Esta aplicación extrae datos en vivo del espacio y los analiza con Inteligencia Artificial.")

# Campo para que el usuario ponga su propia API Key (así tu aplicación sigue siendo 100% gratis para ti)
api_key = st.text_input("Introduce tu Gemini API Key para activar la IA:", type="password")

if st.button("🤖 ¡Analizar el Internet!"):
    if not api_key:
        st.error("Por favor, introduce una API Key válida.")
    else:
        with st.spinner("Buscando datos en vivo y consultando a la IA..."):
            try:
                # 1. Extracción de datos
                url = "http://api.open-notify.org/astros.json"
                with urllib.request.urlopen(url) as response:
                    datos_crudos = json.loads(response.read().decode('utf-8'))
                
                # 2. Configurar el cliente de IA con la clave del usuario
                client = genai.Client(api_key=api_key)
                
                instruccion = f"Actúa como un astrofísico experto. Lista en tiempo real: {json.dumps(datos_crudos)}. Haz un reporte emocionante y breve."
                
                # 3. Llamada a la IA
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=instruccion,
                )
                
                # 4. Mostrar el resultado elegantemente en la web
                st.success("¡Análisis completado con éxito!")
                st.markdown("### 📊 Reporte Generado por la IA:")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
