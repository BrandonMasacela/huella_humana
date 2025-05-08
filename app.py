from shiny import App, ui, render, reactive
import pandas as pd
from shinywidgets import output_widget, register_widget, render_widget
import ipyleaflet as L
from ipywidgets import HTML
import os
import base64
from io import BytesIO
import requests
from faicons import icon_svg
from ipywidgets import Layout
import plotly.express as px

# Firebase configuration
class FirebaseStorage:
    def __init__(self, config, token=None):
        self.base_url = f"https://firebasestorage.googleapis.com/v0/b/{config['storageBucket']}/o/"
        self.token = token

    def get_image_url(self, image_path):
        encoded_path = image_path.replace('/', '%2F')
        token_param = f"&token={self.token}" if self.token else ""
        return f"{self.base_url}{encoded_path}?alt=media{token_param}"
    
    def get_image_data(self, image_path):
        """
        Fetch image data from Firebase Storage
        """
        url = self.get_image_url(image_path)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Error fetching image: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception in get_image_data: {e}")
            return None

# Initialize Firebase Storage
firebase_config = {
    "apiKey": "AIzaSyCKCUZLWHB3ImeWTajyHzGL1Qgtu9VEmyg",
    "authDomain": "pry-tiendavino.firebaseapp.com",
    "databaseURL": "https://pry-tiendavino-default-rtdb.firebaseio.com",
    "projectId": "pry-tiendavino",
    "storageBucket": "pry-tiendavino.appspot.com",
    "messagingSenderId": "49625325609",
    "appId": "1:49625325609:web:157b26e4611ba2a8e63c38"
}
firebase_storage = FirebaseStorage(firebase_config)

# Load CSV data from Firebase Storage
csv_path = "MapasPNG/HH_predeterminado.csv"
csv_url = firebase_storage.get_image_url(csv_path)
data = pd.read_csv(csv_url)

# Extraer categorías y años
categorias = data['txt_rango'].unique().tolist()
years = data['year'].unique().tolist()

# Load data
#data = pd.read_csv("MapasPNG/HH_predeterminado.csv")
#categorias = data['txt_rango'].unique().tolist()
#years = data['year'].unique().tolist()


