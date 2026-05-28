import React, { useRef, useMemo, useState, useCallback, useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Text, Html, Stars, Sky } from '@react-three/drei'
import * as THREE from 'three'

const AGENT_ZONES = [
  {
    id: 'director_fury',
    name: 'Director Fury',
    role: 'Chief of Staff',
    pos: [0, 0, 0],
    color: '#ff4444',
    size: 8,
    platforms: ['JARVIS OS', 'Management Console'],
    revenue: 15000,
    currency: 'USD',
    workType: 'orchestrating',
    stats: { tasks: 847, completed: 823, efficiency: 97 },
  },
  {
    id: 'heimdall',
    name: 'Heimdall',
    role: 'Security & Validation',
    pos: [-30, 0, -20],
    color: '#00ff88',
    size: 10,
    platforms: ['Firewall Pro', 'Threat Detector'],
    revenue: 8500,
    currency: 'USD',
    workType: 'securing',
    stats: { threats: 1247, blocked: 1240, uptime: 99.9 },
  },
  {
    id: 'morpheus',
    name: 'Morpheus',
    role: 'Social Media Commander',
    pos: [-50, 0, 20],
    color: '#8b00ff',
    size: 12,
    platforms: ['TikTok', 'Instagram', 'YouTube', 'Twitter/X'],
    revenue: 25000,
    currency: 'USD',
    workType: 'posting',
    stats: { posts: 3420, followers: 125000, engagement: 8.4 },
  },
  {
    id: 'sherlock_holmes',
    name: 'Sherlock Holmes',
    role: 'Repo Inspector',
    pos: [30, 0, -20],
    color: '#00d9ff',
    size: 10,
    platforms: ['GitHub', 'GitLab', 'BitBucket'],
    revenue: 12000,
    currency: 'USD',
    workType: 'inspecting',
    stats: { repos: 456, issues: 2340, fixed: 2290 },
  },
  {
    id: 'midas',
    name: 'Midas',
    role: 'MoneyMaker Specialist',
    pos: [-40, 0, -40],
    color: '#ffd700',
    size: 14,
    platforms: ['Amazon', 'eBay', 'Shopify', 'Dropshipping'],
    revenue: 85000,
    currency: 'USD',
    workType: 'selling',
    stats: { products: 1250, sales: 8900, profit: 34000 },
  },
  {
    id: 'adforge',
    name: 'AdForge',
    role: 'Ads & Copywriting',
    pos: [40, 0, -40],
    color: '#ff00aa',
    size: 12,
    platforms: ['Google Ads', 'Facebook Ads', 'TikTok Ads'],
    revenue: 45000,
    currency: 'USD',
    workType: 'advertising',
    stats: { campaigns: 89, impressions: 5400000, CTR: 4.2 },
  },
  {
    id: 'saul_goodman',
    name: 'Saul Goodman',
    role: 'Patch Agent',
    pos: [-60, 0, 0],
    color: '#ff6600',
    size: 10,
    platforms: ['GitHub Patches', 'Stack Overflow', 'DevDocs'],
    revenue: 9500,
    currency: 'USD',
    workType: 'patching',
    stats: { patches: 1560, bugs: 780, resolved: 760 },
  },
  {
    id: 'jarvis_build',
    name: 'JARVIS Builder',
    role: 'Build Validator',
    pos: [60, 0, 0],
    color: '#4a9eff',
    size: 10,
    platforms: ['Vite', 'Webpack', 'Docker', 'CI/CD'],
    revenue: 11000,
    currency: 'USD',
    workType: 'building',
    stats: { builds: 2340, failed: 45, success: 2295 },
  },
  {
    id: 'ripley',
    name: 'Ripley',
    role: 'Bug Hunter',
    pos: [-70, 0, 40],
    color: '#ff0044',
    size: 12,
    platforms: ['BugBounty.com', 'HackerOne', 'Syndicate'],
    revenue: 67000,
    currency: 'USD',
    workType: 'hunting',
    stats: { bugs: 234, critical: 45, rewards: 67000 },
  },
  {
    id: 'da_vinci',
    name: 'Da Vinci',
    role: 'UI Agent',
    pos: [70, 0, 40],
    color: '#ff44aa',
    size: 12,
    platforms: ['Figma', 'Dribbble', 'Behance', 'Portfolio'],
    revenue: 38000,
    currency: 'USD',
    workType: 'designing',
    stats: { designs: 189, clients: 45, rating: 4.9 },
  },
  {
    id: 'john_wick',
    name: 'John Wick',
    role: 'Final Implementation',
    pos: [0, 0, 70],
    color: '#ffffff',
    size: 14,
    platforms: ['AWS', 'Azure', 'GCP', 'Deployment'],
    revenue: 55000,
    currency: 'USD',
    workType: 'deploying',
    stats: { deploys: 567, uptime: 99.7, servers: 89 },
  },
  {
    id: 'data',
    name: 'Data',
    role: 'Archivist - Memory',
    pos: [0, 0, -70],
    color: '#00ffff',
    size: 10,
    platforms: ['SQLite', 'MongoDB', 'Redis', 'Cache'],
    revenue: 7500,
    currency: 'USD',
    workType: 'storing',
    stats: { records: 2500000, queries: 8900000, latency: 12 },
  },
  {
    id: 'john_kramer',
    name: 'John Kramer',
    role: 'Planner - Missions',
    pos: [50, 0, 50],
    color: '#ffe600',
    size: 12,
    platforms: ['Jira', 'Notion', 'Roadmaps', 'Tasks'],
    revenue: 13000,
    currency: 'USD',
    workType: 'planning',
    stats: { tasks: 4560, projects: 78, completion: 94 },
  },
]

