import subprocess
import sys
import os
import re
import streamlit as st
import pandas as pd

# -------------------------------------------------------------------
# INSTALACIÓN AUTOMÁTICA DE CHROMIUM EN STREAMLIT CLOUD
# -------------------------------------------------------------------
@st.cache_resource
def instalar_navegador():
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

try:
    instalar_navegador()
except Exception as e:
    st.error(f"Error instalando Chromium: {e}")

from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Juan Modo Dios", page_icon="🏎️", layout="wide")

# --- ESTILO VISUAL (COMPATIBLE CON MODO OSCURO) ---
st.markdown("""
<style>
    button[kind="primary"] { background-color: #B3000C !important; color: white !important; border-radius: 6px !important; font-weight: bold !important; border: none !important; padding: 0.6rem 2rem !important; }
    button[kind="primary"]:hover { background-color: #8A0009 !important; }
    button[kind="secondary"] { background-color: #333333 !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; }
    button[kind="secondary"]:hover { background-color: #000000 !important; }
    h1, h2, h3 { color: #B3000C !important; }
    .stTextArea textarea { border: 1px solid #B3000C !important; }
    code { color: #B3000C !important; font-size: 16px !important; font-weight: bold !important; border-left: 5px solid #B3000C !important; }
    [data-testid="stAlert"] { background-color: #1E1E1E !important; border-left: 5px solid #B3000C !important; color: #FFFFFF !important; }
    [data-testid="stAlert"] p { color: #FFFFFF !important; font-weight: 500 !important; }
</style>
""", unsafe_allow_html=True)

# --- MEMORIA DE JUAN ---
if "resultados" not in st.session_state:
    st.session_state.resultados = []
    st.session_state.lista_referencias = []
    st.session_state.indice_actual = 0
    st.session_state.estado = "ESPERANDO" 

col_logo, col_titulo = st.columns([1.5, 5.5])
with col_logo:
    if os.path.exists("logo.jpg"): st.image("logo.jpg", width=220)
    elif os.path.exists("logo.png"): st.image("logo.png", width=220)

with col_titulo:
    st.title("Juan 🤖 - Extracción Modo Dios")
    st.markdown("Armado con **sangre, sudor, lágrimas** y el infalible **Protocolo Fantasma**.")

st.divider()

def extraer_peso_universal(texto):
    if not texto: return None
    m_lb = re.search(r'Weight[\s\n:-]*(\d*[\.,]?\d+)[\s\n]*(lb|lbs)\b', texto, re.IGNORECASE)
    if not m_lb: m_lb = re.search(r'(\d*[\.,]?\d+)[\s\n]*(lb|lbs)\b', texto, re.IGNORECASE)
    if m_lb:
        try: return float(m_lb.group(1).replace(",", "."))
        except: pass
    m_oz = re.search(r'Weight[\s\n:-]*(\d*[\.,]?\d+)[\s\n]*(oz|ounce|ounces)\b', texto, re.IGNORECASE)
    if not m_oz: m_oz = re.search(r'(\d*[\.,]?\d+)[\s\n]*(oz|ounce|ounces)\b', texto, re.IGNORECASE)
    if m_oz:
        try: return float(m_oz.group(1).replace(",", ".")) / 16.0
        except: pass
    m_kg = re.search(r'(\d*[\.,]?\d+)[\s\n]*(kg|kilo|kilograms)\b', texto, re.IGNORECASE)
    if m_kg:
        try: return float(m_kg.group(1).replace(",", ".")) * 2.20462
        except: pass
    return None

def limpiar_popups(page):
    botones = ["No", "Dismiss", "I Accept", "Accept", "Close", "Select Later", "Decline"]
    for btn_txt in botones:
        try:
            elem = page.locator(f"button:has-text('{btn_txt}')")
            if elem.count() > 0 and elem.first.is_visible():
                elem.first.click(timeout=300)
        except: pass

