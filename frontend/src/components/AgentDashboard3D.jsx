import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars, Text, Box, Sphere, Cylinder, Cone, Trail, Float, MeshDistortMaterial, MeshWobbleMaterial, GradientTexture, Environment, ContactShadows, useTexture } from '@react-three/drei';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';

// ============================================
// AGENT 3D COMPONENTS
// ============================================

const AgentCore = ({ color, active, onClick }) => {
  const meshRef = useRef();
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01;
      meshRef.current.rotation.z += 0.005;
      const scale = active ? 1.2 : 1 + Math.sin(state.clock.elapsedTime * 2) * 0.1;
      meshRef.current.scale.setScalar(scale);
    }
  });

  return (
    <group onClick={onClick}>
      <Sphere ref={meshRef} args={[1, 64, 64]}>
        <MeshDistortMaterial
          color={color}
          distort={0.3}
          speed={2}
          roughness={0.2}
          metalness={0.8}
          emissive={color}
          emissiveIntensity={active ? 0.5 : 0.2}
        />
      </Sphere>
      <pointLight color={color} intensity={2} distance={5} />
    </group>
  );
};

const OrbitingParticles = ({ count = 20, color, radius = 2.5 }) => {
  const particles = useMemo(() => {
    return Array.from({ length: count }, (_, i) => ({
      angle: (i / count) * Math.PI * 2,
      speed: 0.5 + Math.random() * 0.5,
      yOffset: (Math.random() - 0.5) * 2,
      size: 0.1 + Math.random() * 0.2,
    }));
  }, [count]);

  const groupRef = useRef();

  useFrame((state) => {
    if (groupRef.current) {
      particles.forEach((particle, i) => {
        const child = groupRef.current.children[i];
        if (child) {
          const angle = particle.angle + state.clock.elapsedTime * particle.speed;
          child.position.x = Math.cos(angle) * radius;
          child.position.z = Math.sin(angle) * radius;
          child.position.y = particle.yOffset + Math.sin(state.clock.elapsedTime * 2 + i) * 0.3;
          child.rotation.x += 0.02;
          child.rotation.y += 0.03;
        }
      });
    }
  });

  return (
    <group ref={groupRef}>
      {particles.map((p, i) => (
        <Box key={i} args={[p.size, p.size, p.size]}>
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={0.5}
            metalness={0.9}
            roughness={0.1}
          />
        </Box>
      ))}
    </group>
  );
};

const AgentNode = ({ position, type, name, status, earnings, color, onSelect, isSelected }) => {
  const colors = {
    commander: '#ff0000',
    analyst: '#00ff00',
    implementer: '#0000ff',
    integrator: '#ffff00',
    replicator: '#ff00ff',
  };

  const agentColor = colors[type] || color || '#ffffff';

  return (
    <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
      <group position={position} onClick={() => onSelect({ name, type, status, earnings })}>
        <AgentCore color={agentColor} active={isSelected} />
        <OrbitingParticles count={15} color={agentColor} radius={2} />
        
        {/* Agent Label */}
        <Text
          position={[0, -1.8, 0]}
          fontSize={0.3}
          color="white"
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.02}
          outlineColor="black"
        >
          {name}
        </Text>

        {/* Status Indicator */}
        <mesh position={[1.2, 0, 0]}>
          <sphereGeometry args={[0.15, 16, 16]} />
          <meshStandardMaterial 
            color={status === 'active' ? '#00ff00' : status === 'working' ? '#ffff00' : '#ff0000'} 
            emissive={status === 'active' ? '#00ff00' : status === 'working' ? '#ffff00' : '#ff0000'}
            emissiveIntensity={0.5}
          />
        </mesh>

        {/* Earnings Badge */}
        {earnings > 0 && (
          <group position={[-1.2, 0.8, 0]}>
            <Cylinder args={[0.3, 0.3, 0.1, 32]} rotation={[Math.PI / 2, 0, 0]}>
              <meshStandardMaterial color="#ffd700" metalness={0.8} roughness={0.2} />
            </Cylinder>
            <Text
              position={[0, 0, 0.06]}
              fontSize={0.15}
              color="#000"
              anchorX="center"
              anchorY="middle"
              font="/fonts/Roboto-Bold.ttf"
            >
              ${earnings}
            </Text>
          </group>
        )}
      </group>
    </Float>
  );
};

// ============================================
// CONNECTION LINES
// ============================================

