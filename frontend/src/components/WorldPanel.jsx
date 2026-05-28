import React, { useState, useCallback } from 'react'
import { Canvas } from '@react-three/fiber'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import { motion, AnimatePresence } from 'framer-motion'
import { Gamepad2, X, MapPin, TrendingUp, DollarSign, Radio } from 'lucide-react'
import AgentWorld from './AgentWorld'
import AgentDetailPanel from './AgentDetailPanel'

function WorldHUD({ agentCount, totalRevenue, onClose }) {
  return (
    <>
      <div
        className="absolute top-4 left-4 z-50 px-4 py-3"
        style={{
          background: 'rgba(5,10,20,0.95)',
          border: '1px solid #ff0044',
          boxShadow: '0 0 30px rgba(255,0,68,0.3)',
        }}
      >
        <div className="flex items-center gap-3">
          <Gamepad2 size={20} style={{ color: '#ff0044' }} />
          <div>
            <div
              className="text-sm font-bold tracking-widest"
              style={{ fontFamily: 'Orbitron, monospace', color: '#ff0044' }}
            >
              JARVIS CITY SIM
            </div>
            <div
              className="text-xs"
              style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}
            >
              GTA6-STYLE AGENT SIMULATION
            </div>
          </div>
        </div>
      </div>

      <div
        className="absolute top-4 right-4 z-50 px-4 py-3"
        style={{
          background: 'rgba(5,10,20,0.95)',
          border: '1px solid #00ff88',
          boxShadow: '0 0 20px rgba(0,255,136,0.2)',
        }}
      >
        <div className="grid grid-cols-2 gap-x-6 gap-y-1">
          <div className="flex items-center gap-2">
            <Radio size={12} style={{ color: '#00d9ff' }} />
            <span className="text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
              AGENTS
            </span>
          </div>
          <div
            className="text-xs font-bold"
            style={{ fontFamily: 'Orbitron, monospace', color: '#00d9ff' }}
          >
            {agentCount}
          </div>

          <div className="flex items-center gap-2">
            <DollarSign size={12} style={{ color: '#00ff88' }} />
            <span className="text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
              REVENUE
            </span>
          </div>
          <div
            className="text-xs font-bold"
            style={{ fontFamily: 'Orbitron, monospace', color: '#00ff88' }}
          >
            ${(totalRevenue / 1000).toFixed(0)}K
          </div>
        </div>
      </div>

      <div
        className="absolute bottom-4 left-4 z-50 px-4 py-3"
        style={{
          background: 'rgba(5,10,20,0.9)',
          border: '1px solid #00d9ff33',
        }}
      >
        <div className="text-xs mb-1" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
          CONTROLS
        </div>
        <div className="flex gap-4 text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#666688' }}>
          <span>CLICK agent to select</span>
          <span>CLICK zone to zoom</span>
          <span>SCROLL to zoom</span>
        </div>
      </div>

      <button
        onClick={onClose}
        className="absolute top-4 left-1/2 -translate-x-1/2 z-50 px-6 py-2 flex items-center gap-2 transition-all"
        style={{
          background: 'rgba(10,10,20,0.95)',
          border: '1px solid #ff0044',
          boxShadow: '0 0 20px rgba(255,0,68,0.3)',
          color: '#ff0044',
          fontFamily: 'Orbitron, monospace',
          fontSize: '0.7rem',
          letterSpacing: '0.1em',
        }}
      >
        <X size={14} />
        EXIT SIMULATION
      </button>
    </>
  )
}

export default function WorldPanel({ onClose }) {
  const [selectedAgent, setSelectedAgent] = useState(null)

  const handleAgentSelect = useCallback((agent) => {
    setSelectedAgent(agent)
  }, [])

  const handleClose = useCallback(() => {
    setSelectedAgent(null)
    if (onClose) onClose()
  }, [onClose])

  const agentCount = 13
  const totalRevenue = 382500

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="absolute inset-0 z-40"
      style={{ background: '#020408' }}
    >
      <Canvas
        camera={{ position: [0, 120, 150], fov: 60 }}
        gl={{ powerPreference: 'high-performance', antialias: true, alpha: false }}
        style={{ background: '#020408' }}
      >
        <AgentWorld onAgentSelect={handleAgentSelect} selectedAgent={selectedAgent} />
        <EffectComposer>
          <Bloom luminanceThreshold={0.1} intensity={0.6} radius={0.8} />
        </EffectComposer>
      </Canvas>

      <WorldHUD
        agentCount={agentCount}
        totalRevenue={totalRevenue}
        onClose={handleClose}
      />

      <AnimatePresence>
        {selectedAgent && (
          <AgentDetailPanel
            agent={selectedAgent}
            onClose={() => setSelectedAgent(null)}
            onBack={() => setSelectedAgent(null)}
          />
        )}
      </AnimatePresence>

      <div
        className="absolute bottom-4 right-4 z-50 px-3 py-2"
        style={{
          background: 'rgba(0,255,136,0.1)',
          border: '1px solid rgba(0,255,136,0.4)',
        }}
      >
        <span
          className="text-xs"
          style={{ fontFamily: 'Share Tech Mono, monospace', color: '#00ff88' }}
        >
          ● {selectedAgent ? `TRACKING: ${selectedAgent.name.toUpperCase()}` : 'SIMULATION ACTIVE'}
        </span>
      </div>
    </motion.div>
  )
}