st.write("### 1. Juan está listo. Pega tu lista de combate aquí:")
referencias_input = st.text_area("Lista de Referencias:", height=150, placeholder="Pega tus referencias y déjamelo a mí...")

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🚀 Que comience la magia", type="primary"):
        lista_limpia = [r.strip() for r in referencias_input.split('\n') if r.strip()]
        if lista_limpia:
            st.session_state.lista_referencias = lista_limpia
            st.session_state.resultados = []
            st.session_state.indice_actual = 0
            st.session_state.estado = "PROCESANDO"
        else:
            st.warning("Juan dice: ¡Oye! Necesito al menos una referencia para trabajar.")

with col_btn2:
    if st.session_state.estado in ["PAUSADO", "PROCESANDO"] and 0 < st.session_state.indice_actual < len(st.session_state.lista_referencias):
        if st.button("▶️ Juan, continúa", type="primary"):
            st.session_state.estado = "PROCESANDO"

with col_btn3:
    if st.session_state.estado == "PROCESANDO":
        if st.button("🛑 ¡JUAN, DETENTE!", type="secondary"):
            st.session_state.estado = "PAUSADO"

st.write("---")

if st.session_state.estado == "PROCESANDO":
    total = len(st.session_state.lista_referencias)
    st.info("🔥 Juan operando en las sombras. Cruzando redes globales de información.")
    barra_progreso = st.progress(st.session_state.indice_actual / total)
    texto_progreso = st.empty()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        ) 
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        while st.session_state.indice_actual < total:
            idx = st.session_state.indice_actual
            ref = st.session_state.lista_referencias[idx].upper()
            
            texto_progreso.text(f"Juan hackeando el peso de: {ref} ({idx + 1} de {total})")
            barra_progreso.progress((idx + 1) / total)
            peso_lb_encontrado = None
            
            try:
                # MOTOR 1: John Deere Shop
                url_shop = f"https://shop.deere.com/us/search?text={ref}&productType=all"
                page.goto(url_shop, timeout=25000)
                page.wait_for_timeout(1000)
                limpiar_popups(page)
                
                if "/p/" not in page.url and "/product/" not in page.url:
                    enlaces = page.locator('a[href*="/p/"], a[href*="/product/"], a.product-name, a.name')
                    if enlaces.count() > 0:
                        try:
                            enlaces.first.click(force=True, timeout=3000)
                            page.wait_for_timeout(1500)
                            limpiar_popups(page)
                        except: pass
                
                try:
                    tab_details = page.locator("text=/Product Details|Specifications/i")
                    if tab_details.count() > 0 and tab_details.first.is_visible():
                        tab_details.first.click(timeout=1000)
                except: pass

                for pos in [400, 800, 1200]:
                    page.evaluate(f"window.scrollTo(0, {pos})")
                    page.wait_for_timeout(300)
                    limpiar_popups(page)
                    texto_pagina = page.evaluate("document.body.innerText")
                    peso_lb_encontrado = extraer_peso_universal(texto_pagina)
                    if peso_lb_encontrado is not None: break 
                
                # MOTOR 2: RDO Equipment
                if peso_lb_encontrado is None:
                    texto_progreso.text(f"Juan triangulando {ref} en servidores secundarios...")
                    url_rdo = f"https://www.rdoequipment.com/search?q={ref}"
                    try:
                        page.goto(url_rdo, timeout=20000)
                        page.wait_for_timeout(1500)
                        rdo_links = page.locator("a.product-title, a[href*='/product/']")
                        if rdo_links.count() > 0:
                            rdo_links.first.click(force=True, timeout=2500)
                            page.wait_for_timeout(1200)
                        texto_rdo = page.evaluate("document.body.innerText")
                        peso_lb_encontrado = extraer_peso_universal(texto_rdo)
                    except: pass

                # MOTOR 3: GreenPartStore
                if peso_lb_encontrado is None:
                    texto_progreso.text(f"Juan forzando extracción profunda para: {ref}...")
                    url_gps = f"https://www.greenpartstore.com/search.html?Search={ref}"
                    try:
                        page.goto(url_gps, timeout=20000)
                        page.wait_for_timeout(1000)
                        gps_links = page.locator(".product_title a, .product-title a, a[href*='John-Deere']")
                        if gps_links.count() > 0:
                            gps_links.first.click(force=True, timeout=3000)
                            page.wait_for_timeout(1000)
                        
                        for pos in [400, 800]:
                            page.evaluate(f"window.scrollTo(0, {pos})")
                            page.wait_for_timeout(300)
                            texto_gps = page.evaluate("document.body.innerText")
                            peso_lb_encontrado = extraer_peso_universal(texto_gps)
                            if peso_lb_encontrado is not None: break
                    except: pass

                # MOTOR 4: Google
                if peso_lb_encontrado is None:
                    texto_progreso.text(f"Activando Modo Dios en la red global para: {ref}...")
                    url_google = f"https://www.google.com/search?q=John+Deere+part+{ref}+weight+lbs+oz"
                    try:
                        page.goto(url_google, timeout=20000)
                        page.wait_for_timeout(1200)
                        try:
                            page.locator("button:has-text('Aceptar todo'), button:has-text('Accept all')").click(timeout=1000)
                        except: pass
                        texto_google = page.evaluate("document.body.innerText")
                        peso_lb_encontrado = extraer_peso_universal(texto_google)
                    except: pass

            except Exception:
                pass 
            
            # PROTOCOLO FANTASMA
            peso_fantasma = False
            if peso_lb_encontrado is None or peso_lb_encontrado <= 0:
                peso_lb_encontrado = 0.05
                peso_fantasma = True

            st.session_state.resultados.append({
                "Referencia": ref, 
                "peso_lb_raw": peso_lb_encontrado,
                "fantasma": peso_fantasma
            })
            st.session_state.indice_actual += 1
            
        browser.close()
        
    st.session_state.estado = "FINALIZADO"
    st.rerun()

