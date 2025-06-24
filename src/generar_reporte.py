import pandas as pd
from datetime import datetime

def crear_reporte_html():
    try:
        df = pd.read_csv("data/processed.csv")
    except:
        return "<html><body><h1>Error: No hay datos disponibles</h1></body></html>"
    
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Top Productos - MercadoLibre Venezuela</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; background-color: #f8f9fa; color: #333; }}
            .container {{ max-width: 800px; margin: 20px auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            header {{ text-align: center; margin-bottom: 30px; }}
            h1 {{ color: #2c3e50; }}
            .subtitle {{ color: #7f8c8d; margin-bottom: 20px; }}
            .producto {{ border: 1px solid #e1e4e8; border-radius: 8px; padding: 20px; margin-bottom: 20px; transition: transform 0.3s; }}
            .producto:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            .titulo {{ font-size: 1.4rem; margin-bottom: 10px; color: #2c3e50; }}
            .precio {{ font-size: 1.8rem; color: #27ae60; font-weight: bold; margin-bottom: 10px; }}
            .badges {{ display: flex; gap: 10px; margin-bottom: 15px; }}
            .badge {{ display: inline-block; padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 500; }}
            .envio {{ background-color: #e1f0fa; color: #2980b9; }}
            .oficial {{ background-color: #e8f5e9; color: #2ecc71; }}
            .stats {{ display: flex; gap: 20px; margin: 15px 0; }}
            .stat {{ background: #f8f9fa; padding: 12px; border-radius: 8px; flex: 1; text-align: center; }}
            .stat-value {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; }}
            .stat-label {{ font-size: 0.9rem; color: #7f8c8d; }}
            .why {{ background: #fef9e7; padding: 15px; border-radius: 8px; margin: 15px 0; }}
            .btn {{ display: inline-block; background: #3498db; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: 500; margin-top: 10px; }}
            .btn:hover {{ background: #2980b9; }}
            footer {{ text-align: center; margin-top: 30px; color: #7f8c8d; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔥 Top 5 Productos en Tendencia</h1>
                <p class="subtitle">MercadoLibre Venezuela - Reporte diario</p>
                <p class="subtitle">Actualizado: {fecha_actual}</p>
            </header>
    """
    
    for i, row in df.iterrows():
        badges = []
        if row['envio_gratis']:
            badges.append('<span class="badge envio">🚚 Envío Gratis</span>')
        if row['tienda_oficial']:
            badges.append('<span class="badge oficial">🏬 Tienda Oficial</span>')
        
        badges_html = "".join(badges)
        
        html += f"""
        <div class="producto">
            <div class="titulo">#{i+1} {row['titulo']}</div>
            <div class="precio">Bs. {row['precio']:,.2f}</div>
            
            <div class="badges">
                {badges_html}
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{row['ventas']}</div>
                    <div class="stat-label">Ventas</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{row['rating']}/5</div>
                    <div class="stat-label">Rating</div>
                </div>
            </div>
            
            <div class="why">
                <strong>💡 Por qué destaca:</strong> Mejor relación precio-calidad en su categoría
            </div>
            
            <a href="{row['link']}" class="btn" target="_blank">Ver producto en MercadoLibre</a>
        </div>
        """
    
    html += """
            <footer>
                <p>Reporte generado automáticamente - Actualizado diariamente</p>
                <p>⚠️ Este es un proyecto de automatización, no afiliado a MercadoLibre</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open("docs/index.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    crear_reporte_html()
