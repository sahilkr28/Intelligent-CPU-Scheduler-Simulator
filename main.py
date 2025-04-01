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

        # Run Button
        tk.Button(queue_frame, text="Run Simulation",
                 bg=self.colors['accent1'],
                 fg=self.colors['text'],
                 command=self.run_simulation).pack(fill=tk.X, pady=10)

    def create_right_panel(self):
        panel = ttk.Frame(self.main_frame, style='Dark.TFrame')

        # Results Section
        self.create_results_section(panel)
        
        # Visualization Section
        self.create_visualization_section(panel)

        return panel

    def create_results_section(self):
        # Implementation of results display using Plotly
        pass

    def show_gantt_chart(self, gantt_data):
        fig = go.Figure()

        for p_id, start, end in gantt_data:
            fig.add_trace(go.Bar(
                x=[end - start],
                y=[f"P{p_id}"],
                orientation='h',
                base=[start],
                marker_color=px.colors.qualitative.Set3[p_id % len(px.colors.qualitative.Set3)],
                name=f"P{p_id}",
                text=f"P{p_id} ({start}-{end})",
                textposition="inside",
                hoverinfo="text",
                showlegend=False
            ))

        fig.update_layout(
            plot_bgcolor=self.colors['bg'],
            paper_bgcolor=self.colors['bg'],
            font_color=self.colors['text'],
            barmode='overlay',
            xaxis=dict(
                title="Time",
                showgrid=True,
                gridwidth=1,
                gridcolor=self.colors['grid'],
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor=self.colors['accent1']
            ),
            yaxis=dict(
                title="Process",
                showgrid=True,
                gridwidth=1,
                gridcolor=self.colors['grid']
            ),
            margin=dict(l=50, r=50, t=30, b=30)
        )

        # Convert to widget and display
        # Note: You'll need to implement a method to display Plotly figures in tkinter

    def show_metrics(self, processes):
        # Create metrics visualization using Plotly
        metrics_fig = go.Figure()

        # Add Response Time bars
        metrics_fig.add_trace(go.Bar(
            name='Response Time',
            x=[f'P{p.pid}' for p in processes],
            y=[p.response_time for p in processes],
            marker_color='#99FF99',
            width=0.2
        ))

        # Add Turnaround Time bars
        metrics_fig.add_trace(go.Bar(
            name='Turnaround Time',
            x=[f'P{p.pid}' for p in processes],
            y=[p.turnaround_time for p in processes],
            marker_color='#FFB366',
            width=0.2
        ))

        metrics_fig.update_layout(
            plot_bgcolor=self.colors['bg'],
            paper_bgcolor=self.colors['bg'],
            font_color=self.colors['text'],
            barmode='group',
            bargap=0.3,
            bargroupgap=0.1,
            xaxis_title="Process ID",
            yaxis_title="Time",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Convert to widget and display

    def add_process(self):
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
            self.update_ready_queue(process)
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers")

    def update_ready_queue(self, process):
        self.queue_text.delete(1.0, tk.END)
        if process:
            self.queue_text.insert(tk.END, f"PID: {process.pid}\nArrival Time: {process.arrival}\nBurst Time: {process.burst}\nPriority: {process.priority}")

    def run_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "Please add some processes first!")
            return

        algorithm = self.algo_var.get()
        try:
            if algorithm == "FCFS":
                result = fcfs_scheduling(self.processes)
            elif algorithm == "SJF":
                result = sjf_scheduling(self.processes)
            elif algorithm == "Round Robin":
                quantum = int(self.quantum_entry.get())
                result = round_robin_scheduling(self.processes, quantum)
            else:  # Priority
                result = priority_scheduling(self.processes)

            processes, gantt_data, context_switches = result
            
            self.update_results(processes, context_switches)
            self.show_gantt_chart(gantt_data)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_results(self, processes, context_switches):
        # Clear previous results
        self.results_tree.delete(*self.results_tree.get_children())

        # Update results table
        for process in processes:
            self.results_tree.insert("", "end", values=(
                process.pid,
                process.completion_time,
                process.turnaround_time,
                process.waiting_time,
                process.response_time
            ))

        # Calculate and update metrics
        avg_turnaround, avg_waiting, avg_response = calculate_metrics(processes)
        
        self.metrics_labels["Average Waiting Time"].configure(
            text=f"{avg_waiting:.2f}")
        self.metrics_labels["Average Turnaround Time"].configure(
            text=f"{avg_turnaround:.2f}")
        self.metrics_labels["Average Response Time"].configure(
            text=f"{avg_response:.2f}")
        self.metrics_labels["Context Switches"].configure(
            text=str(context_switches))

if __name__ == "__main__":
    root = tk.Tk()
    app = DarkCPUScheduler(root)
    root.mainloop()  