if st.session_state.estado in ["PAUSADO", "FINALIZADO"] and st.session_state.resultados:
    if st.session_state.estado == "PAUSADO":
        st.warning(f"⏸️ **Misión Pausada.** Juan tomó un respiro en la referencia {st.session_state.indice_actual}.")
    else:
        st.success("✅ **¡Juan lo hizo de nuevo!** Extracción masiva terminada. Ni un solo cero en tu lista.")
        
    st.write("### 2. Tu Excel está servido")
    
    unidad_seleccionada = st.radio(
        "⚖️ **Juan, convierte la magia a:**",
        ["Libras (lb)", "Kilogramos (kg)"],
        horizontal=True
    )
    
    factor = 0.45359237 if unidad_seleccionada == "Kilogramos (kg)" else 1.0
    nombre_unidad = "Kilogramos" if unidad_seleccionada == "Kilogramos (kg)" else "Libras"
    
    filas_procesadas = []
    
    for item in st.session_state.resultados:
        ref = item["Referencia"]
        peso_raw = item["peso_lb_raw"]
        fantasma = item.get("fantasma", False)
        
        if fantasma:
            val_ajustado = round(0.05 * factor, 3)
            peso_ajustado = str(val_ajustado).replace(".", ",")
            peso_verdadero = "N/D"
        else:
            if peso_raw < 0.05:
                val_min = round(0.05 * factor, 3)
                val_real = round(peso_raw * factor, 3)
                peso_ajustado = str(val_min).replace(".", ",")
                peso_verdadero = str(val_real).replace(".", ",")
            else:
                val_real = round(peso_raw * factor, 3)
                peso_ajustado = str(val_real).replace(".", ",")
                peso_verdadero = ""
                
        filas_procesadas.append({
            "Referencia": ref,
            f"Peso ({nombre_unidad})": peso_ajustado,
            "Peso Verdadero (< 0,05 lb)": peso_verdadero
        })
        
    df = pd.DataFrame(filas_procesadas)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.write(f"**Columna Principal ({nombre_unidad}):**")
        columna_pesos = "\n".join(df[f"Peso ({nombre_unidad})"].astype(str).tolist())
        st.code(columna_pesos, language="text")
        
    with col2:
        st.write("**Columna Secundaria:**")
        columna_verdadero = "\n".join(df["Peso Verdadero (< 0,05 lb)"].astype(str).tolist())
        st.code(columna_verdadero, language="text")
        
    with col3:
        st.write("**Tabla de Verificación de Juan:**")
        st.dataframe(df, use_container_width=True)
