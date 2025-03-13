document.addEventListener('DOMContentLoaded', function() {
    let lastUpdate = new Date().toISOString();
    let alertTypesChart = null;
    let systemActivityChart = null;

    function updateDashboard() {
        fetch('/api/alerts')
            .then(response => response.json())
            .then(data => {
                updateAlertStats(data.stats);
                updateAlertTable(data.alerts);
                updateCharts(data.stats);
            })
            .catch(error => console.error('Erreur:', error));
    }

    function updateAlertStats(stats) {
        document.getElementById('total-alerts').textContent = stats.total;
        document.getElementById('critical-alerts').textContent = stats.by_priority['1'] || 0;
        document.getElementById('ssh-attempts').textContent = 
            Object.entries(stats.by_classification)
                .filter(([key]) => key.includes('SSH'))
                .reduce((acc, [_, val]) => acc + val, 0);
    }

    function updateAlertTable(alerts) {
        const tbody = document.getElementById('alerts-table-body');
        tbody.innerHTML = '';
        
        alerts.slice(-10).reverse().forEach(alert => {
            const row = document.createElement('tr');
            const priority = parseInt(alert.priority);
            row.className = priority === 1 ? 'table-danger' : 
                           priority === 2 ? 'table-warning' : '';
            
            row.innerHTML = `
                <td>${alert.timestamp}</td>
                <td>${alert.classification}</td>
                <td>${alert.message}</td>
                <td>${alert.priority}</td>
            `;
            tbody.appendChild(row);
        });
    }

    function updateCharts(stats) {
        // Graphique des types d'alertes
        const alertTypes = {
            labels: Object.keys(stats.by_classification),
            datasets: [{
                data: Object.values(stats.by_classification),
                backgroundColor: [
                    '#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0'
                ]
            }]
        };

        if (!alertTypesChart) {
            const ctx = document.getElementById('alertTypesChart').getContext('2d');
            alertTypesChart = new Chart(ctx, {
                type: 'doughnut',
                data: alertTypes,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'right',
                        },
                        title: {
                            display: true,
                            text: 'Distribution des alertes'
                        }
                    }
                }
            });
        } else {
            alertTypesChart.data = alertTypes;
            alertTypesChart.update();
        }

        // Timeline d'activité
        const timelineData = {
            labels: Object.keys(stats.timeline),
            datasets: [{
                label: 'Nombre d\'alertes',
                data: Object.values(stats.timeline),
                fill: false,
                borderColor: '#36a2eb',
                tension: 0.1
            }]
        };

        if (!systemActivityChart) {
            const ctx = document.getElementById('systemActivityChart').getContext('2d');
            systemActivityChart = new Chart(ctx, {
                type: 'line',
                data: timelineData,
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } else {
            systemActivityChart.data = timelineData;
            systemActivityChart.update();
        }
    }

    // Mise à jour initiale et rafraîchissement périodique
    updateDashboard();
    setInterval(updateDashboard, 5000);
}); 