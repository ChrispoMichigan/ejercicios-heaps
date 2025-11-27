
import random
import heapq
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Customer:
    id: int
    arrival_time: int  # Tiempo de llegada
    entry_time: int | None = None # Tiempo de entrada
    exit_time: int | None = None # Tiempo de salida
    
    def __lt__(self, other):
        # Para ordenar en la cola de prioridad por tiempo de llegada
        return self.arrival_time < other.arrival_time

@dataclass
class Event:
    time: int
    event_type: str  # 'arrival', 'finish_turnstile', 'finish_visit'
    customer_id: int | None = None
    turnstile_id: int | None = None
    
    def __lt__(self, other):
        return self.time < other.time

class ArtGallerySimulation:
    def __init__(self, total_time_hours: int = 6) -> None:
        self.total_time = total_time_hours * 3600  # Convertir a segundos
        self.current_time = 0
        
        # Colas y estructuras de datos
        self.waiting_queue = []  # Cola de espera (heap)
        self.event_queue = []    # Cola de eventos (heap)
        self.turnstiles = [None, None, None]  # 3 torniquetes (None = libre)
        self.people_in_gallery = 0  # Personas actualmente en la sala
        
        # Estadísticas
        self.total_arrivals = 0
        self.total_entries = 0
        self.total_departures = 0
        self.waiting_times = []
        self.customers = {}  # Diccionario para almacenar clientes por ID
        
        # Parámetros del sistema
        self.max_capacity = 50
        self.mean_interarrival = 120  # 2 minutos en segundos
        self.service_time = 60  # 1 minuto en segundos
        self.min_visit_time = 15 * 60  # 15 minutos en segundos
        self.max_visit_time = 25 * 60  # 25 minutos en segundos
        
        self.next_customer_id = 1
        
    def calculate_abandonment_probability(self, queue_size: int) -> float:
        """
        Calcula la probabilidad de abandono basada en el tamaño de la cola.
        - > 10 personas: 20% base
        - +10% por cada 15 personas adicionales
        - Máximo 50%
        """
        if queue_size <= 10:
            return 0.0
        
        base_prob = 0.20  # 20% para más de 10 personas
        additional_groups = (queue_size - 10) // 15
        additional_prob = additional_groups * 0.10
        
        return min(base_prob + additional_prob, 0.50)
    
    def generate_interarrival_time(self) -> int:
        """Genera tiempo entre llegadas usando distribución exponencial"""
        lambda_rate = 1 / self.mean_interarrival
        return round(random.expovariate(lambda_rate))
    
    def generate_service_time(self) -> int:
        """Genera tiempo de servicio exponencial con media 1 minuto"""
        lambda_rate = 1 / self.service_time
        return round(random.expovariate(lambda_rate))
    
    def generate_visit_time(self) -> int:
        """Genera tiempo de visita uniformemente distribuido entre 15 y 25 minutos"""
        return random.randint(self.min_visit_time, self.max_visit_time)
    
    def schedule_event(self, time: int, event_type: str, customer_id: int | None = None, turnstile_id: int | None = None):
        """Programa un evento en la cola de eventos"""
        event = Event(time, event_type, customer_id, turnstile_id)
        heapq.heappush(self.event_queue, event)
    
    def process_arrival(self, customer_id: int):
        """Procesa la llegada de un cliente"""
        self.total_arrivals += 1
        queue_size = len(self.waiting_queue)
        
        # Verificar si el cliente abandona
        abandon_prob = self.calculate_abandonment_probability(queue_size)
        if random.random() < abandon_prob:
            print(f"Tiempo {self.current_time}: Cliente {customer_id} abandona la cola (prob: {abandon_prob:.2f})")
            return
        
        # Cliente se une a la cola
        customer = Customer(customer_id, self.current_time)
        self.customers[customer_id] = customer
        heapq.heappush(self.waiting_queue, customer)
        print(f"Tiempo {self.current_time}: Cliente {customer_id} se une a la cola (tamaño: {len(self.waiting_queue)})")
        
        # Intentar asignar a un torniquete si hay uno libre
        self.try_assign_turnstile()
    
    def try_assign_turnstile(self):
        """Intenta asignar clientes en espera a torniquetes libres"""
        if not self.waiting_queue or self.people_in_gallery >= self.max_capacity:
            return
        
        for i in range(3):  # 3 torniquetes
            if self.turnstiles[i] is None and self.waiting_queue:
                # Asignar cliente al torniquete
                customer = heapq.heappop(self.waiting_queue)
                self.turnstiles[i] = customer.id
                
                # Calcular tiempo de espera
                waiting_time = self.current_time - customer.arrival_time
                self.waiting_times.append(waiting_time)
                
                # Programar finalización del servicio
                service_time = self.generate_service_time()
                finish_time = self.current_time + service_time
                self.schedule_event(finish_time, 'finish_turnstile', customer.id, i)
                
                print(f"Tiempo {self.current_time}: Cliente {customer.id} asignado al torniquete {i+1} (espera: {waiting_time}s)")
    
    def process_turnstile_finish(self, customer_id: int, turnstile_id: int):
        """Procesa cuando un cliente termina en el torniquete"""
        # Liberar torniquete
        self.turnstiles[turnstile_id] = None
        
        # Cliente entra a la sala
        customer = self.customers[customer_id]
        customer.entry_time = self.current_time
        self.people_in_gallery += 1
        self.total_entries += 1
        
        # Programar salida de la sala
        visit_time = self.generate_visit_time()
        exit_time = self.current_time + visit_time
        self.schedule_event(exit_time, 'finish_visit', customer_id)
        
        print(f"Tiempo {self.current_time}: Cliente {customer_id} entra a la sala (ocupación: {self.people_in_gallery}/{self.max_capacity})")
        
        # Intentar asignar siguiente cliente al torniquete
        self.try_assign_turnstile()
    
    def process_visit_finish(self, customer_id: int):
        """Procesa cuando un cliente termina su visita"""
        customer = self.customers[customer_id]
        customer.exit_time = self.current_time
        self.people_in_gallery -= 1
        self.total_departures += 1
        
        print(f"Tiempo {self.current_time}: Cliente {customer_id} sale de la sala (ocupación: {self.people_in_gallery}/{self.max_capacity})")
        
        # Intentar asignar clientes en espera a torniquetes
        self.try_assign_turnstile()
    
    def run_simulation(self):
        """Ejecuta la simulación completa"""
        print("=== INICIANDO SIMULACIÓN DE LA SALA DE ARTE ===\n")
        
        # Programar primera llegada
        first_arrival = self.generate_interarrival_time()
        self.schedule_event(first_arrival, 'arrival', self.next_customer_id)
        self.next_customer_id += 1
        
        while self.event_queue and self.current_time < self.total_time:
            # Obtener próximo evento
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            if self.current_time > self.total_time:
                break
            
            # Procesar evento según su tipo
            if event.event_type == 'arrival':
                self.process_arrival(event.customer_id)
                
                # Programar siguiente llegada
                next_arrival = self.current_time + self.generate_interarrival_time()
                if next_arrival <= self.total_time:
                    self.schedule_event(next_arrival, 'arrival', self.next_customer_id)
                    self.next_customer_id += 1
                    
            elif event.event_type == 'finish_turnstile':
                self.process_turnstile_finish(event.customer_id, event.turnstile_id)
                
            elif event.event_type == 'finish_visit':
                self.process_visit_finish(event.customer_id)
        
        self.print_results()
    
    def print_results(self):
        """Imprime los resultados de la simulación"""
        print(f"\n=== RESULTADOS DE LA SIMULACIÓN ===")
        print(f"Tiempo total simulado: {self.total_time/3600:.1f} horas")
        print(f"\nEstadísticas de llegadas:")
        print(f"• Total de personas que llegaron: {self.total_arrivals}")
        print(f"• Total de personas que entraron: {self.total_entries}")
        print(f"• Total de personas que salieron: {self.total_departures}")
        print(f"• Porcentaje de entrada: {(self.total_entries/self.total_arrivals)*100:.1f}%" if self.total_arrivals > 0 else "• Porcentaje de entrada: 0%")
        
        if self.waiting_times:
            avg_waiting_time = sum(self.waiting_times) / len(self.waiting_times)
            print(f"\nTiempos de espera:")
            print(f"• Tiempo medio de espera: {avg_waiting_time/60:.2f} minutos")
            print(f"• Tiempo máximo de espera: {max(self.waiting_times)/60:.2f} minutos")
            print(f"• Tiempo mínimo de espera: {min(self.waiting_times)/60:.2f} minutos")
        else:
            print(f"\nNo hay datos de tiempo de espera")
        
        print(f"\nEstado final:")
        print(f"• Personas en cola al final: {len(self.waiting_queue)}")
        print(f"• Personas en la sala al final: {self.people_in_gallery}")
        
        # Torniquetes ocupados al final
        occupied_turnstiles = sum(1 for t in self.turnstiles if t is not None)
        print(f"• Torniquetes ocupados al final: {occupied_turnstiles}/3")


# Ejecutar simulación
if __name__ == "__main__":
    random.seed(42)  # Para reproducibilidad
    simulation = ArtGallerySimulation(6)  # 6 horas
    simulation.run_simulation()