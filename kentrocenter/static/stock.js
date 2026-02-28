const ctx = document.getElementById('stockChart').getContext('2d')
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
        grid: {
          display: false
        }
      },
      y: {
        grid: {
          display: false
        }
      }
    }
  }
})

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

// Add centre text for bulish indicator

function pieGraphColor (score) {
  if (score < 20) return '#d32f2f'
  if (score < 40) return '#f57c00'
  if (score < 60) return '#fbc02d'
  if (score < 80) return '#7cb342'
  return '#2e7d32'
}

// Add centre text for bulish indicator
const centerText = {
  id: 'centerText',
  afterDraw (chart) {
    const {
      ctx,
      chartArea: { width, height }
    } = chart
    ctx.save()

    ctx.font = 'bold 12px sans-serif'
    ctx.fillStyle = '#ffffff'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('Bullish Indicator', width / 2, height / 2 - 30)

    //  Muddle
    ctx.font = 'bold 26px sans-serif'
    ctx.fillStyle = '#ffffff'
    ctx.fillText(`${score}%`, width / 2, height / 2)

    // Subtitle
    ctx.font = ' 14px sans-serif'
    ctx.fillStyle = '#ffffff'
    ctx.fillText(`Bullish Score`, width / 2, height / 2 + 28)
    ctx.restore()
  }
}

// Grab the chart for bullish indicator
const ctx_chart = document.getElementById('bullishIndicator')

const chart = new Chart(ctx_chart, {
  type: 'doughnut',
  plugins: [centerText],
  data: {
    datasets: [
      {
        data: [0.001, 99.999],
        backgroundColor: [pieGraphColor(score), '#eeeeee'],
        borderWidth: 0
      }
    ]
  }
})

let animation_score = { v: 0 }

gsap.to(animation_score, {
  v: score,
  duration: 1.5,
  ease: 'power3.out',
  onUpdate () {
    const v = Math.max(animation_score.v, 0.0001)

    chart.data.datasets[0].data = [v, 100 - v]
    chart.data.datasets[0].backgroundColor = [pieGraphColor(v), '#222831']

    chart.update('none')
  }
})


const riskCenterText = {
  id: 'riskCenterText',
  afterDraw (chart) {
    const {
      ctx,
      chartArea: { width, height }
    } = chart

    ctx.save()

    // Title
    ctx.font = 'bold 12px sans-serif'
    ctx.fillStyle = '#ffffff'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('Risk Score', width / 2, height / 2 - 30)

    // Big Number
    ctx.font = 'bold 26px sans-serif'
    ctx.fillStyle = '#ffffff'
    ctx.fillText(`${riskScore}`, width / 2, height / 2)

    // Risk Level Label
    let label = 'Low'
    if (riskScore >= 60) label = 'High'
    else if (riskScore >= 30) label = 'Moderate'

    ctx.font = '14px sans-serif'
    ctx.fillStyle = '#9CA3AF'
    ctx.fillText(label, width / 2, height / 2 + 28)

    ctx.restore()
  }
}


const riskCtx = document.getElementById('riskChart')

if (riskCtx) {
  let riskColor

  if (riskScore < 30) {
    riskColor = '#10B981'
  } else if (riskScore < 60) {
    riskColor = '#F59E0B'
  } else {
    riskColor = '#EF4444'
  }

  new Chart(riskCtx, {
    type: 'doughnut',
    plugins: [riskCenterText],
    data: {
      datasets: [
        {
          data: [riskScore, 100 - riskScore],
          backgroundColor: [riskColor, '#1F2937'],
          borderWidth: 0
        }
      ]
    },
    options: {
      cutout: '75%',
      plugins: { legend: { display: false } }
    }
  })
}