function rand(min, max) {
  return Math.random() * (max - min) + min
}

function seededRand(seed, min, max) {
  const x = Math.sin(seed * 9999) * 10000
  return (x - Math.floor(x)) * (max - min) + min
}

function Building({ position, width, height, depth, color, windows = true }) {
  const ref = useRef()
  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.position.y = Math.sin(clock.getElapsedTime() * 0.1 + position[0]) * 0.01
    }
  })

  const windowRows = Math.floor(height / 2)
  const windowCols = Math.floor(width / 1.5)

  return (
    <group ref={ref} position={position}>
      <mesh>
        <boxGeometry args={[width, height, depth]} />
        <meshStandardMaterial color={color} roughness={0.8} metalness={0.2} />
      </mesh>
      {windows && [...Array(windowRows)].map((_, row) =>
        [...Array(windowCols)].map((_, col) => (
          <mesh
            key={`w-${row}-${col}`}
            position={[
              (col - (windowCols - 1) / 2) * 1.2,
              -height / 2 + 1.5 + row * 2,
              depth / 2 + 0.01,
            ]}
          >
            <planeGeometry args={[0.6, 1]} />
            <meshStandardMaterial
              color={Math.random() > 0.3 ? '#88ccff' : '#ffee88'}
              emissive={Math.random() > 0.5 ? '#ffee88' : '#000000'}
              emissiveIntensity={Math.random() > 0.5 ? 0.3 : 0}
            />
          </mesh>
        ))
      )}
      <mesh position={[0, height / 2 + 0.1, 0]}>
        <boxGeometry args={[width + 0.2, 0.2, depth + 0.2]} />
        <meshStandardMaterial color="#333333" metalness={0.9} roughness={0.1} />
      </mesh>
    </group>
  )
}

