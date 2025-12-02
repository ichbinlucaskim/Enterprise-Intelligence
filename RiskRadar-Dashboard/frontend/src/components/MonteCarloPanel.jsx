import React, { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './MonteCarloPanel.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const MonteCarloPanel = () => {
  const [selectedCategory, setSelectedCategory] = useState('market')
  const [iterations, setIterations] = useState(5000)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const categories = [
    { value: 'market', label: 'Market Risk' },
    { value: 'supply_chain', label: 'Supply Chain Risk' },
    { value: 'regulatory', label: 'Regulatory Risk' },
    { value: 'hr', label: 'HR Risk' }
  ]

  const runSimulation = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${API_BASE_URL}/api/monte-carlo/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          risk_category: selectedCategory,
          iterations: iterations,
          use_cached_data: true
        })
      })

      if (!response.ok) {
        throw new Error('Simulation failed')
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message)
      console.error('Error running simulation:', err)
    } finally {
      setLoading(false)
    }
  }

  const generateDistributionData = () => {
    if (!results) return []
    
    // Generate sample distribution data for visualization
    const data = []
    const mean = results.mean
    const std = results.std
    
    // Create a normal distribution approximation
    for (let i = 0; i <= 100; i += 5) {
      // Simplified normal distribution calculation
      const probability = Math.exp(-0.5 * Math.pow((i - mean) / std, 2))
      data.push({
        risk_score: i,
        probability: probability * 100
      })
    }
    
    return data
  }

  return (
    <div className="monte-carlo-panel">
      <h2>Monte Carlo Risk Simulation</h2>
      <p className="panel-description">
        Run Monte Carlo simulations to forecast risk distributions based on historical data.
        This helps estimate potential future risk scenarios.
      </p>

      <div className="simulation-controls">
        <div className="control-group">
          <label htmlFor="category">Risk Category:</label>
          <select
            id="category"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map(cat => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="iterations">Iterations:</label>
          <input
            id="iterations"
            type="number"
            min="100"
            max="100000"
            step="1000"
            value={iterations}
            onChange={(e) => setIterations(parseInt(e.target.value))}
          />
        </div>

        <button
          className="simulate-button"
          onClick={runSimulation}
          disabled={loading}
        >
          {loading ? 'Running Simulation...' : 'Run Simulation'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {results && (
        <div className="simulation-results">
          <h3>Simulation Results</h3>
          <div className="results-grid">
            <div className="result-card">
              <div className="result-label">Mean Risk Score</div>
              <div className="result-value">{results.mean.toFixed(2)}</div>
            </div>
            <div className="result-card">
              <div className="result-label">Standard Deviation</div>
              <div className="result-value">{results.std.toFixed(2)}</div>
            </div>
            <div className="result-card">
              <div className="result-label">5th Percentile</div>
              <div className="result-value">{results.percentiles['5'].toFixed(2)}</div>
            </div>
            <div className="result-card">
              <div className="result-label">50th Percentile (Median)</div>
              <div className="result-value">{results.percentiles['50'].toFixed(2)}</div>
            </div>
            <div className="result-card">
              <div className="result-label">95th Percentile</div>
              <div className="result-value">{results.percentiles['95'].toFixed(2)}</div>
            </div>
            <div className="result-card">
              <div className="result-label">Iterations</div>
              <div className="result-value">{results.iterations.toLocaleString()}</div>
            </div>
          </div>

          <div className="distribution-chart">
            <h4>Risk Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={generateDistributionData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="risk_score" label={{ value: 'Risk Score', position: 'insideBottom', offset: -5 }} />
                <YAxis label={{ value: 'Probability Density', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="probability"
                  stroke="#667eea"
                  strokeWidth={2}
                  name="Probability"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}

export default MonteCarloPanel

