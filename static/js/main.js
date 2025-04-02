// Global state
let processes = [];

// DOM Elements
const processForm = document.getElementById('processForm');
const processList = document.getElementById('processList');
const algorithmSelect = document.getElementById('algorithm');
const algorithmOptions = document.getElementById('algorithmOptions');
const runSimulationBtn = document.getElementById('runSimulation');
const resultsDiv = document.getElementById('results');

// Event Listeners
processForm.addEventListener('submit', handleProcessSubmit);
algorithmSelect.addEventListener('change', handleAlgorithmChange);
runSimulationBtn.addEventListener('click', runSimulation);

// Handle process form submission
function handleProcessSubmit(e) {
    e.preventDefault();
    
    const process = {
        pid: parseInt(document.getElementById('pid').value),
        arrival: parseInt(document.getElementById('arrival').value),
        burst: parseInt(document.getElementById('burst').value),
        priority: parseInt(document.getElementById('priority').value)
    };
    
    processes.push(process);
    updateProcessList();
    processForm.reset();
    document.getElementById('pid').value = processes.length + 1;
}

// Update process list display
function updateProcessList() {
    processList.innerHTML = processes.map((p, index) => `
        <div class="list-group-item d-flex justify-content-between align-items-center">
            <div>
                <strong>P${p.pid}</strong>
                <small class="ms-2">AT: ${p.arrival} | BT: ${p.burst} | Priority: ${p.priority}</small>
            </div>
            <button class="btn btn-sm btn-danger" onclick="deleteProcess(${index})">×</button>
        </div>
    `).join('');
}

// Delete process
function deleteProcess(index) {
    processes.splice(index, 1);
    updateProcessList();
}

// Handle algorithm selection change
function handleAlgorithmChange() {
    const algorithm = algorithmSelect.value;
    let options = '';
    
    if (algorithm === 'RoundRobin') {
        options = `
            <div class="mb-3">
                <label class="form-label">Time Quantum</label>
                <input type="number" class="form-control" id="timeQuantum" min="1" value="2">
            </div>
        `;
    } else if (algorithm === 'Priority') {
        options = `
            <div class="mb-3">
                <label class="form-label">Priority Order</label>
                <select class="form-select" id="priorityOrder">
                    <option value="lower">Lower number = Higher Priority</option>
                    <option value="higher">Higher number = Higher Priority</option>
                </select>
            </div>
        `;
    }
    
    algorithmOptions.innerHTML = options;
}

// Run simulation
async function runSimulation() {
    if (processes.length === 0) {
        alert('Please add at least one process first!');
        return;
    }
    
    const algorithm = algorithmSelect.value;
    const timeQuantum = algorithm === 'RoundRobin' ? parseInt(document.getElementById('timeQuantum').value) : 2;
    const priorityOrder = algorithm === 'Priority' ? document.getElementById('priorityOrder').value : 'lower';
    
    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                processes,
                algorithm,
                timeQuantum,
                priorityOrder
            })
        });
        
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        console.error('Error running simulation:', error);
        alert('An error occurred while running the simulation.');
    }
}

// Display simulation results
function displayResults(data) {
    resultsDiv.style.display = 'block';
    
    // Update metrics
    document.getElementById('avgTurnaround').textContent = data.metrics.avgTurnaround;
    document.getElementById('avgWaiting').textContent = data.metrics.avgWaiting;
    document.getElementById('avgResponse').textContent = data.metrics.avgResponse;
    document.getElementById('contextSwitches').textContent = data.metrics.contextSwitches;
    
    // Update process details table
    const processDetails = document.getElementById('processDetails');
    processDetails.innerHTML = data.processDetails.map(p => `
        <tr>
            <td>P${p.pid}</td>
            <td>${p.completionTime}</td>
            <td>${p.turnaroundTime}</td>
            <td>${p.waitingTime}</td>
            <td>${p.responseTime}</td>
        </tr>
    `).join('');
    
    // Create Gantt Chart
    createGanttChart(data.ganttChart);
    
    // Create Time Distribution Chart
    createTimeDistributionChart(data.processDetails);
    
    // Create Time Metrics Chart
    createTimeMetricsChart(data.processDetails);
}

// Create Gantt Chart
function createGanttChart(ganttData) {
    const traces = ganttData.map(([pid, start, end], index) => ({
        x: [end - start],
        y: [`P${pid}`],
        orientation: 'h',
        base: [start],
        marker: {
            color: `hsl(${index * 360 / ganttData.length}, 70%, 50%)`
        },
        text: [`P${pid} (${start}-${end})`],
        textposition: 'inside',
        hoverinfo: 'text',
        showlegend: false
    }));
    
    const layout = {
        barmode: 'overlay',
        xaxis: {
            title: 'Time',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#2a2d35',
            zeroline: true,
            zerolinewidth: 2,
            zerolinecolor: '#00ff9d'
        },
        yaxis: {
            title: 'Process',
            showgrid: true,
            gridwidth: 1,
            gridcolor: '#2a2d35'
        },
        height: 50 + (processes.length * 40),
        margin: { l: 100, r: 100, t: 30, b: 30 },
        plot_bgcolor: '#1a1c23',
        paper_bgcolor: '#1a1c23',
        font: { color: '#ffffff' }
    };
    
    Plotly.newPlot('ganttChart', traces, layout);
}

// Create Time Distribution Chart
function createTimeDistributionChart(processDetails) {
    const trace1 = {
        name: 'Waiting Time',
        x: processDetails.map(p => `P${p.pid}`),
        y: processDetails.map(p => p.waitingTime),
        type: 'bar',
        marker: { color: '#ff3366' }
    };
    
    const trace2 = {
        name: 'Burst Time',
        x: processDetails.map(p => `P${p.pid}`),
        y: processDetails.map(p => p.burstTime),
        type: 'bar',
        marker: { color: '#00ff9d' }
    };
    
    const layout = {
        barmode: 'stack',
        plot_bgcolor: '#1a1c23',
        paper_bgcolor: '#1a1c23',
        font: { color: '#ffffff' },
        xaxis: { gridcolor: '#2a2d35' },
        yaxis: { gridcolor: '#2a2d35' },
        legend: {
            orientation: 'h',
            yanchor: 'bottom',
            y: 1.02,
            xanchor: 'right',
            x: 1
        }
    };
    
    Plotly.newPlot('timeDistribution', [trace1, trace2], layout);
}

// Create Time Metrics Chart
function createTimeMetricsChart(processDetails) {
    const trace1 = {
        name: 'Response Time',
        x: processDetails.map(p => `P${p.pid}`),
        y: processDetails.map(p => p.responseTime),
        type: 'bar',
        marker: { color: '#00ff9d' }
    };
    
    const trace2 = {
        name: 'Turnaround Time',
        x: processDetails.map(p => `P${p.pid}`),
        y: processDetails.map(p => p.turnaroundTime),
        type: 'bar',
        marker: { color: '#ff3366' }
    };
    
    const layout = {
        barmode: 'group',
        plot_bgcolor: '#1a1c23',
        paper_bgcolor: '#1a1c23',
        font: { color: '#ffffff' },
        xaxis: { gridcolor: '#2a2d35' },
        yaxis: { gridcolor: '#2a2d35' },
        legend: {
            orientation: 'h',
            yanchor: 'bottom',
            y: 1.02,
            xanchor: 'right',
            x: 1
        }
    };
    
    Plotly.newPlot('timeMetrics', [trace1, trace2], layout);
} 