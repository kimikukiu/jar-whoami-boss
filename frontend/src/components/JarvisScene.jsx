import React, { useRef, useMemo, useState, useCallback } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Stars } from '@react-three/drei'
import * as THREE from 'three'

export const AGENT_POSITIONS = [
  { id: 'director_fury',    name: 'Director Fury',    pos: [0, 0, 0],    color: '#ff4444', size: 0.9,  role: 'Chief of Staff' },
  { id: 'heimdall',         name: 'Heimdall',         pos: [-5, 3, -2],   color: '#00ff88', size: 0.65, role: 'Gatekeeper' },
  { id: 'john_kramer',       name: 'John Kramer',       pos: [5, 3, -2],    color: '#ffe600', size: 0.65, role: 'Planner' },
  { id: 'morpheus',         name: 'Morpheus',         pos: [-7, -2, -4],  color: '#8b00ff', size: 0.65, role: 'Dispatcher' },
  { id: 'sherlock_holmes',   name: 'Sherlock Holmes',   pos: [7, -2, -4],   color: '#00d9ff', size: 0.65, role: 'Investigator' },
  { id: 'data',              name: 'Data',              pos: [0, 6, -3],    color: '#00ffff', size: 0.6,  role: 'Archivist' },
  { id: 'midas',            name: 'Midas',            pos: [-4, -5, -5],  color: '#ffe600', size: 0.6,  role: 'MoneyMaker' },
  { id: 'adforge',           name: 'AdForge',           pos: [4, -5, -5],   color: '#ff00aa', size: 0.6,  role: 'Ads & Copy' },
  { id: 'saul_goodman',     name: 'Saul Goodman',     pos: [-9, 1, -6],   color: '#ff6600', size: 0.55, role: 'Patch Agent' },
  { id: 'jarvis_build',      name: 'JARVIS',            pos: [9, 1, -6],    color: '#4a9eff', size: 0.55, role: 'Build Validator' },
  { id: 'ripley',            name: 'Ripley',            pos: [-6, -7, -7],  color: '#ff0044', size: 0.55, role: 'Bug Hunter' },
  { id: 'da_vinci',          name: 'Da Vinci',           pos: [6, -7, -7],   color: '#ff44aa', size: 0.55, role: 'UI Agent' },
  { id: 'john_wick',         name: 'John Wick',          pos: [0, -9, -8],   color: '#ffffff', size: 0.5,  role: 'Final Impl.' },
]

export const CONNECTIONS = [
  [0,1],[0,2],[1,3],[1,5],[2,4],[2,5],
  [3,6],[4,7],[3,8],[4,9],[6,10],[7,11],
  [10,12],[11,12],[8,10],[9,11],
  [0,5],[1,2],[0,6],[2,7],
]

function AgentNode({ agent, index, onHover, onClick, isHovered, isSelected }) {
  const meshRef = useRef()
  const ringRef1 = useRef()
  const ringRef2 = useRef()
  const glowRef = useRef()
  const groupRef = useRef()
  const [hovered, setHovered] = useState(false)

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    if (!groupRef.current) return
    const baseSpeed = 0.3
    groupRef.current.rotation.y = t * baseSpeed + index * 0.4
    groupRef.current.rotation.x = Math.sin(t * 0.25 + index) * 0.35

    const floatY = Math.sin(t * 0.5 + index * 0.7) * 0.15
    const floatX = Math.cos(t * 0.4 + index * 0.5) * 0.08
    groupRef.current.position.y += floatY * 0.01
    groupRef.current.position.x += floatX * 0.01

    if (meshRef.current) {
      const targetScale = hovered || isHovered ? 1.25 : 1.0
      meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.08)
    }
    if (ringRef1.current) {
      ringRef1.current.rotation.z = t * (0.6 + index * 0.05)
      ringRef1.current.rotation.x = t * 0.4 + index * 0.3
      const pulse = 1 + Math.sin(t * 2.5 + index) * 0.12
      ringRef1.current.scale.set(pulse, pulse, pulse)
      ringRef1.current.material.opacity = hovered || isHovered ? 0.9 : 0.55
    }
    if (ringRef2.current) {
      ringRef2.current.rotation.z = -t * 0.4 + index * 0.06
      ringRef2.current.rotation.y = t * 0.3 + index * 0.2
    }
    if (glowRef.current) {
      const glowOpacity = hovered || isHovered ? 0.22 : 0.08
      glowRef.current.material.opacity = glowOpacity + Math.sin(t * 3 + index) * 0.04
      const gs = hovered || isHovered ? 3.2 : 2.5
      glowRef.current.scale.lerp(new THREE.Vector3(gs, gs, gs), 0.06)
      glowRef.current.material.emissiveIntensity = hovered || isHovered ? 0.8 : 0.3
    }
  })

  const handlePointerOver = useCallback((e) => {
    e.stopPropagation()
    setHovered(true)
    onHover(agent)
    document.body.style.cursor = 'pointer'
  }, [agent, onHover])

  const handlePointerOut = useCallback((e) => {
    e.stopPropagation()
    setHovered(false)
    onHover(null)
    document.body.style.cursor = 'default'
  }, [onHover])

  const handleClick = useCallback((e) => {
    e.stopPropagation()
    onClick(agent)
  }, [agent, onClick])

  const emissiveIntensity = hovered || isHovered ? 1.8 : 1.0

  return (
    <group
      ref={groupRef}
      position={agent.pos}
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
      onClick={handleClick}
    >
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[agent.size, 1]} />
        <meshStandardMaterial
          color={agent.color}
          emissive={agent.color}
          emissiveIntensity={emissiveIntensity}
          roughness={0.05}
          metalness={1.0}
          envMapIntensity={1.5}
        />
      </mesh>

      <mesh ref={ringRef1} rotation={[Math.PI / 4, 0, 0]}>
        <torusGeometry args={[agent.size * 1.9, 0.035, 8, 48]} />
        <meshStandardMaterial
          color={agent.color}
          emissive={agent.color}
          emissiveIntensity={1.5}
          transparent
          opacity={0.55}
        />
      </mesh>

      <mesh ref={ringRef2} rotation={[Math.PI / 3, Math.PI / 6, 0]}>
        <torusGeometry args={[agent.size * 2.5, 0.018, 6, 48]} />
        <meshStandardMaterial
          color={agent.color}
          emissive={agent.color}
          emissiveIntensity={1.0}
          transparent
          opacity={0.3}
        />
      </mesh>

      <mesh ref={glowRef}>
        <sphereGeometry args={[agent.size * 2.5, 16, 16]} />
        <meshStandardMaterial
          color={agent.color}
          emissive={agent.color}
          emissiveIntensity={0.3}
          transparent
          opacity={0.08}
          side={THREE.BackSide}
        />
      </mesh>

      <pointLight
        color={agent.color}
        intensity={isSelected ? 3.0 : hovered || isHovered ? 2.0 : 1.2}
        distance={12}
        decay={2}
      />
    </group>
  )
}

