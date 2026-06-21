import streamlit as st
from google import genai
from duckduckgo_search import DDGS
import sqlite3
from datetime import datetime

# Configuración visual de la web
st.set_page_config(page_title="IA con Memoria Autónoma", page_icon="🧠", layout="centered")

st.title("🧠 IA con Memoria y Aprendizaje Continuo")
st.write("Esta IA no solo busca en internet, sino que guarda lo aprendido en su base de datos para volverse más inteligente con cada búsqueda.")

# --- APARTADO DE BASE DE DATOS (MEMORIA) ---
def inicializar_memoria():
    conn = sqlite3.connect("memoria_ia.db")
    cursor = conn.cursor()
    # Creamos la tabla donde la IA guardará sus conocimientos si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conocimiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tema TEXT,
            aprendizaje TEXT,
            fecha TEXT
        )
    """)
    conn.commit()
    conn.close()

def guardar_en_memoria(tema, aprendizaje):
    conn = sqlite3.connect("memoria_ia.db")
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO conocimiento (tema, aprendizaje, fecha) VALUES (?, ?, ?)", (tema, aprendizaje, fecha_actual))
    conn.commit()
    conn.close()

def recuperar_memoria():
    conn = sqlite3.connect("memoria_ia.db")
    cursor = conn.cursor()
    cursor.execute("SELECT tema, aprendizaje, fecha FROM conocimiento ORDER BY id DESC LIMIT 5")
    recuerdos = cursor.fetchall()
    conn.close()
    return recuerdos

# Inicializar la base de datos al cargar la página
inicializar_memoria()

# --- INTERFAZ WEB ---
api_key = st.text_input("Introduce tu Gemini API Key:", type="password")
busqueda_usuario = st.text_input("¿Qué quieres que la IA investigue y aprenda hoy?:", placeholder="Ej: Precios de mercado, tendencias...")

if st.button("🔍 Investigar, Aprender y Guardar"):
    if not api_key:
        st.error("Por favor, introduce tu API Key.")
    elif not busqueda_usuario:
        st.error("Por favor, escribe un tema.")
    else:
        with st.spinner("Buscando en la web y consultando recuerdos..."):
            try:
                # 1. Recuperar los últimos aprendizajes de la IA para darle contexto
                conocimientos_previos = recuperar_memoria()
                recuerdos_texto = ""
                if conocimientos_previos:
                    recuerdos_texto = "\n".join([f"- Sobre '{r[0]}': {r[1]} (Guardado el {r[2]})" for r in conocimientos_previos])
                
                # 2. Buscar datos frescos en internet
                resultados_web = []
                with DDGS() as ddgs:
                    for r in ddgs.text(busqueda_usuario, max_results=3):
                        resultados_web.append(f"Título: {r['title']}\nResumen: {r['body']}\n---")
                texto_internet = "\n".join(resultados_web)
                
                # 3. Conectar con Gemini enviándole el internet + sus propios recuerdos
                client = genai.Client(api_key=api_key)
                
                instruccion = f"""
                Actúa como una IA con memoria evolutiva. Tu objetivo es responder al usuario y extraer un conocimiento clave para guardar en tu base de datos.
                
                El usuario pregunta por: '{busqueda_usuario}'.
                
                Tus recuerdos/aprendizajes anteriores son:
                {recuerdos_texto if recuerdos_texto else 'Aún no tienes recuerdos guardados.'}
                
                Datos frescos de internet en este momento:
                {texto_internet}
                
                Por favor:
                1. Responde a la pregunta del usuario combinando lo nuevo de internet con lo que ya sabías en tus recuerdos (si está relacionado).
                2. Al final, escribe una línea exacta que empiece con 'APRENDIZAJE_CLAVE:' seguido de un resumen de un párrafo con el dato más importante que descubriste hoy y quieres recordar para siempre.
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=instruccion,
                )
                
                respuesta_completa = response.text
                
                # 4. Procesar el aprendizaje y guardarlo en SQLite
                if "APRENDIZAJE_CLAVE:" in respuesta_completa:
                    partes = respuesta_completa.split("APRENDIZAJE_CLAVE:")
                    respuesta_usuario = partes[0]
                    aprendizaje_a_guardar = partes[1].strip()
                    # Guardamos el dato en la base de datos para la próxima vez
                    guardar_en_memoria(busqueda_usuario, aprendizaje_a_guardar)
                    st.success("🤖 ¡He aprendido algo nuevo y lo guardé en mi memoria!")
                else:
                    respuesta_usuario = respuesta_completa
                
                st.markdown("### 📋 Respuesta de la IA:")
                st.write(respuesta_usuario)
                
            except Exception as e:
                st.error(f"Error: {e}")

# --- MOSTRAR LA MEMORIA EN LA PANTALLA ---
st.write("---")
st.subheader("🧠 Cuaderno de Recuerdos de la IA (Base de datos SQLite)")
recuerdos_actuales = recuperar_memoria()
if recuerdos_actuales:
    for r in recuerdos_actuales:
        st.info(f"**Tema:** {r[0]} | **Fecha:** {r[2]}\n\n**Lo que aprendí:** {r[1]}")
else:
    st.write("Mi memoria está vacía. ¡Haz una búsqueda para que empiece a aprender!")
