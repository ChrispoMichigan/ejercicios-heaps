
import random
from dataclasses import dataclass

@dataclass
class Customer:
    priority: int
    arrival_time: int  # Tiempo de llegada
    entry_time : int | None # Tiempo de entrada
    exit_time: int | None # Tiempo de salida

'''
## Prioridad 1 para los pase general
## Prioridad 2 para los pase preferente 
## Prioridad 3 para los pase VIP
'''

class Queue:
    def __init__(self) -> None:
        self.cola : list[Customer] = []

    def put(self, customer: Customer):
        if self.full():
            return None
        self.cola.append(customer)

    def empty(self):
        return len(self.cola) == 0
    
    def get(self):
        if not self.empty():
            return self.cola.pop()
        return None
    
    def full(self):
        pass

    def size(self):
        return len(self.cola)
    
class EventQueue(Queue):
    def __init__(self) -> None:
        super().__init__()

    def full(self):
        return len(self.cola) >= 50
    
class Simulation:
    def __init__(self, total_time) -> None:
        self.total_time: int = total_time
        self.current_time : int = 0
        self.cola = Queue()
        self.event_cola = EventQueue()
        self.next_arrival_time: int
        self.init_simulation()

    def init_simulation(self):
        self.next_arrival_time = self.generate_interarrival_time()
        while self.current_time <= self.total_time:
            if self.current_time >= self.next_arrival_time:
                self.next_arrival_time = self.current_time + self.generate_interarrival_time()
                print(f'Generando nuevo cliente en el tiempo {self.current_time}')
            self.current_time += 1

    def generate_customer(self, arrival_time) -> Customer:
        #* Generar prioridad aleatoria
        priority = random.randint(1, 3)
        return Customer(priority, arrival_time, None, None)
    
    def time_to_enter(self):
        pass

    def new_in_queue(self):
        pass

    def generate_interarrival_time(self) -> int:
        """
        Genera tiempo entre llegadas usando distribución exponencial
        Tiempo medio = 2 minutos = 120 segundos
        Lambda (tasa) = 1/tiempo_medio = 1/120
        """
        mean_time = 120  # 2 minutos en segundos
        lambda_rate = 1 / mean_time
        
        return round(random.expovariate(lambda_rate))


init = Simulation(21600) # 21600 segundos siendo 6 horas