import React, { useRef, useMemo, useState, useCallback, useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Text, Html, Stars } from '@react-three/drei'
import * as THREE from 'three'

const NEIGHBORHOODS = [
  { id: 'HQ', name: 'CENTRAL HQ', pos: [0, 0, 0], color: '#ff4444', size: 15, agents: ['director_fury'] },
  { id: 'security', name: 'SECURITY GRID', pos: [-25, 0, -15], color: '#00ff88', size: 18, agents: ['heimdall'] },
  { id: 'planning', name: 'PLANNING ZONE', pos: [25, 0, -15], color: '#ffe600', size: 18, agents: ['john_kramer'] },
  { id: 'dispatch', name: 'DISPATCH HUB', pos: [-30, 0, 15], color: '#8b00ff', size: 20, agents: ['morpheus'] },
  { id: 'research', name: 'RESEARCH LAB', pos: [30, 0, 15], color: '#00d9ff', size: 20, agents: ['sherlock_holmes'] },
  { id: 'memory', name: 'MEMORY CORE', pos: [0, 0, -35], color: '#00ffff', size: 15, agents: ['data'] },
  { id: 'commerce', name: 'COMMERCE DISTRICT', pos: [-40, 0, -30], color: '#ffe600', size: 25, agents: ['midas'] },
  { id: 'creative', name: 'CREATIVE STUDIO', pos: [40, 0, -30], color: '#ff00aa', size: 22, agents: ['adforge'] },
  { id: 'legal', name: 'LEGAL OPS', pos: [-35, 0, 30], color: '#ff6600', size: 18, agents: ['saul_goodman'] },
  { id: 'build', name: 'BUILD BAY', pos: [35, 0, 30], color: '#4a9eff', size: 18, agents: ['jarvis_build'] },
  { id: 'bug_hunt', name: 'BUG HUNTERS', pos: [-45, 0, 0], color: '#ff0044', size: 20, agents: ['ripley'] },
  { id: 'design', name: 'DESIGN ATELIER', pos: [45, 0, 0], color: '#ff44aa', size: 20, agents: ['da_vinci'] },
  { id: 'ops', name: 'OPS CENTER', pos: [0, 0, 45], color: '#ffffff', size: 22, agents: ['john_wick'] },
]

const BUILDING_TYPES = [
  { name: 'Tower', floors: 8, width: 3, depth: 3, color: '#1a2a3a' },
  { name: 'Warehouse', floors: 2, width: 6, depth: 5, color: '#0d1520' },
  { name: 'Dome', floors: 1, width: 5, depth: 5, color: '#1a1a2e', isDome: true },
  { name: 'Antenna', floors: 4, width: 1, depth: 1, color: '#2a3a4a', isAntenna: true },
  { name: 'Bunker', floors: 1, width: 4, depth: 4, color: '#152025' },
]

function rand(min, max) {
  return Math.random() * (max - min) + min
}

function seededRand(seed, min, max) {
  const x = Math.sin(seed) * 10000
  return (x - Math.floor(x)) * (max - min) + min
}

