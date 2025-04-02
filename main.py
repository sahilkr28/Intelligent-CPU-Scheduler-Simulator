#pip install matplotlib numpy
# python main.py
import tkinter as tk
from tkinter import ttk, messagebox
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from scheduling_algorithms import Process, fcfs_scheduling, sjf_scheduling, round_robin_scheduling, priority_scheduling

class DarkCPUScheduler:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1400x900")
        
        # Dark theme colors
        self.colors = {
            'bg': '#1a1a1a',
            'card': '#2d2d2d',
            'text': '#ffffff',
            'accent1': '#61afef',
            'accent2': '#98c379',
            'accent3': '#e06c75',
            'grid': '#3d3d3d'
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.initialize_data()
        self.setup_styles()
        self.create_layout()

    def initialize_data(self):
        self.processes = []
        self.process_counter = 1
        self.algo_var = None
        self.quantum_frame = None
        self.quantum_entry = None

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Dark.TFrame', background=self.colors['bg'])
        style.configure('Dark.TLabel', 
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=('Arial', 10))
        style.configure('Header.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['accent1'],
                       font=('Arial', 14, 'bold'))

    def create_layout(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left panel for input and process queue
        self.left_panel = self.create_left_panel()
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right panel for results and visualizations
        self.right_panel = self.create_right_panel()
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def create_left_panel(self):
        panel = ttk.Frame(self.main_frame, style='Dark.TFrame')
        
        # Process Input Section
        input_frame = ttk.LabelFrame(panel, text="Add New Process", 
                                   style='Dark.TFrame', padding=10)
        input_frame.pack(fill=tk.X, pady=10)

        # Input fields
        fields = [("PID", self.process_counter), 
                 ("Arrival Time", 0),
                 ("Burst Time", 1),
                 ("Priority", 0)]

        self.entries = {}
        for i, (label, default) in enumerate(fields):
            container = ttk.Frame(input_frame, style='Dark.TFrame')
            container.pack(fill=tk.X, pady=5)
            
            ttk.Label(container, text=f"{label}:", 
                     style='Dark.TLabel').pack(side=tk.LEFT)
            
            entry = tk.Entry(container, bg=self.colors['card'],
                           fg=self.colors['text'],
                           insertbackground=self.colors['text'])
            entry.pack(side=tk.RIGHT, expand=True)
            entry.insert(0, str(default))
            self.entries[label] = entry

        # Add Process Button
        tk.Button(input_frame, text="Add Process",
                 bg=self.colors['accent2'],
                 fg=self.colors['text'],
                 command=self.add_process).pack(fill=tk.X, pady=10)

        # Process Queue
        self.create_process_queue(panel)
        
        return panel

    def create_process_queue(self, parent):
        queue_frame = ttk.LabelFrame(parent, text="Process Queue",
                                   style='Dark.TFrame', padding=10)
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create DataFrame display
        self.queue_text = tk.Text(queue_frame,
                                bg=self.colors['card'],
                                fg=self.colors['text'],
                                height=10)
        self.queue_text.pack(fill=tk.BOTH, expand=True)

        # Algorithm Selection
        algo_frame = ttk.Frame(queue_frame, style='Dark.TFrame')
        algo_frame.pack(fill=tk.X, pady=10)

        self.algo_var = tk.StringVar(value="FCFS")
        algorithms = ["FCFS", "SJF (Non-preemptive)", 
                     "SRTF (Preemptive)", "Round Robin", "Priority"]

        for algo in algorithms:
            tk.Radiobutton(algo_frame, text=algo,
                          variable=self.algo_var,
                          value=algo,
                          bg=self.colors['bg'],
                          fg=self.colors['text'],
                          selectcolor=self.colors['card'],
                          command=self.on_algorithm_change).pack(side=tk.LEFT)

        # Time Quantum input
        self.quantum_frame = ttk.Frame(queue_frame, style='Dark.TFrame')
        ttk.Label(self.quantum_frame, text="Time Quantum:",
                 style='Dark.TLabel').pack(side=tk.LEFT)
        self.quantum_entry = tk.Entry(self.quantum_frame,
                                    bg=self.colors['card'],
                                    fg=self.colors['text'])
        self.quantum_entry.pack(side=tk.RIGHT)
        self.quantum_entry.insert(0, "2")
        self.quantum_frame.pack_forget()  # Hide initially

        # Run Button
        tk.Button(queue_frame, text="Run Simulation",
                 bg=self.colors['accent1'],
                 fg=self.colors['text'],
                 command=self.run_simulation).pack(fill=tk.X, pady=10)

    def create_right_panel(self):
        panel = ttk.Frame(self.main_frame, style='Dark.TFrame')
        
        # Results header
        ttk.Label(panel, text="Simulation Results", 
                 style='Header.TLabel').pack(pady=10)

        # Create frames for visualizations
        self.gantt_frame = ttk.LabelFrame(panel, text="Gantt Chart",
                                        style='Dark.TFrame', padding=10)
        self.gantt_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.metrics_frame = ttk.LabelFrame(panel, text="Performance Metrics",
                                          style='Dark.TFrame', padding=10)
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        return panel

    def on_algorithm_change(self):
        """Handle algorithm selection changes"""
        selected_algo = self.algo_var.get()
        if selected_algo == "Round Robin":
            self.quantum_frame.pack(fill=tk.X, pady=5)
        else:
            self.quantum_frame.pack_forget()

    def add_process(self):
        """Add a new process to the queue"""
        try:
            process = Process(
                pid=int(self.entries["PID"].get()),
                arrival=int(self.entries["Arrival Time"].get()),
                burst=int(self.entries["Burst Time"].get()),
                priority=int(self.entries["Priority"].get())
            )
            self.processes.append(process)
            self.process_counter += 1
            self.entries["PID"].delete(0, tk.END)
            self.entries["PID"].insert(0, str(self.process_counter))
            self.update_queue_display()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    def update_queue_display(self):
        """Update the process queue display"""
        self.queue_text.delete(1.0, tk.END)
        for p in self.processes:
            self.queue_text.insert(tk.END, 
                f"P{p.pid}: Arrival={p.arrival}, Burst={p.burst}, Priority={p.priority}\n")

    def run_simulation(self):
        """Run the selected scheduling algorithm"""
        if not self.processes:
            messagebox.showerror("Error", "Please add some processes first!")
            return

        algorithm = self.algo_var.get()
        try:
            processes_copy = [Process(p.pid, p.arrival, p.burst, p.priority) for p in self.processes]
            
            if algorithm == "FCFS":
                processes, gantt_data, switches = fcfs_scheduling(processes_copy)
            elif algorithm == "SJF (Non-preemptive)":
                processes, gantt_data, switches = sjf_scheduling(processes_copy, preemptive=False)
            elif algorithm == "SRTF (Preemptive)":
                processes, gantt_data, switches = sjf_scheduling(processes_copy, preemptive=True)
            elif algorithm == "Round Robin":
                try:
                    quantum = int(self.quantum_entry.get())
                    if quantum <= 0:
                        raise ValueError("Time quantum must be positive")
                    processes, gantt_data, switches = round_robin_scheduling(processes_copy, quantum)
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    return
            else:  # Priority
                processes, gantt_data, switches = priority_scheduling(processes_copy)

            self.show_results(processes, gantt_data, switches)
        except ValueError as e:
            messagebox.showerror("Error", f"Simulation error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def show_results(self, processes, gantt_data, switches):
        """Display simulation results"""
        # Clear previous results
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()

        # Calculate metrics
        avg_turnaround = sum(p.turnaround_time for p in processes) / len(processes)
        avg_waiting = sum(p.waiting_time for p in processes) / len(processes)
        avg_response = sum(p.response_time for p in processes) / len(processes)

        # Create metrics display
        metrics_text = (
            f"Average Turnaround Time: {avg_turnaround:.2f}\n"
            f"Average Waiting Time: {avg_waiting:.2f}\n"
            f"Average Response Time: {avg_response:.2f}\n"
            f"Context Switches: {switches}"
        )
        
        metrics_label = ttk.Label(self.metrics_frame, 
                                text=metrics_text,
                                style='Dark.TLabel')
        metrics_label.pack(pady=10)

        # Create results table
        results_frame = ttk.Frame(self.metrics_frame, style='Dark.TFrame')
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Headers
        headers = ["PID", "Arrival", "Burst", "Completion", "Turnaround", "Waiting", "Response"]
        for col, header in enumerate(headers):
            ttk.Label(results_frame, text=header,
                     style='Dark.TLabel').grid(row=0, column=col, padx=5, pady=5)

        # Process data
        for row, p in enumerate(processes, start=1):
            data = [p.pid, p.arrival, p.burst, p.completion_time,
                    p.turnaround_time, p.waiting_time, p.response_time]
            for col, value in enumerate(data):
                ttk.Label(results_frame, text=str(value),
                         style='Dark.TLabel').grid(row=row, column=col, padx=5, pady=2)

        # Create Gantt chart
        self.create_gantt_chart(gantt_data)

    def create_gantt_chart(self, gantt_data):
        """Create a simple Gantt chart using tkinter canvas"""
        canvas_height = 100
        canvas_width = 600
        time_scale = canvas_width / (max(end for _, _, end in gantt_data) + 1)
        
        canvas = tk.Canvas(self.gantt_frame, 
                          height=canvas_height,
                          width=canvas_width,
                          bg=self.colors['card'])
        canvas.pack(pady=10)

        # Draw time axis
        canvas.create_line(0, canvas_height-20, canvas_width, canvas_height-20,
                          fill=self.colors['text'])

        # Draw process blocks
        y_top = 20
        y_bottom = canvas_height - 40
        for pid, start, end in gantt_data:
            x1 = start * time_scale
            x2 = end * time_scale
            
            # Process block
            canvas.create_rectangle(x1, y_top, x2, y_bottom,
                                  fill=self.colors['accent1'])
            
            # Process label
            canvas.create_text((x1 + x2) / 2, (y_top + y_bottom) / 2,
                              text=f"P{pid}",
                              fill=self.colors['text'])
            
            # Time labels
            canvas.create_text(x1, canvas_height-10,
                              text=str(start),
                              fill=self.colors['text'])
            canvas.create_text(x2, canvas_height-10,
                              text=str(end),
                              fill=self.colors['text'])

if __name__ == "__main__":
    root = tk.Tk()
    app = DarkCPUScheduler(root)
    root.mainloop()  