function Tree({ position, type = 'cypress' }) {
  const ref = useRef()
  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.rotation.z = Math.sin(clock.getElapsedTime() * 0.5 + position[0]) * 0.02
    }
  })

  if (type === 'round') {
    return (
      <group ref={ref} position={position}>
        <mesh position={[0, 3, 0]}>
          <sphereGeometry args={[2, 8, 8]} />
          <meshStandardMaterial color="#228822" roughness={0.9} />
        </mesh>
        <mesh position={[0, 0.5, 0]}>
          <cylinderGeometry args={[0.3, 0.4, 1, 8]} />
          <meshStandardMaterial color="#553311" roughness={0.9} />
        </mesh>
      </group>
    )
  }

  return (
    <group ref={ref} position={position}>
      <mesh position={[0, 3, 0]}>
        <coneGeometry args={[1, 6, 8]} />
        <meshStandardMaterial color="#226622" roughness={0.9} />
      </mesh>
      <mesh position={[0, 6, 0]}>
        <coneGeometry args={[0.7, 4, 8]} />
        <meshStandardMaterial color="#2a7a2a" roughness={0.9} />
      </mesh>
      <mesh position={[0, 8.5, 0]}>
        <coneGeometry args={[0.4, 2.5, 8]} />
        <meshStandardMaterial color="#33aa33" roughness={0.9} />
      </mesh>
      <mesh position={[0, 0.3, 0]}>
        <cylinderGeometry args={[0.2, 0.3, 0.6, 8]} />
        <meshStandardMaterial color="#443311" roughness={0.9} />
      </mesh>
    </group>
  )
}

function Street({ from, to, width = 3 }) {
  const direction = [to[0] - from[0], 0, to[2] - from[2]]
  const length = Math.sqrt(direction[0] ** 2 + direction[2] ** 2)
  const angle = Math.atan2(direction[0], direction[2])

  return (
    <group position={[(from[0] + to[0]) / 2, 0.01, (from[2] + to[2]) / 2]} rotation={[0, angle, 0]}>
      <mesh>
        <boxGeometry args={[width, 0.05, length]} />
        <meshStandardMaterial color="#333333" roughness={0.95} />
      </mesh>
      {[...Array(Math.floor(length / 4))].map((_, i) => (
        <mesh key={`line-${i}`} position={[0, 0.03, -length / 2 + 2 + i * 4]}>
          <boxGeometry args={[0.2, 0.02, 2]} />
          <meshStandardMaterial color="#ffdd44" />
        </mesh>
      ))}
    </group>
  )
}

function Car({ position, color, direction = 0 }) {
  const ref = useRef()
  const [state] = useState(() => ({
    x: position[0],
    z: position[2],
    speed: rand(3, 8),
    targetX: position[0] + rand(-60, 60),
    targetZ: position[2] + rand(-60, 60),
    timer: rand(2, 5),
  }))

  useFrame((_, delta) => {
    if (!ref.current) return
    const s = state
    s.timer -= delta

    if (s.timer <= 0) {
      s.targetX = s.x + rand(-80, 80)
      s.targetZ = s.z + rand(-80, 80)
      s.timer = rand(3, 8)
    }

    const dx = s.targetX - s.x
    const dz = s.targetZ - s.z
    const dist = Math.sqrt(dx * dx + dz * dz)

    if (dist > 0.5) {
      s.x += (dx / dist) * s.speed * delta
      s.z += (dz / dist) * s.speed * delta
      ref.current.rotation.y = Math.atan2(dx, dz)
    }

    ref.current.position.set(s.x, 0.3, s.z)
  })

  return (
    <group ref={ref} position={position}>
      <mesh position={[0, 0.3, 0]}>
        <boxGeometry args={[1.6, 0.6, 3.5]} />
        <meshStandardMaterial color={color} metalness={0.6} roughness={0.4} />
      </mesh>
      <mesh position={[0, 0.7, -0.3]}>
        <boxGeometry args={[1.4, 0.5, 1.5]} />
        <meshStandardMaterial color="#1a2a3a" metalness={0.3} roughness={0.5} transparent opacity={0.7} />
      </mesh>
      {[...Array(4)].map((_, i) => (
        <mesh key={`w-${i}`} position={[(i % 2 === 0 ? -0.7 : 0.7), -0.1, (i < 2 ? -1 : 1)]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.3, 0.3, 0.2, 12]} />
          <meshStandardMaterial color="#1a1a1a" metalness={0.5} roughness={0.5} />
        </mesh>
      ))}
      <pointLight position={[0, 0.5, 1.5]} color="#ffff88" intensity={1} distance={8} />
    </group>
  )
}