function Building({ position, type, seed }) {
  const ref = useRef()
  const { floors, width, depth, color, isDome, isAntenna } = type

  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.position.y = Math.sin(clock.getElapsedTime() * 0.3 + seed) * 0.02
    }
  })

  if (isDome) {
    return (
      <group position={position}>
        <mesh ref={ref}>
          <sphereGeometry args={[width / 2, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
          <meshStandardMaterial color={color} metalness={0.8} roughness={0.2} transparent opacity={0.85} />
        </mesh>
        <mesh position={[0, -0.5, 0]}>
          <cylinderGeometry args={[width / 2.2, width / 2, 0.3, 16]} />
          <meshStandardMaterial color="#0a1520" metalness={0.9} roughness={0.1} />
        </mesh>
      </group>
    )
  }

  if (isAntenna) {
    return (
      <group position={position}>
        {[...Array(floors)].map((_, i) => (
          <mesh key={i} position={[0, i * 2 + 1, 0]}>
            <boxGeometry args={[width, 1.8, depth]} />
            <meshStandardMaterial color={color} metalness={0.7} roughness={0.3} />
          </mesh>
        ))}
        <mesh position={[0, floors * 2 + 2, 0]}>
          <coneGeometry args={[0.5, 2, 8]} />
          <meshStandardMaterial color="#ff0044" emissive="#ff0044" emissiveIntensity={2} />
        </mesh>
        <mesh position={[0, floors * 2 + 0.5, 0]}>
          <torusGeometry args={[1.5, 0.05, 8, 32]} />
          <meshStandardMaterial color="#00ffff" emissive="#00ffff" emissiveIntensity={1.5} />
        </mesh>
      </group>
    )
  }

  return (
    <group position={position}>
      {[...Array(floors)].map((_, i) => (
        <mesh key={i} position={[0, i * 3 + 1.5, 0]}>
          <boxGeometry args={[width, 2.8, depth]} />
          <meshStandardMaterial color={color} metalness={0.6} roughness={0.4} />
        </mesh>
      ))}
      <mesh position={[0, floors * 3 + 0.2, 0]}>
        <boxGeometry args={[width * 1.1, 0.3, depth * 1.1]} />
        <meshStandardMaterial color="#0a1a2a" metalness={0.9} roughness={0.1} />
      </mesh>
      {width > 3 && [...Array(Math.floor(width))].map((_, i) => (
        <mesh key={`light-${i}`} position={[(i - (width - 1) / 2) * (width / (width - 1)), floors * 3 + 1, 0]}>
          <sphereGeometry args={[0.15, 8, 8]} />
          <meshStandardMaterial color="#00ffff" emissive="#00ffff" emissiveIntensity={3} />
        </mesh>
      ))}
    </group>
  )
}

function Infrastructure({ position, type }) {
  if (type === 'solar') {
    return (
      <group position={position}>
        <mesh rotation={[-Math.PI / 6, 0, 0]}>
          <planeGeometry args={[8, 5]} />
          <meshStandardMaterial color="#1a3a5a" metalness={0.9} roughness={0.1} />
        </mesh>
        <mesh position={[0, -2, 0]}>
          <boxGeometry args={[0.3, 4, 0.3]} />
          <meshStandardMaterial color="#2a3a4a" metalness={0.7} roughness={0.3} />
        </mesh>
      </group>
    )
  }
  if (type === 'tank') {
    return (
      <group position={position}>
        <mesh>
          <cylinderGeometry args={[3, 3, 4, 16]} />
          <meshStandardMaterial color="#152530" metalness={0.8} roughness={0.2} />
        </mesh>
        <mesh position={[0, 2.5, 0]}>
          <coneGeometry args={[3.2, 1, 16]} />
          <meshStandardMaterial color="#1a3040" metalness={0.7} roughness={0.3} />
        </mesh>
      </group>
    )
  }
  if (type === 'antenna') {
    return (
      <group position={position}>
        <mesh position={[0, 5, 0]}>
          <cylinderGeometry args={[0.1, 0.1, 10, 8]} />
          <meshStandardMaterial color="#3a4a5a" metalness={0.9} roughness={0.1} />
        </mesh>
        {[2, 4, 6, 8].map((h, i) => (
          <mesh key={h} position={[0, h, 0]} rotation={[0, i * 0.5, Math.PI / 2]}>
            <torusGeometry args={[1.5 - i * 0.3, 0.05, 8, 16]} />
            <meshStandardMaterial color="#00ffff" emissive="#00ffff" emissiveIntensity={1} />
          </mesh>
        ))}
        <mesh position={[0, 10.5, 0]}>
          <sphereGeometry args={[0.2, 8, 8]} />
          <meshStandardMaterial color="#ff0044" emissive="#ff0044" emissiveIntensity={3} />
        </mesh>
      </group>
    )
  }
  return null
}

function AgriculturalRobot({ position, id, color, task }) {
  const groupRef = useRef()
  const wheelRefs = useRef([])
  const [pos] = useState(() => ({
    x: position[0],
    y: position[1],
    z: position[2],
    targetX: position[0],
    targetZ: position[2],
    speed: rand(0.5, 1.5),
    rotation: rand(0, Math.PI * 2),
    taskTimer: rand(3, 8),
    workingTimer: 0,
    isWorking: false,
    armAngle: 0,
  }))

  useFrame(({ clock }, delta) => {
    if (!groupRef.current) return
    const t = clock.getElapsedTime()
    const p = pos

    p.taskTimer -= delta
    if (p.taskTimer <= 0) {
      p.targetX = p.x + rand(-8, 8)
      p.targetZ = p.z + rand(-8, 8)
      p.taskTimer = rand(5, 15)
      p.isWorking = rand(0, 1) > 0.5
    }

    const dx = p.targetX - p.x
    const dz = p.targetZ - p.z
    const dist = Math.sqrt(dx * dx + dz * dz)

    if (dist > 0.1) {
      p.x += (dx / dist) * p.speed * delta * 2
      p.z += (dz / dist) * p.speed * delta * 2
      p.rotation = Math.atan2(dx, dz)
      p.isWorking = false
    } else if (p.isWorking) {
      p.workingTimer += delta
    }

    groupRef.current.position.set(p.x, p.y, p.z)
    groupRef.current.rotation.y = p.rotation

    const bobY = Math.sin(t * 3 + id.charCodeAt(0)) * 0.05
    groupRef.current.position.y = p.y + bobY

    wheelRefs.current.forEach((w, i) => {
      if (w) {
        w.rotation.x += p.speed * delta * 3
      }
    })

    if (groupRef.current.children[1]) {
      groupRef.current.children[1].rotation.x = Math.sin(t * 2 + id.charCodeAt(0)) * 0.3
    }
  })

  return (
    <group ref={groupRef} position={position}>
      <mesh>
        <boxGeometry args={[1.2, 0.8, 1.6]} />
        <meshStandardMaterial color="#2a3a4a" metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[0, 0.7, 0.3]}>
        <boxGeometry args={[0.8, 0.6, 0.4]} />
        <meshStandardMaterial color="#1a2a3a" metalness={0.7} roughness={0.3} />
      </mesh>
      <mesh position={[0, 0.95, 0.3]}>
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={1.5} />
      </mesh>
      <group position={[0, 0.3, 0.9]}>
        <mesh>
          <boxGeometry args={[0.15, 0.8, 0.15]} />
          <meshStandardMaterial color="#3a4a5a" metalness={0.7} roughness={0.3} />
        </mesh>
        <mesh position={[0, 0.5, 0]}>
          <boxGeometry args={[0.4, 0.1, 0.3]} />
          <meshStandardMaterial color="#4a5a6a" metalness={0.6} roughness={0.4} />
        </mesh>
      </group>
      {[...Array(4)].map((_, i) => (
        <mesh
          key={`wheel-${i}`}
          ref={el => wheelRefs.current[i] = el}
          position={[
            (i % 2 === 0 ? -0.7 : 0.7),
            -0.3,
            (i < 2 ? -0.5 : 0.5)
          ]}
          rotation={[0, 0, Math.PI / 2]}
        >
          <cylinderGeometry args={[0.3, 0.3, 0.2, 12]} />
          <meshStandardMaterial color="#1a1a1a" metalness={0.5} roughness={0.5} />
        </mesh>
      ))}
      {pos.isWorking && (
        <mesh position={[0, -0.2, 0]}>
          <circleGeometry args={[0.8, 16]} />
          <meshStandardMaterial color="#00ff8844" emissive="#00ff88" emissiveIntensity={0.5} transparent opacity={0.5} />
        </mesh>
      )}
    </group>
  )
}

