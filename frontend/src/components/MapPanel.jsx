import React, { useState, useCallback, useEffect, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import { motion, AnimatePresence } from 'framer-motion'
import { Map, X, Navigation, ZoomIn, ZoomOut, RotateCcw, Eye, EyeOff, Play, Pause } from 'lucide-react'
import AgentMap3D, { NEIGHBORHOODS } from './AgentMap3D'

function MapOverlay({ neighborhood, onClose, onBack }) {
  if (!neighborhood) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="absolute top-4 left-1/2 -translate-x-1/2 z-50"
    >
      <div
        className="relative px-6 py-3"
        style={{
          background: 'rgba(10,10,20,0.95)',
          border: `1px solid ${neighborhood.color}`,
          boxShadow: `0 0 30px ${neighborhood.color}55, inset 0 0 20px ${neighborhood.color}11`,
          clipPath: 'polygon(8px 0, calc(100% - 8px) 0, 100% 50%, calc(100% - 8px) 100%, 8px 100%, 0 50%)',
        }}
      >
        <div
          className="h-0.5 w-full absolute top-0 left-0"
          style={{ background: `linear-gradient(90deg, transparent, ${neighborhood.color}, transparent)` }}
        />
        <div className="flex items-center gap-4">
          <div
            className="w-10 h-10 flex items-center justify-center"
            style={{
              background: `${neighborhood.color}22`,
              border: `1px solid ${neighborhood.color}66`,
              boxShadow: `0 0 15px ${neighborhood.color}44`,
            }}
          >
            <Navigation size={20} style={{ color: neighborhood.color }} />
          </div>
          <div>
            <h3
              className="text-sm font-bold tracking-widest"
              style={{
                fontFamily: 'Orbitron, monospace',
                color: neighborhood.color,
                textShadow: `0 0 8px ${neighborhood.color}88`,
              }}
            >
              {neighborhood.name}
            </h3>
            <p
              className="text-xs"
              style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}
            >
              SECTOR: {neighborhood.id.toUpperCase()} // AGENTS: {neighborhood.agents.length}
            </p>
          </div>
          <div className="flex items-center gap-2 ml-4">
            <button
              onClick={onBack}
              className="w-8 h-8 flex items-center justify-center transition-all"
              style={{
                color: '#00d9ff',
                border: '1px solid #00d9ff55',
                background: 'transparent',
              }}
              title="Back to overview"
            >
              <RotateCcw size={14} />
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center transition-all"
              style={{
                color: '#ff0044',
                border: '1px solid #ff004455',
                background: 'transparent',
              }}
              title="Close map"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function DistrictInfo({ neighborhood }) {
  if (!neighborhood) return null

  return (
    <motion.div
      initial={{ x: 320, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 320, opacity: 0 }}
      className="absolute right-4 top-1/2 -translate-y-1/2 z-40 w-72"
    >
      <div
        className="relative"
        style={{
          background: 'rgba(10,10,20,0.97)',
          border: `1px solid ${neighborhood.color}`,
          boxShadow: `0 0 30px ${neighborhood.color}55`,
        }}
      >
        <div
          className="h-1"
          style={{ background: `linear-gradient(90deg, ${neighborhood.color}, transparent)` }}
        />
        <div className="p-4">
          <h3
            className="text-sm font-bold tracking-widest mb-3"
            style={{ fontFamily: 'Orbitron, monospace', color: neighborhood.color }}
          >
            {neighborhood.name}
          </h3>

          <div className="space-y-2 mb-4">
            {[
              { label: 'SECTOR', value: neighborhood.id.toUpperCase() },
              { label: 'RADIUS', value: `${neighborhood.size}m` },
              { label: 'AGENTS', value: neighborhood.agents.length },
              { label: 'STATUS', value: 'ACTIVE' },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center justify-between">
                <span className="text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
                  {label}
                </span>
                <span className="text-xs font-bold" style={{ fontFamily: 'Share Tech Mono, monospace', color: neighborhood.color }}>
                  {value}
                </span>
              </div>
            ))}
          </div>

          <div className="h-px w-full mb-3" style={{ background: `${neighborhood.color}44` }} />

          <div>
            <span className="text-xs tracking-widest mb-2 block" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
              ASSIGNED AGENTS
            </span>
            <div className="space-y-1">
              {neighborhood.agents.map((agentId) => (
                <div
                  key={agentId}
                  className="px-2 py-1 text-xs"
                  style={{
                    fontFamily: 'Share Tech Mono, monospace',
                    color: neighborhood.color,
                    background: `${neighborhood.color}11`,
                    borderLeft: `2px solid ${neighborhood.color}`,
                  }}
                >
                  {agentId.replace('_', ' ').toUpperCase()}
                </div>
              ))}
            </div>
          </div>

          <div className="h-px w-full my-3" style={{ background: `${neighborhood.color}44` }} />

          <div className="grid grid-cols-2 gap-2">
            {['View Stats', 'Task Log', 'History', 'Export'].map((action) => (
              <button
                key={action}
                className="py-1.5 text-xs tracking-wider transition-all"
                style={{
                  fontFamily: 'Orbitron, monospace',
                  fontSize: '0.55rem',
                  color: '#8890bb',
                  border: '1px solid #8890bb33',
                  background: 'transparent',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.color = neighborhood.color
                  e.currentTarget.style.borderColor = `${neighborhood.color}66`
                  e.currentTarget.style.background = `${neighborhood.color}11`
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.color = '#8890bb'
                  e.currentTarget.style.borderColor = '#8890bb33'
                  e.currentTarget.style.background = 'transparent'
                }}
              >
                {action.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function MiniMapLegend() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="absolute bottom-4 left-4 z-40"
    >
      <div
        className="p-3"
        style={{
          background: 'rgba(10,10,20,0.9)',
          border: '1px solid #00d9ff33',
        }}
      >
        <div className="text-xs tracking-widest mb-2" style={{ fontFamily: 'Orbitron, monospace', color: '#00d9ff' }}>
          SECTOR LEGEND
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
          {NEIGHBORHOODS.slice(0, 8).map((nh) => (
            <div key={nh.id} className="flex items-center gap-1.5">
              <div className="w-2 h-2 rounded-full" style={{ background: nh.color, boxShadow: `0 0 4px ${nh.color}` }} />
              <span className="text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb', fontSize: '0.6rem' }}>
                {nh.name.split(' ')[0]}
              </span>
            </div>
          ))}
        </div>
        <div className="h-px w-full my-2" style={{ background: '#00d9ff22' }} />
        <div className="flex items-center gap-2 text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
          <div className="w-3 h-3 rounded" style={{ background: '#00ff8844', border: '1px solid #00ff88' }} />
          <span style={{ fontSize: '0.55rem' }}>AGRIDROBOT</span>
          <div className="w-3 h-3 rounded-full ml-2" style={{ background: '#00ffff44', border: '1px solid #00ffff' }} />
          <span style={{ fontSize: '0.55rem' }}>PERSONNEL</span>
        </div>
      </div>
    </motion.div>
  )
}

export default function MapPanel({ onClose, selectedAgent }) {
  const [activeNeighborhood, setActiveNeighborhood] = useState(null)
  const [isPlaying, setIsPlaying] = useState(true)
  const [showLabels, setShowLabels] = useState(true)
  const [cameraMode, setCameraMode] = useState('auto')

  useEffect(() => {
    if (selectedAgent) {
      const agentNeighborhood = NEIGHBORHOODS.find(nh => nh.agents.includes(selectedAgent.id))
      if (agentNeighborhood) {
        setActiveNeighborhood(agentNeighborhood)
      } else {
        setActiveNeighborhood(NEIGHBORHOODS[0])
      }
    }
  }, [selectedAgent])

  const handleNeighborhoodSelect = useCallback((nh) => {
    setActiveNeighborhood(nh)
  }, [])

  const handleBack = useCallback(() => {
    setActiveNeighborhood(null)
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="absolute inset-0 z-30"
    >
      <Canvas
        camera={{ position: [0, 60, 80], fov: 55 }}
        gl={{ powerPreference: 'high-performance', antialias: true, alpha: false }}
        style={{ background: '#030308' }}
      >
        <AgentMap3D
          onNeighborhoodSelect={handleNeighborhoodSelect}
          selectedAgent={null}
          onAgentClick={() => {}}
        />
        <EffectComposer>
          <Bloom luminanceThreshold={0.05} intensity={0.8} radius={0.8} />
        </EffectComposer>
      </Canvas>

      <MapOverlay
        neighborhood={activeNeighborhood}
        onClose={onClose}
        onBack={handleBack}
      />

      <AnimatePresence>
        {activeNeighborhood && <DistrictInfo key="district" neighborhood={activeNeighborhood} />}
      </AnimatePresence>

      <MiniMapLegend />

      <div className="absolute bottom-4 right-4 z-40 flex flex-col gap-2">
        <button
          onClick={() => setCameraMode(m => m === 'auto' ? 'manual' : 'auto')}
          className="w-10 h-10 flex items-center justify-center transition-all"
          style={{
            background: 'rgba(10,10,20,0.9)',
            border: '1px solid #00d9ff55',
            color: '#00d9ff',
          }}
          title="Camera mode"
        >
          <Eye size={16} />
        </button>
        <button
          onClick={() => setShowLabels(l => !l)}
          className="w-10 h-10 flex items-center justify-center transition-all"
          style={{
            background: 'rgba(10,10,20,0.9)',
            border: '1px solid #00d9ff55',
            color: showLabels ? '#00ff88' : '#8890bb',
          }}
          title="Toggle labels"
        >
          {showLabels ? <Eye size={16} /> : <EyeOff size={16} />}
        </button>
        <button
          onClick={() => setIsPlaying(p => !p)}
          className="w-10 h-10 flex items-center justify-center transition-all"
          style={{
            background: 'rgba(10,10,20,0.9)',
            border: '1px solid #00d9ff55',
            color: isPlaying ? '#00ff88' : '#ff6600',
          }}
          title={isPlaying ? 'Pause simulation' : 'Resume simulation'}
        >
          {isPlaying ? <Pause size={16} /> : <Play size={16} />}
        </button>
      </div>

      <div
        className="absolute top-4 right-4 z-40 px-3 py-1.5"
        style={{
          background: 'rgba(10,10,20,0.9)',
          border: '1px solid #00d9ff33',
        }}
      >
        <span className="text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#00d9ff' }}>
          CITY OVERVIEW // {NEIGHBORHOODS.length} SECTORS ACTIVE
        </span>
      </div>

      <div
        className="absolute top-4 left-4 z-40 flex items-center gap-2 px-3 py-2"
        style={{
          background: 'rgba(10,10,20,0.95)',
          border: '1px solid #ff004455',
        }}
      >
        <Map size={14} style={{ color: '#ff0044' }} />
        <span className="text-xs font-bold tracking-widest" style={{ fontFamily: 'Orbitron, monospace', color: '#ff0044' }}>
          FULL-SCREEN MAP MODE
        </span>
      </div>

      <div
        className="absolute bottom-4 right-4 z-40 px-3 py-1.5"
        style={{
          background: 'rgba(10,10,20,0.9)',
          border: '1px solid #00ff8844',
        }}
      >
        <span className="text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#00ff88' }}>
          {isPlaying ? '● SIMULATION ACTIVE' : '○ SIMULATION PAUSED'}
        </span>
      </div>
    </motion.div>
  )
}
