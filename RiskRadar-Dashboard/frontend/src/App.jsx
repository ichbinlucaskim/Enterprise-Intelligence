import React, { useState, useEffect } from 'react'
import RiskRadarChart from './components/RiskRadarChart'
import RiskGauges from './components/RiskGauges'
import MonteCarloPanel from './components/MonteCarloPanel'
import DataRefreshButton from './components/DataRefreshButton'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [riskData, setRiskData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetchRiskData = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${API_BASE_URL}/api/risk/radar`)
      if (!response.ok) {
        throw new Error('Failed to fetch risk data')
      }
      const data = await response.json()
      setRiskData(data)
      setLastUpdated(new Date(data.last_updated))
    } catch (err) {
      setError(err.message)
      console.error('Error fetching risk data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRiskData()
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchRiskData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const handleRefresh = async () => {
    await fetchRiskData()
  }

  if (loading && !riskData) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading risk data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Enterprise Risk Radar Dashboard</h1>
        <div className="header-controls">
          {lastUpdated && (
            <span className="last-updated">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <DataRefreshButton onRefresh={handleRefresh} />
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <p>Error: {error}</p>
          <button onClick={fetchRiskData}>Retry</button>
        </div>
      )}

      <main className="dashboard-content">
        {riskData && (
          <>
            <div className="dashboard-row">
              <div className="radar-container">
                <RiskRadarChart riskData={riskData} />
              </div>
              <div className="gauges-container">
                <RiskGauges riskData={riskData} />
              </div>
            </div>
            <div className="monte-carlo-container">
              <MonteCarloPanel />
            </div>
          </>
        )}
      </main>
    </div>
  )
}

export default App