function Person({ position, color }) {
  const ref = useRef()
  const speed = rand(0.3, 0.8)
  const [pos] = useState(() => ({
    x: position[0],
    z: position[2],
    targetX: position[0],
    targetZ: position[2],
    timer: rand(2, 6),
  }))

  useFrame((_, delta) => {
    if (!ref.current) return
    const p = pos
    p.timer -= delta

    if (p.timer <= 0) {
      p.targetX = p.x + rand(-5, 5)
      p.targetZ = p.z + rand(-5, 5)
      p.timer = rand(3, 8)
    }

    const dx = p.targetX - p.x
    const dz = p.targetZ - p.z
    const dist = Math.sqrt(dx * dx + dz * dz)

    if (dist > 0.05) {
      p.x += (dx / dist) * speed * delta
      p.z += (dz / dist) * speed * delta
      ref.current.rotation.y = Math.atan2(dx, dz)
    }

    ref.current.position.set(p.x, p.y || 0, p.z)
  })

  return (
    <group ref={ref} position={position}>
      <mesh position={[0, 0.9, 0]}>
        <sphereGeometry args={[0.15, 8, 8]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0, 0.4, 0]}>
        <capsuleGeometry args={[0.12, 0.4, 4, 8]} />
        <meshStandardMaterial color={color} />
      </mesh>
    </group>
  )
}

