import React from 'react'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend
} from 'recharts'
import './RiskRadarChart.css'

const RiskRadarChart = ({ riskData }) => {
  if (!riskData) return null

  const chartData = [
    {
      category: 'Market',
      risk: riskData.market_risk.score,
      fullMark: 100
    },
    {
      category: 'Supply Chain',
      risk: riskData.supply_chain_risk.score,
      fullMark: 100
    },
    {
      category: 'Regulatory',
      risk: riskData.regulatory_risk.score,
      fullMark: 100
    },
    {
      category: 'HR',
      risk: riskData.hr_risk.score,
      fullMark: 100
    }
  ]

  // Color based on overall risk
  const getRiskColor = (score) => {
    if (score < 33) return '#4ade80' // green
    if (score < 66) return '#fbbf24' // yellow
    return '#ef4444' // red
  }

  const riskColor = getRiskColor(riskData.overall_risk)

  return (
    <div className="radar-chart-container">
      <h2>Risk Radar Overview</h2>
      <div className="overall-risk-badge" style={{ backgroundColor: riskColor }}>
        Overall Risk: {riskData.overall_risk.toFixed(1)}
      </div>
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="category" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} />
          <Radar
            name="Risk Score"
            dataKey="risk"
            stroke={riskColor}
            fill={riskColor}
            fillOpacity={0.6}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
      <div className="risk-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#4ade80' }}></span>
          <span>Low (0-33)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#fbbf24' }}></span>
          <span>Medium (34-66)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#ef4444' }}></span>
          <span>High (67-100)</span>
        </div>
      </div>
    </div>
  )
}

export default RiskRadarChart

