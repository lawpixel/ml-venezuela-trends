import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime
import time
import random

def scrape_ml_venezuela():
    url = "https://listado.mercadolibre.com.ve/ofertas?filter=YES#D[A:YES,orden:ventas]"
    
    # User-Agents aleatorios para evitar bloqueos
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    
    headers = {'User-Agent': random.choice(user_agents)}
    
    # Espera aleatoria entre requests
    time.sleep(random.uniform(1.0, 3.0))
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    productos = []
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    for item in soup.select('.ui-search-layout__item'):
        try:
            # Extraer datos básicos
            titulo = item.select_one('.ui-search-item__title').text.strip()
            precio_text = item.select_one('.andes-money-amount__fraction').text
            precio = float(precio_text.replace('.', '').replace(',', '.'))
            link = item.select_one('a.ui-search-link')['href']
            
            # Extraer ventas
            ventas_text = item.select_one('.ui-search-item__quantity-label')
            ventas = int(re.search(r'\d+', ventas_text.text).group()) if ventas_text else 0
            
            # Extraer rating
            rating_elem = item.select_one('.ui-search-reviews__rating-number')
            rating = float(rating_elem.text) if rating_elem else 0.0
            
            # Características especiales
            envio_gratis = bool(item.select_one('.ui-search-item__shipping--free'))
            tienda_oficial = bool(item.select_one('.ui-search-official-store-label'))
            
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
            continue
    
    return pd.DataFrame(productos)

if __name__ == "__main__":
    df = scrape_ml_venezuela()
    df.to_csv("data/raw.csv", index=False)
    print(f"Scraping completado! Productos encontrados: {len(df)}")