function Vehicle({ position, color, type }) {
  const ref = useRef()
  const [pos] = useState(() => ({
    x: position[0],
    z: position[2],
    targetX: position[0] + rand(-15, 15),
    targetZ: position[2] + rand(-15, 15),
    speed: rand(2, 5),
    rotation: 0,
    timer: rand(5, 12),
  }))

  useFrame((_, delta) => {
    if (!ref.current) return
    const p = pos
    p.timer -= delta

    if (p.timer <= 0) {
      p.targetX = p.x + rand(-20, 20)
      p.targetZ = p.z + rand(-20, 20)
      p.timer = rand(8, 18)
    }

    const dx = p.targetX - p.x
    const dz = p.targetZ - p.z
    const dist = Math.sqrt(dx * dx + dz * dz)

    if (dist > 0.5) {
      p.x += (dx / dist) * p.speed * delta
      p.z += (dz / dist) * p.speed * delta
      p.rotation = Math.atan2(dx, dz)
    }

    ref.current.position.set(p.x, 0.4, p.z)
    ref.current.rotation.y = p.rotation
  })

  const isDrone = type === 'drone'
  const isCar = type === 'car'

  return (
    <group ref={ref} position={position} rotation={[0, pos.rotation, 0]}>
      {isDrone && (
        <>
          <mesh>
            <boxGeometry args={[1.5, 0.2, 1]} />
            <meshStandardMaterial color="#2a3a4a" metalness={0.8} roughness={0.2} />
          </mesh>
          {[...Array(4)].map((_, i) => (
            <mesh key={`prop-${i}`} position={[(i % 2 === 0 ? -0.9 : 0.9), 0.2, (i < 2 ? -0.4 : 0.4)]}>
              <cylinderGeometry args={[0.05, 0.05, 0.8, 8]} />
              <meshStandardMaterial color="#1a2a3a" metalness={0.7} roughness={0.3} />
            </mesh>
          ))}
          <pointLight color="#00ffff" intensity={2} distance={5} />
        </>
      )}
      {isCar && (
        <>
          <mesh position={[0, 0.2, 0]}>
            <boxGeometry args={[0.8, 0.4, 1.8]} />
            <meshStandardMaterial color={color} metalness={0.7} roughness={0.3} />
          </mesh>
          <mesh position={[0, 0.5, -0.2]}>
            <boxGeometry args={[0.6, 0.3, 0.8]} />
            <meshStandardMaterial color="#1a2a3a" metalness={0.5} roughness={0.5} transparent opacity={0.7} />
          </mesh>
          {[...Array(4)].map((_, i) => (
            <mesh key={`wheel-${i}`} position={[(i % 2 === 0 ? -0.35 : 0.35), -0.1, (i < 2 ? -0.6 : 0.6)]} rotation={[0, 0, Math.PI / 2]}>
              <cylinderGeometry args={[0.2, 0.2, 0.15, 12]} />
              <meshStandardMaterial color="#1a1a1a" metalness={0.5} roughness={0.5} />
            </mesh>
          ))}
        </>
      )}
    </group>
  )
}

