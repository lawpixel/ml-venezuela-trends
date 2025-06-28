from playwright.sync_api import sync_playwright
import pandas as pd
import re
import datetime
import os
import time
import random

def scrape_ml_venezuela():
    print("🚀 Iniciando scraping de MercadoLibre Venezuela")
    os.makedirs("data", exist_ok=True)
    
    # Configuración de Playwright con opciones stealth
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
            ]),
            viewport={"width": 1280, "height": 1024},
            locale="es-VE"
        )
        
        page = context.new_page()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Definir timestamp aquí
        
        try:
            # URL optimizada para productos con más mensajes
            url = "https://listado.mercadolibre.com.ve/_OrderId_MSGS"
            print(f"🌍 Accediendo a: {url}")
            
            # Navegación con timeout extendido
            page.goto(url, timeout=60000)
            page.wait_for_selector(".ui-search-layout__item", timeout=30000)
            
            # Manejar posibles popups
            handle_popups(page)  # CORREGIDO: Quitar self.
            
            # Scroll para cargar más productos
            print("🖱️ Realizando scroll para cargar productos...")
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(1.5, 3.0))
                page.wait_for_timeout(1000)
            
            # Tomar screenshot para depuración
            screenshot_path = f"data/screenshot_{timestamp}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Captura guardada: {screenshot_path}")
            
            # Extraer productos
            productos = []
            items = page.query_selector_all(".ui-search-layout__item, .andes-card")
            print(f"🔍 {len(items)} productos encontrados en la página")
            
            for item in items:
                try:
                    product_data = extract_product_data(item)  # CORREGIDO: Quitar self.
                    if product_data["titulo"] and product_data["precio"] > 0:
                        productos.append(product_data)
                except Exception as e:
                    print(f"⚠️ Error procesando item: {str(e)}")
                    continue
            
            return pd.DataFrame(productos)
            
        except Exception as e:
            print(f"❌ Error durante el scraping: {str(e)}")
            # Guardar HTML para diagnóstico
            html_path = f"data/error_{timestamp}.html"
            try:
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(page.content())
                print(f"📄 HTML guardado para diagnóstico: {html_path}")
            except Exception as file_error:
                print(f"⚠️ No se pudo guardar HTML: {file_error}")
            return pd.DataFrame()
            
        finally:
            browser.close()

def handle_popups(page):
    """Maneja popups y banners de cookies"""
    popup_selectors = [
        "button:has-text('Aceptar cookies')",
        "button:has-text('Entendido')",
        "button:has-text('Continuar')",
        ".cookie-banner-lgpd-button",
        "button:has-text('Aceptar')"
    ]
    
    for selector in popup_selectors:
        try:
            page.click(selector, timeout=5000)
            print(f"✅ Popup cerrado: {selector}")
            time.sleep(1)
        except:
            pass

def extract_product_data(item):
    """Extrae datos de un producto individual con selectores actualizados"""
    data = {
        "titulo": "",
        "precio": 0.0,
        "ventas": 0,
        "mensajes": 0,
        "rating": 0.0,
        "envio_gratis": False,
        "tienda_oficial": False,
        "link": "#",
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    
    try:
        # Selectores actualizados (Junio 2024)
        title_elem = item.query_selector(".ui-search-item__title, .ui-search-item__group__element")
        if title_elem:
            data["titulo"] = title_elem.text_content().strip()
        
        price_elem = item.query_selector(".andes-money-amount__fraction, .price-tag-fraction")
        if price_elem:
            try:
                price_text = price_elem.text_content().strip()
                data["precio"] = float(price_text.replace(".", "").replace(",", "."))
            except:
                pass
        
        # Extraer mensajes (nuevo selector)
        msg_elem = item.query_selector(".ui-search-item__questions, .ui-search-item__action--question")
        if msg_elem:
            msg_text = msg_elem.text_content()
            numeros = re.findall(r"\d+", msg_text)
            if numeros:
                data["mensajes"] = int(numeros[0])
        
        # Extraer ventas
        sales_elem = item.query_selector(".ui-search-item__sold-quantity")
        if sales_elem:
            sales_text = sales_elem.text_content()
            numeros = re.findall(r"\d+", sales_text)
            if numeros:
                data["ventas"] = int(numeros[0])
        
        # Extraer rating
        rating_elem = item.query_selector(".ui-search-reviews__rating")
        if rating_elem:
            rating_text = rating_elem.get_attribute("aria-label") or ""
            rating_match = re.search(r"(\d+[.,]\d+)", rating_text)
            if rating_match:
                data["rating"] = float(rating_match.group(1).replace(",", "."))
        
        # Verificar envío gratis
        envio_elem = item.query_selector(".ui-search-shipping")
        if envio_elem and "gratis" in envio_elem.text_content().lower():
            data["envio_gratis"] = True
        
        # Verificar tienda oficial
        oficial_elem = item.query_selector(".ui-search-official-store-label")
        if oficial_elem:
            data["tienda_oficial"] = True
        
        # Extraer link
        link_elem = item.query_selector("a.ui-search-link")
        if link_elem:
            href = link_elem.get_attribute("href")
            if href:
                data["link"] = href if href.startswith("http") else f"https://mercadolibre.com.ve{href}"
                
    except Exception as e:
        print(f"⚠️ Error extrayendo datos del producto: {e}")
    
    return data

if __name__ == "__main__":
    df = scrape_ml_venezuela()
    if not df.empty:
        df.to_csv("data/raw.csv", index=False, encoding='utf-8')
        print(f"✅ Scraping completado! {len(df)} productos encontrados")
        print(f"📊 Primeros 5 productos:")
        print(df.head().to_string())
    else:
        print("❌ Scraping completado pero no se encontraron productos")
        # Crear CSV vacío con headers correctos
        empty_df = pd.DataFrame(columns=["titulo", "precio", "ventas", "mensajes", "rating", "envio_gratis", "tienda_oficial", "link", "fecha"])
        empty_df.to_csv("data/raw.csv", index=False, encoding='utf-8')