function DataStream({ start, end, color, speed = 0.003, active = false }) {
  const ref = useRef()
  const COUNT = 40

  const basePoints = useMemo(() => {
    return Array.from({ length: COUNT }, (_, i) => {
      const t = i / (COUNT - 1)
      return new THREE.Vector3(
        start[0] + (end[0] - start[0]) * t,
        start[1] + (end[1] - start[1]) * t,
        start[2] + (end[2] - start[2]) * t,
      )
    })
  }, [start, end])

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()
    const positions = new Float32Array(COUNT * 3)
    const colors = new Float32Array(COUNT * 3)
    const tmpColor = new THREE.Color(color)
    for (let i = 0; i < COUNT; i++) {
      positions[i * 3] = basePoints[i].x
      positions[i * 3 + 1] = basePoints[i].y
      positions[i * 3 + 2] = basePoints[i].z
      colors[i * 3] = tmpColor.r
      colors[i * 3 + 1] = tmpColor.g
      colors[i * 3 + 2] = tmpColor.b
    }
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))
    return geo
  }, [basePoints, color])

  useFrame(() => {
    if (!ref.current) return
    const positions = ref.current.geometry.attributes.position.array
    const t = performance.now() * 0.001
    for (let i = 0; i < COUNT; i++) {
      const bt = i / (COUNT - 1)
      const wave = Math.sin(bt * Math.PI * 2 + t * 3) * 0.1
      const activeBoost = active ? 2.0 : 1.0
      positions[i * 3] = basePoints[i].x + wave * activeBoost
      positions[i * 3 + 1] = basePoints[i].y + Math.cos(bt * Math.PI * 3 + t * 2) * 0.07 * activeBoost
      positions[i * 3 + 2] = basePoints[i].z + wave * 0.6 * activeBoost
    }
    ref.current.geometry.attributes.position.needsUpdate = true
    ref.current.material.opacity = active ? 0.7 : (0.3 + Math.sin(t * 2) * 0.12)
  })

  return (
    <line ref={ref} geometry={geometry}>
      <lineBasicMaterial
        vertexColors
        transparent
        opacity={0.4}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </line>
  )
}

function HolographicRing({ radius = 22, count = 280, color = '#00d9ff', speed = 0.015 }) {
  const ref = useRef()

  const geometry = useMemo(() => {
    const positions = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2
      const r = radius + Math.sin(angle * 6) * 0.9
      positions[i * 3] = Math.cos(angle) * r
      positions[i * 3 + 1] = Math.sin(angle) * r
      positions[i * 3 + 2] = -5 + Math.sin(angle * 3) * 0.6
    }
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    return geo
  }, [radius, count])

  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.rotation.z = clock.getElapsedTime() * speed
      ref.current.rotation.x = Math.sin(clock.getElapsedTime() * speed * 0.5) * 0.08
    }
  })

  return (
    <points ref={ref} geometry={geometry}>
      <pointsMaterial
        color={color}
        size={0.12}
        transparent
        opacity={0.4}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  )
}