# UI - All in one dashboard
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.style("""
            /* ESTILOS GENERALES */
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
            body {
                font-family: 'Poppins', sans-serif;
                background-color: #f5f7fa;
                color: #2c3e50;
            }
            
            /* NAVBAR */
            .navbar {
                background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border: none;
            }
            .navbar-brand {
                color: white !important;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            
            /* TARJETAS */
            .card {
                border-radius: 10px;
                border: none;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                overflow: hidden;
            }
            .card:hover {
                box-shadow: 0 6px 20px rgba(0,0,0,0.12);
                transform: translateY(-2px);
            }
            .card-header {
                background: linear-gradient(to right, #f8f9fa, #e9ecef);
                font-weight: 600;
                border-bottom: 1px solid #e9ecef;
                padding: 15px 20px;
                color: #2c3e50;
                font-size: 1.1em;
            }
            
            /* TITULO PRINCIPAL */
            .dashboard-title {
                background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
                color: white;
                padding: 20px;
                margin-bottom: 25px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                position: relative;
                overflow: hidden;
            }
            .dashboard-title h1 {
                margin: 0;
                font-weight: 700;
                letter-spacing: 1px;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
            }
            .dashboard-title::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0,0 L100,0 L100,100 Z" fill="rgba(255,255,255,0.05)"/></svg>') no-repeat;
                background-size: 100% 100%;
            }
            
            /* PANEL DE CONTROL */
            .control-panel {
                padding: 20px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                height: 100%;
            }
            .control-panel h4 {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #e9ecef;
            }
            
            /* BOTONES */
            .btn-primary {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                border: none;
                font-weight: 500;
                letter-spacing: 0.5px;
                padding: 10px 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            .btn-primary:hover {
                background: linear-gradient(135deg, #2980b9 0%, #2471a3 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            /* DOWNLOAD BUTTON */
            .btn-download {
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                border: none;
                font-weight: 500;
                letter-spacing: 0.5px;
                padding: 10px 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
                color: white;
                margin-top: 15px;
            }
            .btn-download:hover {
                background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            
            /* INFO BOX */
            .info-box {
                padding: 20px;
                background-color: #f8f9fa;
                border-left: 5px solid #3498db;
                margin-bottom: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            .info-box h4 {
                color: #2c3e50;
                margin-top: 0;
                font-weight: 600;
                border-bottom: none;
                padding-bottom: 5px;
            }
            .info-box p {
                color: #5d6d7e;
                line-height: 1.6;
            }
            .info-box ul {
                padding-left: 20px;
                color: #5d6d7e;
            }
            .info-box ul li {
                margin-bottom: 8px;
                list-style-type: none;
                position: relative;
            }
            
            /* ELEMENTOS DE ENTRADA */
            .form-control, .selectize-control {
                border-radius: 5px;
                border: 1px solid #dce4ec;
                box-shadow: none;
                transition: all 0.3s ease;
            }
            .form-control:focus, .selectize-input.focus {
                border-color: #3498db;
                box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.25);
            }
            .selectize-dropdown {
                border-radius: 0 0 5px 5px;
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            }
            .selectize-dropdown-content .option.active {
                background-color: #3498db;
            }
            
            /* SLIDER */
            .js-irs-0 .irs-bar {
                background: #3498db;
                border-color: #3498db;
            }
            .js-irs-0 .irs-handle {
                border-color: #3498db;
            }
            
            /* TABLA */
            .reactable {
                border-radius: 5px;
                overflow: hidden;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }
            .reactable-header {
                background-color: #f8f9fa;
                font-weight: 600;
            }
            
            /* DIAGNÓSTICO */
            #diagnostico {
                font-family: 'Courier New', monospace;
                font-size: 0.8em;
                color: #7f8c8d;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 5px;
                margin: 10px 0;
            }
            
            /* CATEGORÍAS COLORES */
            .category-dot {
                display: inline-block;
                width: 15px;
                height: 15px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .cat-very-low { background-color: green; }
            .cat-low { background-color: yellow; }
            .cat-medium { background-color: orange; }
            .cat-high { background-color: red; }
            
            /* RESPONSIVE */
            @media (max-width: 768px) {
                .dashboard-row {
                    flex-direction: column;
                }
                .control-panel {
                    margin-bottom: 20px;
                }
            }
            
            /* ANIMACIONES */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .card {
                animation: fadeIn 0.5s ease;
            }
            
            /* STAT CARD STYLES MEJORADOS */
            .stat-card {
                background: linear-gradient(135deg, #f8f9fa, #edf2f7);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 20px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
            }

            .stat-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.12);
            }

            .stats-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                gap: 20px;
            }

            .stat-item {
                flex: 1;
                min-width: 150px;
                background: white;
                padding: 18px 20px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                position: relative;
                overflow: hidden;
                border: none;
                display: flex;
                flex-direction: column;
                transition: all 0.3s ease;
            }

            .stat-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.12);
            }

            /* Colores de fondo con gradientes */
            .stat-item.blue {
                background: linear-gradient(135deg, #ffffff, #f0f7ff);
                border-left: 5px solid #3498db;
            }

            .stat-item.indigo {
                background: linear-gradient(135deg, #ffffff, #f0f4ff);
                border-left: 5px solid #4b6cb7;
            }

            .stat-item.green {
                background: linear-gradient(135deg, #ffffff, #f0fff7);
                border-left: 5px solid #27ae60;
            }

            .stat-item.orange {
                background: linear-gradient(135deg, #ffffff, #fff8f0);
                border-left: 5px solid #f39c12;
            }

            .stat-item.red {
                background: linear-gradient(135deg, #ffffff, #fff0f0);
                border-left: 5px solid #e74c3c;
            }

            .stat-label {
                font-size: 0.85rem;
                color: #64748b;
                margin-bottom: 8px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .stat-value {
                font-size: 1.4rem;
                font-weight: 700;
                color: #1e293b;
                display: flex;
                align-items: center;
                margin-top: 4px;
            }

            .stat-icon {
                position: absolute;
                top: 50%;
                right: 20px;
                transform: translateY(-50%);
                color: rgba(0,0,0,0.07);
                font-size: 2.2rem;
                transition: all 0.3s ease;
            }

            .stat-item:hover .stat-icon {
                transform: translateY(-50%) scale(1.1);
                color: rgba(0,0,0,0.09);
            }

            /* Indicador de tendencia */
            .stat-trend {
                display: flex;
                align-items: center;
                font-size: 0.8rem;
                margin-top: 8px;
                font-weight: 500;
            }

            .trend-up {
                color: #22c55e;
            }

            .trend-down {
                color: #ef4444;
            }

            .trend-stable {
                color: #64748b;
            }

            .trend-icon {
                margin-right: 4px;
            }

            /* Responsive */
            @media (max-width: 768px) {
                .stats-container {
                    flex-direction: column;
                }
                
                .stat-item {
                    width: 100%;
                    margin-bottom: 15px;
                }
            }
        """),
        ui.tags.link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css"),
    ),
    ui.div(
        ui.div(
            ui.h1("Huella Humana - Ecuador", class_="text-center"),
            ui.p("Sistema de Monitoreo del Impacto de las Actividades Humanas", class_="text-center text-white mb-0"),
            class_="dashboard-title"
        ),
        class_="dashboard-row"
    ),
    ui.row(
        # Left column - Controls
        ui.column(
            3,
            ui.div(
                ui.h4("Panel de Control", class_="mb-3"),
                ui.card(
                    ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-map"), " Controles del Mapa")),
                    ui.card_body(
                        ui.div(
                            ui.tags.div(ui.tags.i(class_="fas fa-filter"), " Año:", class_="mb-2"),
                            ui.input_select("year", "", choices=years, width="100%"),
                            ui.tags.div(style="margin-bottom: 15px"),
                            ui.output_text_verbatim("diagnostico"),
                            ui.tags.div(style="margin-bottom: 15px"),
                            ui.tags.div(ui.tags.i(class_="fas fa-adjust"), " Opacidad:", class_="mb-2"),
                            ui.input_slider("opacidad", "", min=0, max=1, value=0.8, step=0.1),
                        )
                    )
                ),
                ui.card(
                    ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-filter"), " Filtros")),
                    ui.card_body(
                        ui.tags.div(ui.tags.i(class_="fas fa-tags"), " Categorías:", class_="mb-2"),
                        ui.input_selectize("categorias", "", 
                                         choices=categorias, 
                                         selected=[categorias[0]], 
                                         multiple=True,
                                         width="100%"),
                        ui.input_action_button("aplicar_filtro", 
                                              ui.tags.div(ui.tags.i(class_="fas fa-check"), " Aplicar Filtros"), 
                                              class_="btn-primary w-100"),
                        # Botón para descargar datos
                        ui.download_button("descargar_datos", 
                                          ui.tags.div(ui.tags.i(class_="fas fa-download"), " Descargar Datos"), 
                                          class_="btn-download w-100")
                    )
                ),
                ui.div(
                    ui.h4(ui.tags.i(class_="fas fa-info-circle"), " Acerca del Dashboard", class_="mt-4"),
                    ui.p("Este dashboard presenta información sobre el índice de Huella Humana en Ecuador, una herramienta para el monitoreo ambiental y la toma de decisiones."),
                    ui.p("El Índice de Huella Humana (HH) es una medida espacial que cuantifica el impacto acumulativo de las actividades humanas en los ecosistemas y la biodiversidad."),
                    ui.tags.p(ui.tags.strong("Clasificación por categorías:")),
                    ui.tags.ul(
                        ui.tags.li(ui.tags.span("", class_="category-dot cat-very-low"), "Muy Baja: Áreas con mínima influencia humana"),
                        ui.tags.li(ui.tags.span("", class_="category-dot cat-low"), "Baja: Áreas con influencia humana limitada"),
                        ui.tags.li(ui.tags.span("", class_="category-dot cat-medium"), "Media: Áreas con moderada influencia humana"),
                        ui.tags.li(ui.tags.span("", class_="category-dot cat-high"), "Alta: Áreas con intensa influencia humana")
                    ),
                    class_="info-box"
                ),
                class_="control-panel"
            )
        ),
        # Right column - Visualization
        ui.column(
            9,
             ui.div(
                ui.div(
                    ui.div(
                        # Stat card para Año
                        ui.div(
                            ui.div("Año", class_="stat-label"),
                            ui.div(ui.output_text("vb_anio"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-calendar"), class_="stat-icon"),
                            class_="stat-item blue"
                        ),
                        
                        # Stat card para Categoría
                        ui.div(
                            ui.div("Categoría", class_="stat-label"),
                            ui.div(ui.output_text("vb_categoria"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-map"), class_="stat-icon"),
                            class_="stat-item orange"
                        ),
                        
                        # Stat card para Área
                        ui.div(
                            ui.div("Área (ha)", class_="stat-label"),
                            ui.div(ui.output_text("vb_area"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-chart-bar"), class_="stat-icon"),
                            class_="stat-item green"
                        ),
                        
                        # Stat card para Porcentaje
                        ui.div(
                            ui.div("Porcentaje", class_="stat-label"),
                            ui.div(ui.output_text("vb_porcentaje"), class_="stat-value"),
                            ui.div(ui.tags.i(class_="fas fa-percent"), class_="stat-icon"),
                            class_="stat-item red"
                        ),
                        
                        class_="stats-container"
                    ),
                    class_="stat-card"
                ),
                class_="mb-4"
            ),
            ui.row(
                ui.column(
                    12,
                    ui.card(
                        ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-globe-americas"), " Mapa de Huella Humana")),
                        ui.card_body(
                            output_widget("map", height="600px"),
                        )
                    ),
                    class_="mb-4"
                )
            ),
            ui.row(
                ui.column(
                    6,
                    ui.card(
                        ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-chart-line"), " Evolución Temporal")),
                        ui.card_body(
                            output_widget("grafico_temporal", height="400px"),
                        )
                    ),
                ),
                ui.column(
                    6,
                    ui.card(
                        ui.card_header(ui.tags.div(ui.tags.i(class_="fas fa-table"), " Tabla de Datos")),
                        ui.card_body(
                            ui.div(
                                ui.output_data_frame("tabla"),
                                style="height:400px; overflow:auto;"
                            ),
                        )
                    ),
                )
            )
        )
    ),
    ui.tags.footer(
        ui.div(
            ui.p("© 2025 Huella Humana Ecuador | Desarrollado con Python Shiny", class_="text-center text-muted"),
            class_="mt-4 pt-3 border-top"
        )
    ),
    ui.tags.script(src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/js/all.min.js", integrity="sha512-u3fPA7V8qQAdO2+QAMSaL0NAW7uK7fEdm5nG4K97YunNkXrtLJ8sFPxO3hWVtYZUh8Dyg24KnPBwunjTqX0VOkQ==", crossorigin="anonymous"),
    title="Huella Humana - Ecuador"
)

# Server logic - unchanged
def server(input, output, session):
    # Mapeo de categorías
    category_mapping = {
        "Muy baja": 1,
        "Baja": 2,
        "Media": 3,
        "Alta": 4
    }
    
    # Mapeo de colores
    color_mapping = {
        "Muy baja": "#228b22",
        "Baja": "#ffff00",
        "Media": "#ffa500",
        "Alta": "#ff0000"
    }
    
    # Estados reactivos
    filtered_data = reactive.Value(data)
    current_categories = reactive.Value([])
    map_obj = reactive.Value(None)
    layer_dict = reactive.Value({})
    legend_control = reactive.Value(None)
    
    # Método para calcular porcentajes por categoría y año
    def get_category_percentages(year):
        df_year = data[data['year'] == int(year)]
        if df_year.empty:
            return {cat: 0 for cat in category_mapping}
        
        total_area = df_year['area'].sum()
        percentages = {}
        for cat in category_mapping:
            cat_area = df_year[df_year['txt_rango'] == cat]['area'].sum()
            percentage = (cat_area / total_area * 100) if total_area > 0 else 0
            percentages[cat] = round(percentage, 2)
        return percentages
    
    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_anio():
        return str(input.year())

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_categoria():
        selected_year = str(input.year())
        # Load CSV data from Firebase Storage
        csv_path = "MapasPNG/HH_predeterminado.csv"
        csv_url = firebase_storage.get_image_url(csv_path)
        data = pd.read_csv(csv_url)
        data = data[data["year"] == int(selected_year)]

        if not data.empty:
            if selected_year == "2014":
                fila_max = data.loc[data["area"].idxmax()]
                return str(fila_max["txt_rango"])
            elif selected_year == "2016":
                fila_max = data.loc[data["area"].idxmax()]
                return str(fila_max["txt_rango"])
            elif selected_year == "2018":
                fila_max = data.loc[data["area"].idxmax()]
                return str(fila_max["txt_rango"])
            elif selected_year == "2020":
                fila_max = data.loc[data["area"].idxmax()]
                return str(fila_max["txt_rango"])
        return "Sin datos"

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_area():
        selected_year = str(input.year())
        # Load CSV data from Firebase Storage
        csv_path = "MapasPNG/HH_predeterminado.csv"
        csv_url = firebase_storage.get_image_url(csv_path)
        data = pd.read_csv(csv_url)
        data = data[data["year"] == int(selected_year)]

        if not data.empty:
            if selected_year == "2014":
                fila_max = data.loc[data["area"].idxmax()]
                return str(round(fila_max["area"], 2))
            elif selected_year == "2016":
                fila_max = data.loc[data["area"].idxmax()]
                return str(round(fila_max["area"], 2))
            elif selected_year == "2018":
                fila_max = data.loc[data["area"].idxmax()]
                return str(round(fila_max["area"], 2))
            elif selected_year == "2020":
                fila_max = data.loc[data["area"].idxmax()]
                return str(round(fila_max["area"], 2))
        return "0.00"

    @render.text
    @reactive.event(input.aplicar_filtro)
    def vb_porcentaje():
        selected_year = str(input.year())
        # Load CSV data from Firebase Storage
        csv_path = "MapasPNG/HH_predeterminado.csv"
        csv_url = firebase_storage.get_image_url(csv_path)
        data = pd.read_csv(csv_url)
        data = data[data["year"] == int(selected_year)]

        if not data.empty:
            if selected_year == "2014":
                fila_max = data.loc[data["area"].idxmax()]
                return f"{round(fila_max['percentage'], 2)}%"
            elif selected_year == "2016":
                fila_max = data.loc[data["area"].idxmax()]
                return f"{round(fila_max['percentage'], 2)}%"
            elif selected_year == "2018":
                fila_max = data.loc[data["area"].idxmax()]
                return f"{round(fila_max['percentage'], 2)}%"
            elif selected_year == "2020":
                fila_max = data.loc[data["area"].idxmax()]
                return f"{round(fila_max['percentage'], 2)}%"
        return "0.00%"
    
    # Inicialización del mapa
    @reactive.Effect
    def initialize_map():
        print("Inicializando mapa")
        m = L.Map(
            center=(-1.8, -78.5),
            zoom=7,
            scroll_wheel_zoom=True,
            layout=Layout(width="100%", height="600px")  # Cambia el tamaño aquí
        )
        m.add_layer(L.TileLayer(url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png"))
        
        # Crear leyenda inicial
        year = str(input.year())
        percentages = get_category_percentages(year)
        legend_content = ""
        for cat in input.categorias():
            if cat in category_mapping:
                color = color_mapping[cat]
                percentage = percentages.get(cat, 0)
                legend_content += f'''
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                        <div style="width: 20px; height: 20px; background: {color}; border-radius: 50%; border: 1px solid rgba(0,0,0,0.2);"></div>
                        <span>{cat} ({percentage}%)</span>
                    </div>
                '''
        
        legend_html = HTML(f'''
            <div style="
                background: white;
                padding: 12px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                border: 1px solid rgba(0,0,0,0.05);
                max-width: 200px;
                font-family: 'Poppins', sans-serif;
            ">
                <h4 style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px;">Leyenda HH ({year})</h4>
                <div style="display: flex; flex-direction: column;">
                    {legend_content}
                </div>
            </div>
        ''')
        legend_control = L.WidgetControl(widget=legend_html, position='bottomright')
        m.add_control(legend_control)
        
        map_obj.set(m)
        layer_dict.set({})
        register_widget("map", m)
        
        # Cargar capas para el año inicial
        load_layers_for_year(year)

    # Modificación de la función load_layers_for_year para usar la clase FirebaseStorage

    def load_layers_for_year(year):
        print(f"Cargando capas para el año {year}")
        m = map_obj.get()
        layers = layer_dict.get()

        if year not in layers:
            layers[year] = {}
            bounds = [[-5.01, -81.12], [1.45, -75.17]]  # Extensión geográfica de Ecuador
            
            # Cargar capa combinada
            firebase_path = f"MapasPNG/HH_predeterminado_{year}_cat_all.png"
            #firebase_path = f"https://firebasestorage.googleapis.com/v0/b/pry-tiendavino.appspot.com/o/MapasPNG%2FHH_predeterminado_{year}_cat_all.png?alt=media&token=da6b6902-ec4c-4c54-9ce3-5baaac52eb74"
            img_url = firebase_storage.get_image_url(firebase_path)
            
            if img_url:
                try:
                    image_layer = L.ImageOverlay(
                        url=img_url,
                        bounds=bounds,
                        opacity=1.0,
                        name=f"all_{year}"
                    )
                    layers[year]['all'] = image_layer
                    print(f"Capa 'todas' creada para el año {year}")
                except Exception as e:
                    print(f"Error cargando capa combinada para {year}: {str(e)}")
            
            # Cargar capas individuales
            for cat, cat_num in category_mapping.items():
                firebase_path = f"MapasPNG/HH_predeterminado_{year}_cat_{cat_num}.png"
                #firebase_path = f"https://firebasestorage.googleapis.com/v0/b/pry-tiendavino.appspot.com/o/MapasPNG%2FHH_predeterminado_{year}_cat_{cat_num}.png?alt=media&token=da6b6902-ec4c-4c54-9ce3-5baaac52eb74"
                img_url = firebase_storage.get_image_url(firebase_path)
                
                if img_url:
                    try:
                        image_layer = L.ImageOverlay(
                            url=img_url,
                            bounds=bounds,
                            opacity=0.8,
                            name=f"{cat}_{year}"
                        )
                        layers[year][cat] = image_layer
                        print(f"Capa '{cat}' creada para el año {year}")
                    except Exception as e:
                        print(f"Error cargando capa {cat} para {year}: {str(e)}")
        
        layer_dict.set(layers)
        return layers

    # Actualizar filtros y capas
    @reactive.Effect
    @reactive.event(input.aplicar_filtro)
    def actualizar_filtros():
        cats_validas = [c for c in input.categorias() if c in category_mapping]
        year = str(input.year())
        
        print(f"Actualizando filtros: Año={year}, Categorías={cats_validas}")
        current_categories.set(cats_validas)
        filtered_data.set(data[data['txt_rango'].isin(cats_validas)])
        
        layers = load_layers_for_year(year)
        m = map_obj.get()
        
        for layer in list(m.layers):
            if isinstance(layer, L.ImageOverlay):
                m.remove_layer(layer)
        
        if sorted(cats_validas) == sorted(categorias) and 'all' in layers[year]:
            layers[year]['all'].opacity = input.opacidad()
            m.add_layer(layers[year]['all'])
            print("Mostrando capa combinada")
        else:
            for cat in cats_validas:
                if cat in layers[year]:
                    layers[year][cat].opacity = input.opacidad()
                    m.add_layer(layers[year][cat])
                    print(f"Mostrando capa para categoría: {cat}")

    # Actualizar opacidad
    @reactive.Effect
    @reactive.event(input.opacidad)
    def actualizar_opacidad():
        m = map_obj.get()
        if m is None:
            return
        new_opacity = input.opacidad()
        for layer in m.layers:
            if isinstance(layer, L.ImageOverlay):
                layer.opacity = new_opacity
        print(f"Opacidad actualizada a {new_opacity}")

    # Gráfico temporal
    @output
    @render_widget
    def grafico_temporal():
        df = filtered_data.get()
        if df.empty:
            return px.scatter(title="Sin datos")
        
        df_grouped = df.groupby(['txt_rango', 'year'])['area'].sum().reset_index()
        color_discrete_map = {
            "Muy baja": "green",
            "Baja": "yellow",
            "Media": "orange",
            "Alta": "red"
        }
        
        fig = px.line(
            df_grouped,
            x="year",
            y="area",
            color="txt_rango",
            color_discrete_map=color_discrete_map,
            markers=True,
            title="Evolución Temporal de la Huella Humana",
            labels={"year": "Año", "area": "Área (km²)", "txt_rango": "Categoría"}
        )
        fig.update_traces(hovertemplate="<b>Año:</b> %{x}<br><b>Área:</b> %{y:.2f} km²<extra></extra>")
        fig.update_layout(hovermode="x unified", legend_title_text="Categorías", template="plotly_white", xaxis=dict(tickmode='linear', dtick=1))
        return fig

    # Tabla de datos
    @output
    @render.data_frame
    def tabla():
        df = filtered_data.get()
        df = df[df['year'] == int(input.year())]
        
        # Renombrar columnas y formatear
        df_display = df.rename(columns={
            'year': 'Año',
            'txt_rango': 'Categoría',
            'area': 'Área (km²)'
        })
        
        # Seleccionar columnas y formatear decimales
        df_display = df_display[['Año', 'Categoría', 'Área (km²)']]
        df_display['Área (km²)'] = df_display['Área (km²)'].round(2)  # Redondear a 2 decimales
        
        return render.DataGrid(
            df_display, 
            filters=True,
            height="350px",
            width="100%"
        )
    
    # Diagnóstico
    @output
    @render.text
    def diagnostico():
        return f"Estado: Año {input.year()} | Categorías: {', '.join(current_categories.get())}"
    
    # Funcionalidad de descarga
    @session.download(filename="huella_humana_ecuador.csv")
    def descargar_datos():
        # Obtener los datos filtrados actuales
        df = filtered_data.get()
        
        # Calcular el porcentaje por categoría para cada año
        result_data = []
        for year in df['year'].unique():
            df_year = df[df['year'] == year]
            total_area = df_year['area'].sum()
            
            for _, row in df_year.iterrows():
                percentage = (row['area'] / total_area * 100) if total_area > 0 else 0
                result_data.append({
                    'Anio': row['year'],
                    'Categoria': row['txt_rango'],
                    'Area (km²)': round(row['area'], 2),
                    'Porcentaje (%)': round(percentage, 2)
                })
        
        # Crear DataFrame con los datos procesados
        result_df = pd.DataFrame(result_data)
        
        # Crear un BytesIO buffer para guardar el CSV
        buffer = BytesIO()
        
        # Guardar los datos procesados en formato CSV
        result_df.to_csv(buffer, index=False, encoding='utf-8')
        
        # Mover el cursor al inicio del buffer
        buffer.seek(0)
        
        # Devolver el contenido del buffer
        return buffer

# Create app
app = App(app_ui, server)