function Person({ position, color }) {
  const ref = useRef()
  const [state] = useState(() => ({
    x: position[0],
    z: position[2],
    targetX: position[0] + rand(-10, 10),
    targetZ: position[2] + rand(-10, 10),
    speed: rand(1, 2.5),
    timer: rand(2, 6),
  }))

  useFrame((_, delta) => {
    if (!ref.current) return
    const s = state
    s.timer -= delta

    if (s.timer <= 0) {
      s.targetX = s.x + rand(-15, 15)
      s.targetZ = s.z + rand(-15, 15)
      s.timer = rand(3, 8)
    }

    const dx = s.targetX - s.x
    const dz = s.targetZ - s.z
    const dist = Math.sqrt(dx * dx + dz * dz)

    if (dist > 0.1) {
      s.x += (dx / dist) * s.speed * delta
      s.z += (dz / dist) * s.speed * delta
      ref.current.rotation.y = Math.atan2(dx, dz)
    }

    ref.current.position.set(s.x, 0, s.z)
  })

  return (
    <group ref={ref} position={position}>
      <mesh position={[0, 1.6, 0]}>
        <sphereGeometry args={[0.25, 8, 8]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0, 0.9, 0]}>
        <capsuleGeometry args={[0.2, 0.8, 4, 8]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0, 0.1, 0]}>
        <capsuleGeometry args={[0.15, 0.2, 4, 8]} />
        <meshStandardMaterial color="#333344" />
      </mesh>
    </group>
  )
}

function AgriculturalRobot({ position, agentColor, task }) {
  const ref = useRef()
  const armRef = useRef()
  const wheelRefs = useRef([])
  const [state] = useState(() => ({
    x: position[0],
    z: position[2],
    targetX: position[0] + rand(-8, 8),
    targetZ: position[2] + rand(-8, 8),
    speed: rand(1, 3),
    timer: rand(3, 8),
    isWorking: false,
    workTimer: 0,
    rotation: 0,
  }))

  useFrame(({ clock }, delta) => {
    if (!ref.current) return
    const s = state
    const t = clock.getElapsedTime()

    s.timer -= delta
    if (s.timer <= 0) {
      s.targetX = s.x + rand(-12, 12)
      s.targetZ = s.z + rand(-12, 12)
      s.timer = rand(4, 10)
      s.isWorking = Math.random() > 0.4
      s.workTimer = 0
    }

    const dx = s.targetX - s.x
    const dz = s.targetZ - s.z
    const dist = Math.sqrt(dx * dx + dz * dz)

    if (dist > 0.3) {
      s.x += (dx / dist) * s.speed * delta
      s.z += (dz / dist) * s.speed * delta
      s.rotation = Math.atan2(dx, dz)
      s.isWorking = false
    } else if (s.isWorking) {
      s.workTimer += delta
    }

    ref.current.position.set(s.x, 0.5, s.z)
    ref.current.rotation.y = s.rotation + Math.sin(t * 2) * 0.1

    wheelRefs.current.forEach((w) => {
      if (w) w.rotation.x += s.speed * delta * 2
    })

    if (armRef.current) {
      armRef.current.rotation.x = s.isWorking ? Math.sin(t * 3) * 0.5 : 0
    }
  })

  return (
    <group ref={ref} position={position}>
      <mesh>
        <boxGeometry args={[2, 1.2, 2.5]} />
        <meshStandardMaterial color="#2a3a4a" metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[0, 1, 0.3]}>
        <boxGeometry args={[1.4, 0.8, 0.6]} />
        <meshStandardMaterial color="#1a2a3a" metalness={0.7} roughness={0.3} />
      </mesh>
      <mesh position={[0, 1.4, 0.3]}>
        <sphereGeometry args={[0.35, 16, 16]} />
        <meshStandardMaterial color={agentColor} emissive={agentColor} emissiveIntensity={2} />
      </mesh>

      <group ref={armRef} position={[0, 0.5, 1.4]}>
        <mesh position={[0, 0, 0.5]}>
          <cylinderGeometry args={[0.1, 0.1, 1, 8]} />
          <meshStandardMaterial color="#3a4a5a" metalness={0.7} roughness={0.3} />
        </mesh>
        <mesh position={[0, 0.6, 0.5]}>
          <boxGeometry args={[0.8, 0.15, 0.5]} />
          <meshStandardMaterial color="#4a5a6a" metalness={0.6} roughness={0.4} />
        </mesh>
      </group>

      {[...Array(6)].map((_, i) => (
        <mesh
          key={`wheel-${i}`}
          ref={(el) => (wheelRefs.current[i] = el)}
          position={[(i % 2 === 0 ? -1 : 1) * 1.1, -0.4, (i < 3 ? -0.8 : 0.8)]}
          rotation={[0, 0, Math.PI / 2]}
        >
          <cylinderGeometry args={[0.5, 0.5, 0.3, 12]} />
          <meshStandardMaterial color="#1a1a1a" metalness={0.5} roughness={0.5} />
        </mesh>
      ))}

      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[2.4, 0.1, 2.9]} />
        <meshStandardMaterial color="#00ff8844" emissive="#00ff88" emissiveIntensity={0.5} transparent opacity={0.3} />
      </mesh>
    </group>
  )
}

