from playwright.sync_api import sync_playwright
import pandas as pd
import re
import datetime
import os
import time
import random

def scrape_ml_venezuela():
    print("🚀 Iniciando scraping de productos con más mensajes...")
    os.makedirs("data", exist_ok=True)
    start_time = time.time()
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        attempts += 1
        print(f"🔄 Intento #{attempts}/{max_attempts}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                user_agent=random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
                ]),
                viewport={"width": 1280, "height": 1024},
            )
            
            page = context.new_page()
            
            try:
                # URL para productos con más mensajes
                url = "https://listado.mercadolibre.com.ve/_OrderId_MSGS"
                print(f"🌐 Accediendo a: {url}")
                page.goto(url, timeout=120000)
                
                # Esperar a que cargue el contenido principal
                print("⏳ Esperando a que cargue el contenido...")
                page.wait_for_selector(".ui-search-layout__item:visible, .promotions_item:visible", timeout=30000)
                
                # Manejar posibles popups
                self.handle_popups(page)
                
                # Hacer scroll para cargar productos
                print("🖱️ Haciendo scroll para cargar más productos...")
                for i in range(8):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(random.uniform(1.5, 2.5))
                    page.wait_for_timeout(1000)
                
                # Tomar screenshot para depuración
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"data/screenshot_{timestamp}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot guardado: {screenshot_path}")
                
                # Extraer productos
                productos = self.extract_products(page)
                
                if productos:
                    print(f"✅ Productos encontrados: {len(productos)}")
                    return pd.DataFrame(productos)
                else:
                    print("⚠️ No se encontraron productos en este intento")
                
            except Exception as e:
                print(f"❌ Error durante el scraping: {str(e)}")
                # Guardar HTML para depuración
                html_path = f"data/error_{timestamp}.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(page.content())
                print(f"📄 HTML guardado para depuración: {html_path}")
            
            finally:
                browser.close()
    
    print(f"⏱️ Tiempo total: {time.time() - start_time:.2f} segundos")
    return pd.DataFrame()

def handle_popups(page):
    """Maneja posibles popups y modales"""
    popup_selectors = [
        "button:has-text('Aceptar cookies')",
        "button:has-text('Entendido')",
        "button:has-text('Continuar')",
        "button:has-text('Aceptar')",
        ".cookie-banner-lgpd-button"
    ]
    
    for selector in popup_selectors:
        try:
            page.click(selector, timeout=5000)
            print(f"✅ Popup cerrado: {selector}")
            time.sleep(1)
        except:
            pass

def extract_products(page):
    """Extrae productos de la página"""
    print("🔍 Extrayendo productos...")
    
    # Intentar múltiples selectores para encontrar items
    items_selectors = [
        "li.ui-search-layout__item",
        "li.promotions_item",
        ".ui-search-result__wrapper",
        ".results-item"
    ]
    
    items = []
    for selector in items_selectors:
        items = page.query_selector_all(selector)
        if items:
            print(f"🔧 Selector usado: {selector}")
            break
    
    print(f"🔎 Elementos encontrados: {len(items)}")
    productos = []
    
    for item in items:
        try:
            # Validar que sea un producto visible
            if not item.is_visible():
                continue
                
            # Extraer datos básicos con múltiples selectores alternativos
            product_data = self.extract_product_data(item)
            
            if product_data["titulo"] and product_data["precio"] > 0:
                productos.append(product_data)
        
        except Exception as e:
            print(f"⚠️ Error procesando item: {str(e)}")
            continue
    
    return productos

def extract_product_data(item):
    """Extrae datos de un producto individual"""
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
    
    # Título
    title_selectors = [
        ".ui-search-item__title",
        ".promotion-item__title",
        ".ui-search-item__group__element",
        ".item__title"
    ]
    for selector in title_selectors:
        title_elem = item.query_selector(selector)
        if title_elem:
            data["titulo"] = title_elem.text_content().strip()
            break
    
    # Precio
    price_selectors = [
        ".andes-money-amount__fraction",
        ".price-tag-fraction",
        ".promotion-item__price",
        ".item__price"
    ]
    for selector in price_selectors:
        price_elem = item.query_selector(selector)
        if price_elem:
            price_text = price_elem.text_content().strip()
            # Limpiar y convertir a float
            price_clean = re.sub(r"[^\d.,]", "", price_text)
            price_clean = price_clean.replace(".", "").replace(",", ".")
            try:
                data["precio"] = float(price_clean)
            except:
                pass
            break
    
    # Mensajes
    msg_selectors = [
        ".ui-search-item__questions",
        ".promotion-item__questions",
        ".item__questions"
    ]
    for selector in msg_selectors:
        msg_elem = item.query_selector(selector)
        if msg_elem:
            msg_text = msg_elem.text_content()
            numeros = re.findall(r"\d+", msg_text)
            if numeros:
                data["mensajes"] = min(int(numeros[0]), 1000)  # Limitar a 1000
            break
    
    # Ventas
    sales_selectors = [
        ".ui-search-item__quantity-label",
        ".promotion-item__quantity-selling",
        ".item__quantity"
    ]
    for selector in sales_selectors:
        sales_elem = item.query_selector(selector)
        if sales_elem:
            sales_text = sales_elem.text_content()
            numeros = re.findall(r"\d+", sales_text)
            if numeros:
                data["ventas"] = min(int(numeros[0]), 10000)  # Limitar a 10000
            break
    
    # Rating
    rating_selectors = [
        ".ui-search-reviews__rating-number",
        ".promotion-item__rating",
        ".item__rating"
    ]
    for selector in rating_selectors:
        rating_elem = item.query_selector(selector)
        if rating_elem:
            rating_text = rating_elem.text_content()
            match = re.search(r"(\d+\.\d+|\d+)", rating_text)
            if match:
                rating_value = float(match.group())
                data["rating"] = max(0.0, min(rating_value, 5.0))  # Limitar a 0-5
            break
    
    # Características especiales
    data["envio_gratis"] = any(item.query_selector(selector) for selector in [
        ".ui-search-item__shipping--free",
        ".promotion-item__free-shipping",
        ".item__free-shipping"
    ])
    
    data["tienda_oficial"] = any(item.query_selector(selector) for selector in [
        ".ui-search-official-store-label",
        ".promotion-item__official-store",
        ".item__official-store"
    ])
    
    # Link
    link_selectors = [
        "a.ui-search-link",
        "a.promotion-item__link-container",
        "a.item__link"
    ]
    for selector in link_selectors:
        link_elem = item.query_selector(selector)
        if link_elem:
            data["link"] = link_elem.get_attribute("href") or "#"
            break
    
    return data

if __name__ == "__main__":
    df = scrape_ml_venezuela()
    if not df.empty:
        df.to_csv("data/raw.csv", index=False)
        print(f"🎉 Scraping completado! Productos encontrados: {len(df)}")
    else:
        print("🤷 Scraping completado pero no se encontraron productos")
        # Crear archivo vacío para evitar errores
        pd.DataFrame().to_csv("data/raw.csv")