const ConnectionLine = ({ start, end, active }) => {
  const points = useMemo(() => {
    return [new THREE.Vector3(...start), new THREE.Vector3(...end)];
  }, [start, end]);

  const lineRef = useRef();

  useFrame((state) => {
    if (lineRef.current && active) {
      const progress = (state.clock.elapsedTime * 2) % 1;
      lineRef.current.material.dashOffset = -progress * 10;
    }
  });

  return (
    <line ref={lineRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={2}
          array={new Float32Array([...start, ...end])}
          itemSize={3}
        />
      </bufferGeometry>
      <lineDashedMaterial
        color={active ? "#00ff00" : "#444444"}
        dashSize={0.5}
        gapSize={0.3}
        linewidth={2}
      />
    </line>
  );
};

// ============================================
// MAIN SCENE
// ============================================

const Scene = ({ agents, selectedAgent, onSelectAgent }) => {
  const connections = [
    { from: 0, to: 1 },
    { from: 0, to: 2 },
    { from: 0, to: 3 },
    { from: 0, to: 4 },
    { from: 1, to: 2 },
    { from: 2, to: 3 },
    { from: 3, to: 4 },
  ];

  return (
    <>
      <ambientLight intensity={0.3} />
      <directionalLight position={[10, 10, 5]} intensity={1} color="#ffffff" />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#00ffff" />
      <pointLight position={[10, -10, -10]} intensity={0.5} color="#ff00ff" />
      
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
      
      {/* Grid Floor */}
      <gridHelper args={[50, 50, '#333333', '#222222']} position={[0, -5, 0]} />
      
      {/* Connection Lines */}
      {connections.map((conn, idx) => (
        <ConnectionLine
          key={idx}
          start={agents[conn.from]?.position || [0, 0, 0]}
          end={agents[conn.to]?.position || [0, 0, 0]}
          active={agents[conn.from]?.status === 'active' && agents[conn.to]?.status === 'active'}
        />
      ))}
      
      {/* Agent Nodes */}
      {agents.map((agent, idx) => (
        <AgentNode
          key={idx}
          position={agent.position}
          type={agent.type}
          name={agent.name}
          status={agent.status}
          earnings={agent.earnings}
          onSelect={onSelectAgent}
          isSelected={selectedAgent?.name === agent.name}
        />
      ))}
      
      <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
    </>
  );
};

// ============================================
// UI COMPONENTS
// ============================================

const AgentInfoPanel = ({ agent, onClose }) => {
  if (!agent) return null;

  const typeDescriptions = {
    commander: 'Agent suprem coordonator. Gestionează toate operațiunile și ia decizii strategice.',
    analyst: 'Analizează date complexe, video-uri și extrage informații cheie.',
    implementer: 'Implementează funcționalități și generează cod de înaltă calitate.',
    integrator: 'Gestionează deploy-ul în multiple ecosisteme și platforme.',
    replicator: 'Replica design-uri UI din video-uri și generează componente.',
  };

  return (
    <motion.div
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 300, opacity: 0 }}
      className="fixed right-0 top-0 h-full w-96 bg-black/90 backdrop-blur-xl border-l border-cyan-500/30 p-6 overflow-y-auto z-50"
    >
      <button
        onClick={onClose}
        className="absolute top-4 right-4 text-cyan-400 hover:text-cyan-200 transition-colors"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <div className="mt-8">
        <div className={`w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center text-3xl font-bold
          ${agent.type === 'commander' ? 'bg-red-500/20 text-red-400 border-2 border-red-500' : ''}
          ${agent.type === 'analyst' ? 'bg-green-500/20 text-green-400 border-2 border-green-500' : ''}
          ${agent.type === 'implementer' ? 'bg-blue-500/20 text-blue-400 border-2 border-blue-500' : ''}
          ${agent.type === 'integrator' ? 'bg-yellow-500/20 text-yellow-400 border-2 border-yellow-500' : ''}
          ${agent.type === 'replicator' ? 'bg-purple-500/20 text-purple-400 border-2 border-purple-500' : ''}
        `}>
          {agent.name.charAt(0)}
        </div>

        <h2 className="text-2xl font-bold text-center text-white mb-2">{agent.name}</h2>
        <p className="text-center text-cyan-400 text-sm uppercase tracking-wider mb-6">{agent.type}</p>

        <div className="space-y-4">
          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="text-cyan-400 text-sm font-semibold mb-2">Status</h3>
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${
                agent.status === 'active' ? 'bg-green-500 animate-pulse' :
                agent.status === 'working' ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span className="text-white capitalize">{agent.status}</span>
            </div>
          </div>

          {agent.earnings > 0 && (
            <div className="bg-gradient-to-r from-yellow-500/20 to-amber-500/20 rounded-lg p-4 border border-yellow-500/30">
              <h3 className="text-yellow-400 text-sm font-semibold mb-1">💰 Câștiguri Generate</h3>
              <p className="text-2xl font-bold text-white">${agent.earnings.toLocaleString()}</p>
            </div>
          )}

          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="text-cyan-400 text-sm font-semibold mb-2">Descriere</h3>
            <p className="text-gray-300 text-sm leading-relaxed">
              {typeDescriptions[agent.type] || 'Agent specializat pentru operațiuni JARVIS.'}
            </p>
          </div>

          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="text-cyan-400 text-sm font-semibold mb-2">Capabilități</h3>
            <ul className="space-y-1">
              {agent.type === 'commander' && (
                <>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">⚡</span> Orchestrare completă</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">🧠</span> Decizii autonome</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">📊</span> Monitoring real-time</li>
                </>
              )}
              {agent.type === 'analyst' && (
                <>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">🎥</span> Analiză video</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">📝</span> OCR & Extracție text</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">🔍</span> Pattern recognition</li>
                </>
              )}
              {agent.type === 'implementer' && (
                <>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">💻</span> Code generation</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">🔧</span> Feature implementation</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">🧪</span> Testing & validation</li>
                </>
              )}
              {agent.type === 'integrator' && (
                <>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">🚀</span> Multi-ecosystem deploy</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">⚙️</span> Auto-configuration</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">🔄</span> Rollback capability</li>
                </>
              )}
              {agent.type === 'replicator' && (
                <>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">🎨</span> UI analysis</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">🎯</span> Design extraction</li>
                  <li className="text-gray-300 text-sm flex items-center gap-2"><span className="text-cyan-400">✨</span> Component generation</li>
                </>
              )}
            </ul>
          </div>

          <button
            onClick={onClose}
            className="w-full py-3 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg text-white font-semibold hover:from-cyan-400 hover:to-blue-400 transition-all"
          >
            Închide
          </button>
        </div>
      </div>
    </motion.div>
  );
};

