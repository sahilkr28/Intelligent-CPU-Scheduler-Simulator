import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scheduling_algorithms import Process, fcfs_scheduling, sjf_scheduling, round_robin_scheduling, priority_scheduling

class ModernCPUScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic CPU Scheduler")
        self.root.geometry("1200x800")
        
        # Modern color scheme
        self.colors = {
            'bg': '#1e1e1e',
            'accent1': '#61afef',
            'accent2': '#98c379',
            'accent3': '#e06c75',
            'text': '#abb2bf',
            'header': '#c678dd'
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.setup_styles()
        self.create_layout()
        self.initialize_data()

    def setup_styles(self):
        # Configure modern styles
        style = ttk.Style()
        style.configure('Modern.TFrame', background=self.colors['bg'])
        style.configure('Modern.TLabel', 
                       background=self.colors['bg'], 
                       foreground=self.colors['text'])
        style.configure('Header.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['header'],
                       font=('Arial', 14, 'bold'))

    def create_layout(self):
        # Main container with three columns
        self.main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left column - Process Input
        self.input_frame = self.create_input_section()
        self.input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Middle column - Process Queue and Controls
        self.queue_frame = self.create_queue_section()
        self.queue_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Right column - Visualization
        self.viz_frame = self.create_visualization_section()
        self.viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

    def create_input_section(self):
        frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        
        # Header
        ttk.Label(frame, text="Process Creation", 
                 style='Header.TLabel').pack(pady=10)

        # Input fields with modern styling
        input_fields = [
            ("Process ID", self.generate_pid),
            ("Arrival Time", lambda: 0),
            ("Burst Time", lambda: 1),
            ("Priority", lambda: 0)
        ]

        self.entries = {}
        for label, default_value in input_fields:
            container = ttk.Frame(frame, style='Modern.TFrame')
            container.pack(fill=tk.X, pady=5)
            
            ttk.Label(container, text=label, 
                     style='Modern.TLabel').pack(side=tk.LEFT)
            
            entry = tk.Entry(container, bg=self.colors['bg'], 
                           fg=self.colors['text'],
                           insertbackground=self.colors['text'])
            entry.pack(side=tk.RIGHT, expand=True)
            entry.insert(0, str(default_value()))
            self.entries[label] = entry

        # Modern buttons
        btn_frame = ttk.Frame(frame, style='Modern.TFrame')
        btn_frame.pack(fill=tk.X, pady=20)

        self.create_modern_button(btn_frame, "Add Process", 
                                self.add_process, self.colors['accent2'])
        self.create_modern_button(btn_frame, "Clear All", 
                                self.clear_processes, self.colors['accent3'])

        return frame

    def create_queue_section(self):
        frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        
        ttk.Label(frame, text="Process Queue", 
                 style='Header.TLabel').pack(pady=10)

        # Process list with custom styling
        self.queue_display = tk.Text(frame, height=10,
                                   bg=self.colors['bg'],
                                   fg=self.colors['text'],
                                   relief=tk.FLAT)
        self.queue_display.pack(fill=tk.BOTH, expand=True, pady=10)

        # Algorithm selection
        algo_frame = ttk.Frame(frame, style='Modern.TFrame')
        algo_frame.pack(fill=tk.X, pady=10)

        ttk.Label(algo_frame, text="Algorithm:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)

        # Initialize algo_var if it hasn't been initialized yet
        if self.algo_var is None:
            self.algo_var = tk.StringVar(value="FCFS")
        
        algorithms = ["FCFS", "SJF", "Round Robin", "Priority"]
        
        for algo in algorithms:
            self.create_radio_button(algo_frame, algo)

        # Time quantum input for Round Robin
        self.quantum_frame = ttk.Frame(frame, style='Modern.TFrame')
        ttk.Label(self.quantum_frame, text="Time Quantum:", 
                 style='Modern.TLabel').pack(side=tk.LEFT)
        self.quantum_entry = tk.Entry(self.quantum_frame, 
                                    bg=self.colors['bg'],
                                    fg=self.colors['text'])
        self.quantum_entry.pack(side=tk.RIGHT)
        self.quantum_entry.insert(0, "2")

        # Run button
        self.create_modern_button(frame, "Run Simulation", 
                                self.run_simulation, self.colors['accent1'])

        return frame

    def create_visualization_section(self):
        frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        
        ttk.Label(frame, text="Visualization", 
                 style='Header.TLabel').pack(pady=10)

        # Gantt chart
        self.gantt_frame = ttk.Frame(frame, style='Modern.TFrame')
        self.gantt_frame.pack(fill=tk.BOTH, expand=True)

        # Statistics
        self.stats_frame = ttk.Frame(frame, style='Modern.TFrame')
        self.stats_frame.pack(fill=tk.BOTH, expand=True)

        return frame

    def create_modern_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command,
                       bg=color, fg='white',
                       relief=tk.FLAT,
                       font=('Arial', 10),
                       padx=15, pady=5)
        btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        return btn

    def create_radio_button(self, parent, text):
        rb = tk.Radiobutton(parent, text=text, 
                           variable=self.algo_var,
                           value=text,
                           bg=self.colors['bg'],
                           fg=self.colors['text'],
                           selectcolor=self.colors['accent1'],
                           command=self.on_algorithm_change)
        rb.pack(side=tk.LEFT, padx=5)
        return rb

    def initialize_data(self):
        self.processes = []
        self.process_counter = 1
        self.algo_var = None  # Initialize this here too

    def generate_pid(self):
        return self.process_counter

    def add_process(self):
        try:
            process = Process(
                pid=int(self.entries["Process ID"].get()),
                arrival=int(self.entries["Arrival Time"].get()),
                burst=int(self.entries["Burst Time"].get()),
                priority=int(self.entries["Priority"].get())
            )
            self.processes.append(process)
            self.process_counter += 1
            self.entries["Process ID"].delete(0, tk.END)
            self.entries["Process ID"].insert(0, str(self.process_counter))
            self.update_queue_display()
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers")

    def clear_processes(self):
        self.processes = []
        self.process_counter = 1
        self.entries["Process ID"].delete(0, tk.END)
        self.entries["Process ID"].insert(0, "1")
        self.update_queue_display()

    def update_queue_display(self):
        self.queue_display.delete(1.0, tk.END)
        for p in self.processes:
            self.queue_display.insert(tk.END, 
                f"P{p.pid}: Arrival={p.arrival}, Burst={p.burst}, Priority={p.priority}\n")

    def on_algorithm_change(self):
        if self.algo_var.get() == "Round Robin":
            self.quantum_frame.pack(fill=tk.X, pady=10)
        else:
            self.quantum_frame.pack_forget()

    def run_simulation(self):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to simulate!")
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

            self.show_results(result)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_results(self, result):
        # Clear previous visualizations
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        processes, gantt_data = result
        self.plot_gantt_chart(gantt_data)
        self.show_statistics(processes)

    def plot_gantt_chart(self, gantt_data):
        fig = Figure(figsize=(8, 3), facecolor=self.colors['bg'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['bg'])

        for pid, start, end in gantt_data:
            ax.barh(y=0, width=end-start, left=start, 
                   color=self.colors['accent1'], alpha=0.7)
            ax.text((start + end)/2, 0, f'P{pid}',
                   ha='center', va='center', color='white')

        ax.set_yticks([])
        ax.set_xlabel('Time', color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])

        canvas = FigureCanvasTkAgg(fig, self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_statistics(self, processes):
        stats = self.calculate_statistics(processes)
        
        fig = Figure(figsize=(8, 3), facecolor=self.colors['bg'])
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors['bg'])

        metrics = list(stats.items())
        x = range(len(metrics))
        ax.bar(x, [v for k, v in metrics], 
               color=[self.colors['accent1'], self.colors['accent2'], 
                     self.colors['accent3']])

        ax.set_xticks(x)
        ax.set_xticklabels([k for k, v in metrics], rotation=45)
        ax.tick_params(colors=self.colors['text'])

        canvas = FigureCanvasTkAgg(fig, self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def calculate_statistics(self, processes):
        return {
            'Avg Waiting Time': sum(p.waiting_time for p in processes) / len(processes),
            'Avg Turnaround Time': sum(p.turnaround_time for p in processes) / len(processes),
            'Avg Response Time': sum(p.response_time for p in processes) / len(processes)
        }

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernCPUScheduler(root)
    root.mainloop()  