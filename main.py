import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.style as style
import numpy as np
from scheduling_algorithms import (
    Process,
    fcfs_scheduling,
    sjf_scheduling,
    round_robin_scheduling,
    priority_scheduling
)

class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator")
        self.root.geometry("1400x900")
        
        # Set theme colors
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define color scheme
        self.colors = {
            'bg': '#2C3E50',
            'fg': '#ECF0F1',
            'accent1': '#3498DB',
            'accent2': '#E74C3C',
            'accent3': '#2ECC71'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Configure styles
        style.configure('Custom.TFrame', background=self.colors['bg'])
        style.configure('Custom.TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('Custom.TButton', 
                       background=self.colors['accent1'], 
                       foreground=self.colors['fg'],
                       padding=5)
        
        # Create main frames
        self.create_frames()
        self.create_input_section()
        self.create_process_table()
        self.create_algorithm_section()
        self.create_statistics_section()
        self.create_visualization_section()

        # Initialize statistics variables
        self.current_stats = {
            'waiting_times': [],
            'turnaround_times': [],
            'response_times': [],
            'completion_times': [],
            'idle_time': 0
        }
        
        # Initialize visualization frames
        self.gantt_canvas = None
        self.stats_canvas = None

    def create_frames(self):
        # Main container frame
        self.main_container = ttk.Frame(self.root, padding=10)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Left frame for inputs (using width in the Frame creation instead of pack)
        self.left_frame = ttk.Frame(self.main_container, padding=10, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.left_frame.pack_propagate(False)  # This prevents the frame from shrinking

        # Right frame for outputs and visualizations
        self.right_frame = ttk.Frame(self.main_container, padding=10)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame for visualizations below statistics
        self.viz_frame = ttk.Frame(self.right_frame, padding=10)
        self.viz_frame.pack(fill=tk.BOTH, expand=True)

        # Separate frames for Gantt chart and performance graphs
        self.gantt_frame = ttk.LabelFrame(self.viz_frame, text="Gantt Chart", padding=10)
        self.gantt_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.performance_frame = ttk.LabelFrame(self.viz_frame, text="Performance Metrics", padding=10)
        self.performance_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    def create_input_section(self):
        input_frame = ttk.LabelFrame(self.left_frame, text="Add New Process", padding=10)
        input_frame.pack(fill=tk.X, pady=10)

        # Process ID
        ttk.Label(input_frame, text="PID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.pid_entry = ttk.Entry(input_frame)
        self.pid_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.pid_entry.insert(0, self.generate_unique_pid())

        # Arrival Time
        ttk.Label(input_frame, text="Arrival Time:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.arrival_entry = ttk.Entry(input_frame)
        self.arrival_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Burst Time
        ttk.Label(input_frame, text="Burst Time:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.burst_entry = ttk.Entry(input_frame)
        self.burst_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Priority
        ttk.Label(input_frame, text="Priority:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.priority_entry = ttk.Entry(input_frame)
        self.priority_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.priority_entry.insert(0, "0")

        # Add Process Button
        add_button = tk.Button(input_frame, text="Add Process", command=self.add_process,
                             bg='#4CAF50', fg='white', relief=tk.RAISED,
                             font=('Arial', 10, 'bold'), padx=10, pady=5)
        add_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

    def create_process_table(self):
        table_frame = ttk.LabelFrame(self.left_frame, text="Processes", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create Treeview
        self.tree = ttk.Treeview(table_frame, columns=("PID", "Arrival", "Burst", "Priority"), show='headings')
        self.tree.heading("PID", text="PID")
        self.tree.heading("Arrival", text="Arrival Time")
        self.tree.heading("Burst", text="Burst Time")
        self.tree.heading("Priority", text="Priority")

        self.tree.column("PID", width=50, anchor=tk.CENTER)
        self.tree.column("Arrival", width=100, anchor=tk.CENTER)
        self.tree.column("Burst", width=100, anchor=tk.CENTER)
        self.tree.column("Priority", width=80, anchor=tk.CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Delete button
        delete_button = tk.Button(table_frame, text="Delete Selected", command=self.delete_process,
                                bg='#f44336', fg='white', relief=tk.RAISED,
                                font=('Arial', 10, 'bold'), padx=10, pady=5)
        delete_button.pack(pady=5, fill=tk.X)

    def create_algorithm_section(self):
        algo_frame = ttk.LabelFrame(self.left_frame, text="Scheduling Algorithm", padding=10)
        algo_frame.pack(fill=tk.X, pady=10)

        self.algo_var = tk.StringVar(self.root)
        algorithms = ["Select Algorithm", "FCFS", "SJF", "Round Robin", "Priority Scheduling"]
        self.algo_var.set(algorithms[0])

        # Algorithm selection
        ttk.Label(algo_frame, text="Select Algorithm:").pack(pady=5)
        algo_menu = ttk.Combobox(algo_frame, textvariable=self.algo_var, values=algorithms, state="readonly")
        algo_menu.pack(pady=5, fill=tk.X)
        algo_menu.bind("<<ComboboxSelected>>", self.show_algorithm_options)

        # Time Quantum for Round Robin
        self.time_quantum_label = ttk.Label(algo_frame, text="Time Quantum:")
        self.time_quantum_entry = ttk.Entry(algo_frame)
        
        # Run button
        run_button = tk.Button(algo_frame, text="Run Scheduler", command=self.run_scheduler,
                             bg='#2196F3', fg='white', relief=tk.RAISED,
                             font=('Arial', 10, 'bold'), padx=10, pady=5)
        run_button.pack(pady=10, fill=tk.X)

    def create_statistics_section(self):
        stats_frame = ttk.LabelFrame(self.right_frame, text="Process Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Create Treeview for statistics
        self.stats_tree = ttk.Treeview(stats_frame, columns=("PID", "Wait", "Turnaround", "Response"), show='headings')
        self.stats_tree.heading("PID", text="PID")
        self.stats_tree.heading("Wait", text="Waiting Time")
        self.stats_tree.heading("Turnaround", text="Turnaround Time")
        self.stats_tree.heading("Response", text="Response Time")

        self.stats_tree.column("PID", width=50, anchor=tk.CENTER)
        self.stats_tree.column("Wait", width=100, anchor=tk.CENTER)
        self.stats_tree.column("Turnaround", width=100, anchor=tk.CENTER)
        self.stats_tree.column("Response", width=100, anchor=tk.CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)

        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_visualization_section(self):
        viz_frame = ttk.LabelFrame(self.right_frame, text="Visualizations", padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Frame for Gantt Chart
        self.gantt_frame = ttk.Frame(viz_frame, style='Custom.TFrame')
        self.gantt_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Frame for Performance Metrics
        self.metrics_frame = ttk.Frame(viz_frame, style='Custom.TFrame')
        self.metrics_frame.pack(fill=tk.BOTH, expand=True, pady=5)

    def generate_unique_pid(self):
        if not hasattr(self, 'process_count'):
            self.process_count = 1
        else:
            self.process_count += 1
        return self.process_count

    def add_process(self):
        try:
            pid = int(self.pid_entry.get())
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())
            
            if arrival < 0 or burst <= 0 or priority < 0:
                raise ValueError("Arrival and priority cannot be negative, burst must be positive.")
                
            self.tree.insert("", "end", values=(pid, arrival, burst, priority))
            
            # Clear entries
            self.pid_entry.delete(0, tk.END)
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
            
            # Set next PID
            self.pid_entry.insert(0, self.generate_unique_pid())
            self.priority_entry.insert(0, "0")
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def delete_process(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a process to delete.")
            return
        self.tree.delete(selected_item)

    def show_algorithm_options(self, event):
        selected_algo = self.algo_var.get()
        if selected_algo == "Round Robin":
            self.time_quantum_label.pack(pady=5)
            self.time_quantum_entry.pack(pady=5, fill=tk.X)
        else:
            self.time_quantum_label.pack_forget()
            self.time_quantum_entry.pack_forget()

    def run_scheduler(self):
        process_data = []
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            process_data.append(Process(int(values[0]), int(values[1]), int(values[2]), int(values[3])))

        if not process_data:
            messagebox.showerror("Error", "Please add some processes first!")
            return

        selected_algo = self.algo_var.get()
        if selected_algo == "Select Algorithm":
            messagebox.showerror("Error", "Please select an algorithm!")
            return

        # Clear previous statistics
        self.stats_tree.delete(*self.stats_tree.get_children())

        try:
            # Run selected algorithm
            if selected_algo == "FCFS":
                scheduled_processes, gantt_chart = fcfs_scheduling(process_data)
            elif selected_algo == "SJF":
                scheduled_processes, gantt_chart = sjf_scheduling(process_data)
            elif selected_algo == "Round Robin":
                try:
                    time_quantum = int(self.time_quantum_entry.get())
                    if time_quantum <= 0:
                        raise ValueError("Time quantum must be positive")
                    scheduled_processes, gantt_chart = round_robin_scheduling(process_data, time_quantum)
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                    return
            elif selected_algo == "Priority Scheduling":
                scheduled_processes, gantt_chart = priority_scheduling(process_data)

            # Update displays
            self.calculate_statistics(scheduled_processes, gantt_chart)
            self.update_statistics_table(scheduled_processes)
            self.show_gantt_chart(gantt_chart, selected_algo)
            self.show_performance_graphs()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def calculate_statistics(self, processes, gantt_chart):
        self.current_stats = {
            'waiting_times': [],
            'turnaround_times': [],
            'response_times': [],
            'completion_times': [],
            'idle_time': 0
        }

        for process in processes:
            self.current_stats['waiting_times'].append(process.waiting_time)
            self.current_stats['turnaround_times'].append(process.turnaround_time)
            self.current_stats['completion_times'].append(process.completion_time)

            # Calculate response time
            first_execution = next((g for g in gantt_chart if g[0] == process.pid), None)
            if first_execution:
                response_time = first_execution[1] - process.arrival
                self.current_stats['response_times'].append(response_time)
            else:
                self.current_stats['response_times'].append(0)

    def update_statistics_table(self, processes):
        self.stats_tree.delete(*self.stats_tree.get_children())
        for i, p in enumerate(processes):
            self.stats_tree.insert("", "end", values=(
                p.pid,
                p.waiting_time,
                p.turnaround_time,
                self.current_stats['response_times'][i]
            ))

    def show_gantt_chart(self, gantt_chart, algorithm_name):
        # Clear previous chart if it exists
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(10, 2))
        ax = fig.add_subplot(111)

        # Create color map for processes
        unique_pids = len(set(g[0] for g in gantt_chart))
        colors = plt.cm.get_cmap('Set3')(np.linspace(0, 1, unique_pids))

        for i, (pid, start, end) in enumerate(gantt_chart):
            ax.barh(y=0, width=end-start, left=start, height=0.3,
                   color=colors[pid-1], alpha=0.75)
            ax.text((start + end)/2, 0, f'P{pid}',
                   ha='center', va='center')

        ax.set_xlabel('Time')
        ax.set_yticks([])
        ax.set_title(f'{algorithm_name} - Gantt Chart')
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_performance_graphs(self):
        # Clear previous graphs if they exist
        for widget in self.performance_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(10, 3))
        
        # Create one row with three columns for the metrics
        gs = fig.add_gridspec(1, 3, hspace=0.3)
        
        metrics = [
            ('Average Waiting Time', 'waiting_times', '#2196F3'),
            ('Average Turnaround Time', 'turnaround_times', '#4CAF50'),
            ('Average Response Time', 'response_times', '#f44336')
        ]
        
        for idx, (title, metric, color) in enumerate(metrics):
            ax = fig.add_subplot(gs[0, idx])
            avg_value = sum(self.current_stats[metric])/len(self.current_stats[metric])
            
            bar = ax.bar([title], [avg_value], color=color)
            ax.set_title(title, fontsize=8, pad=10)
            ax.grid(True, alpha=0.3)
            
            # Add value label on top of bar
            ax.text(0, avg_value, f'{avg_value:.2f}',
                    ha='center', va='bottom')
            
            # Rotate x-axis labels for better readability
            ax.tick_params(axis='x', rotation=15)

        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.performance_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()  