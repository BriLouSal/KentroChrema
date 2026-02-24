const ctx = document.getElementById('stockChart').getContext('2d');
// Graph for the Stock
new Chart(ctx, {
  type: 'line',
  data: {
    labels: chartLabels, // From my Django connected via stock.html
    datasets: [
      {
        label: `${stockTicker} Price`,
        data: stockData,
        borderColor: '#3b82f6',
        fill: true,
        tension: 0.1,
        backgroundColor: 'rgba(59, 130, 246, 0.2)'
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: {
          maxTicksLimit: 10,
          autoSkip: true,
          display: false
        },
        grid: {
          display: false
        }
      },
      // y: {
      //   ticks: {
      //     display: false
      //   },
      //   grid: {
      //     display: false
      //   }
      // }
    }
  }
});

// function graph_colour () {
//   const currentPrice = stockData[stockData.length - 1]
//   const previousPrice = Chart_yesterday_price
//   // Stock currentPrice should be green!
//   if (currentPrice > previousPrice) return '#36ff0f'
//   // If the price of the stock is same, return blue (normal colour:)
//   else if (currentPrice === previousPrice) return '#7df0ff'
//   // Else it should be red
//   else return '#FF3131'
// }

