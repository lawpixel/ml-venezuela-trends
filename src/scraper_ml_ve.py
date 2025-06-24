import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime
import time
import random
import os

def scrape_ml_venezuela():
    
# Cambiar la URL a esta versión funcional
url = "https://listado.mercadolibre.com.ve/ofertas#D[A:ofertas]"
   
# User-Agents actualizados
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es,es-ES;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        # Espera aleatoria más larga
        time.sleep(random.uniform(2.0, 5.0))
        
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        productos = []
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Selector actualizado para productos
        items = soup.select('.ui-search-layout__item, .andes-card')
        print(f"Elementos encontrados: {len(items)}")
        
        for item in items:
            try:
                # Título - selector actualizado
                title_elem = item.select_one('.ui-search-item__title, .ui-search-item__group__element')
                if not title_elem:
                    continue
                titulo = title_elem.text.strip()
                
                # Precio - selector actualizado
                price_elem = item.select_one('.andes-money-amount__fraction, .price-tag-fraction')
                if not price_elem:
                    continue
                precio_text = price_elem.text
                precio = float(precio_text.replace('.', '').replace(',', '.'))
                
                # Link
                link_elem = item.select_one('a.ui-search-link')
                link = link_elem['href'] if link_elem else "#"
                
                # Ventas - selector alternativo
                ventas = 0
                ventas_elem = item.select_one('.ui-search-item__quantity-label, .ui-search-official-store-label + div')
                if ventas_elem:
                    ventas_text = ventas_elem.text
                    numeros = re.findall(r'\d+', ventas_text)
                    if numeros:
                        ventas = int(numeros[0])
                
                # Rating - selector alternativo
                rating = 0.0
                rating_elem = item.select_one('.ui-search-reviews__rating-number, .ui-search-reviews__rating')
                if rating_elem:
                    rating_text = rating_elem.text
                    rating = float(re.search(r'\d+\.?\d*', rating_text).group())
                
                # Características especiales
                envio_gratis = bool(item.select_one('.ui-search-item__shipping--free, .free-shipping-icon'))
                tienda_oficial = bool(item.select_one('.ui-search-official-store-label, .official-store-logo'))
                
                productos.append({
                    'titulo': titulo,
                    'precio': precio,
                    'ventas': ventas,
                    'rating': rating,
                    'envio_gratis': envio_gratis,
                    'tienda_oficial': tienda_oficial,
                    'link': link,
                    'fecha': today
                })
                
            except Exception as e:
                print(f"Error procesando item: {str(e)}")
                continue
        
        return pd.DataFrame(productos)
    
    except Exception as e:
        print(f"Error en el scraping: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Crear carpeta data si no existe
    os.makedirs("data", exist_ok=True)
    
    df = scrape_ml_venezuela()
    if not df.empty:
        df.to_csv("data/raw.csv", index=False)
        print(f"Scraping completado! Productos encontrados: {len(df)}")
    else:
        print("Scraping completado pero no se encontraron productos")
        # Crear archivo vacío para evitar errores
        pd.DataFrame().to_csv("data/raw.csv")
