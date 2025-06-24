import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def procesar_productos():
    logger.info("Iniciando procesamiento de datos...")
    os.makedirs("data", exist_ok=True)
    
    try:
        df = pd.read_csv("data/raw.csv")
        logger.info(f"Datos cargados: {len(df)} registros")
    except Exception as e:
        logger.error(f"Error leyendo raw.csv: {str(e)}")
        return pd.DataFrame()
    
    if df.empty:
        logger.warning("DataFrame vacío. No hay datos para procesar.")
        return pd.DataFrame()
    
    # Manejo de valores faltantes
    df.fillna({
        'ventas': 0,
        'mensajes': 0,
        'rating': 0,
        'envio_gratis': False,
        'tienda_oficial': False
    }, inplace=True)
    
    # Validar y limpiar datos
    df = df[
        (df['titulo'].str.len() > 3) & 
        (df['precio'] > 0) &
        (df['precio'] < 1000000) &
        (df['ventas'] >= 0) &
        (df['mensajes'] >= 0) &
        (df['rating'].between(0, 5))
    ]
    
    if df.empty:
        logger.warning("No quedan productos válidos después de la limpieza")
        return pd.DataFrame()
    
    logger.info(f"Productos válidos: {len(df)}")
    
    # Calcular popularidad con pesos ajustados
    df['popularidad'] = (
        (df['mensajes'] * 0.8) +  # Mayor peso a los mensajes
        (df['ventas'] * 0.5) + 
        (df['rating'] * 20) +
        (df['envio_gratis'] * 15) +
        (df['tienda_oficial'] * 10)
    )
    
    # Clasificar productos similares
    if len(df) > 1:
        logger.info("Agrupando productos similares...")
        try:
            vectorizer = TfidfVectorizer(
                stop_words=['de', 'en', 'con', 'para', 'y', 'el', 'la', 'los', 'las'],
                max_features=500
            )
            tfidf = vectorizer.fit_transform(df['titulo'])
            
            n_clusters = min(15, len(df) // 2)
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            df['grupo'] = kmeans.fit_predict(tfidf)
            
            # Seleccionar top productos por popularidad
            top_products = df.sort_values('popularidad', ascending=False).head(30)
            
            # Mejor oferta por grupo
            mejores_ofertas = []
            for grupo_id in top_products['grupo'].unique():
                grupo = top_products[top_products['grupo'] == grupo_id]
                mejor = grupo.loc[grupo['precio'].idxmin()]
                mejores_ofertas.append(mejor)
            
            top_5 = pd.DataFrame(mejores_ofertas).head(5)
            logger.info(f"Top 5 productos seleccionados")
            
        except Exception as e:
            logger.error(f"Error en clustering: {str(e)}")
            # Fallback: seleccionar los 5 más populares
            top_5 = df.sort_values('popularidad', ascending=False).head(5)
    else:
        top_5 = df.sort_values('popularidad', ascending=False).head(5)
    
    top_5.to_csv("data/processed.csv", index=False)
    return top_5

if __name__ == "__main__":
    procesar_productos()
