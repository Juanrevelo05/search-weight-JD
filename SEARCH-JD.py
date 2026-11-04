import subprocess
import sys
import os
import re
import streamlit as st
import pandas as pd

# -------------------------------------------------------------------
# CONFIGURACIÓN AUTOMÁTICA DEL NAVEGADOR EN LA NUBE
# -------------------------------------------------------------------
@st.cache_resource
def instalar_navegador():
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

try:
    instalar_navegador()
except Exception as e:
    st.error(f"Error al inicializar el servicio de consulta: {e}")

from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Extractor de Pesos JD", page_icon="🏎️", layout="wide")

# --- ESTILOS VISUALES CORPORATIVOS ---
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

# --- CONTROL DE ESTADO DE SESIÓN ---
if "resultados" not in st.session_state:
    st.session_state.resultados = []
    st.session_state.lista_referencias = []
    st.session_state.indice_actual = 0
    st.session_state.estado = "ESPERANDO" 

# --- ENCABEZADO CON LOGO Y TÍTULO ---
col_logo, col_titulo = st.columns([1.5, 5.5])
with col_logo:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=220)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=220)
    elif os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", width=220)

with col_titulo:
    st.title("🏎️ Extractor de Pesos John Deere")
    st.markdown("Consulta y conversión automatizada de catálogo técnico | Salida en **Libras** y **Kilogramos**.")

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

st.write("### 1. Ingrese el listado de referencias:")
referencias_input = st.text_area("Referencias (una por línea):", height=150, placeholder="CE31805\nCE31720\n19M7785")

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🚀 Iniciar Consulta", type="primary"):
        lista_limpia = [r.strip() for r in referencias_input.split('\n') if r.strip()]
        if lista_limpia:
            st.session_state.lista_referencias = lista_limpia
            st.session_state.resultados = []
            st.session_state.indice_actual = 0
            st.session_state.estado = "PROCESANDO"
        else:
            st.warning("Ingrese al menos una referencia para procesar.")

with col_btn2:
    if st.session_state.estado in ["PAUSADO", "PROCESANDO"] and 0 < st.session_state.indice_actual < len(st.session_state.lista_referencias):
        if st.button("▶️ Reanudar Consulta", type="primary"):
            st.session_state.estado = "PROCESANDO"

with col_btn3:
    if st.session_state.estado == "PROCESANDO":
        if st.button("🛑 Pausar Consulta", type="secondary"):
            st.session_state.estado = "PAUSADO"

st.write("---")

if st.session_state.estado == "PROCESANDO":
    total = len(st.session_state.lista_referencias)
    st.info("Procesando consulta en catálogos oficiales...")
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
            
            texto_progreso.text(f"Consultando referencia: {ref} ({idx + 1} de {total})")
            barra_progreso.progress((idx + 1) / total)
            peso_lb_encontrado = None
            
            try:
                # Servidor 1: John Deere Shop
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
                
                # Servidor 2: RDO Equipment
                if peso_lb_encontrado is None:
                    texto_progreso.text(f"Consultando fuentes secundarias para: {ref}...")
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

                # Servidor 3: GreenPartStore
                if peso_lb_encontrado is None:
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

                # Servidor 4: Búsqueda web directa
                if peso_lb_encontrado is None:
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
            
            # REGLA FANTASMA / ESTIMADO
            es_estimado = False
            if peso_lb_encontrado is None or peso_lb_encontrado <= 0:
                peso_lb_encontrado = 0.05
                es_estimado = True

            st.session_state.resultados.append({
                "Referencia": ref, 
                "peso_lb_raw": peso_lb_encontrado,
                "estimado": es_estimado
            })
            st.session_state.indice_actual += 1
            
        browser.close()
        
    st.session_state.estado = "FINALIZADO"
    st.rerun()

if st.session_state.estado in ["PAUSADO", "FINALIZADO"] and st.session_state.resultados:
    if st.session_state.estado == "PAUSADO":
        st.warning(f"Proceso en pausa en la referencia {st.session_state.indice_actual}.")
    else:
        st.success("Extracción completada satisfactoriamente.")
        
    st.write("### 2. Resultados listos para exportar")
    
    unidad_seleccionada = st.radio(
        "Formato de unidad principal:",
        ["Libras (lb)", "Kilogramos (kg)"],
        horizontal=True
    )
    
    factor = 0.45359237 if unidad_seleccionada == "Kilogramos (kg)" else 1.0
    nombre_unidad = "Kilogramos" if unidad_seleccionada == "Kilogramos (kg)" else "Libras"
    
    filas_procesadas = []
    lista_copiar = []
    
    for item in st.session_state.resultados:
        ref = item["Referencia"]
        peso_raw = item["peso_lb_raw"]
        estimado = item.get("estimado", False)
        
        if estimado:
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
            "Peso Original (< 0,05 lb)": peso_verdadero
        })
        lista_copiar.append(peso_ajustado)
        
    df = pd.DataFrame(filas_procesadas)
    # Numeración comenzando en 1
    df.index = range(1, len(df) + 1)
    
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.write(f"**Columna ({nombre_unidad}):**")
        st.code("\n".join(lista_copiar), language="text")
        
    with col2:
        st.write("**Tabla Consolidada:**")
        st.dataframe(df, use_container_width=True)
