import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Process:
    pid: int
    arrival: int
    burst: int
    priority: int = 0
    remaining_burst: Optional[int] = None
    completion_time: int = 0
    turnaround_time: int = 0
    waiting_time: int = 0
    response_time: int = -1

    def __post_init__(self):
        self.remaining_burst = self.burst

    def __repr__(self):
        return f"P{self.pid}(A:{self.arrival}, B:{self.burst}, P:{self.priority})"

def calculate_metrics(processes: List[Process]):
    avg_turnaround = np.mean([p.turnaround_time for p in processes])
    avg_waiting = np.mean([p.waiting_time for p in processes])
    avg_response = np.mean([p.response_time for p in processes])
    return avg_turnaround, avg_waiting, avg_response

def fcfs_scheduling(processes):
    """First Come First Serve scheduling algorithm"""
    processes = sorted(processes, key=lambda x: x.arrival)
    current_time = 0
    gantt_chart = []
    scheduled_processes = []

    for process in processes:
        p = Process(process.pid, process.arrival, process.burst, process.priority)
        if current_time < p.arrival:
            current_time = p.arrival
        p.waiting_time = current_time - p.arrival
        p.completion_time = current_time + p.burst
        p.turnaround_time = p.completion_time - p.arrival
        gantt_chart.append((p.pid, current_time, p.completion_time))
        current_time = p.completion_time
        scheduled_processes.append(p)

    return scheduled_processes, gantt_chart

def sjf_scheduling(processes):
    """Shortest Job First scheduling algorithm"""
    current_time = 0
    remaining_processes = sorted(processes, key=lambda x: x.arrival)
    gantt_chart = []
    scheduled_processes = []

    while remaining_processes:
        available = [p for p in remaining_processes if p.arrival <= current_time]
        if not available:
            current_time = min(p.arrival for p in remaining_processes)
            continue

        selected = min(available, key=lambda x: x.burst)
        remaining_processes.remove(selected)

        p = Process(selected.pid, selected.arrival, selected.burst, selected.priority)
        p.waiting_time = current_time - p.arrival
        p.completion_time = current_time + p.burst
        p.turnaround_time = p.completion_time - p.arrival
        gantt_chart.append((p.pid, current_time, p.completion_time))
        current_time = p.completion_time
        scheduled_processes.append(p)

    return scheduled_processes, gantt_chart

def round_robin_scheduling(processes, time_quantum):
    """Round Robin scheduling algorithm"""
    if not processes:
        return [], []
    
    current_time = 0
    remaining_processes = sorted(processes, key=lambda x: x.arrival)
    gantt_chart = []
    scheduled_processes = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    ready_queue = []
    remaining_bursts = {p.pid: p.burst for p in processes}

    while remaining_processes or ready_queue:
        while remaining_processes and remaining_processes[0].arrival <= current_time:
            ready_queue.append(remaining_processes.pop(0))

        if not ready_queue:
            if remaining_processes:
                current_time = remaining_processes[0].arrival
                continue
            break

        current_process = ready_queue.pop(0)
        execution_time = min(time_quantum, remaining_bursts[current_process.pid])
        gantt_chart.append((current_process.pid, current_time, current_time + execution_time))
        remaining_bursts[current_process.pid] -= execution_time
        current_time += execution_time

        if remaining_bursts[current_process.pid] > 0:
            while remaining_processes and remaining_processes[0].arrival <= current_time:
                ready_queue.append(remaining_processes.pop(0))
            ready_queue.append(current_process)
        else:
            for p in scheduled_processes:
                if p.pid == current_process.pid:
                    p.completion_time = current_time
                    p.turnaround_time = p.completion_time - p.arrival
                    p.waiting_time = p.turnaround_time - p.burst
                    break

    return scheduled_processes, gantt_chart

def priority_scheduling(processes):
    """Priority scheduling algorithm (lower number = higher priority)"""
    current_time = 0
    remaining_processes = sorted(processes, key=lambda x: x.arrival)
    gantt_chart = []
    scheduled_processes = []

    while remaining_processes:
        available = [p for p in remaining_processes if p.arrival <= current_time]
        if not available:
            current_time = min(p.arrival for p in remaining_processes)
            continue

        selected = min(available, key=lambda x: (x.priority, x.arrival))
        remaining_processes.remove(selected)

        p = Process(selected.pid, selected.arrival, selected.burst, selected.priority)
        p.waiting_time = current_time - p.arrival
        p.completion_time = current_time + p.burst
        p.turnaround_time = p.completion_time - p.arrival
        gantt_chart.append((p.pid, current_time, p.completion_time))
        current_time = p.completion_time
        scheduled_processes.append(p)

    return scheduled_processes, gantt_chart