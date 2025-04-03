import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

class Process:
    def __init__(self, pid: int, arrival: int, burst: int, priority: int = 0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining_burst = burst
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = -1
        self.start_time = -1

def calculate_metrics(processes: List[Process]) -> Tuple[float, float, float]:
    total_turnaround = 0
    total_waiting = 0
    total_response = 0
    
    for p in processes:
        p.turnaround_time = p.completion_time - p.arrival
        p.waiting_time = p.turnaround_time - p.burst
        total_turnaround += p.turnaround_time
        total_waiting += p.waiting_time
        total_response += p.response_time
    
    n = len(processes)
    return total_turnaround/n, total_waiting/n, total_response/n

def fcfs_scheduling(processes: List[Process]) -> Tuple[List[Process], List[Tuple[int, int, int]], int]:
    processes = sorted(processes, key=lambda x: x.arrival)
    current_time = 0
    gantt_data = []
    switches = 0
    
    for p in processes:
        if current_time < p.arrival:
            current_time = p.arrival
        p.start_time = current_time
        p.response_time = current_time - p.arrival
        p.completion_time = current_time + p.burst
        gantt_data.append((p.pid, current_time, p.completion_time))
        current_time = p.completion_time
    
    return processes, gantt_data, switches

def sjf_scheduling(processes: List[Process], preemptive: bool = False) -> Tuple[List[Process], List[Tuple[int, int, int]], int]:
    processes = sorted(processes, key=lambda x: x.arrival)
    current_time = 0
    gantt_data = []
    switches = 0
    ready_queue = []
    current_process = None
    
    while True:
        # Add arrived processes to ready queue
        for p in processes:
            if p.arrival <= current_time and p.remaining_burst > 0:
                if p not in ready_queue and p != current_process:
                    ready_queue.append(p)
        
        # If no process is running and ready queue is not empty
        if not current_process and ready_queue:
            # Select process with shortest remaining burst
            current_process = min(ready_queue, key=lambda x: x.remaining_burst)
            ready_queue.remove(current_process)
            if current_process.start_time == -1:
                current_process.start_time = current_time
                current_process.response_time = current_time - current_process.arrival
            switches += 1
        
        # If preemptive and a shorter process arrives
        if preemptive and current_process and ready_queue:
            shortest = min(ready_queue, key=lambda x: x.remaining_burst)
            if shortest.remaining_burst < current_process.remaining_burst:
                gantt_data.append((current_process.pid, current_process.start_time, current_time))
                ready_queue.append(current_process)
                current_process = shortest
                ready_queue.remove(shortest)
                current_process.start_time = current_time
                switches += 1
        
        # If no process is running and no process will arrive
        if not current_process and not ready_queue and current_time >= max(p.arrival for p in processes):
            break
        
        # Execute current process
        if current_process:
            current_process.remaining_burst -= 1
            if current_process.remaining_burst == 0:
                current_process.completion_time = current_time + 1
                gantt_data.append((current_process.pid, current_process.start_time, current_process.completion_time))
                current_process = None
        
        current_time += 1
    
    return processes, gantt_data, switches

def round_robin_scheduling(processes: List[Process], time_quantum: int) -> Tuple[List[Process], List[Tuple[int, int, int]], int]:
    processes = sorted(processes, key=lambda x: x.arrival)
    current_time = 0
    gantt_data = []
    switches = 0
    ready_queue = []
    current_process = None
    time_slice = 0
    
    while True:
        # Add arrived processes to ready queue
        for p in processes:
            if p.arrival <= current_time and p.remaining_burst > 0:
                if p not in ready_queue and p != current_process:
                    ready_queue.append(p)
        
        # If no process is running and ready queue is not empty
        if not current_process and ready_queue:
            current_process = ready_queue.pop(0)
            if current_process.start_time == -1:
                current_process.start_time = current_time
                current_process.response_time = current_time - current_process.arrival
            time_slice = time_quantum
            switches += 1
        
        # If time quantum expires
        if current_process and time_slice == 0:
            if current_process.remaining_burst > 0:
                ready_queue.append(current_process)
            else:
                current_process.completion_time = current_time
                gantt_data.append((current_process.pid, current_process.start_time, current_process.completion_time))
            current_process = None
        
        # If no process is running and no process will arrive
        if not current_process and not ready_queue and current_time >= max(p.arrival for p in processes):
            break
        
        # Execute current process
        if current_process:
            current_process.remaining_burst -= 1
            time_slice -= 1
            if current_process.remaining_burst == 0:
                current_process.completion_time = current_time + 1
                gantt_data.append((current_process.pid, current_process.start_time, current_process.completion_time))
                current_process = None
        
        current_time += 1
    
    return processes, gantt_data, switches

def priority_scheduling(processes: List[Process], ascending: bool = True) -> Tuple[List[Process], List[Tuple[int, int, int]], int]:
    processes = sorted(processes, key=lambda x: x.arrival)
    current_time = 0
    gantt_data = []
    switches = 0
    ready_queue = []
    current_process = None
    
    while True:
        # Add arrived processes to ready queue
        for p in processes:
            if p.arrival <= current_time and p.remaining_burst > 0:
                if p not in ready_queue and p != current_process:
                    ready_queue.append(p)
        
        # If no process is running and ready queue is not empty
        if not current_process and ready_queue:
            # Select process with highest/lowest priority
            current_process = min(ready_queue, key=lambda x: x.priority if ascending else -x.priority)
            ready_queue.remove(current_process)
            if current_process.start_time == -1:
                current_process.start_time = current_time
                current_process.response_time = current_time - current_process.arrival
            switches += 1
        
        # If a higher priority process arrives
        if current_process and ready_queue:
            highest_priority = min(ready_queue, key=lambda x: x.priority if ascending else -x.priority)
            if (ascending and highest_priority.priority < current_process.priority) or \
               (not ascending and highest_priority.priority > current_process.priority):
                gantt_data.append((current_process.pid, current_process.start_time, current_time))
                ready_queue.append(current_process)
                current_process = highest_priority
                ready_queue.remove(highest_priority)
                current_process.start_time = current_time
                switches += 1
        
        # If no process is running and no process will arrive
        if not current_process and not ready_queue and current_time >= max(p.arrival for p in processes):
            break
        
        # Execute current process
        if current_process:
            current_process.remaining_burst -= 1
            if current_process.remaining_burst == 0:
                current_process.completion_time = current_time + 1
                gantt_data.append((current_process.pid, current_process.start_time, current_process.completion_time))
                current_process = None
        
        current_time += 1
    
    return processes, gantt_data, switches