function Neighborhood({ data, onAgentClick, selectedAgent }) {
  const groupRef = useRef()
  const buildings = useMemo(() => {
    const result = []
    for (let i = 0; i < Math.floor(data.size / 3); i++) {
      const angle = (i / Math.floor(data.size / 3)) * Math.PI * 2
      const radius = rand(data.size * 0.3, data.size * 0.7)
      const x = data.pos[0] + Math.cos(angle) * radius
      const z = data.pos[2] + Math.sin(angle) * radius
      const typeIdx = Math.floor(seededRand(i * 13 + data.id.charCodeAt(0), 0, BUILDING_TYPES.length))
      result.push({
        position: [x, 0, z],
        type: BUILDING_TYPES[typeIdx],
        seed: i * 7 + data.id.charCodeAt(0),
      })
    }
    return result
  }, [data])

  const infrastructure = useMemo(() => [
    { position: [data.pos[0] + rand(-5, 5), 0, data.pos[2] + rand(-5, 5)], type: 'solar' },
    { position: [data.pos[0] + rand(-5, 5), 0, data.pos[2] + rand(-5, 5)], type: 'tank' },
    { position: [data.pos[0] + rand(-3, 3), 0, data.pos[2] + rand(-3, 3)], type: 'antenna' },
  ], [data])

  const robots = useMemo(() => [...Array(Math.floor(data.size / 6))].map((_, i) => ({
    position: [
      data.pos[0] + rand(-data.size * 0.5, data.size * 0.5),
      0.5,
      data.pos[2] + rand(-data.size * 0.5, data.size * 0.5)
    ],
    id: `${data.id}-robot-${i}`,
    color: data.color,
    task: ['plowing', 'planting', 'harvesting', 'monitoring'][i % 4],
  })), [data])

  const people = useMemo(() => [...Array(Math.floor(data.size / 4))].map((_, i) => ({
    position: [
      data.pos[0] + rand(-data.size * 0.4, data.size * 0.4),
      0,
      data.pos[2] + rand(-data.size * 0.4, data.size * 0.4)
    ],
    color: ['#ff8844', '#88ff44', '#4488ff', '#ff44aa', '#ffff44'][i % 5],
  })), [data])

  const vehicles = useMemo(() => [
    {
      position: [data.pos[0] + rand(-8, 8), 0, data.pos[2] + rand(-8, 8)],
      color: '#ff4444',
      type: 'car',
    },
    {
      position: [data.pos[0] + rand(-8, 8), 2, data.pos[2] + rand(-8, 8)],
      color: '#00ffff',
      type: 'drone',
    },
  ], [data])

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.position.y = Math.sin(clock.getElapsedTime() * 0.2 + data.id.charCodeAt(0)) * 0.03
    }
  })

  return (
    <group ref={groupRef}>
      <mesh position={[data.pos[0], -0.05, data.pos[2]]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[data.size, 32]} />
        <meshStandardMaterial color="#0a1520" transparent opacity={0.6} />
      </mesh>
      <mesh position={[data.pos[0], -0.04, data.pos[2]]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[data.size * 0.95, data.size, 32]} />
        <meshStandardMaterial color={data.color} emissive={data.color} emissiveIntensity={0.5} transparent opacity={0.8} />
      </mesh>

      {buildings.map((b, i) => (
        <Building key={`${data.id}-bld-${i}`} {...b} />
      ))}

      {infrastructure.map((inf, i) => (
        <Infrastructure key={`${data.id}-inf-${i}`} {...inf} />
      ))}

      {robots.map((r, i) => (
        <AgriculturalRobot key={`${data.id}-robot-${i}`} {...r} />
      ))}

      {people.map((p, i) => (
        <Person key={`${data.id}-person-${i}`} {...p} />
      ))}

      {vehicles.map((v, i) => (
        <Vehicle key={`${data.id}-vehicle-${i}`} {...v} />
      ))}

      <Text
        position={[data.pos[0], data.size * 0.5 + 3, data.pos[2]]}
        fontSize={1.5}
        color={data.color}
        anchorX="center"
        anchorY="middle"
        font="https://fonts.gstatic.com/s/orbitron/v29/yMJRMIlzdpvBhQQL_Qq7dy0.woff2"
        outlineWidth={0.05}
        outlineColor="#000000"
      >
        {data.name}
      </Text>
    </group>
  )
}

function GridFloor() {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]}>
        <planeGeometry args={[300, 300, 60, 60]} />
        <meshStandardMaterial color="#050a10" wireframe={false} />
      </mesh>
      <gridHelper args={[300, 60, '#0a2040', '#0a1525']} position={[0, 0, 0]} />
    </group>
  )
}

