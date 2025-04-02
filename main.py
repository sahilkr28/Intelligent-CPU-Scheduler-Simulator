import streamlit as st
import pandas as pd
import plotly.graph_objects as go 
import plotly.express as px
from scheduling_algorithms import *

# Set page config with custom theme
st.set_page_config(
    page_title="CPU Scheduler Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #00ff9d;
            --secondary-color: #ff3366;
            --accent-color: #9d00ff;
            --background-color: #0e1117;
            --text-color: #ffffff;
            --card-bg: #1a1c23;
            --border-color: #2a2d35;
            --gradient-1: linear-gradient(135deg, rgba(0, 255, 157, 0.1), rgba(255, 51, 102, 0.1));
            --gradient-2: linear-gradient(45deg, rgba(157, 0, 255, 0.1), rgba(0, 255, 157, 0.1));
        }
        
        /* General styling */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color) !important;
        }
        
        /* Title and Headers */
        .title-container {
            text-align: center;
            padding: 2rem 0;
            background: var(--gradient-1);
            border-radius: 15px;
            margin-bottom: 2rem;
            border: 1px solid rgba(0, 255, 157, 0.2);
            box-shadow: 0 4px 20px rgba(0, 255, 157, 0.1);
        }
        
        h1 { 
            font-size: 50px !important;
            color: var(--text-color) !important;
            text-shadow: 0 0 20px rgba(0, 255, 157, 0.5);
            font-weight: 800 !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: 2px !important;
        }
        
        h3 { 
            font-size: 26px !important;
            color: var(--text-color) !important;
            font-weight: 700 !important;
            margin-bottom: 1rem !important;
            text-shadow: 0 0 10px rgba(157, 0, 255, 0.3);
        }
        
        /* Input Section */
        .input-section {
            background: var(--gradient-2);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(157, 0, 255, 0.2);
            box-shadow: 0 4px 20px rgba(157, 0, 255, 0.1);
            margin-bottom: 20px;
        }
        
        /* Output Section */
        .output-section {
            background: var(--gradient-1);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 157, 0.2);
            box-shadow: 0 4px 20px rgba(0, 255, 157, 0.1);
        }
        
        /* Metrics */
        .metric-container { 
            font-size: 22px !important;
            background-color: var(--card-bg) !important;
            padding: 20px !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
            border: 1px solid var(--accent-color) !important;
            color: var(--text-color) !important;
            transition: transform 0.3s ease;
        }
        
        .metric-container:hover {
            transform: translateY(-5px);
        }
        
        /* DataFrames */
        .stDataFrame { 
            font-size: 18px !important;
            background-color: var(--card-bg) !important;
            border-radius: 15px !important;
            padding: 15px !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-color) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Buttons */
        .stButton>button {
            background: linear-gradient(45deg, var(--primary-color), var(--accent-color)) !important;
            color: var(--background-color) !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
            border: none !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            box-shadow: 0 4px 15px rgba(0, 255, 157, 0.3) !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0, 255, 157, 0.4) !important;
        }
        
        /* Input fields */
        .stNumberInput>div>div>input {
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--accent-color) !important;
            border-radius: 10px !important;
            padding: 10px !important;
            transition: all 0.3s ease;
        }
        
        .stNumberInput>div>div>input:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 15px rgba(0, 255, 157, 0.2) !important;
        }
        
        /* Selectbox */
        .stSelectbox>div>div>select {
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
            border: 2px solid var(--accent-color) !important;
            border-radius: 10px !important;
            padding: 10px !important;
            transition: all 0.3s ease;
        }
        
        .stSelectbox>div>div>select:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 15px rgba(0, 255, 157, 0.2) !important;
        }
        
        /* Radio buttons */
        .stRadio>div {
            background-color: var(--card-bg) !important;
            padding: 15px !important;
            border-radius: 15px !important;
            border: 1px solid var(--accent-color) !important;
        }
        
        /* Success message */
        .stSuccess {
            background: linear-gradient(45deg, rgba(0, 255, 157, 0.1), rgba(157, 0, 255, 0.1)) !important;
            border: 1px solid var(--primary-color) !important;
            border-radius: 10px !important;
            padding: 15px !important;
            color: var(--text-color) !important;
            box-shadow: 0 4px 15px rgba(0, 255, 157, 0.1) !important;
        }
        
        /* Error message */
        .stError {
            background: linear-gradient(45deg, rgba(255, 51, 102, 0.1), rgba(157, 0, 255, 0.1)) !important;
            border: 1px solid var(--secondary-color) !important;
            border-radius: 10px !important;
            padding: 15px !important;
            color: var(--text-color) !important;
            box-shadow: 0 4px 15px rgba(255, 51, 102, 0.1) !important;
        }

        /* Make all text white */
        .stMarkdown, .stText, .stSelectbox label, .stRadio label, .stNumberInput label {
            color: var(--text-color) !important;
        }

        /* DataFrame headers and cells */
        .stDataFrame th, .stDataFrame td {
            color: var(--text-color) !important;
        }

        /* Subheaders */
        .stSubheader {
            color: var(--text-color) !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1rem;
        }

        /* Metric labels and values */
        .stMetric label {
            color: var(--accent-color) !important;
            font-size: 0.9rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stMetric div {
            color: var(--text-color) !important;
            font-size: 1.5rem !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Title with custom container
st.markdown("""
    <div class="title-container">
        <h1>🖥️ INTELLIGENT CPU SIMULATOR</h1>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if 'processes' not in st.session_state:
    st.session_state.processes = []

# Create two columns for the main layout
left_col, right_col = st.columns([1, 1.5])

# Left Column - Input Section
with left_col:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    
    st.subheader("📝 Process Input")
    col1, col2 = st.columns(2)
    with col1:
        pid = st.number_input("Process ID", min_value=1, value=len(st.session_state.processes) + 1)
        arrival = st.number_input("Arrival Time", min_value=0, value=0)
    with col2:
        burst = st.number_input("Burst Time", min_value=1, value=1)
        priority = st.number_input("Priority", min_value=0, value=0)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Process", use_container_width=True):
            new_process = Process(pid, arrival, burst, priority)
            st.session_state.processes.append(new_process)
            st.success(f"✅ Process {pid} added successfully!")
    
    with col2:
        if st.session_state.processes:
            delete_pid = st.selectbox("Select Process to Delete", [p.pid for p in st.session_state.processes])
            if st.button(f"Delete (P{delete_pid})", use_container_width=True):
                st.session_state.processes = [p for p in st.session_state.processes if p.pid != delete_pid]
                st.rerun()

    st.subheader("⚙️ Algorithm Selection")
    algorithm = st.selectbox(
        "Choose Algorithm",
        ["FCFS", "SJF (Non-preemptive)", "SRTF (Preemptive)", "Round Robin", "Priority"]
    )

    if algorithm == "Priority":
        priority_order = st.radio("Priority Order", ["Lower number = Higher Priority", "Higher number = Higher Priority"])

    if algorithm == "Round Robin":
        time_quantum = st.number_input("Time Quantum", min_value=1, value=2)

    if st.session_state.processes:
        if st.button("Clear All Processes", use_container_width=True):
            st.session_state.processes = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Right Column - Output Section
with right_col:
    st.markdown('<div class="output-section">', unsafe_allow_html=True)
    
    if st.session_state.processes:
        st.subheader(" Process Table")
        process_df = pd.DataFrame(sorted([
            {
                "PID": p.pid,
                "Arrival Time": p.arrival,
                "Burst Time": p.burst,
                "Priority": p.priority
            } for p in st.session_state.processes
        ], key=lambda x: x["PID"], reverse=False))
        st.dataframe(process_df, use_container_width=True)

        if st.button(" Run Simulation", use_container_width=True):
            # Run selected algorithm
            if algorithm == "FCFS":
                processes, gantt_data, switches = fcfs_scheduling(st.session_state.processes)
            elif algorithm == "SJF (Non-preemptive)":
                processes, gantt_data, switches = sjf_scheduling(st.session_state.processes, preemptive=False)
            elif algorithm == "SRTF (Preemptive)":
                processes, gantt_data, switches = sjf_scheduling(st.session_state.processes, preemptive=True)
            elif algorithm == "Round Robin":
                processes, gantt_data, switches = round_robin_scheduling(st.session_state.processes, time_quantum)
            else:  # Priority
                processes, gantt_data, switches = priority_scheduling(st.session_state.processes, ascending=(priority_order == "Lower number = Higher Priority"))

            # Calculate metrics
            avg_turnaround, avg_waiting, avg_response = calculate_metrics(processes)
            processes.sort(key=lambda p: p.pid)

            st.subheader(" Gantt Chart")
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
                barmode='overlay',
                xaxis=dict(
                    title="Time",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor='var(--primary-color)',
                    color='#ffffff'
                ),
                yaxis=dict(
                    title="Process",
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    color='#ffffff'
                ),
                height=50 + (len(st.session_state.processes) * 40),
                margin=dict(l=100, r=100, t=30, b=30),
                plot_bgcolor='rgba(26, 28, 35, 0.8)',
                paper_bgcolor='rgba(26, 28, 35, 0)',
                font=dict(color='#ffffff')
            )

            st.plotly_chart(fig, use_container_width=True)

            st.subheader(" Performance Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Turnaround", f"{avg_turnaround:.2f}")
            with col2:
                st.metric("Avg Waiting", f"{avg_waiting:.2f}")
            with col3:
                st.metric("Avg Response", f"{avg_response:.2f}")
            with col4:
                st.metric("Context Switches", switches)

            st.subheader(" Process Details")
            details_df = pd.DataFrame([
                {
                    "PID": p.pid,
                    "Completion Time": p.completion_time,
                    "Turnaround Time": p.turnaround_time,
                    "Waiting Time": p.waiting_time,
                    "Response Time": p.response_time
                } for p in processes
            ])
            st.dataframe(details_df, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)