import React, { useState, useCallback, useEffect, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { EffectComposer, Bloom, ChromaticAberration } from '@react-three/postprocessing'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutGrid, Users, Terminal, Activity, MessageSquare,
  Volume2, Mic, Shield, Zap, X, ChevronRight, Radio,
  Cpu, Database, Eye, Bug, Code, Palette, Rocket,
  AlertTriangle, Wifi, Map, Gamepad2
} from 'lucide-react'
import JarvisScene, { AGENT_POSITIONS } from './components/JarvisScene'
import Dashboard from './components/Dashboard'
import AgentRoster from './components/AgentRoster'
import TerminalPanel from './components/TerminalPanel'
import TaskBoard from './components/TaskBoard'
import CommsPanel from './components/CommsPanel'
import WorldPanel from './components/WorldPanel'
import WorldMapCyberpunk from './components/WorldMapCyberpunk'
import VoiceIndicator from './components/VoiceIndicator'

const NAV_ITEMS = [
  { id: 'dashboard', icon: LayoutGrid, label: 'Dashboard' },
  { id: 'roster', icon: Users, label: 'Agent Roster' },
  { id: 'terminal', icon: Terminal, label: 'Terminal' },
  { id: 'tasks', icon: Activity, label: 'Task Board' },
  { id: 'comms', icon: MessageSquare, label: 'Comms' },
  { id: 'simulation', icon: Gamepad2, label: 'GTA6 Sim' },
]

const AGENT_ICONS = {
  Shield, Cpu, Database, Eye, Bug, Code, Palette, Rocket, AlertTriangle, Wifi, Zap,
}