function AgentAvatar({ data, onClick, isSelected }) {
  const ref = useRef()
  const [hovered, setHovered] = useState(false)

  useFrame(({ clock }) => {
    if (!ref.current) return
    const t = clock.getElapsedTime()

    ref.current.position.y = 1.5 + Math.sin(t * 2 + data.pos[0]) * 0.2

    if (isSelected || hovered) {
      ref.current.scale.setScalar(1.3)
    } else {
      ref.current.scale.setScalar(1)
    }
  })

  return (
    <group
      ref={ref}
      position={[data.pos[0], 1.5, data.pos[2]]}
      onClick={(e) => {
        e.stopPropagation()
        onClick(data)
      }}
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={() => {
        setHovered(false)
        document.body.style.cursor = 'default'
      }}
    >
      <mesh>
        <capsuleGeometry args={[0.8, 1.5, 4, 16]} />
        <meshStandardMaterial
          color={data.color}
          emissive={data.color}
          emissiveIntensity={hovered || isSelected ? 1.5 : 0.5}
          metalness={0.6}
          roughness={0.3}
        />
      </mesh>

      <mesh position={[0, 1.5, 0]}>
        <sphereGeometry args={[0.6, 16, 16]} />
        <meshStandardMaterial
          color={data.color}
          emissive={data.color}
          emissiveIntensity={hovered || isSelected ? 2 : 0.8}
        />
      </mesh>

      <pointLight
        position={[0, 2, 0]}
        color={data.color}
        intensity={(hovered || isSelected) ? 5 : 2}
        distance={15}
      />

      {(hovered || isSelected) && (
        <mesh position={[0, 3.5, 0]}>
          <ringGeometry args={[1.5, 2, 32]} />
          <meshBasicMaterial color={data.color} transparent opacity={0.5} />
        </mesh>
      )}

      <Text
        position={[0, 3.8, 0]}
        fontSize={0.8}
        color={data.color}
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.05}
        outlineColor="#000000"
      >
        {data.name.toUpperCase()}
      </Text>
    </group>
  )
}

