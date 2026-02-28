const ctx = document.getElementById('portfolioChart').getContext('2d');

const portfolioChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: portfolioLabels,
    datasets: [{
      label: 'Portfolio Value',
      data: portfolioValues,
      borderColor: '#3b82f6',
      fill: true,
      backgroundColor: 'rgba(59,130,246,0.2)'
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false
  }
});


// Use the same feature that I used to have with MarketSight, and this will prevent the portfolio from updatng everytime :)

document.querySelectorAll('[data-range]').forEach(button => {
  button.addEventListener('click', async () => {

    const range = button.dataset.range;

    document.querySelectorAll('.range-btn').forEach(btn => {
      btn.classList.remove(
        'bg-green-500/20',
        'text-green-400',
        'shadow-lg',
        'shadow-green-500/30'
      );
    });

    // Add active glow, such as that we add when the users clicks on the button so boom it glows lol
    button.classList.add(
      'bg-green-500/20',
      'text-green-400',
      'shadow-lg',
      'shadow-green-500/30'
    );

    // Fetch new data
    const response = await fetch(`/portfolio/chart-data/?range=${range}`);
    const data = await response.json();

    portfolioChart.data.labels = data.labels;
    portfolioChart.data.datasets[0].data = data.values;

    portfolioChart.update();
  });
});