import pandas as pd
from datetime import datetime
import os
import json

def crear_reporte_html():
    os.makedirs("docs", exist_ok=True)
    
    # Intentar cargar datos históricos para tendencias
    historical_data = load_historical_data()
    
    try:
        df = pd.read_csv("data/processed.csv")
    except:
        df = pd.DataFrame()
    
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    hora_actual = datetime.now().strftime('%H:%M')
    
    if df.empty:
        html = generate_error_html(fecha_actual, hora_actual)
    else:
        html = generate_success_html(df, fecha_actual, hora_actual, historical_data)
    
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("📊 Reporte HTML generado")

def load_historical_data():
    """Carga datos históricos para análisis de tendencias"""
    historical = []
    try:
        # Intentar cargar datos de días anteriores
        for i in range(1, 4):
            file_path = f"data/raw_{datetime.now().strftime('%Y%m%d')}_{i}.csv"
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                historical.append(df)
        print(f"📚 Datos históricos cargados: {len(historical)} archivos")
    except:
        pass
    return historical

def generate_error_html(fecha, hora):
    """Genera HTML para cuando no hay datos"""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte Diario - MercadoLibre VE</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #f5f7fa 0%, #e4e7f1 100%);
                color: #333;
                text-align: center;
                padding: 50px 20px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            h1 {{ 
                color: #e74c3c;
                margin-bottom: 20px;
            }}
            .error-icon {{
                font-size: 80px;
                color: #e74c3c;
                margin: 20px 0;
            }}
            .suggestions {{
                text-align: left;
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 30px 0;
            }}
            .suggestions ul {{
                padding-left: 20px;
            }}
            .suggestions li {{
                margin-bottom: 10px;
            }}
            .timestamp {{
                color: #7f8c8d;
                margin-top: 30px;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="error-icon">⚠️</div>
            <h1>No se encontraron productos hoy</h1>
            <p>El scraping no recuperó datos en la ejecución de hoy</p>
            
            <div class="suggestions">
                <p><strong>Posibles causas:</strong></p>
                <ul>
                    <li>Cambios en la estructura de MercadoLibre</li>
                    <li>Bloqueo temporal de las solicitudes</li>
                    <li>Problemas de conectividad</li>
                    <li>Actualizaciones en los selectores CSS</li>
                </ul>
                <p><strong>Acciones recomendadas:</strong></p>
                <ul>
                    <li>Revisar los logs de GitHub Actions</li>
                    <li>Verificar los screenshots en la carpeta /data</li>
                    <li>Actualizar los selectores en el código</li>
                    <li>Intentar nuevamente mañana</li>
                </ul>
            </div>
            
            <div class="timestamp">
                <p>Reporte generado el: {fecha} a las {hora}</p>
            </div>
        </div>
    </body>
    </html>
    """

def generate_success_html(df, fecha, hora, historical_data):
    """Genera HTML exitoso con los productos"""
    # Encabezado del reporte
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Top Productos con Más Mensajes - MercadoLibre VE</title>
        <style>
            /* Estilos generales */
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            :root {{
                --primary: #2968c8;
                --secondary: #e67e22;
                --success: #27ae60;
                --danger: #e74c3c;
                --light: #f8f9fa;
                --dark: #2c3e50;
            }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                line-height: 1.6; 
                background: linear-gradient(135deg, #f5f7fa 0%, #e4e7f1 100%);
                color: #333;
                padding: 20px;
            }}
            .container {{ 
                max-width: 1000px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 15px; 
                padding: 30px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            header {{ 
                text-align: center; 
                margin-bottom: 30px; 
                padding-bottom: 20px;
                border-bottom: 1px solid #eee;
            }}
            h1 {{ 
                color: var(--primary);
                margin-bottom: 10px;
                font-size: 2.2rem;
            }}
            .subtitle {{
                color: #7f8c8d; 
                margin-bottom: 5px;
            }}
            .timestamp {{
                color: #95a5a6;
                font-size: 0.9rem;
            }}
            
            /* Estilos de productos */
            .products-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 25px;
                margin-top: 30px;
            }}
            .product-card {{
                border: 1px solid #e1e4e8; 
                border-radius: 12px; 
                padding: 25px; 
                transition: all 0.3s ease;
                background: white;
                position: relative;
                overflow: hidden;
            }}
            .product-card:hover {{
                transform: translateY(-8px); 
                box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            }}
            .product-badge {{
                position: absolute;
                top: 15px;
                right: 15px;
                background: var(--secondary);
                color: white;
                padding: 5px 12px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.9rem;
            }}
            .product-title {{
                font-size: 1.3rem; 
                margin-bottom: 15px; 
                color: var(--dark);
                min-height: 60px;
            }}
            .product-price {{
                font-size: 1.8rem; 
                color: var(--success); 
                font-weight: bold; 
                margin-bottom: 15px;
            }}
            .badges-container {{
                display: flex; 
                flex-wrap: wrap; 
                gap: 10px; 
                margin-bottom: 20px;
            }}
            .badge {{
                display: inline-block; 
                padding: 7px 15px; 
                border-radius: 20px; 
                font-size: 0.9rem; 
                font-weight: 500;
            }}
            .envio {{ background-color: #e1f0fa; color: #2980b9; }}
            .oficial {{ background-color: #e8f5e9; color: #2ecc71; }}
            .stats-container {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: #f8f9fa; 
                padding: 15px; 
                border-radius: 10px; 
                text-align: center;
                transition: transform 0.2s;
            }}
            .stat-card:hover {{
                transform: scale(1.05);
            }}
            .stat-value {{
                font-size: 1.5rem; 
                font-weight: bold; 
                color: var(--primary);
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 0.85rem; 
                color: #7f8c8d;
            }}
            .highlight-stat {{ 
                background: linear-gradient(135deg, #2968c8 0%, #3a9efd 100%);
                color: white;
            }}
            .highlight-stat .stat-value {{ color: white; }}
            .highlight-stat .stat-label {{ color: rgba(255,255,255,0.9); }}
            .why-box {{
                background: #fef9e7; 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0;
                border-left: 4px solid var(--secondary);
            }}
            .btn {{
                display: block;
                width: 100%;
                background: linear-gradient(135deg, var(--primary) 0%, #3a9efd 100%);
                color: white;
                padding: 12px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                text-align: center;
                margin-top: 15px;
                transition: all 0.3s;
            }}
            .btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(41, 104, 200, 0.4);
            }}
            
            footer {{ 
                text-align: center; 
                margin-top: 40px; 
                color: #7f8c8d; 
                font-size: 0.9rem;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }}
            
            @media (max-width: 768px) {{
                .products-grid {{
                    grid-template-columns: 1fr;
                }}
                .stats-container {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔥 Productos con Más Mensajes</h1>
                <p class="subtitle">MercadoLibre Venezuela - Reporte diario</p>
                <p class="timestamp">Actualizado: {fecha} a las {hora}</p>
            </header>
            
            <div class="products-grid">
    """
    
    # Generar tarjetas de productos
    for i, row in df.iterrows():
        badges = []
        if row.get('envio_gratis', False):
            badges.append('<span class="badge envio">🚚 Envío Gratis</span>')
        if row.get('tienda_oficial', False):
            badges.append('<span class="badge oficial">🏬 Tienda Oficial</span>')
        
        badges_html = "".join(badges)
        
        # Determinar si el producto es tendencia
        is_trending = row.get('mensajes', 0) > 50 or row.get('ventas', 0) > 100
        
        html += f"""
        <div class="product-card">
            {"<span class='product-badge'>🔥 TENDENCIA</span>" if is_trending else ""}
            <div class="product-title">{row['titulo']}</div>
            <div class="product-price">Bs. {row['precio']:,.2f}</div>
            
            <div class="badges-container">
                {badges_html}
            </div>
            
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-value">{row['ventas']}</div>
                    <div class="stat-label">Ventas</div>
                </div>
                <div class="stat-card {'highlight-stat' if row.get('mensajes', 0) > 20 else ''}">
                    <div class="stat-value">{row.get('mensajes', 0)}</div>
                    <div class="stat-label">Mensajes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{row['rating']:.1f}/5</div>
                    <div class="stat-label">Rating</div>
                </div>
            </div>
            
            <div class="why-box">
                <strong>💡 Por qué destaca:</strong> Alto interés de compradores con {row.get('mensajes', 0)} mensajes en los últimos días
            </div>
            
            <a href="{row['link']}" class="btn" target="_blank">Ver Producto en MercadoLibre</a>
        </div>
        """
    
    html += """
            </div>
            
            <footer>
                <p>Reporte generado automáticamente - Actualizado diariamente</p>
                <p>⚠️ Este es un proyecto de automatización, no afiliado a MercadoLibre</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return html

if __name__ == "__main__":
    crear_reporte_html()