function City() {
  const buildings = useMemo(() => {
    const result = []
    for (let i = 0; i < 80; i++) {
      const x = rand(-90, 90)
      const z = rand(-90, 90)
      const distFromCenter = Math.sqrt(x * x + z * z)
      if (distFromCenter < 15) continue

      const zone = AGENT_ZONES.find((z) => {
        const dx = z.pos[0] - x
        const dz = z.pos[2] - z
        return Math.sqrt(dx * dx + dz * dz) < z.size
      })

      if (!zone) {
        result.push({
          position: [x, 0, z],
          width: rand(4, 12),
          height: rand(8, 40),
          depth: rand(4, 12),
          color: ['#2a3a4a', '#1a2a3a', '#3a4a5a', '#4a5a6a', '#1e2a3a'][Math.floor(Math.random() * 5)],
        })
      }
    }
    return result
  }, [])

  const trees = useMemo(() => {
    const result = []
    for (let i = 0; i < 60; i++) {
      const x = rand(-95, 95)
      const z = rand(-95, 95)
      const distFromCenter = Math.sqrt(x * x + z * z)
      if (distFromCenter < 12) continue
      const tooClose = AGENT_ZONES.some((zone) => {
        const dx = zone.pos[0] - x
        const dz = zone.pos[2] - z
        return Math.sqrt(dx * dx + dz * dz) < zone.size + 2
      })
      if (!tooClose) {
        result.push({
          position: [x, 0, z],
          type: Math.random() > 0.6 ? 'round' : 'cypress',
        })
      }
    }
    return result
  }, [])

  const cars = useMemo(() => [
    { position: [rand(-80, 80), 0, rand(-80, 80)], color: ['#ff4444', '#4444ff', '#44ff44', '#ffff44', '#ff44ff', '#44ffff'][Math.floor(Math.random() * 6)] },
    { position: [rand(-80, 80), 0, rand(-80, 80)], color: ['#ff4444', '#4444ff', '#44ff44', '#ffff44', '#ff44ff', '#44ffff'][Math.floor(Math.random() * 6)] },
    { position: [rand(-80, 80), 0, rand(-80, 80)], color: ['#ff4444', '#4444ff', '#44ff44', '#ffff44', '#ff44ff', '#44ffff'][Math.floor(Math.random() * 6)] },
    { position: [rand(-80, 80), 0, rand(-80, 80)], color: ['#ff4444', '#4444ff', '#44ff44', '#ffff44', '#ff44ff', '#44ffff'][Math.floor(Math.random() * 6)] },
    { position: [rand(-80, 80), 0, rand(-80, 80)], color: ['#ff4444', '#4444ff', '#44ff44', '#ffff44', '#ff44ff', '#44ffff'][Math.floor(Math.random() * 6)] },
    { position: [rand(-80, 80), 0, rand(-80, 80)], color: ['#ff4444', '#4444ff', '#44ff44', '#ffff44', '#ff44ff', '#44ffff'][Math.floor(Math.random() * 6)] },
  ], [])

  const people = useMemo(() => {
    const result = []
    for (let i = 0; i < 30; i++) {
      result.push({
        position: [rand(-85, 85), 0, rand(-85, 85)],
        color: ['#ff8844', '#88ff44', '#4488ff', '#ff44aa', '#ffff44', '#44ffaa', '#ff88ff'][Math.floor(Math.random() * 7)],
      })
    }
    return result
  }, [])

  const streets = useMemo(() => [
    { from: [-100, 0, 0], to: [100, 0, 0] },
    { from: [0, 0, -100], to: [0, 0, 100] },
    { from: [-70, 0, -70], to: [70, 0, -70] },
    { from: [-70, 0, 70], to: [70, 0, 70] },
    { from: [-100, 0, 40], to: [100, 0, 40] },
    { from: [-100, 0, -40], to: [100, 0, -40] },
  ], [])

  return (
    <group>
      {streets.map((s, i) => (
        <Street key={`street-${i}`} {...s} />
      ))}

      {buildings.map((b, i) => (
        <Building key={`building-${i}`} {...b} />
      ))}

      {trees.map((t, i) => (
        <Tree key={`tree-${i}`} {...t} />
      ))}

      {cars.map((c, i) => (
        <Car key={`car-${i}`} {...c} />
      ))}

      {people.map((p, i) => (
        <Person key={`person-${i}`} {...p} />
      ))}
    </group>
  )
}

