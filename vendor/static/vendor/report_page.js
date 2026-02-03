document.addEventListener('DOMContentLoaded', function() {
    // 1. Retrieve the data from the JSON script tags in the HTML
    // 
    const labels = JSON.parse(JSON.parse(document.getElementById('chart-labels-data').textContent));
    const revenueData = JSON.parse(JSON.parse(document.getElementById('chart-revenue-data').textContent));

    const ctx = document.getElementById('revenueChart').getContext('2d');
    
    // Gradient for the chart
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(242, 140, 40, 0.5)'); 
    gradient.addColorStop(1, 'rgba(242, 140, 40, 0.0)');

    const chartConfig = {
        type: 'line',
        data: {
            labels: labels, // Use the variable we parsed above
            datasets: [{
                label: 'Revenue (₦)',
                data: revenueData, // Use the variable we parsed above
                borderColor: '#F28C28', 
                backgroundColor: gradient,
                borderWidth: 3,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#F28C28',
                pointBorderWidth: 2,
                pointRadius: 4,
                tension: 0.4, 
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1F2937',
                    padding: 12,
                    titleFont: { family: 'sans-serif', size: 13 },
                    bodyFont: { family: 'sans-serif', size: 13, weight: 'bold' },
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return '₦ ' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { borderDash: [5, 5], color: '#f3f4f6' },
                    ticks: {
                        font: { size: 10, weight: 'bold' },
                        color: '#9CA3AF',
                        callback: function(value) { return '₦' + value/1000 + 'k'; }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { size: 10, weight: 'bold' },
                        color: '#9CA3AF'
                    }
                }
            }
        }
    };

    new Chart(ctx, chartConfig);
});