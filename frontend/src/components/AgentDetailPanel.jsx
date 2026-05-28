import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, DollarSign, TrendingUp, Globe, Users, Activity, Zap, ExternalLink, RefreshCw, Loader } from 'lucide-react'

function StatCard({ label, value, icon: Icon, color, subtext }) {
  return (
    <div
      className="p-3 rounded"
      style={{
        background: `${color}11`,
        border: `1px solid ${color}44`,
      }}
    >
      <div className="flex items-center gap-2 mb-1">
        <Icon size={14} style={{ color }} />
        <span className="text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
          {label}
        </span>
      </div>
      <div className="text-lg font-bold" style={{ fontFamily: 'Orbitron, monospace', color }}>
        {value}
      </div>
      {subtext && (
        <div className="text-xs mt-0.5" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#666688' }}>
          {subtext}
        </div>
      )}
    </div>
  )
}

function WorkAnimation({ type, color }) {
  const bars = [40, 70, 55, 90, 65, 80, 45, 95, 60, 75]

  return (
    <div className="flex items-end gap-1 h-12">
      {bars.map((h, i) => (
        <motion.div
          key={i}
          className="w-2 rounded-t"
          style={{ background: color }}
          animate={{
            height: [`${h}%`, `${h + 10}%`, `${h - 5}%`, `${h}%`],
          }}
          transition={{
            duration: 1 + i * 0.1,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  )
}

function PlatformLink({ name, url, color }) {
  return (
    <a
      href={url || '#'}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 px-3 py-2 rounded transition-all"
      style={{
        background: `${color}11`,
        border: `1px solid ${color}33`,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = `${color}22`
        e.currentTarget.style.borderColor = `${color}66`
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = `${color}11`
        e.currentTarget.style.borderColor = `${color}33`
      }}
    >
      <Globe size={12} style={{ color }} />
      <span className="text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color }}>
        {name}
      </span>
      <ExternalLink size={10} style={{ color, marginLeft: 'auto' }} />
    </a>
  )
}

export default function AgentDetailPanel({ agent, onClose, onBack }) {
  const [realData, setRealData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastFetch, setLastFetch] = useState(null)

  useEffect(() => {
    if (!agent) return

    setLoading(true)
    const controller = new AbortController()

    fetch(`/api/monetization/agent/${agent.id}`, { signal: controller.signal })
      .then(r => r.json())
      .then(data => {
        setRealData(data)
        setLastFetch(new Date())
        setLoading(false)
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          console.error('Monetization fetch error:', err)
          setLoading(false)
        }
      })

    return () => controller.abort()
  }, [agent])

  if (!agent) return null

  const displayData = realData || agent
  const revenue = displayData.total_revenue || displayData.revenue || 0
  const platforms = displayData.platforms || []
  const stats = displayData.stats || {}
  const color = agent.color || '#00d9ff'

  const revenueFormatted = typeof revenue === 'number'
    ? revenue.toLocaleString('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 })
    : revenue

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: 420, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 420, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="fixed right-4 top-1/2 -translate-y-1/2 z-50 w-80 max-h-[85vh] overflow-y-auto"
      >
        <div
          className="relative"
          style={{
            background: 'rgba(5,10,20,0.98)',
            border: `1px solid ${color}`,
            boxShadow: `0 0 40px ${color}55, 0 0 80px ${color}22`,
          }}
        >
          <div
            className="h-1 w-full"
            style={{
              background: `linear-gradient(90deg, ${color}, transparent)`,
              boxShadow: `0 0 20px ${color}`,
            }}
          />

          <div className="p-4">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2
                  className="text-lg font-bold tracking-widest"
                  style={{
                    fontFamily: 'Orbitron, monospace',
                    color,
                    textShadow: `0 0 15px ${color}88`,
                  }}
                >
                  {(displayData.name || agent.name).toUpperCase()}
                </h2>
                <p
                  className="text-xs mt-1"
                  style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}
                >
                  {displayData.role || agent.role}
                </p>
                {lastFetch && (
                  <p className="text-xs mt-0.5" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#666688' }}>
                    Updated: {lastFetch.toLocaleTimeString()}
                  </p>
                )}
              </div>
              <div className="flex gap-1">
                {onBack && (
                  <button
                    onClick={onBack}
                    className="w-8 h-8 flex items-center justify-center rounded transition-all"
                    style={{
                      background: 'transparent',
                      border: '1px solid #00d9ff55',
                      color: '#00d9ff',
                    }}
                    title="Back to city"
                  >
                    ←
                  </button>
                )}
                <button
                  onClick={onClose}
                  className="w-8 h-8 flex items-center justify-center rounded transition-all"
                  style={{
                    background: 'transparent',
                    border: '1px solid #ff004455',
                    color: '#ff0044',
                  }}
                >
                  <X size={14} />
                </button>
              </div>
            </div>

            <div
              className="h-px w-full mb-4"
              style={{ background: `linear-gradient(90deg, ${color}66, transparent)` }}
            />

            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign size={14} style={{ color: '#00ff88' }} />
                <span className="text-xs tracking-widest" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#00ff88' }}>
                  REVENUE LUNAR
                </span>
              </div>
              <div
                className="text-3xl font-bold"
                style={{
                  fontFamily: 'Orbitron, monospace',
                  color: '#00ff88',
                  textShadow: '0 0 20px rgba(0,255,136,0.5)',
                }}
              >
                {loading ? <Loader size={20} className="animate-spin" style={{ color: '#00ff88' }} /> : revenueFormatted}
              </div>
              <p className="text-xs mt-1" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#666688' }}>
                DATE REALE DIN CONTURI
              </p>
            </div>

            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <Activity size={14} style={{ color: color }} />
                <span className="text-xs tracking-widest" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
                  WORKING: {(agent.workType || 'earning').toUpperCase()}
                </span>
              </div>
              <WorkAnimation type={agent.workType} color={color} />
            </div>

            {Object.keys(stats).length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp size={14} style={{ color: '#00d9ff' }} />
                  <span className="text-xs tracking-widest" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
                    STATISTICI PLATFORME
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(stats).slice(0, 6).map(([key, valueObj]) => {
                    const val = typeof valueObj === 'object' ? valueObj.value : valueObj
                    const label = key.replace(/_/g, ' ').toUpperCase()
                    return (
                      <div key={key} className="p-2 rounded" style={{ background: `${color}11`, border: `1px solid ${color}33` }}>
                        <div className="text-xs truncate" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#666688', fontSize: '0.6rem' }}>
                          {label}
                        </div>
                        <div className="text-sm font-bold" style={{ fontFamily: 'Orbitron, monospace', color }}>
                          {typeof val === 'number' ? val.toLocaleString() : val}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {platforms.length > 0 && (
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Globe size={14} style={{ color: '#00d9ff' }} />
                  <span className="text-xs tracking-widest" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
                    PLATFORME ({platforms.length})
                  </span>
                </div>
                <div className="grid grid-cols-1 gap-1">
                  {platforms.map((platform) => (
                    <PlatformLink
                      key={platform.name}
                      name={platform.name}
                      color={color}
                      url={platform.url}
                    />
                  ))}
                </div>
              </div>
            )}

            <div className="mb-4">
              <div className="flex items-center gap-2 mb-2">
                <Users size={14} style={{ color: '#8b00ff' }} />
                <span className="text-xs tracking-widest" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
                  AGENT ID
                </span>
              </div>
              <div
                className="px-2 py-1 text-xs rounded"
                style={{
                  fontFamily: 'Share Tech Mono, monospace',
                  color: '#8b00ff',
                  background: 'rgba(139,0,255,0.1)',
                  border: '1px solid rgba(139,0,255,0.3)',
                }}
              >
                {agent.id?.toUpperCase().replace(/_/g, '-')}
              </div>
            </div>

            <div
              className="h-px w-full mb-4"
              style={{ background: `${color}33` }}
            />

            <div className="flex gap-2">
              {['Refresh', 'History', 'Tasks', 'Export'].map((action) => (
                <button
                  key={action}
                  className="flex-1 py-2 text-xs tracking-wider transition-all rounded"
                  style={{
                    fontFamily: 'Orbitron, monospace',
                    fontSize: '0.6rem',
                    color: action === 'Refresh' ? '#00ff88' : '#8890bb',
                    background: action === 'Refresh' ? '#00ff8811' : 'transparent',
                    border: `1px solid ${action === 'Refresh' ? '#00ff8866' : '#8890bb33'}`,
                    cursor: 'pointer',
                  }}
                  onClick={() => {
                    if (action === 'Refresh') {
                      setLoading(true)
                      fetch(`/api/monetization/fetch`, { method: 'POST' })
                        .then(r => r.json())
                        .then(() => {
                          return fetch(`/api/monetization/agent/${agent.id}`)
                        })
                        .then(r => r.json())
                        .then(data => {
                          setRealData(data)
                          setLastFetch(new Date())
                          setLoading(false)
                        })
                        .catch(() => setLoading(false))
                    }
                  }}
                >
                  {action === 'Refresh' ? '↻ REFRESH' : action.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div
            className="absolute bottom-0 left-0 right-0 h-0.5"
            style={{
              background: `linear-gradient(90deg, transparent, ${color}88, transparent)`,
            }}
          />
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