function Ground() {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
        <planeGeometry args={[300, 300]} />
        <meshStandardMaterial color="#0a1520" roughness={1} />
      </mesh>
      <gridHelper args={[200, 100, '#0a2535', '#0a1a25']} position={[0, 0, 0]} />
    </group>
  )
}

function CameraControls({ target, zoom }) {
  const { camera } = useThree()
  const targetPos = useRef(new THREE.Vector3(0, 80, 100))
  const targetLookAt = useRef(new THREE.Vector3(0, 0, 0))

  useEffect(() => {
    if (target) {
      targetPos.current.set(target.pos[0], 40, target.pos[2] + 50)
      targetLookAt.current.set(target.pos[0], 0, target.pos[2])
    } else if (zoom === 'city') {
      targetPos.current.set(0, 120, 150)
      targetLookAt.current.set(0, 0, 0)
    } else {
      targetPos.current.set(0, 80, 100)
      targetLookAt.current.set(0, 0, 0)
    }
  }, [target, zoom])

  useFrame(() => {
    camera.position.lerp(targetPos.current, 0.02)
    camera.lookAt(targetLookAt.current)
  })

  return null
}

function ZoneCircle({ data, onClick }) {
  const ref = useRef()
  const [hovered, setHovered] = useState(false)

  useFrame(({ clock }) => {
    if (ref.current) {
      const t = clock.getElapsedTime()
      ref.current.material.opacity = hovered ? 0.5 : 0.2
      ref.current.scale.setScalar(1 + Math.sin(t * 2) * 0.02)
    }
  })

  return (
    <mesh
      ref={ref}
      position={[data.pos[0], 0.02, data.pos[2]]}
      rotation={[-Math.PI / 2, 0, 0]}
      onClick={(e) => {
        e.stopPropagation()
        onClick(data)
      }}
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={() => setHovered(false)}
    >
      <circleGeometry args={[data.size, 32]} />
      <meshBasicMaterial color={data.color} transparent opacity={0.2} />
    </mesh>
  )
}

export default function AgentWorld({ onAgentSelect, selectedAgent }) {
  const [activeAgent, setActiveAgent] = useState(null)
  const [viewMode, setViewMode] = useState('city')

  const handleAgentClick = useCallback((agent) => {
    setActiveAgent(agent)
    setViewMode('agent')
    if (onAgentSelect) onAgentSelect(agent)
  }, [onAgentSelect])

  const handleZoneClick = useCallback((zone) => {
    const agent = AGENT_ZONES.find((a) => a.id === zone.id)
    if (agent) handleAgentClick(agent)
  }, [handleAgentClick])

  return (
    <>
      <color attach="background" args={['#020408']} />
      <fog attach="fog" args={['#020408', 100, 300]} />
      <ambientLight intensity={0.3} />
      <directionalLight position={[50, 100, 50]} intensity={0.6} color="#aabbcc" />
      <pointLight position={[0, 60, 0]} intensity={1} color="#00ffff" distance={150} />

      <Ground />

      <City />

      {AGENT_ZONES.map((zone) => (
        <group key={zone.id}>
          <ZoneCircle data={zone} onClick={handleZoneClick} />
          <AgentAvatar
            data={zone}
            onClick={handleAgentClick}
            isSelected={activeAgent?.id === zone.id}
          />
          {[...Array(Math.floor(zone.size / 6))].map((_, i) => (
            <AgriculturalRobot
              key={`robot-${zone.id}-${i}`}
              position={[
                zone.pos[0] + rand(-zone.size * 0.7, zone.size * 0.7),
                0.5,
                zone.pos[2] + rand(-zone.size * 0.7, zone.size * 0.7),
              ]}
              agentColor={zone.color}
              task={zone.workType}
            />
          ))}
        </group>
      ))}

      <CameraControls
        target={viewMode === 'agent' ? activeAgent : null}
        zoom={viewMode}
      />

      <Stars radius={250} depth={100} count={4000} factor={7} saturation={0.3} fade speed={0.5} />
    </>
  )
}

export { AGENT_ZONES }
