# src/final_project/city.py

import random
import pandas as pd
from .place import Place
from .hosts import Host

class City:
    def __init__(self, size, area_rates, seed=42, is_v1_active=False):
        self.size = size 
        self.area_rates = area_rates
        self.step = 0
        self.places = {} 
        self.hosts = {} 
        self.is_v1_active = is_v1_active # Flag para la versión modificada
        
        random.seed(seed) # Asegura la reproducibilidad
        
    def initialize(self):
        """Crea todos los objetos Place y Host iniciales."""
        
        host_id_counter = 0
        total_places = self.size * self.size
        
        for place_id in range(total_places):
            
            # Crea el Place y lo configura
            place = Place(place_id, host_id_counter, self)
            place.setup(self.size, self.area_rates)
            self.places[place_id] = place
            
            # Crea el Host. Le pasamos el área de origen
            host = Host(host_id_counter, place_id, place.area)
            self.hosts[host_id_counter] = host
            
            host_id_counter += 1
            
    def get_area_avg_rate(self, area):
        """Calcula la tarifa promedio actual en un área."""
        rates = [place.rate for place in self.places.values() if place.area == area]
        # Devuelve un valor por defecto si no hay listings (aunque siempre habrá)
        return sum(rates) / len(rates) if rates else 100 

    def approve_bids(self, bids):
        """Ordena las ofertas y determina qué transacciones son válidas."""
        if not bids:
            return []
            
        df_bids = pd.DataFrame(bids)
        # 1. Ordenar por 'spread' descendente (oferta más alta sobre el precio de venta)
        df_bids = df_bids.sort_values(by='spread', ascending=False)
        
        approved_transactions = []
        sold_places = set() 
        buyers_who_bought = set() 
        
        for _, bid in df_bids.iterrows():
            place_id = bid['place_id']
            buyer_id = bid['buyer_id']
            
            # 2. Comprobar disponibilidad
            if place_id not in sold_places and buyer_id not in buyers_who_bought:
                
                # Comprobar que el host comprador todavía tiene fondos (por si se modificó)
                buyer = self.hosts.get(buyer_id)
                if buyer and buyer.profits >= bid['bid_price']:
                    approved_transactions.append(bid.to_dict())
                    sold_places.add(place_id)
                    buyers_who_bought.add(buyer_id)
                    
        return approved_transactions

    def execute_transactions(self, transactions):
        """Realiza las transferencias de dinero y propiedad."""
        for tx in transactions:
            place_id = tx['place_id']
            buyer_id = tx['buyer_id']
            seller_id = tx['seller_id']
            bid_price = tx['bid_price']
            
            place = self.places[place_id]
            buyer = self.hosts[buyer_id]
            seller = self.hosts[seller_id]
            
            # 1. Actualizar Propiedad
            if place_id in seller.assets:
                seller.assets.remove(place_id)
            buyer.assets.add(place_id)
            place.host_id = buyer_id
            
            # 2. Actualizar Fondos
            buyer.profits -= bid_price
            seller.profits += bid_price
            
            # 3. Registrar Historial de Precios
            place.price_history[self.step] = bid_price
            
    def clear_market(self):
        """Coordina el proceso completo de clearing."""
        all_bids = []
        for host in self.hosts.values():
            # Solo hosts con activos y ganancias pueden pujar
            if host.assets and host.profits > 0: 
                all_bids.extend(host.make_bids(self))
            
        approved_transactions = self.approve_bids(all_bids)
        
        if approved_transactions:
            self.execute_transactions(approved_transactions)
            
        return approved_transactions

    def iterate(self):
        """Avanza la simulación un paso (mes)."""
        self.step += 1
        
        # 1. Actualizar Ocupación/Demanda
        for place in self.places.values():
            place.calculate_demand()

        # 2. Actualizar Ganancias (antes de pujar)
        for host in self.hosts.values():
            host.update_profits(self)
            
        # 3. Limpiar el Mercado (Bids y Transactions)
        transactions = self.clear_market()
        
        return transactions