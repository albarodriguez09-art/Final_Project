# src/final_project/hosts.py

class Host:
    def __init__(self, host_id, place_id, area_of_origin):
        self.host_id = host_id
        self.profits = 0.0  # Fondos disponibles (float para mejor manejo)
        self.assets = {place_id} # Conjunto de place_id propios
        self.area_of_origin = area_of_origin 

    def update_profits(self, city):
        """Actualiza los fondos del host con las ganancias mensuales de sus listings."""
        total_earnings = 0.0
        # Es crucial usar una copia de self.assets porque la propiedad puede cambiar
        # si una transacción se ejecuta en el paso intermedio.
        for place_id in list(self.assets): 
            if place_id in city.places:
                place = city.places[place_id]
                total_earnings += place.get_monthly_earnings()
        
        self.profits += total_earnings
        
    def make_bids(self, city):
        """Genera una lista de ofertas para adquirir propiedades adyacentes."""
        bids = []
        opportunities = set()
        
        # 1. Identificar Oportunidades
        for my_place_id in self.assets:
            if my_place_id in city.places:
                my_place = city.places[my_place_id]
                for neighbor_id in my_place.neighbors:
                    neighbor_place = city.places[neighbor_id]
                    # Oportunidad: vecino que NO es propiedad de este host
                    if neighbor_place.host_id != self.host_id:
                        opportunities.add(neighbor_id)
                    
        # 2. Crear Ofertas
        for pid in opportunities:
            place = city.places[pid]
            ask_price = place.get_ask_price()
            
            # ----------------------------------------------------------------------
            # [Inicio] Lógica para el Graph 2 V1: Modificación de la Regla
            # Descomenta las siguientes 2 líneas y comenta la anterior para probar V1
            # ----------------------------------------------------------------------
            # if city.is_v1_active and place.area != self.area_of_origin:
            #     continue # El host solo puede comprar en su área de origen (V1)
            # ----------------------------------------------------------------------
            # [Fin] Lógica V1
            # ----------------------------------------------------------------------

            # Condición de oferta: el host puede pagar
            if self.profits >= ask_price:
                # La oferta (bid_price) es el total de sus ganancias disponibles
                bid = {
                    'place_id': pid,
                    'seller_id': place.host_id,
                    'buyer_id': self.host_id,
                    'spread': self.profits - ask_price, 
                    'bid_price': self.profits
                }
                bids.append(bid)
                
        return bids