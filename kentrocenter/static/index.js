const canvases = document.querySelectorAll('.gainerGraph')
const losing_canvases = document.querySelectorAll('.loserGraph')

canvases.forEach((canvas, index) => {
  new Chart(canvas, {
    type: 'line',

    data: {
      labels: winner_percentage[index].map((_, i) => i),
      datasets: [
        {
          label: ticker_winner[index],
          data: winner_percentage[index],
          borderColor: '#4fc51c',
          backgroundColor: '#166534',
          borderWidth: 0
        }
      ]
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,

      plugins: {
        legend: { display: false }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        border: {
          display: false
        }
      },
      y: {
        grid: {
          display: false
        },
        border: {
          display: false
        }
      }
    }
  })
})

losing_canvases.forEach((canvas, index) => {
  new Chart(canvas, {
    type: 'line',

    data: {
      labels: loser_percentage[index].map((_, i) => i),
      datasets: [
        {
          label: ticker_loser[index],
          data: loser_percentage[index],
          borderColor: '#DC2626',
          backgroundColor: '#DC2626',
          borderWidth: 0
        }
      ]
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,

      plugins: {
        legend: { display: false }
      }
    },
    scales: {
      x: {
        gridLines: {
          display: false
        }
      },
      y: {
        gridLines: {
          display: false
        }
      }
    }
  })
})