// ============================================
// MONETIZATION DASHBOARD
// ============================================

const MonetizationDashboard = ({ totalEarnings, agentEarnings, onClose }) => {
  const [timeframe, setTimeframe] = useState('24h');
  
  const stats = {
    '24h': { earnings: totalEarnings, transactions: 156, growth: '+12.5%' },
    '7d': { earnings: totalEarnings * 7, transactions: 1092, growth: '+18.3%' },
    '30d': { earnings: totalEarnings * 30, transactions: 4680, growth: '+25.7%' },
  };

  const currentStats = stats[timeframe];

  return (
    <motion.div
      initial={{ y: 300, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: 300, opacity: 0 }}
      className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-black via-black/95 to-transparent p-6 z-40"
    >
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <span className="text-yellow-400">💰</span> Monetizare în Timp Real
          </h2>
          <div className="flex gap-2">
            {['24h', '7d', '30d'].map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  timeframe === tf
                    ? 'bg-gradient-to-r from-yellow-500 to-amber-500 text-white'
                    : 'bg-white/10 text-gray-400 hover:bg-white/20'
                }`}
              >
                {tf === '24h' ? '24 Ore' : tf === '7d' ? '7 Zile' : '30 Zile'}
              </button>
            ))}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gradient-to-br from-yellow-500/20 to-amber-500/20 rounded-xl p-4 border border-yellow-500/30">
            <p className="text-yellow-400 text-sm font-medium mb-1">Venit Total</p>
            <p className="text-3xl font-bold text-white">${currentStats.earnings.toLocaleString()}</p>
            <p className="text-green-400 text-sm mt-1">{currentStats.growth} vs perioada anterioară</p>
          </div>

          <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-xl p-4 border border-cyan-500/30">
            <p className="text-cyan-400 text-sm font-medium mb-1">Tranzacții</p>
            <p className="text-3xl font-bold text-white">{currentStats.transactions.toLocaleString()}</p>
            <p className="text-gray-400 text-sm mt-1">Completate cu succes</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl p-4 border border-purple-500/30">
            <p className="text-purple-400 text-sm font-medium mb-1">Agenți Activi</p>
            <p className="text-3xl font-bold text-white">{agentEarnings.length}</p>
            <p className="text-gray-400 text-sm mt-1">Toți operaționali</p>
          </div>

          <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-xl p-4 border border-green-500/30">
            <p className="text-green-400 text-sm font-medium mb-1">Rata de Succes</p>
            <p className="text-3xl font-bold text-white">98.5%</p>
            <p className="text-green-400 text-sm mt-1">↑ 2.3% vs luna trecută</p>
          </div>
        </div>

        {/* Top Agents by Earnings */}
        <div className="bg-white/5 rounded-xl p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Top Agenți după Venituri Generate</h3>
          <div className="space-y-3">
            {agentEarnings
              .sort((a, b) => b.earnings - a.earnings)
              .slice(0, 5)
              .map((agent, idx) => (
                <div key={idx} className="flex items-center gap-4 bg-white/5 rounded-lg p-3">
                  <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                    idx === 0 ? 'bg-yellow-500 text-black' :
                    idx === 1 ? 'bg-gray-300 text-black' :
                    idx === 2 ? 'bg-amber-600 text-white' :
                    'bg-white/10 text-white'
                  }`}>
                    {idx + 1}
                  </span>
                  <div className="flex-1">
                    <p className="text-white font-medium">{agent.name}</p>
                    <p className="text-gray-400 text-sm">{agent.type}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-yellow-400 font-bold">${agent.earnings.toLocaleString()}</p>
                    <p className="text-green-400 text-sm">+{agent.growth}%</p>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// ============================================
// MAIN DASHBOARD COMPONENT
// ============================================

const AgentDashboard3D = () => {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [showMonetization, setShowMonetization] = useState(false);
  const [totalEarnings, setTotalEarnings] = useState(15750);

  const agents = [
    { position: [0, 0, 0], type: 'commander', name: 'Supreme Commander', status: 'active', earnings: 5250 },
    { position: [6, 2, -4], type: 'analyst', name: 'Video Analyzer', status: 'active', earnings: 3200 },
    { position: [-6, -1, -4], type: 'implementer', name: 'Feature Implementer', status: 'working', earnings: 2800 },
    { position: [4, -3, 4], type: 'replicator', name: 'UI Replicator', status: 'active', earnings: 2200 },
    { position: [-4, 2, 4], type: 'integrator', name: 'Ecosystem Integrator', status: 'working', earnings: 2300 },
  ];

  useEffect(() => {
    // Simulate real-time earnings updates
    const interval = setInterval(() => {
      setTotalEarnings(prev => prev + Math.floor(Math.random() * 50) + 10);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full h-screen bg-black overflow-hidden relative">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 p-6 flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
              JARVIS
            </span>{' '}
            Agent Network
          </h1>
          <p className="text-gray-400">Sistem Multi-Agent cu Monetizare Reală</p>
        </div>
        
        <div className="flex gap-4">
          <button
            onClick={() => setShowMonetization(!showMonetization)}
            className="px-6 py-3 bg-gradient-to-r from-yellow-500 to-amber-500 rounded-lg text-black font-bold hover:from-yellow-400 hover:to-amber-400 transition-all flex items-center gap-2"
          >
            <span>💰</span>
            ${totalEarnings.toLocaleString()}
          </button>
        </div>
      </div>

      {/* 3D Scene */}
      <div className="w-full h-full">
        <Canvas camera={{ position: [0, 5, 15], fov: 60 }}>
          <Scene
            agents={agents}
            selectedAgent={selectedAgent}
            onSelectAgent={setSelectedAgent}
          />
        </Canvas>
      </div>

      {/* Instructions */}
      <div className="absolute bottom-6 left-6 z-10 text-gray-400 text-sm">
        <p>🖱️ Click pe un agent pentru detalii</p>
        <p>🖱️ Drag pentru a roti camera</p>
        <p>📜 Scroll pentru zoom</p>
      </div>

      {/* Agent Info Panel */}
      <AnimatePresence>
        {selectedAgent && (
          <AgentInfoPanel
            agent={selectedAgent}
            onClose={() => setSelectedAgent(null)}
          />
        )}
      </AnimatePresence>

      {/* Monetization Dashboard */}
      <AnimatePresence>
        {showMonetization && (
          <MonetizationDashboard
            totalEarnings={totalEarnings}
            agentEarnings={agents.map(a => ({ name: a.name, type: a.type, earnings: a.earnings, growth: (Math.random() * 20 + 5).toFixed(1) }))}
            onClose={() => setShowMonetization(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default AgentDashboard3D;
