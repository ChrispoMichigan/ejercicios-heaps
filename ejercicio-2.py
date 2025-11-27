import random
import heapq
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

@dataclass
class Student:
    id: int
    arrival_time: int  # Tiempo de llegada en minutos desde las 10:00
    computer_id: Optional[int] = None
    usage_duration: Optional[int] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    
    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

@dataclass
class Event:
    time: int  # Tiempo en minutos desde las 10:00
    event_type: str  # 'arrival' o 'computer_free'
    student_id: Optional[int] = None
    computer_id: Optional[int] = None
    
    def __lt__(self, other):
        return self.time < other.time

class ComputerLabSimulation:
    def __init__(self):
        # Configuración del sistema
        self.total_computers = 15
        self.start_hour = 10  # 10:00 AM
        self.end_hour = 20    # 8:00 PM
        self.total_simulation_time = (self.end_hour - self.start_hour) * 60  # 10 horas en minutos
        
        # Tiempos de llegada
        self.arrival_time_first_2h = 18  # 18 minutos las primeras 2 horas
        self.arrival_time_rest = 15      # 15 minutos el resto del día
        self.first_period_duration = 120  # 2 horas en minutos
        
        # Tiempo de uso del computador
        self.min_usage_time = 30
        self.max_usage_time = 55
        
        # Estado del sistema
        self.current_time = 0
        self.computers: List[Optional[int]] = [None] * self.total_computers  # None = libre, student_id = ocupado
        self.event_queue = []
        self.students = {}
        self.next_student_id = 1
        
        # Estadísticas
        self.total_arrivals = 0
        self.total_served = 0
        self.total_rejected = 0
        
    def time_to_string(self, minutes_since_start: int) -> str:
        """Convierte minutos desde las 10:00 a formato HH:MM"""
        total_minutes = (self.start_hour * 60) + minutes_since_start
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    
    def get_arrival_interval(self, current_time: int) -> int:
        """Determina el intervalo de llegada según la hora del día"""
        if current_time < self.first_period_duration:
            return self.arrival_time_first_2h
        else:
            return self.arrival_time_rest
    
    def generate_usage_time(self) -> int:
        """Genera tiempo de uso aleatorio entre 30 y 55 minutos"""
        return random.randint(self.min_usage_time, self.max_usage_time)
    
    def find_free_computer(self) -> Optional[int]:
        """Busca un computador libre y devuelve su ID, None si no hay"""
        for i, computer in enumerate(self.computers):
            if computer is None:
                return i
        return None
    
    def schedule_event(self, time: int, event_type: str, student_id: Optional[int] = None, computer_id: Optional[int] = None):
        """Programa un evento en la cola de eventos"""
        if time <= self.total_simulation_time:
            event = Event(time, event_type, student_id, computer_id)
            heapq.heappush(self.event_queue, event)
    
    def process_student_arrival(self, student_id: int):
        """Procesa la llegada de un estudiante"""
        self.total_arrivals += 1
        student = self.students[student_id]
        
        print(f"[{self.time_to_string(self.current_time)}] Llega el estudiante {student_id}")
        
        # Buscar computador libre
        computer_id = self.find_free_computer()
        
        if computer_id is not None:
            # Asignar computador al estudiante
            self.computers[computer_id] = student_id
            student.computer_id = computer_id
            student.start_time = self.current_time
            student.usage_duration = self.generate_usage_time()
            student.end_time = self.current_time + student.usage_duration
            
            self.total_served += 1
            
            print(f"Asignado al computador {computer_id + 1}")
            print(f"Tiempo de conexión: {student.usage_duration} minutos")
            print(f"Terminará a las {self.time_to_string(student.end_time)}")
            
            # Programar liberación del computador
            self.schedule_event(student.end_time, 'computer_free', student_id, computer_id)
            
        else:
            # No hay computadores libres
            self.total_rejected += 1
            print(f"NO HAY COMPUTADORES LIBRES - El estudiante se va")
    
    def process_computer_free(self, student_id: int, computer_id: int):
        """Procesa cuando un computador se libera"""
        student = self.students[student_id]
        self.computers[computer_id] = None
        
        print(f"[{self.time_to_string(self.current_time)}] El estudiante {student_id} termina y libera el computador {computer_id + 1}")
        print(f"Tiempo total de uso: {student.usage_duration} minutos")
    
    def schedule_next_arrival(self):
        """Programa la próxima llegada de estudiante"""
        interval = self.get_arrival_interval(self.current_time)
        next_arrival_time = self.current_time + interval
        
        if next_arrival_time < self.total_simulation_time:
            student = Student(self.next_student_id, next_arrival_time)
            self.students[self.next_student_id] = student
            self.schedule_event(next_arrival_time, 'arrival', self.next_student_id)
            self.next_student_id += 1
    
    def run_simulation(self):
        """Ejecuta la simulación completa"""
        print("=" * 80)
        print("SIMULACIÓN DEL LABORATORIO DE COMPUTADORES - UNIVERSIDAD DE LA ALCARRIA")
        print("=" * 80)
        print(f"Horario: {self.start_hour}:00 - {self.end_hour}:00")
        print(f"Computadores disponibles: {self.total_computers}")
        print(f"Frecuencia de llegada:")
        print(f"Primeras 2 horas: cada {self.arrival_time_first_2h} minutos")
        print(f"Resto del día: cada {self.arrival_time_rest} minutos")
        print(f"Tiempo de uso: {self.min_usage_time}-{self.max_usage_time} minutos")
        print("=" * 80)
        print()
        
        # Programar primera llegada
        first_arrival_interval = self.get_arrival_interval(0)
        first_student = Student(self.next_student_id, first_arrival_interval)
        self.students[self.next_student_id] = first_student
        self.schedule_event(first_arrival_interval, 'arrival', self.next_student_id)
        self.next_student_id += 1
        
        # Procesar eventos
        while self.event_queue and self.current_time < self.total_simulation_time:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            if self.current_time >= self.total_simulation_time:
                break
            
            if event.event_type == 'arrival':
                self.process_student_arrival(event.student_id)
                self.schedule_next_arrival()
                
            elif event.event_type == 'computer_free':
                self.process_computer_free(event.student_id, event.computer_id)
        
        self.print_final_statistics()
    
    def print_final_statistics(self):
        """Imprime estadísticas finales de la simulación"""
        
        print(f"\nResumen general:")
        print(f"Total de estudiantes que llegaron: {self.total_arrivals}")
        print(f"Estudiantes atendidos: {self.total_served}")
        print(f"Estudiantes rechazados (sin computador): {self.total_rejected}")
        
        if self.total_arrivals > 0:
            success_rate = (self.total_served / self.total_arrivals) * 100
            rejection_rate = (self.total_rejected / self.total_arrivals) * 100
            print(f"Tasa de éxito: {success_rate:.1f}%")
            print(f"Tasa de rechazo: {rejection_rate:.1f}%")
        
        print(f"\nEstado final de computadores:")
        occupied_computers = sum(1 for computer in self.computers if computer is not None)
        print(f"Computadores ocupados al final: {occupied_computers}/{self.total_computers}")
        print(f"Computadores libres al final: {self.total_computers - occupied_computers}/{self.total_computers}")
        
        # Mostrar qué computadores están ocupados al final
        if occupied_computers > 0:
            print(f"Computadores aún en uso:")
            for i, student_id in enumerate(self.computers):
                if student_id is not None:
                    student = self.students[student_id]
                    remaining_time = student.end_time - self.current_time
                    print(f"Computador {i+1}: Estudiante {student_id} (quedan {remaining_time} min)")
        
        print("\n" + "=" * 80)


# Ejecutar simulación
if __name__ == "__main__":
    random.seed(42)  # Para reproducibilidad de resultados
    simulation = ComputerLabSimulation()
    simulation.run_simulation()