function PulseRing() {
  const ref = useRef()
  useFrame(({ clock }) => {
    if (ref.current) {
      const t = (clock.getElapsedTime() % 6) / 6
      const scale = 1 + t * 22
      ref.current.scale.set(scale, scale, scale)
      ref.current.material.opacity = (1 - t) * 0.2
    }
  })
  return (
    <mesh ref={ref} rotation={[Math.PI / 2, 0, 0]}>
      <ringGeometry args={[0.8, 0.85, 64]} />
      <meshBasicMaterial
        color="#00d9ff"
        transparent
        opacity={0.2}
        side={THREE.DoubleSide}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </mesh>
  )
}

function CursorParticles({ mouse }) {
  const ref = useRef()
  const COUNT = 60

  const { positions, velocities } = useMemo(() => {
    const positions = new Float32Array(COUNT * 3)
    const velocities = []
    for (let i = 0; i < COUNT; i++) {
      positions[i * 3] = 0
      positions[i * 3 + 1] = 0
      positions[i * 3 + 2] = 0
      velocities.push({ x: 0, y: 0, life: 0, maxLife: 0 })
    }
    return { positions, velocities }
  }, [])

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    return geo
  }, [positions])

  const idxRef = useRef(0)
  const velRef = useRef(velocities)

  useFrame(() => {
    if (!ref.current || !mouse) return

    const posAttr = ref.current.geometry.attributes.position
    const vels = velRef.current

    posAttr.array[idxRef.current * 3] = mouse.x * 25
    posAttr.array[idxRef.current * 3 + 1] = mouse.y * 25
    posAttr.array[idxRef.current * 3 + 2] = 0
    vels[idxRef.current] = {
      x: (Math.random() - 0.5) * 0.3,
      y: (Math.random() - 0.5) * 0.3,
      life: 1.0,
      maxLife: 0.8 + Math.random() * 0.4,
    }
    idxRef.current = (idxRef.current + 1) % COUNT

    for (let i = 0; i < COUNT; i++) {
      const vel = vels[i]
      if (vel.life <= 0) {
        posAttr.array[i * 3 + 2] = -999
        continue
      }
      posAttr.array[i * 3] += vel.x
      posAttr.array[i * 3 + 1] += vel.y
      vel.x *= 0.96
      vel.y *= 0.96
      vel.life -= 0.02
      posAttr.array[i * 3 + 2] = vel.life * 2
    }
    posAttr.needsUpdate = true
  })

  return (
    <points ref={ref} geometry={geometry}>
      <pointsMaterial
        color="#00d9ff"
        size={0.25}
        transparent
        opacity={0.8}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  )
}

function CameraController({ mouse }) {
  const { camera } = useThree()
  useFrame(() => {
    camera.position.x += (mouse.x * 8 - camera.position.x) * 0.02
    camera.position.y += (mouse.y * 5 - camera.position.y) * 0.02
    camera.lookAt(0, 0, 0)
  })
  return null
}

function JarvisScene({ onAgentHover, onAgentClick, selectedAgent, hoveredAgent, mouse }) {
  return (
    <>
      <color attach="background" args={['#030308']} />
      <fog attach="fog" args={['#030308', 25, 80]} />

      <ambientLight intensity={0.06} />
      <pointLight position={[0, 0, 20]} intensity={1.5} color="#00d9ff" />
      <pointLight position={[-20, -10, -10]} intensity={0.7} color="#ff00aa" />
      <pointLight position={[20, 10, -10]} intensity={0.6} color="#8b00ff" />
      <pointLight position={[0, 20, -5]} intensity={0.5} color="#00ff88" />
      <pointLight position={[0, -15, 5]} intensity={0.3} color="#ffe600" />

      <Stars radius={100} depth={50} count={5000} factor={3} saturation={0.2} fade speed={0.2} />

      <CameraController mouse={mouse} />

      {AGENT_POSITIONS.map((agent, i) => (
        <AgentNode
          key={agent.id}
          agent={agent}
          index={i}
          onHover={onAgentHover}
          onClick={onAgentClick}
          isHovered={hoveredAgent?.id === agent.id}
          isSelected={selectedAgent?.id === agent.id}
        />
      ))}

      {CONNECTIONS.map(([a, b], i) => {
        const isActive = selectedAgent &&
          (AGENT_POSITIONS[a].id === selectedAgent.id || AGENT_POSITIONS[b].id === selectedAgent.id)
        return (
          <DataStream
            key={`conn-${a}-${b}-${i}`}
            start={AGENT_POSITIONS[a].pos}
            end={AGENT_POSITIONS[b].pos}
            color={AGENT_POSITIONS[a].color}
            speed={0.002 + (i % 5) * 0.0004}
            active={isActive}
          />
        )
      })}

      <HolographicRing radius={20} count={300} color="#00d9ff" speed={0.012} />
      <HolographicRing radius={26} count={220} color="#8b00ff" speed={0.009} />
      <HolographicRing radius={33} count={160} color="#ff00aa" speed={0.007} />
      <HolographicRing radius={40} count={120} color="#00ff88" speed={0.005} />

      <PulseRing />
      <CursorParticles mouse={mouse} />
    </>
  )
}

export default JarvisScene
