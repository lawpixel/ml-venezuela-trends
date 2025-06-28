import pandas as pd
from datetime import datetime, timedelta
import os
import json

def crear_reporte_html():
    os.makedirs("docs", exist_ok=True)
    
    # Intentar cargar datos históricos para tendencias
    historical_data = load_historical_data()
    
    # Manejo específico de excepciones
    try:
        df = pd.read_csv("data/processed.csv")
        # Validar que el DataFrame tiene las columnas necesarias
        required_columns = ['titulo', 'precio', 'link']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"⚠️ Columnas faltantes: {missing_columns}")
            df = pd.DataFrame()
    except FileNotFoundError:
        print("❌ Archivo processed.csv no encontrado")
        df = pd.DataFrame()
    except pd.errors.EmptyDataError:
        print("❌ Archivo CSV vacío")
        df = pd.DataFrame()
    except pd.errors.ParserError as e:
        print(f"❌ Error parseando CSV: {e}")
        df = pd.DataFrame()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        df = pd.DataFrame()
    
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    hora_actual = datetime.now().strftime('%H:%M')
    
    if df.empty:
        html = generate_error_html(fecha_actual, hora_actual)
    else:
        html = generate_success_html(df, fecha_actual, hora_actual, historical_data)
    
    try:
        with open("docs/index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("📊 Reporte HTML generado exitosamente")
    except Exception as e:
        print(f"❌ Error escribiendo HTML: {e}")

def load_historical_data():
    """Carga datos históricos para análisis de tendencias"""
    historical = []
    try:
        # Buscar archivos de los últimos 3 días
        for i in range(1, 4):
            fecha_anterior = datetime.now() - timedelta(days=i)
            file_path = f"data/processed_{fecha_anterior.strftime('%Y%m%d')}.csv"
            if os.path.exists(file_path):
                try:
                    df_hist = pd.read_csv(file_path)
                    historical.append(df_hist)
                except Exception as e:
                    print(f"⚠️ Error cargando archivo histórico {file_path}: {e}")
                    continue
        print(f"📚 Datos históricos cargados: {len(historical)} archivos")
    except Exception as e:
        print(f"⚠️ Error general cargando datos históricos: {e}")
    return historical

def safe_format_price(price_value):
    """Formatea precios de manera segura"""
    try:
        if pd.isna(price_value):
            return "No disponible"
        price_float = float(price_value)
        return f"Bs. {price_float:,.2f}"
    except (ValueError, TypeError):
        return "Precio no válido"

def safe_format_rating(rating_value):
    """Formatea rating de manera segura"""
    try:
        if pd.isna(rating_value):
            return "Sin rating"
        rating_float = float(rating_value)
        return f"{rating_float:.1f}/5"
    except (ValueError, TypeError):
        return "N/A"

def safe_get_int(row, column, default=0):
    """Obtiene valor entero de manera segura"""
    try:
        value = row.get(column, default)
        if pd.isna(value):
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default

def generate_success_html(df, fecha, hora, historical_data):
    """Genera HTML exitoso con los productos"""
    # Validar y limpiar datos antes de generar HTML
    df = df.fillna({
        'titulo': 'Sin título',
        'precio': 0,
        'ventas': 0,
        'mensajes': 0,
        'rating': 0,
        'envio_gratis': False,
        'tienda_oficial': False,
        'link': '#'
    })
    
    # Encabezado del reporte (mantener igual)
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Top Productos con Más Mensajes - MercadoLibre VE</title>
        <style>
            /* Estilos iguales al original */
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
    
    # Generar tarjetas de productos con manejo seguro
    for i, row in df.iterrows():
        badges = []
        if row.get('envio_gratis', False):
            badges.append('<span class="badge envio">🚚 Envío Gratis</span>')
        if row.get('tienda_oficial', False):
            badges.append('<span class="badge oficial">🏬 Tienda Oficial</span>')
        
        badges_html = "".join(badges)
        
        # Obtener valores de manera segura
        titulo = str(row.get('titulo', 'Sin título'))[:100] + ('...' if len(str(row.get('titulo', ''))) > 100 else '')
        precio_formatted = safe_format_price(row.get('precio', 0))
        ventas = safe_get_int(row, 'ventas', 0)
        mensajes = safe_get_int(row, 'mensajes', 0)
        rating_formatted = safe_format_rating(row.get('rating', 0))
        link = str(row.get('link', '#'))
        
        # Determinar si el producto es tendencia
        is_trending = mensajes > 50 or ventas > 100
        
        html += f"""
        <div class="product-card">
            {"<span class='product-badge'>🔥 TENDENCIA</span>" if is_trending else ""}
            <div class="product-title">{titulo}</div>
            <div class="product-price">{precio_formatted}</div>
            
            <div class="badges-container">
                {badges_html}
            </div>
            
            <div class="stats-container">
                <div class="stat-card">
                    <div class="stat-value">{ventas}</div>
                    <div class="stat-label">Ventas</div>
                </div>
                <div class="stat-card {'highlight-stat' if mensajes > 20 else ''}">
                    <div class="stat-value">{mensajes}</div>
                    <div class="stat-label">Mensajes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{rating_formatted}</div>
                    <div class="stat-label">Rating</div>
                </div>
            </div>
            
            <div class="why-box">
                <strong>💡 Por qué destaca:</strong> Alto interés de compradores con {mensajes} mensajes en los últimos días
            </div>
            
            <a href="{link}" class="btn" target="_blank">Ver Producto en MercadoLibre</a>
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

# Mantener generate_error_html igual al original

if __name__ == "__main__":
    crear_reporte_html()
