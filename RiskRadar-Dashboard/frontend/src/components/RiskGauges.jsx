import React from 'react'
import { Cell, Pie, PieChart, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import './RiskGauges.css'

const RiskGauges = ({ riskData }) => {
  if (!riskData) return null

  const gaugeData = [
    { name: 'Market Risk', value: riskData.market_risk.score },
    { name: 'Supply Chain Risk', value: riskData.supply_chain_risk.score },
    { name: 'Regulatory Risk', value: riskData.regulatory_risk.score },
    { name: 'HR Risk', value: riskData.hr_risk.score }
  ]

  const getColor = (value) => {
    if (value < 33) return '#4ade80'
    if (value < 66) return '#fbbf24'
    return '#ef4444'
  }

  const COLORS = gaugeData.map(item => getColor(item.value))

  return (
    <div className="risk-gauges-container">
      <h2>Risk Category Breakdown</h2>
      <div className="gauges-grid">
        {gaugeData.map((item, index) => (
          <div key={item.name} className="gauge-item">
            <h3>{item.name}</h3>
            <div className="gauge-value" style={{ color: getColor(item.value) }}>
              {item.value.toFixed(1)}
            </div>
            <div className="gauge-bar-container">
              <div
                className="gauge-bar"
                style={{
                  width: `${item.value}%`,
                  backgroundColor: getColor(item.value)
                }}
              ></div>
            </div>
          </div>
        ))}
      </div>
      <div className="pie-chart-container">
        <h3>Risk Distribution</h3>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={gaugeData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value.toFixed(1)}`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {gaugeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default RiskGauges

