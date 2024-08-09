let logs = [];

// Apply Rule Function
function applyRule() {
    const ip = document.getElementById('ip').value;
    const action = document.getElementById('action').value;
    fetch('/apply_rule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip, action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            logs.push({ ip, action, timestamp: new Date().toISOString() });
            updateLogTable();
        }
    });
}

// Update Log Table Function
function updateLogTable() {
    const table = document.getElementById('log-table');
    table.innerHTML = '<tr><th>IP Address</th><th>Action</th><th>Timestamp</th></tr>';
    logs.forEach(log => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${log.ip}</td><td>${log.action}</td><td>${log.timestamp}</td>`;
        table.appendChild(row);
    });
}

// Download PDF Function
function downloadPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    doc.text("Access Logs", 10, 10);
    logs.forEach((log, index) => {
        doc.text(`${index + 1}. IP: ${log.ip}, Action: ${log.action}, Timestamp: ${log.timestamp}`, 10, 20 + (index * 10));
    });
    doc.save('access_logs.pdf');
}

// Clear Logs Function
function clearLogs() {
    logs = [];
    updateLogTable();
}

// Fetch Logs Function
function fetchLogs() {
    fetch('/get_logs')
        .then(response => response.json())
        .then(data => {
            logs = data;
            updateLogTable();
        });
}

// Call fetchLogs to load logs when the page loads
fetchLogs();
