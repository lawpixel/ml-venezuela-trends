import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import os

def procesar_productos():
    # Crear carpeta data si no existe
    os.makedirs("data", exist_ok=True)
    
    try:
        df = pd.read_csv("data/raw.csv")
    except Exception as e:
        print(f"Error leyendo raw.csv: {str(e)}")
        return pd.DataFrame()
    
    if df.empty:
        print("DataFrame vacío. No hay datos para procesar.")
        return pd.DataFrame()
    
    # Calcular popularidad con manejo de valores nulos
    df['ventas'] = df['ventas'].fillna(0)
    df['rating'] = df['rating'].fillna(0)
    df['popularidad'] = df['ventas'] * np.where(df['rating'] > 0, df['rating'], 1)
    
    # Clasificar productos similares solo si hay datos suficientes
    if len(df) > 1:
        vectorizer = TfidfVectorizer(stop_words=['de', 'en', 'con', 'para', 'y', 'el', 'la'])
        tfidf = vectorizer.fit_transform(df['titulo'])
        
        n_clusters = min(10, len(df))
        kmeans = KMeans(n_clusters=n_clusters)
        df['grupo'] = kmeans.fit_predict(tfidf)
        
        # Seleccionar top productos
        top_products = df.sort_values('popularidad', ascending=False).head(20)
        
        # Mejor oferta por grupo
        mejores_ofertas = []
        for grupo_id in top_products['grupo'].unique():
            grupo = top_products[top_products['grupo'] == grupo_id]
            mejor = grupo.loc[grupo['precio'].idxmin()]
            mejores_ofertas.append(mejor)
        
        top_5 = pd.DataFrame(mejores_ofertas).head(5)
    else:
        # Si hay pocos productos, tomar los más populares
        top_5 = df.sort_values('popularidad', ascending=False).head(5)
    
    top_5.to_csv("data/processed.csv", index=False)
    return top_5

if __name__ == "__main__":
    procesar_productos()
