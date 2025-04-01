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
        self.root.geometry("1400x900")
        
        # Initialize data first
        self.initialize_data()
        
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
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left panel - Process Input and Ready Queue
        self.left_panel = ttk.Frame(self.main_frame, style='Modern.TFrame')
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Create input section
        self.create_input_section()
        
        # Create ready queue table
        self.create_ready_queue_table()
        
        # Right panel - Results and Visualization
        self.right_panel = ttk.Frame(self.main_frame, style='Modern.TFrame')
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Create results section
        self.create_results_section()

    def create_input_section(self):
        frame = ttk.Frame(self.left_panel, style='Modern.TFrame')
        
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

    def create_ready_queue_table(self):
        # Ready Queue Table
        queue_frame = ttk.LabelFrame(self.left_panel, text="Ready Queue", padding=10)
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create Treeview for ready queue
        self.ready_queue = ttk.Treeview(queue_frame, 
            columns=("PID", "Arrival", "Burst", "Priority", "Status"),
            show='headings', height=8)
        
        # Configure columns
        columns = [
            ("PID", "PID", 50),
            ("Arrival", "Arrival Time", 80),
            ("Burst", "Burst Time", 80),
            ("Priority", "Priority", 60),
            ("Status", "Status", 100)
        ]
        
        for col, heading, width in columns:
            self.ready_queue.heading(col, text=heading)
            self.ready_queue.column(col, width=width, anchor=tk.CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL, 
                                command=self.ready_queue.yview)
        self.ready_queue.configure(yscrollcommand=scrollbar.set)
        
        self.ready_queue.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_results_section(self):
        # Results Table
        results_frame = ttk.LabelFrame(self.right_panel, text="Process Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create Treeview for results
        self.results_tree = ttk.Treeview(results_frame, 
            columns=("PID", "CT", "TAT", "WT", "RT"),
            show='headings', height=8)
        
        # Configure columns
        columns = [
            ("PID", "Process ID", 70),
            ("CT", "Completion Time", 100),
            ("TAT", "Turnaround Time", 100),
            ("WT", "Waiting Time", 100),
            ("RT", "Response Time", 100)
        ]
        
        for col, heading, width in columns:
            self.results_tree.heading(col, text=heading)
            self.results_tree.column(col, width=width, anchor=tk.CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Metrics Frame
        metrics_frame = ttk.LabelFrame(self.right_panel, text="Performance Metrics", padding=10)
        metrics_frame.pack(fill=tk.X, pady=10)

        # Create labels for metrics
        self.metrics_labels = {}
        metrics = [
            "Average Waiting Time",
            "Average Turnaround Time",
            "Average Response Time",
            "Context Switches",
            "CPU Idle Time"
        ]

        for i, metric in enumerate(metrics):
            label = ttk.Label(metrics_frame, text=f"{metric}:", style='Modern.TLabel')
            label.grid(row=i//2, column=(i%2)*2, padx=5, pady=5, sticky='e')
            
            value_label = ttk.Label(metrics_frame, text="0.00", style='Modern.TLabel')
            value_label.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5, sticky='w')
            
            self.metrics_labels[metric] = value_label

    def create_modern_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, command=command,
                       bg=color, fg='white',
                       relief=tk.FLAT,
                       font=('Arial', 10),
                       padx=15, pady=5)
        btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        return btn

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
            self.update_ready_queue(process)
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers")

    def clear_processes(self):
        self.processes = []
        self.process_counter = 1
        self.entries["Process ID"].delete(0, tk.END)
        self.entries["Process ID"].insert(0, "1")
        self.update_ready_queue(None)

    def update_ready_queue(self, process):
        self.ready_queue.delete(*self.ready_queue.get_children())
        if process:
            self.ready_queue.insert("", "end", values=(
                process.pid,
                process.arrival,
                process.burst,
                process.priority,
                "Waiting"
            ))

    def update_results(self, processes, context_switches, idle_time):
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

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
        self.metrics_labels["CPU Idle Time"].configure(
            text=f"{idle_time:.2f}")

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
            
            # Calculate idle time
            total_time = max(p.completion_time for p in processes)
            busy_time = sum(end - start for _, start, end in gantt_data)
            idle_time = total_time - busy_time

            self.update_results(processes, context_switches, idle_time)
            self.show_gantt_chart(gantt_data)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_gantt_chart(self, gantt_data):
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

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernCPUScheduler(root)
    root.mainloop()  