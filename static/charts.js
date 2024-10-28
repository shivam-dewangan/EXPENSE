<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    // Example data for pie chart and income vs expense chart
    const categoryData = {
        labels: ['Food', 'EMI', 'Fuel', 'Education', 'Shopping'],
        datasets: [{
            data: [100, 200, 150, 80, 120], // Example values
            backgroundColor: ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0'],
        }]
    };

    const incomeExpenseData = {
        labels: ['January', 'February', 'March', 'April'], // Update labels as needed
        datasets: [
            {
                label: 'Income',
                data: [500, 600, 750, 800], // Example income values
                borderColor: '#4caf50', // Green for income
                fill: false
            },
            {
                label: 'Expense',
                data: [300, 400, 500, 600], // Example expense values
                borderColor: '#f44336', // Red for expense
                fill: false
            }
        ]
    };

    // Initialize the pie chart for expenses by category
    const categoryCtx = document.getElementById('categoryPieChart').getContext('2d');
    new Chart(categoryCtx, {
        type: 'pie',
        data: categoryData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            const data = tooltipItem.dataset.data[tooltipItem.dataIndex];
                            return `${tooltipItem.label}: ${data}`;
                        }
                    }
                }
            }
        }
    });

    // Initialize the line chart for income vs. expense
    const incomeExpenseCtx = document.getElementById('incomeExpenseChart').getContext('2d');
    new Chart(incomeExpenseCtx, {
        type: 'line',
        data: incomeExpenseData,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount ($)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                }
            }
        }
    });
</script>
