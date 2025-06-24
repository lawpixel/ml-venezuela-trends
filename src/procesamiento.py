import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import os

def procesar_productos():
    os.makedirs("data", exist_ok=True)
    
    try:
        df = pd.read_csv("data/raw.csv")
    except Exception as e:
        print(f"Error leyendo raw.csv: {str(e)}")
        return pd.DataFrame()
    
    if df.empty:
        print("DataFrame vacío. No hay datos para procesar.")
        return pd.DataFrame()
    
    # Manejo de valores faltantes
    df['ventas'] = df['ventas'].fillna(0)
    df['mensajes'] = df['mensajes'].fillna(0)
    df['rating'] = df['rating'].fillna(0)
    
    # Calcular popularidad dando más peso a los mensajes
    df['popularidad'] = (df['mensajes'] * 0.7) + (df['ventas'] * 0.3) + (df['
