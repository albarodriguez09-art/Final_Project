# main.py

import random
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

# Importa la clase City desde tu módulo
from src.final_project.city import City 

# ------------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------------
GRID_SIZE = 10
AREA_RATES = {0: (100, 200), 1: (50, 250), 2: (250, 350), 3: (150, 450)}
SIMULATION_STEPS = 180 # 15 años * 12 meses
SEED = 42

# ------------------------------------------------------------------
# FUNCIONES DE SIMULACIÓN Y ANÁLISIS
# ------------------------------------------------------------------

def run_simulation(city):
    """Ejecuta el bucle principal de la simulación."""
    city.initialize()
    
    # Lista para almacenar el precio promedio en cada paso (útil para Graph 2)
    avg_price_history = [] 
    
    for step in range(1, SIMULATION_STEPS + 1):
        city.iterate()
        
        # Recopilar datos: Precio promedio de venta
        all_prices = [place.get_ask_price() for place in city.places.values()]
        if all_prices:
            avg_price_history.append(sum(all_prices) / len(all_prices))

    return avg_price_history

def calculate_host_wealth(city):
    """Calcula la riqueza total de cada host (Profits + Valor de Activos)."""
    wealth_data = []
    
    for host_id, host in city.hosts.items():
        total_assets_value = 0.0
        
        for place_id in host.assets:
            if place_id in city.places: # Comprobación de seguridad
                place = city.places[place_id]
                total_assets_value += place.get_ask_price()
            
        total_wealth = host.profits + total_assets_value
        
        # Filtrar hosts sin activos o riqueza (si han desaparecido del juego)
        if total_wealth > 0 or len(host.assets) > 0:
            wealth_data.append({
                'host_id': host_id,
                'wealth': total_wealth,
                'area_of_origin': host.area_of_origin
            })
        
    return pd.DataFrame(wealth_data)

# ------------------------------------------------------------------
# FUNCIONES DE GRÁFICOS
# ------------------------------------------------------------------

def generate_graph1(wealth_df, filename="reports/graph1.png"):
    """
    Genera el gráfico de barras vertical de riqueza total de los hosts.
    - Altura: Riqueza total.
    - Color: Área de origen.
    - Orden: De menor a mayor riqueza.
    """
    
    # 1. Ordenar por riqueza
    wealth_df = wealth_df.sort_values(by='wealth').reset_index(drop=True)
    
    # 2. Definir colores para las áreas
    colors = {0: '#3498db', 1: '#2ecc71', 2: '#e74c3c', 3: '#f39c12'}
    bar_colors = [colors[area] for area in wealth_df['area_of_origin']]
    
    plt.figure(figsize=(20, 10)) # Un tamaño más grande para 100 barras
    
    # 3. Graficar
    plt.bar(wealth_df['host_id'].astype(str), wealth_df['wealth'], color=bar_colors)
    
    plt.title('Riqueza Total de los Hosts al Final de la Simulación', fontsize=16)
    plt.xlabel('ID del Host (Ordenado por Riqueza)', fontsize=14)
    plt.ylabel('Riqueza Total (Profits + Valor de Activos)', fontsize=14)
    
    # 4. Leyenda para los colores de las áreas
    handles = [plt.Rectangle((0,0),1,1, color=colors[area]) for area in colors]
    labels = [f'Área {area}' for area in colors]
    plt.legend(handles, labels, title='Área de Origen', fontsize=12)
    
    # Reducir ticks del eje X para mejor visualización
    n = len(wealth_df)
    tick_positions = np.arange(0, n, max(1, n // 20)) # Mostrar máximo 20 ticks
    plt.xticks(tick_positions, wealth_df['host_id'].iloc[tick_positions].astype(str), rotation=90, fontsize=8)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    print(f"✅ Gráfico 1 guardado en {filename}")
    plt.close()

def generate_graph2(avg_price_history, version, filename_template="reports/graph2_v{}.png"):
    """Genera el gráfico adicional que muestra un aspecto interesante."""
    
    filename = filename_template.format(version)
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(avg_price_history) + 1), avg_price_history, 
             label=f'V{version} Promedio de Precio', color='purple' if version == 0 else 'green')
    
    title = f'V{version}: Evolución del Precio de Venta Promedio de Propiedades'
    if version == 1:
        title += ' (Regla Modificada: Hosts solo compran en Área de Origen)'
        
    plt.title(title)
    plt.xlabel('Paso de Tiempo (Meses)')
    plt.ylabel('Precio Promedio de Venta')
    plt.grid(True, alpha=0.5)
    
    plt.tight_layout()
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    print(f"✅ Gráfico 2 V{version} guardado en {filename}")
    plt.close()

# ------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ------------------------------------------------------------------

if __name__ == "__main__":
    
    # --- V0: Versión Original del Modelo ---
    print("Iniciando Simulación (Versión Original V0)...")
    city_v0 = City(GRID_SIZE, AREA_RATES, SEED, is_v1_active=False)
    random.seed(SEED) # Resetear seed para la reproducibilidad
    avg_price_history_v0 = run_simulation(city_v0)
    
    # Calcular Riqueza V0
    wealth_df_v0 = calculate_host_wealth(city_v0)
    
    # Generar Gráficos V0
    generate_graph1(wealth_df_v0) 
    generate_graph2(avg_price_history_v0, version=0)

    # --- V1: Versión Modificada del Modelo ---
    # Para activar el cambio, descomenta las líneas en src/final_project/hosts.py
    # donde se usa `city.is_v1_active`.
    print("\nIniciando Simulación (Versión Modificada V1)...")
    city_v1 = City(GRID_SIZE, AREA_RATES, SEED, is_v1_active=True)
    random.seed(SEED) # Resetear seed para la reproducibilidad
    avg_price_history_v1 = run_simulation(city_v1)
    
    # Generar Gráfico V1
    generate_graph2(avg_price_history_v1, version=1)
    
    print("\nSimulación completa. Verifica la carpeta 'reports/'.")