import pandas as pd
from datetime import datetime
import os

def crear_reporte_html():
    # Crear carpeta docs si no existe
    os.makedirs("docs", exist_ok=True)
    
    try:
        df = pd.read_csv("data/processed.csv")
    except:
        df = pd.DataFrame()
    
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    
    if df.empty:
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Reporte Diario - MercadoLibre VE</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                h1 {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <h1>⚠️ No se encontraron productos hoy</h1>
            <p>El scraping no recuperó datos en la ejecución de hoy ({fecha_actual})</p>
            <p>Posibles causas:</p>
            <ul style="text-align: left; display: inline-block;">
                <li>Cambios en la estructura de MercadoLibre</li>
                <li>Bloqueo temporal de las solicitudes</li>
                <li>Problemas de conectividad</li>
            </ul>
            <p>Intenta nuevamente mañana o revisa los logs de GitHub Actions.</p>
        </body>
        </html>
        """
    else:
        # ... (mantener el mismo código de generación de reporte)
    
    with open("docs/index.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    crear_reporte_html()
