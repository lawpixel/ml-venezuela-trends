from playwright.sync_api import sync_playwright
import pandas as pd
import re
import datetime
import os
import time

def scrape_ml_venezuela():
    print("Iniciando scraping de productos con más mensajes...")
    os.makedirs("data", exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 1024},
        )
        
        page = context.new_page()
        
        try:
            # URL para productos con más mensajes
            print("Buscando productos con más mensajes...")
            page.goto("https://listado.mercadolibre.com.ve/_OrderId_MSGS*", timeout=60000)
            page.wait_for_load_state("networkidle")
            
            # Aceptar cookies si aparece
            try:
                page.click("button:has-text('Aceptar cookies')", timeout=5000)
                print("Cookies aceptadas")
            except:
                pass
            
            # Hacer scroll para cargar productos
            print("Cargando productos...")
            for i in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                page.wait_for_load_state("domcontentloaded")
            
            # Tomar screenshot para depuración
            page.screenshot(path="data/screenshot.png", full_page=True)
            print("Screenshot guardado para depuración")
            
            # Extraer productos
            productos = []
            items = page.query_selector_all("li.ui-search-layout__item")
            print(f"Elementos encontrados: {len(items)}")
            
            for item in items:
                try:
                    # Extraer datos básicos
                    titulo = item.query_selector(".ui-search-item__title").text_content().strip()
                    
                    # Precio
                    price_elem = item.query_selector(".andes-money-amount__fraction")
                    precio_text = price_elem.text_content().strip() if price_elem else ""
                    precio = float(precio_text.replace('.', '').replace(',', '.')) if precio_text else 0.0
                    
                    # Link
                    link_elem = item.query_selector("a.ui-search-link")
                    link = link_elem.get_attribute("href") if link_elem else "#"
                    
                    # Mensajes (nuevo campo)
                    mensajes = 0
                    mensajes_elem = item.query_selector(".ui-search-item__questions")
                    if mensajes_elem:
                        mensajes_text = mensajes_elem.text_content()
                        numeros = re.findall(r"\d+", mensajes_text)
                        if numeros:
                            mensajes = int(numeros[0])
                    
                    # Ventas
                    ventas = 0
                    ventas_elem = item.query_selector(".ui-search-item__quantity-label")
                    if ventas_elem:
                        ventas_text = ventas_elem.text_content()
                        numeros = re.findall(r"\d+", ventas_text)
                        if numeros:
                            ventas = int(numeros[0])
                    
                    # Rating
                    rating = 0.0
                    rating_elem = item.query_selector(".ui-search-reviews__rating-number")
                    if rating_elem:
                        rating_text = rating_elem.text_content()
                        match = re.search(r"(\d+\.\d+|\d+)", rating_text)
                        if match:
                            rating = float(match.group())
                    
                    # Características especiales
                    envio_gratis = bool(item.query_selector(".ui-search-item__shipping--free"))
                    tienda_oficial = bool(item.query_selector(".ui-search-official-store-label"))
                    
                    productos.append({
                        "titulo": titulo,
                        "precio": precio,
                        "ventas": ventas,
                        "mensajes": mensajes,  # Nuevo campo
                        "rating": rating,
                        "envio_gratis": envio_gratis,
                        "tienda_oficial": tienda_oficial,
                        "link": link,
                        "fecha": datetime.datetime.now().strftime("%Y-%m-%d")
                    })
                    
                except Exception as e:
                    print(f"Error procesando item: {str(e)}")
                    continue
            
            return pd.DataFrame(productos)
        
        except Exception as e:
            print(f"Error durante el scraping: {str(e)}")
            return pd.DataFrame()
        
        finally:
            browser.close()

if __name__ == "__main__":
    df = scrape_ml_venezuela()
    if not df.empty:
        df.to_csv("data/raw.csv", index=False)
        print(f"Scraping completado! Productos encontrados: {len(df)}")
    else:
        print("Scraping completado pero no se encontraron productos")
        pd.DataFrame().to_csv("data/raw.csv")