function CameraController({ zoomLevel, targetNeighborhood }) {
  const { camera } = useThree()
  const targetPos = useRef(new THREE.Vector3(0, 60, 80))
  const targetLookAt = useRef(new THREE.Vector3(0, 0, 0))

  useEffect(() => {
    if (targetNeighborhood) {
      const n = NEIGHBORHOODS.find(nh => nh.id === targetNeighborhood)
      if (n) {
        targetPos.current.set(n.pos[0], n.size * 2 + 15, n.pos[2] + n.size + 10)
        targetLookAt.current.set(n.pos[0], 0, n.pos[2])
      }
    } else {
      targetPos.current.set(0, 60, 80)
      targetLookAt.current.set(0, 0, 0)
    }
  }, [targetNeighborhood, zoomLevel])

  useFrame(() => {
    camera.position.lerp(targetPos.current, 0.02)
    const lookTarget = new THREE.Vector3()
    camera.getWorldDirection(lookTarget)
    const currentLookAt = new THREE.Vector3()
    camera.getWorldDirection(currentLookAt)
    currentLookAt.lerp(targetLookAt.current, 0.02)
    camera.lookAt(targetLookAt.current)
  })

  return null
}

export default function AgentMap3D({
  onClose,
  onNeighborhoodSelect,
  selectedAgent,
  onAgentClick,
}) {
  const [activeNeighborhood, setActiveNeighborhood] = useState(null)
  const [viewMode, setViewMode] = useState('overview')
  const [hoveredNeighborhood, setHoveredNeighborhood] = useState(null)

  const handleNeighborhoodClick = useCallback((nh) => {
    setActiveNeighborhood(nh.id)
    setViewMode('district')
    if (onNeighborhoodSelect) onNeighborhoodSelect(nh)
  }, [onNeighborhoodSelect])

  const handleBack = useCallback(() => {
    setActiveNeighborhood(null)
    setViewMode('overview')
  }, [])

  return (
    <>
      <color attach="background" args={['#030308']} />
      <fog attach="fog" args={['#030308', 80, 250]} />
      <ambientLight intensity={0.15} />
      <directionalLight position={[50, 100, 50]} intensity={0.4} color="#8899bb" />
      <pointLight position={[0, 50, 0]} intensity={1} color="#00ffff" distance={100} />
      <Stars radius={200} depth={100} count={3000} factor={6} saturation={0.5} fade speed={0.5} />

      <GridFloor />

      {NEIGHBORHOODS.map((nh) => (
        <group key={nh.id}>
          <mesh
            position={[nh.pos[0], 0.1, nh.pos[2]]}
            rotation={[-Math.PI / 2, 0, 0]}
            onClick={() => handleNeighborhoodClick(nh)}
            onPointerOver={() => setHoveredNeighborhood(nh.id)}
            onPointerOut={() => setHoveredNeighborhood(null)}
          >
            <circleGeometry args={[nh.size + 2, 32]} />
            <meshBasicMaterial
              color={hoveredNeighborhood === nh.id ? nh.color : '#0a1520'}
              transparent
              opacity={hoveredNeighborhood === nh.id ? 0.4 : 0.15}
            />
          </mesh>
          <Neighborhood
            data={nh}
            onAgentClick={onAgentClick}
            selectedAgent={selectedAgent}
          />
        </group>
      ))}

      <CameraController
        zoomLevel={viewMode === 'district' ? 'zoom' : 'overview'}
        targetNeighborhood={activeNeighborhood}
      />

      <Html
        position={[0, 0.5, 0]}
        center
        distanceFactor={80}
        style={{ pointerEvents: 'none' }}
      >
        <div style={{
          fontFamily: 'Orbitron, monospace',
          fontSize: '10px',
          color: '#00ffff',
          textShadow: '0 0 10px #00ffff',
          textAlign: 'center',
          whiteSpace: 'nowrap',
        }}>
          {'█'.repeat(40)}<br />
          JARVIS CITY OVERVIEW<br />
          {'█'.repeat(40)}
        </div>
      </Html>
    </>
  )
}

export { NEIGHBORHOODS }
