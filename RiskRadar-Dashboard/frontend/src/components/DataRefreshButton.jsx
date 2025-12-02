import React, { useState } from 'react'
import './DataRefreshButton.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const DataRefreshButton = ({ onRefresh }) => {
  const [refreshing, setRefreshing] = useState(false)

  const handleRefresh = async () => {
    try {
      setRefreshing(true)
      const response = await fetch(`${API_BASE_URL}/api/data/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          data_types: null // Refresh all
        })
      })

      if (!response.ok) {
        throw new Error('Refresh failed')
      }

      // Wait a moment for background processing, then refresh UI
      setTimeout(() => {
        if (onRefresh) {
          onRefresh()
        }
        setRefreshing(false)
      }, 2000)
    } catch (err) {
      console.error('Error refreshing data:', err)
      setRefreshing(false)
      alert('Failed to refresh data. Please try again.')
    }
  }

  return (
    <button
      className="refresh-button"
      onClick={handleRefresh}
      disabled={refreshing}
    >
      {refreshing ? 'Refreshing...' : 'Refresh Data'}
    </button>
  )
}

export default DataRefreshButton