function AgentInfoPanel({ agent, onClose }) {
  if (!agent) return null
  const Icon = AGENT_ICONS[agent.icon] || Cpu
  return (
    <motion.div
      initial={{ x: -320, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -320, opacity: 0 }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed left-4 top-1/2 -translate-y-1/2 z-50 w-72"
    >
      <div
        className="relative"
        style={{
          background: 'rgba(10,10,20,0.97)',
          border: `1px solid ${agent.color}`,
          boxShadow: `0 0 30px ${agent.color}55, 0 0 60px ${agent.color}22, inset 0 0 20px ${agent.color}11`,
          clipPath: 'polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 16px 100%, 0 calc(100% - 16px))',
        }}
      >
        <div
          className="h-1"
          style={{
            background: `linear-gradient(90deg, transparent, ${agent.color}, transparent)`,
            boxShadow: `0 0 12px ${agent.color}`,
          }}
        />
        <div className="p-5">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div
                className="w-12 h-12 flex items-center justify-center"
                style={{
                  background: `${agent.color}18`,
                  border: `1px solid ${agent.color}66`,
                  boxShadow: `0 0 15px ${agent.color}44`,
                }}
              >
                <Icon size={22} style={{ color: agent.color }} />
              </div>
              <div>
                <h3
                  className="text-sm font-bold tracking-wider"
                  style={{
                    fontFamily: 'Orbitron, monospace',
                    color: agent.color,
                    textShadow: `0 0 8px ${agent.color}88`,
                  }}
                >
                  {agent.name.toUpperCase()}
                </h3>
                <p
                  className="text-xs mt-0.5"
                  style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}
                >
                  {agent.role}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-7 h-7 flex items-center justify-center transition-colors"
              style={{
                color: '#8890bb',
                border: '1px solid #8890bb44',
                background: 'transparent',
              }}
              onMouseEnter={e => { e.currentTarget.style.color = '#ff0044'; e.currentTarget.style.borderColor = '#ff0044' }}
              onMouseLeave={e => { e.currentTarget.style.color = '#8890bb'; e.currentTarget.style.borderColor = '#8890bb44' }}
            >
              <X size={14} />
            </button>
          </div>

          <div
            className="h-px w-full mb-4"
            style={{ background: `linear-gradient(90deg, ${agent.color}66, transparent)` }}
          />

          <div className="space-y-3">
            {[
              { label: 'STATUS', value: 'ONLINE' },
              { label: 'TIER', value: `T${agent.tier || 0}` },
              { label: 'NODE ID', value: agent.id },
              { label: 'COLOR', value: agent.color },
            ].map(({ label, value }) => (
              <div key={label} className="flex items-center justify-between">
                <span
                  className="text-xs tracking-widest"
                  style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}
                >
                  {label}
                </span>
                <span
                  className="text-xs font-bold"
                  style={{ fontFamily: 'Share Tech Mono, monospace', color: agent.color }}
                >
                  {value}
                </span>
              </div>
            ))}
          </div>

          <div
            className="h-px w-full mt-4 mb-3"
            style={{ background: `linear-gradient(90deg, transparent, ${agent.color}44)` }}
          />

          <div className="flex gap-2">
            {['SIM', 'Stats', 'Money'].map((action, i) => (
              <button
                key={action}
                className="flex-1 py-1.5 text-xs tracking-widest transition-all"
                style={{
                  fontFamily: 'Orbitron, monospace',
                  fontSize: '0.6rem',
                  color: i === 0 ? '#00ff88' : '#8890bb',
                  border: `1px solid ${i === 0 ? '#00ff8888' : '#8890bb33'}`,
                  background: i === 0 ? '#00ff8811' : 'transparent',
                  cursor: 'pointer',
                }}
                onClick={() => {
                  if (i === 0) {
                    setActivePanel('simulation')
                  }
                }}
                onMouseEnter={e => {
                  if (i !== 0) {
                    e.currentTarget.style.color = '#00d9ff'
                    e.currentTarget.style.borderColor = '#00d9ff44'
                  }
                }}
                onMouseLeave={e => {
                  if (i !== 0) {
                    e.currentTarget.style.color = '#8890bb'
                    e.currentTarget.style.borderColor = '#8890bb33'
                  }
                }}
              >
                {action.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        <div
          className="absolute bottom-0 left-0 right-0 h-0.5"
          style={{
            background: `linear-gradient(90deg, transparent, ${agent.color}88, transparent)`,
          }}
        />
      </div>
    </motion.div>
  )
}

function App() {
  const [activePanel, setActivePanel] = useState('dashboard')
  const [voiceEnabled, setVoiceEnabled] = useState(false)
  const [systemStatus, setSystemStatus] = useState('booting')
  const [fps, setFps] = useState(60)
  const [webglOk, setWebglOk] = useState(true)
  const [mouse, setMouse] = useState({ x: 0, y: 0 })
  const [voiceStatus, setVoiceStatus] = useState('listening')
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [hoveredAgent, setHoveredAgent] = useState(null)
  const fpsRef = useRef(0)
  const lastFpsRef = useRef(performance.now())
  const rafRef = useRef(null)

  useEffect(() => {
    const webgl = document.createElement('canvas')
    const gl = webgl.getContext('webgl2') || webgl.getContext('webgl')
    setWebglOk(!!gl)

    const tick = () => {
      const now = performance.now()
      fpsRef.current++
      if (now - lastFpsRef.current >= 1000) {
        setFps(fpsRef.current)
        fpsRef.current = 0
        lastFpsRef.current = now
      }
      rafRef.current = requestAnimationFrame(tick)
    }
    rafRef.current = requestAnimationFrame(tick)
    const bootTimer = setTimeout(() => setSystemStatus('online'), 2000)

    const voicePoll = setInterval(() => {
      fetch('/api/voice/status')
        .then(r => r.json())
        .then(data => {
          if (data.speaking) {
            setVoiceStatus('speaking')
          } else {
            setVoiceStatus('listening')
          }
        })
        .catch(() => setVoiceStatus('idle'))
    }, 500)

    return () => {
      clearTimeout(bootTimer)
      clearInterval(voicePoll)
      cancelAnimationFrame(rafRef.current)
    }
  }, [])

  const handleMouseMove = useCallback((e) => {
    const x = (e.clientX / window.innerWidth) * 2 - 1
    const y = -(e.clientY / window.innerHeight) * 2 + 1
    setMouse({ x, y })
  }, [])

  const handleAgentHover = useCallback((agent) => {
    setHoveredAgent(agent)
  }, [])

  const handleAgentClick = useCallback((agent) => {
    setSelectedAgent(prev => prev?.id === agent.id ? null : agent)
    setActivePanel('simulation')
  }, [])

  const toggleVoice = () => setVoiceEnabled(v => !v)

  return (
    <div
      className="h-screen w-screen overflow-hidden relative"
      style={{ background: '#030308' }}
      onMouseMove={handleMouseMove}
    >
      {webglOk && activePanel !== 'simulation' && (
        <Canvas
          className="absolute inset-0 z-0"
          gl={{ powerPreference: 'high-performance', antialias: false, alpha: true }}
          camera={{ position: [0, 0, 50], fov: 55 }}
        >
          <JarvisScene
            onAgentHover={handleAgentHover}
            onAgentClick={handleAgentClick}
            selectedAgent={selectedAgent}
            hoveredAgent={hoveredAgent}
            mouse={mouse}
          />
          <EffectComposer>
            <Bloom luminanceThreshold={0.08} intensity={0.65} radius={0.7} />
            <ChromaticAberration offset={[0.00035, 0.00035]} />
          </EffectComposer>
        </Canvas>
      )}

      <VoiceIndicator status={voiceStatus} />

      <AgentInfoPanel agent={selectedAgent} onClose={() => setSelectedAgent(null)} />

      <div className="relative z-10 h-full flex flex-col">

        <header
          className="h-16 flex items-center justify-between px-6 shrink-0"
          style={{
            background: 'linear-gradient(180deg, rgba(10,10,20,0.98) 0%, rgba(10,10,20,0.9) 100%)',
            borderBottom: '1px solid rgba(0,217,255,0.25)',
            boxShadow: '0 0 40px rgba(0,217,255,0.12), 0 4px 20px rgba(0,0,0,0.8)',
          }}
        >
          <div className="flex items-center gap-4">
            <div
              className="relative w-10 h-10 flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, #00d9ff15, #8b00ff15)',
                border: '1px solid #00d9ff',
                boxShadow: '0 0 20px rgba(0,217,255,0.5), inset 0 0 12px rgba(0,217,255,0.1)',
              }}
            >
              <Radio size={20} style={{ color: '#00d9ff', filter: 'drop-shadow(0 0 6px #00d9ff)' }} />
              <div
                className="absolute inset-0 rounded"
                style={{ animation: 'node-ping 2s ease-in-out infinite' }}
              />
            </div>
            <div>
              <h1
                className="text-2xl font-bold tracking-widest"
                style={{
                  fontFamily: 'Orbitron, monospace',
                  color: '#00d9ff',
                  textShadow: '0 0 10px rgba(0,217,255,0.8), 0 0 20px rgba(0,217,255,0.4)',
                  letterSpacing: '0.2em',
                }}
              >
                JARVIS
              </h1>
              <div className="flex items-center gap-2">
                <span
                  className="text-xs tracking-widest"
                  style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}
                >
                  {systemStatus === 'booting' ? 'INITIALIZING...' : 'OPERATIONAL'}
                </span>
                <span
                  className="text-xs px-2 py-0.5"
                  style={{
                    fontFamily: 'Share Tech Mono, monospace',
                    color: '#00ff88',
                    background: 'rgba(0,255,136,0.1)',
                    border: '1px solid rgba(0,255,136,0.3)',
                  }}
                >
                  {fps} FPS
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              {[...Array(7)].map((_, i) => (
                <div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full"
                  style={{
                    background: i % 2 === 0 ? '#00d9ff' : '#ff00aa',
                    boxShadow: `0 0 6px ${i % 2 === 0 ? 'rgba(0,217,255,0.8)' : 'rgba(255,0,170,0.8)'}`,
                    animation: `neon-pulse ${1.5 + i * 0.2}s ease-in-out infinite`,
                    animationDelay: `${i * 100}ms`,
                  }}
                />
              ))}
            </div>

            <button
              onClick={toggleVoice}
              className="relative w-10 h-10 flex items-center justify-center transition-all duration-300"
              style={{
                background: voiceEnabled ? 'rgba(0,255,136,0.15)' : 'transparent',
                border: `1px solid ${voiceEnabled ? '#00ff88' : '#00d9ff'}`,
                boxShadow: voiceEnabled ? '0 0 20px rgba(0,255,136,0.4)' : '0 0 10px rgba(0,217,255,0.3)',
              }}
              aria-label={voiceEnabled ? 'Voice on' : 'Voice off'}
            >
              {voiceEnabled
                ? <Mic size={18} style={{ color: '#00ff88', filter: 'drop-shadow(0 0 6px #00ff88)' }} />
                : <Volume2 size={18} style={{ color: '#00d9ff' }} />
              }
              {voiceEnabled && (
                <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-green-400 animate-pulse" />
              )}
            </button>

            <div
              className="px-3 py-1.5 flex items-center gap-2"
              style={{
                background: 'rgba(255,0,68,0.1)',
                border: '1px solid rgba(255,0,68,0.4)',
                boxShadow: '0 0 10px rgba(255,0,68,0.2)',
              }}
            >
              <Shield size={14} style={{ color: '#ff0044' }} />
              <span
                className="text-xs font-bold tracking-widest"
                style={{ fontFamily: 'Orbitron, monospace', color: '#ff0044' }}
              >
                ADMIN
              </span>
            </div>
          </div>
        </header>

        <nav
          className="h-12 flex items-center justify-center gap-1 shrink-0"
          style={{
            background: 'rgba(10,10,20,0.95)',
            borderBottom: '1px solid rgba(0,217,255,0.12)',
          }}
        >
          {NAV_ITEMS.map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => setActivePanel(id)}
              className="relative flex items-center gap-2 px-5 py-2 transition-all duration-300"
              style={{
                fontFamily: 'Orbitron, monospace',
                fontSize: '0.7rem',
                letterSpacing: '0.1em',
                fontWeight: 600,
                color: activePanel === id ? '#00d9ff' : '#8890bb',
                background: activePanel === id ? 'rgba(0,217,255,0.1)' : 'transparent',
                border: activePanel === id ? '1px solid rgba(0,217,255,0.4)' : '1px solid transparent',
                clipPath: 'polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)',
                textTransform: 'uppercase',
                boxShadow: activePanel === id ? '0 0 15px rgba(0,217,255,0.2), inset 0 0 10px rgba(0,217,255,0.05)' : 'none',
              }}
            >
              {activePanel === id && (
                <div
                  className="absolute inset-0 opacity-20"
                  style={{
                    background: 'linear-gradient(90deg, transparent, rgba(0,217,255,0.3), transparent)',
                    animation: 'sweep-line 3s ease-in-out infinite',
                  }}
                />
              )}
              <Icon size={14} />
              <span>{label}</span>
              {activePanel === id && (
                <div
                  className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5"
                  style={{ background: '#00d9ff', boxShadow: '0 0 8px #00d9ff', borderRadius: '1px' }}
                />
              )}
            </button>
          ))}
        </nav>

        <main className="flex-1 p-4 overflow-hidden" style={{ position: 'relative' }}>
          <AnimatePresence mode="wait">
            {activePanel === 'dashboard' && <Dashboard key="dashboard" agents={AGENT_POSITIONS} />}
            {activePanel === 'roster' && <AgentRoster key="roster" agents={AGENT_POSITIONS} />}
            {activePanel === 'terminal' && <TerminalPanel key="terminal" onCommand={() => {}} />}
            {activePanel === 'tasks' && <TaskBoard key="tasks" />}
            {activePanel === 'comms' && <CommsPanel key="comms" />}
          </AnimatePresence>
        </main>

        {activePanel === 'simulation' && (
          <div className="absolute inset-0 z-40" style={{ background: '#020408' }}>
            <WorldPanel onClose={() => setActivePanel('dashboard')} />
          </div>
        )}

        <footer
          className="h-8 flex items-center justify-between px-6 shrink-0"
          style={{
            background: 'rgba(10,10,20,0.95)',
            borderTop: '1px solid rgba(0,217,255,0.1)',
          }}
        >
          <div className="flex items-center gap-4">
            <span
              className="text-xs"
              style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}
            >
              JARVIS ECOSYSTEM v2.0 // NEURAL MESH ACTIVE
            </span>
            {hoveredAgent && (
              <span
                className="text-xs animate-pulse"
                style={{ fontFamily: 'Share Tech Mono, monospace', color: hoveredAgent.color }}
              >
                HOVER: {hoveredAgent.name.toUpperCase()}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            {[
              { label: 'CORE', color: '#00ff88' },
              { label: 'NET', color: '#00d9ff' },
              { label: 'MEM', color: '#8b00ff' },
              { label: 'AI', color: '#ff00aa' },
            ].map(({ label, color }) => (
              <div key={label} className="flex items-center gap-1">
                <div className="w-1.5 h-1.5 rounded-full" style={{ background: color, boxShadow: `0 0 6px ${color}` }} />
                <span className="text-xs" style={{ fontFamily: 'Share Tech Mono, monospace', color: '#8890bb' }}>
                  {label}
                </span>
              </div>
            ))}
          </div>
        </footer>
      </div>

      {voiceEnabled && (
        <motion.div
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
        >
          <div
            className="relative px-8 py-3 flex items-center gap-5"
            style={{
              background: 'rgba(10,10,20,0.95)',
              border: '1px solid rgba(0,217,255,0.5)',
              boxShadow: '0 0 40px rgba(0,217,255,0.3), inset 0 0 20px rgba(0,217,255,0.05)',
              clipPath: 'polygon(12px 0, calc(100% - 12px) 0, 100% 50%, calc(100% - 12px) 100%, 12px 100%, 0 50%)',
            }}
          >
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{
                background: '#ff0044',
                boxShadow: '0 0 12px #ff0044',
                animation: 'neon-pulse 1s ease-in-out infinite',
              }}
            />
            <span
              className="text-sm tracking-widest"
              style={{ fontFamily: 'Share Tech Mono, monospace', color: '#00d9ff' }}
            >
              LISTENING FOR COMMANDS...
            </span>
            <div className="flex gap-0.5 items-end h-5">
              {[...Array(8)].map((_, i) => (
                <div
                  key={i}
                  className="w-1 rounded-full"
                  style={{
                    background: '#00d9ff',
                    height: `${6 + Math.random() * 14}px`,
                    boxShadow: '0 0 6px rgba(0,217,255,0.8)',
                    animation: `neon-pulse ${0.4 + i * 0.1}s ease-in-out infinite`,
                    animationDelay: `${i * 60}ms`,
                  }}
                />
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {!webglOk && (
        <div
          className="fixed bottom-4 right-4 z-50 px-4 py-3"
          style={{
            background: 'rgba(10,10,20,0.95)',
            border: '1px solid rgba(255,224,0,0.5)',
            boxShadow: '0 0 20px rgba(255,224,0,0.2)',
          }}
        >
          <div className="flex items-center gap-2">
            <Zap size={14} style={{ color: '#ffe600' }} />
            <span
              className="text-xs"
              style={{ fontFamily: 'Share Tech Mono, monospace', color: '#ffe600' }}
            >
              WebGL unavailable — using CSS fallback
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
