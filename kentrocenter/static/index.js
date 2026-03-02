const canvases = document.querySelectorAll('.gainerGraph')
const losing_canvases = document.querySelectorAll('.loserGraph')

canvases.forEach((canvas, index) => {

  canvas.addEventListener('click', () => {
    window.location.href = `/stock/${ticker_winner[index]}/`
  })
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
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 0,
          tension: 0.3
        }
      ]
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,

      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { display: false },
        y: { display: false }
      }
    }
  })
})

losing_canvases.forEach((canvas, index) => {
    canvas.addEventListener('click', () => {
    window.location.href = `/stock/${ticker_winner[index]}/`
  })
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
          borderWidth: 2,
          pointRadius: 0,
          pointHoverRadius: 0,
          tension: 0.3
        }
      ]
    },

    options: {
      responsive: true,
      maintainAspectRatio: false,

      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { display: false },
        y: { display: false }
      }
    }
  })
})
