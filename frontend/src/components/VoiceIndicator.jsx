import React, { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

/**
 * JARVIS Voice Indicator - Cyberpunk Style
 * Advanced audio visualization with neon glow effects
 * Inspired by Iron Man's JARVIS interface
 */
const VoiceIndicator = ({ status }) => {
  const canvasRef = useRef(null)
  const particlesRef = useRef([])
  const animationRef = useRef(null)
  const [audioData, setAudioData] = useState(new Array(64).fill(0))

  // Color schemes for different states
  const colorSchemes = {
    listening: {
      primary: '#00d9ff',
      secondary: '#0088ff',
      accent: '#00ffff',
      glow: 'rgba(0,217,255,0.8)',
      bgGradient: 'radial-gradient(ellipse at center, rgba(0,217,255,0.15) 0%, transparent 70%)',
      text: 'JARVIS ASCULTĂ',
      icon: '◉',
      ringColor: '#00d9ff'
    },
    speaking: {
      primary: '#00ff88',
      secondary: '#00cc66',
      accent: '#88ffaa',
      glow: 'rgba(0,255,136,0.8)',
      bgGradient: 'radial-gradient(ellipse at center, rgba(0,255,136,0.15) 0%, transparent 70%)',
      text: 'JARVIS VORBEȘTE',
      icon: '◆',
      ringColor: '#00ff88'
    },
    processing: {
      primary: '#ff6600',
      secondary: '#ff8800',
      accent: '#ffaa44',
      glow: 'rgba(255,102,0,0.8)',
      bgGradient: 'radial-gradient(ellipse at center, rgba(255,102,0,0.15) 0%, transparent 70%)',
      text: 'JARVIS PROCESEAZĂ',
      icon: '⚙',
      ringColor: '#ff6600'
    },
    idle: {
      primary: '#8890bb',
      secondary: '#6677aa',
      accent: '#99aacc',
      glow: 'rgba(136,144,187,0.5)',
      bgGradient: 'radial-gradient(ellipse at center, rgba(136,144,187,0.1) 0%, transparent 70%)',
      text: 'JARVIS STANDBY',
      icon: '○',
      ringColor: '#8890bb'
    }
  }

  const current = colorSchemes[status] || colorSchemes.idle

  // Simulate audio waveform data
  useEffect(() => {
    let interval
    if (status === 'speaking' || status === 'listening') {
      interval = setInterval(() => {
        const newData = audioData.map(() => {
          const base = status === 'speaking' ? 0.7 : 0.4
          const random = Math.random() * 0.3
          return Math.min(1, base + random)
        })
        setAudioData(newData)
      }, status === 'speaking' ? 50 : 100)
    } else {
      setAudioData(new Array(64).fill(0.1))
    }
    return () => clearInterval(interval)
  }, [status])

  // Canvas animation with particles and waveforms
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    let time = 0

    // Initialize particles
    if (particlesRef.current.length === 0) {
      for (let i = 0; i < 30; i++) {
        particlesRef.current.push({
          x: Math.random() * 200,
          y: Math.random() * 100,
          vx: (Math.random() - 0.5) * 2,
          vy: (Math.random() - 0.5) * 2,
          size: Math.random() * 2 + 1,
          alpha: Math.random() * 0.5 + 0.3
        })
      }
    }

    const animate = () => {
      // Clear with trail effect
      ctx.fillStyle = 'rgba(5, 10, 20, 0.2)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      const centerX = canvas.width / 2
      const centerY = canvas.height / 2

      // Draw concentric rings
      const ringCount = 4
      for (let i = 0; i < ringCount; i++) {
        const radius = 30 + i * 25
        const pulse = Math.sin(time * 0.05 + i * 0.5) * 5
        
        ctx.beginPath()
        ctx.arc(centerX, centerY, radius + pulse, 0, Math.PI * 2)
        ctx.strokeStyle = current.primary
        ctx.lineWidth = 1
        ctx.globalAlpha = 0.3 - i * 0.05
        ctx.stroke()
      }

      // Draw particles
      ctx.globalAlpha = 1
      particlesRef.current.forEach(p => {
        p.x += p.vx
        p.y += p.vy

        // Bounce off edges
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1

        // Draw particle
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fillStyle = current.accent
        ctx.globalAlpha = p.alpha
        ctx.fill()

        // Draw connections
        particlesRef.current.forEach(p2 => {
          const dx = p.x - p2.x
          const dy = p.y - p2.y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < 60) {
            ctx.beginPath()
            ctx.moveTo(p.x, p.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.strokeStyle = current.primary
            ctx.globalAlpha = (1 - dist / 60) * 0.2
            ctx.lineWidth = 0.5
            ctx.stroke()
          }
        })
      })

      // Draw audio waveform
      if (status !== 'idle') {
        const barCount = 32
        const barWidth = 3
        const spacing = 4
        const startX = centerX - ((barCount * (barWidth + spacing)) / 2)

        for (let i = 0; i < barCount; i++) {
          const dataIndex = Math.floor((i / barCount) * audioData.length)
          const value = audioData[dataIndex] || 0.1
          const barHeight = value * 40
          const x = startX + i * (barWidth + spacing)

          // Draw mirrored bars (up and down)
          const gradient = ctx.createLinearGradient(0, centerY - barHeight, 0, centerY + barHeight)
          gradient.addColorStop(0, current.accent)
          gradient.addColorStop(0.5, current.primary)
          gradient.addColorStop(1, current.secondary)

          ctx.fillStyle = gradient
          ctx.globalAlpha = 0.8

          // Top bar
          ctx.fillRect(x, centerY - barHeight - 5, barWidth, barHeight)
          // Bottom bar
          ctx.fillRect(x, centerY + 5, barWidth, barHeight)
        }
      }

      // Draw rotating elements for processing state
      if (status === 'processing') {
        for (let i = 0; i < 3; i++) {
          const angle = time * 0.02 + (i * Math.PI * 2 / 3)
          const radius = 50 + i * 20
          const x = centerX + Math.cos(angle) * radius
          const y = centerY + Math.sin(angle) * radius

          ctx.beginPath()
          ctx.arc(x, y, 5, 0, Math.PI * 2)
          ctx.fillStyle = current.accent
          ctx.globalAlpha = 1
          ctx.fill()

          // Draw trail
          for (let j = 1; j <= 5; j++) {
            const trailAngle = angle - j * 0.1
            const trailX = centerX + Math.cos(trailAngle) * radius
            const trailY = centerY + Math.sin(trailAngle) * radius

            ctx.beginPath()
            ctx.arc(trailX, trailY, 5 - j * 0.8, 0, Math.PI * 2)
            ctx.fillStyle = current.accent
            ctx.globalAlpha = 1 - j * 0.15
            ctx.fill()
          }
        }
      }

      ctx.globalAlpha = 1
      time++
      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [status, current, audioData])

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -100, scale: 0.8 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -100, scale: 0.8 }}
        transition={{ 
          type: 'spring', 
          damping: 20, 
          stiffness: 300,
          duration: 0.5 
        }}
        className="fixed top-6 left-1/2 -translate-x-1/2 z-[100]"
      >
        {/* Main container */}
        <div
          className="relative overflow-hidden"
          style={{
            background: 'linear-gradient(135deg, rgba(5,10,25,0.98) 0%, rgba(10,20,45,0.95) 50%, rgba(5,10,25,0.98) 100%)',
            border: `3px solid ${current.primary}`,
            borderRadius: '24px',
            boxShadow: `
              0 0 80px ${current.glow},
              0 0 160px ${current.glow},
              0 0 240px ${current.glow},
              inset 0 0 80px ${current.glow},
              0 30px 60px rgba(0,0,0,0.9)
            `,
            minWidth: '600px',
            height: '140px',
          }}
        >
          {/* Animated background glow */}
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.6, 0.3],
            }}
            transition={{
              duration: status === 'speaking' ? 0.3 : status === 'listening' ? 0.8 : 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="absolute inset-0"
            style={{
              background: current.bgGradient,
              filter: 'blur(40px)',
            }}
          />

          {/* Scan lines overlay */}
          <div 
            className="absolute inset-0 opacity-30 pointer-events-none overflow-hidden"
            style={{
              background: `repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0,0,0,0.4) 2px,
                rgba(0,0,0,0.4) 4px
              )`,
            }}
          />

          {/* Main content */}
          <div className="relative h-full flex items-center justify-between px-8">
            
            {/* Left: Animated orb with rings */}
            <div className="relative w-24 h-24 flex-shrink-0">
              {/* Outer rotating ring */}
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 rounded-full border-2 border-dashed"
                style={{ 
                  borderColor: `${current.primary}60`,
                  boxShadow: `0 0 20px ${current.glow}`,
                }}
              />
              
              {/* Middle ring */}
              <motion.div
                animate={{ rotate: -360 }}
                transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
                className="absolute inset-2 rounded-full border border-dotted"
                style={{ 
                  borderColor: `${current.secondary}40`,
                }}
              />
              
              {/* Central orb */}
              <motion.div
                animate={{
                  scale: status === 'speaking' ? [1, 1.3, 1] : 
                         status === 'listening' ? [1, 1.15, 1] : 
                         status === 'processing' ? [1, 1.1, 1] : [1, 1.05, 1],
                  rotate: status === 'processing' ? [0, 360] : 0,
                }}
                transition={{
                  duration: status === 'speaking' ? 0.4 : 
                            status === 'listening' ? 0.8 : 
                            status === 'processing' ? 2 : 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
                className="absolute inset-4 rounded-full"
                style={{
                  background: `radial-gradient(circle at 30% 30%, ${current.primary}, ${current.secondary})`,
                  boxShadow: `
                    0 0 30px ${current.glow},
                    0 0 60px ${current.glow},
                    inset 0 0 20px rgba(255,255,255,0.5)
                  `,
                  border: `2px solid ${current.accent}`,
                }}
              />
              
              {/* Inner glow pulse */}
              <motion.div
                animate={{
                  opacity: [0.3, 0.8, 0.3],
                  scale: [0.8, 1.1, 0.8],
                }}
                transition={{
                  duration: status === 'speaking' ? 0.5 : status === 'listening' ? 1 : 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
                className="absolute inset-6 rounded-full"
                style={{
                  background: `radial-gradient(circle, ${current.accent} 0%, transparent 70%)`,
                }}
              />
            </div>

            {/* Center: Canvas waveform visualization */}
            <div className="flex-1 mx-8 relative">
              <canvas
                ref={canvasRef}
                width={400}
                height={100}
                className="w-full h-24"
                style={{
                  filter: `drop-shadow(0 0 10px ${current.glow})`,
                }}
              />
              
              {/* Status text overlay */}
              <motion.div
                key={current.text}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="absolute bottom-0 left-0 right-0 text-center"
              >
                <span
                  className="text-lg font-bold tracking-[0.3em]"
                  style={{
                    fontFamily: 'Orbitron, monospace',
                    color: current.primary,
                    textShadow: `
                      0 0 10px ${current.glow},
                      0 0 20px ${current.glow},
                      0 0 30px ${current.glow}
                    `,
                  }}
                >
                  {current.text}
                </span>
              </motion.div>
            </div>

            {/* Right: Status indicators */}
            <div className="flex flex-col items-end gap-2">
              <motion.div
                animate={{
                  opacity: [0.4, 1, 0.4],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
                className="flex items-center gap-2"
              >
                <div
                  className="w-2 h-2 rounded-full"
                  style={{
                    background: current.primary,
                    boxShadow: `0 0 10px ${current.glow}`,
                  }}
                />
                <span
                  className="text-xs tracking-wider"
                  style={{
                    fontFamily: 'Share Tech Mono, monospace',
                    color: current.secondary,
                  }}
                >
                  {status === 'speaking' ? 'AUDIO_OUT' : 
                   status === 'listening' ? 'AUDIO_IN' :
                   status === 'processing' ? 'AI_CORE' : 'STANDBY'}
                </span>
              </motion.div>

              {/* Signal strength bars */}
              <div className="flex items-end gap-1 h-6">
                {[...Array(5)].map((_, i) => (
                  <motion.div
                    key={i}
                    animate={{
                      height: status === 'idle' ? 4 : 
                              [8 + i * 3, 20 + i * 4, 8 + i * 3],
                      opacity: status === 'idle' ? 0.3 : 1,
                    }}
                    transition={{
                      duration: 0.5 + i * 0.1,
                      repeat: status === 'idle' ? 0 : Infinity,
                      ease: "easeInOut",
                    }}
                    className="w-1.5 rounded-sm"
                    style={{
                      background: `linear-gradient(to top, ${current.primary}, ${current.accent})`,
                      boxShadow: `0 0 5px ${current.glow}`,
                    }}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Bottom decorative line */}
          <motion.div
            animate={{
              scaleX: [0, 1, 0],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="absolute bottom-0 left-1/2 -translate-x-1/2 h-0.5 w-1/2"
            style={{
              background: `linear-gradient(90deg, transparent, ${current.primary}, transparent)`,
            }}
          />
        </div>

        {/* Corner decorations */}
        {['top-left', 'top-right', 'bottom-left', 'bottom-right'].map((corner) => (
          <div
            key={corner}
            className={`absolute w-4 h-4 ${
              corner.includes('top') ? 'top-2' : 'bottom-2'
            } ${
              corner.includes('left') ? 'left-2' : 'right-2'
            }`}
            style={{
              border: `2px solid ${current.primary}`,
              borderRadius: corner.includes('top') 
                ? corner.includes('left') ? '8px 0 0 0' : '0 8px 0 0'
                : corner.includes('left') ? '0 0 0 8px' : '0 0 8px 0',
              opacity: 0.6,
            }}
          />
        ))}
      </motion.div>
    </AnimatePresence>
  )
}

export default VoiceIndicator