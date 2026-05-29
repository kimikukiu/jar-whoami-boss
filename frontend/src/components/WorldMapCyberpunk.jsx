import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars, Text, Box, Sphere, Cylinder, Trail, Float, Line, MeshDistortMaterial, Environment, Html } from '@react-three/drei';
import { motion, AnimatePresence } from 'framer-motion';
import * as THREE from 'three';

// ============================================
// CYBERPUNK WORLD MAP COMPONENT
// ============================================

// Cities data with coordinates
const CITIES = [
  { name: 'LONDON', lat: 51.5074, lon: -0.1278, type: 'hub', status: 'active', earnings: 12500 },
  { name: 'PARIS', lat: 48.8566, lon: 2.3522, type: 'hub', status: 'active', earnings: 11200 },
  { name: 'NEW YORK', lat: 40.7128, lon: -74.0060, type: 'hub', status: 'active', earnings: 15800 },
  { name: 'TOKYO', lat: 35.6762, lon: 139.6503, type: 'hub', status: 'scanning', earnings: 13400 },
  { name: 'SINGAPORE', lat: 1.3521, lon: 103.8198, type: 'node', status: 'active', earnings: 8900 },
  { name: 'DUBAI', lat: 25.2048, lon: 55.2708, type: 'node', status: 'active', earnings: 10200 },
  { name: 'SYDNEY', lat: -33.8688, lon: 151.2093, type: 'node', status: 'scanning', earnings: 7600 },
  { name: 'BERLIN', lat: 52.5200, lon: 13.4050, type: 'node', status: 'active', earnings: 9500 },
  { name: 'MUMBAI', lat: 19.0760, lon: 72.8777, type: 'node', status: 'offline', earnings: 5400 },
];

// Convert lat/lon to 3D coordinates on a sphere
const latLonToVector3 = (lat, lon, radius = 10) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  
  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);
  
  return new THREE.Vector3(x, y, z);
};

// Globe Wireframe Component
const GlobeWireframe = ({ radius = 10 }) => {
  const meshRef = useRef();
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.001;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[radius, 64, 64]} />
      <meshBasicMaterial
        color="#00ffff"
        wireframe
        transparent
        opacity={0.15}
      />
    </mesh>
  );
};

// City Marker Component
const CityMarker = ({ city, onSelect, isSelected, isScanning }) => {
  const position = latLonToVector3(city.lat, city.lon, 10.2);
  const markerRef = useRef();
  const pulseRef = useRef();
  
  const color = city.status === 'active' ? '#00ff00' : 
                city.status === 'scanning' ? '#ffff00' : '#ff0000';
  
  useFrame((state) => {
    if (markerRef.current) {
      markerRef.current.lookAt(new THREE.Vector3(0, 0, 0));
    }
    if (pulseRef.current) {
      const scale = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.3;
      pulseRef.current.scale.setScalar(scale);
      pulseRef.current.material.opacity = 0.5 - (scale - 1) * 0.5;
    }
  });

  return (
    <group position={position} onClick={() => onSelect(city)}>
      {/* Pulse effect */}
      <mesh ref={pulseRef} position={[0, 0, 0.1]}>
        <circleGeometry args={[0.4, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.5} />
      </mesh>
      
      {/* Main marker */}
      <mesh ref={markerRef}>
        <cylinderGeometry args={[0.08, 0.08, 0.4, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>
      
      {/* Glow sphere at base */}
      <mesh position={[0, -0.2, 0]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <meshBasicMaterial color={color} transparent opacity={0.6} />
      </mesh>
      
      {/* Label */}
      <Html distanceFactor={15} position={[0, 0.5, 0]}>
        <div
          className={`px-2 py-1 rounded text-xs font-bold whitespace-nowrap cursor-pointer transition-all ${
            isSelected 
              ? 'bg-cyan-500 text-black' 
              : 'bg-black/80 text-cyan-400 border border-cyan-500/50'
          }`}
          style={{
            textShadow: isSelected ? 'none' : '0 0 10px rgba(0, 255, 255, 0.5)',
            boxShadow: isSelected ? '0 0 20px rgba(0, 255, 255, 0.5)' : 'none',
          }}
        >
          {city.name}
        </div>
      </Html>
      
      {/* Scanning effect */}
      {isScanning && (
        <mesh>
          <ringGeometry args={[0.3, 0.35, 32]} />
          <meshBasicMaterial color="#ffff00" transparent opacity={0.8} />
        </mesh>
      )}
    </group>
  );
};

// Connection Lines between cities
const ConnectionLines = ({ cities }) => {
  const connections = [
    [0, 1], [0, 2], [0, 3], [1, 4], [2, 5], [3, 6], [4, 7], [5, 8], [6, 9], [8, 9]
  ];
  
  const lineRefs = useRef([]);
  
  useFrame((state) => {
    lineRefs.current.forEach((line, idx) => {
      if (line) {
        line.material.dashOffset = -state.clock.elapsedTime * 2;
      }
    });
  });

  return (
    <>
      {connections.map(([from, to], idx) => {
        const start = latLonToVector3(cities[from].lat, cities[from].lon, 10.2);
        const end = latLonToVector3(cities[to].lat, cities[to].lon, 10.2);
        
        return (
          <line key={idx} ref={el => lineRefs.current[idx] = el}>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={2}
                array={new Float32Array([...start.toArray(), ...end.toArray()])}
                itemSize={3}
              />
            </bufferGeometry>
            <lineDashedMaterial
              color="#00ffff"
              dashSize={0.3}
              gapSize={0.2}
              linewidth={2}
              transparent
              opacity={0.6}
            />
          </line>
        );
      })}
    </>
  );
};

// Scanning Animation
const ScanningLine = ({ radius = 10 }) => {
  const lineRef = useRef();
  
  useFrame((state) => {
    if (lineRef.current) {
      const angle = (state.clock.elapsedTime * 0.3) % (Math.PI * 2);
      lineRef.current.rotation.y = angle;
    }
  });
  
  return (
    <group ref={lineRef}>
      <mesh rotation={[0, 0, Math.PI / 2]}>
        <planeGeometry args={[radius * 0.1, radius * 2.2]} />
        <meshBasicMaterial
          color="#ffff00"
          transparent
          opacity={0.3}
          side={THREE.DoubleSide}
        />
      </mesh>
    </group>
  );
};

// Main Scene
const WorldMapScene = ({ onCitySelect, selectedCity, scanningCity }) => {
  return (
    <>
      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#00ffff" />
      <pointLight position={[-10, -10, -10]} intensity={0.5} color="#ff00ff" />
      
      <Stars radius={200} depth={100} count={3000} factor={6} saturation={0.8} fade speed={0.5} />
      
      <GlobeWireframe />
      <ConnectionLines cities={CITIES} />
      
      {CITIES.map((city, idx) => (
        <CityMarker
          key={idx}
          city={city}
          onSelect={onCitySelect}
          isSelected={selectedCity?.name === city.name}
          isScanning={scanningCity?.name === city.name}
        />
      ))}
      
      <ScanningLine />
      
      <OrbitControls
        enablePan={false}
        enableZoom={true}
        enableRotate={true}
        minDistance={12}
        maxDistance={30}
        autoRotate
        autoRotateSpeed={0.5}
      />
    </>
  );
};

// Main Component
const WorldMapCyberpunk = () => {
  const [selectedCity, setSelectedCity] = useState(null);
  const [scanningCity, setScanningCity] = useState(null);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanResults, setScanResults] = useState(null);
  const [activeScans, setActiveScans] = useState([]);
  const [totalEarnings, setTotalEarnings] = useState(15750);

  // Simulate scanning process
  useEffect(() => {
    if (scanningCity) {
      const interval = setInterval(() => {
        setScanProgress(prev => {
          if (prev >= 100) {
            setScanResults({
              city: scanningCity.name,
              status: 'SECURE',
              threat: 'NONE',
              nodes: Math.floor(Math.random() * 50) + 10,
              latency: Math.floor(Math.random() * 50) + 10,
            });
            setActiveScans(prev => [...prev, { city: scanningCity, timestamp: Date.now() }]);
            setScanningCity(null);
            return 0;
          }
          return prev + 2;
        });
      }, 50);
      return () => clearInterval(interval);
    }
  }, [scanningCity]);

  const handleCitySelect = (city) => {
    setSelectedCity(city);
    setScanResults(null);
  };

  const handleScan = () => {
    if (selectedCity) {
      setScanningCity(selectedCity);
      setScanProgress(0);
      setScanResults(null);
    }
  };

  return (
    <div className="w-full h-screen bg-black overflow-hidden relative">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-20 p-6">
        <div className="flex justify-between items-start">
          <div>
            <motion.h1 
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-5xl font-bold text-white mb-2"
              style={{ fontFamily: 'Orbitron, monospace' }}
            >
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600">
                JARVIS
              </span>
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="text-cyan-400 text-sm tracking-widest"
              style={{ fontFamily: 'Share Tech Mono, monospace' }}
            >
              GLOBAL MONITORING SYSTEM v2.4.7
            </motion.p>
          </div>
          
          <div className="flex gap-4">
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-black/60 backdrop-blur-md border border-cyan-500/30 rounded-lg p-4"
            >
              <p className="text-cyan-400 text-xs mb-1" style={{ fontFamily: 'Share Tech Mono' }}>TOTAL REVENUE</p>
              <p className="text-2xl font-bold text-white" style={{ fontFamily: 'Orbitron' }}>
                ${totalEarnings.toLocaleString()}
              </p>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-black/60 backdrop-blur-md border border-green-500/30 rounded-lg p-4"
            >
              <p className="text-green-400 text-xs mb-1" style={{ fontFamily: 'Share Tech Mono' }}>ACTIVE NODES</p>
              <p className="text-2xl font-bold text-white" style={{ fontFamily: 'Orbitron' }}>
                {CITIES.filter(c => c.status === 'active').length}/{CITIES.length}
              </p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* 3D World Map */}
      <div className="absolute inset-0 z-10">
        <Canvas camera={{ position: [0, 0, 25], fov: 45 }}>
          <WorldMapScene 
            onCitySelect={handleCitySelect}
            selectedCity={selectedCity}
            scanningCity={scanningCity}
          />
        </Canvas>
      </div>

      {/* Left Panel - City Info */}
      <AnimatePresence>
        {selectedCity && (
          <motion.div
            initial={{ x: -400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -400, opacity: 0 }}
            className="absolute left-6 top-1/2 -translate-y-1/2 z-30 w-80"
          >
            <div 
              className="bg-black/80 backdrop-blur-xl border border-cyan-500/30 rounded-lg overflow-hidden"
              style={{
                boxShadow: '0 0 40px rgba(0, 255, 255, 0.1), inset 0 0 20px rgba(0, 255, 255, 0.05)',
              }}
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 p-4 border-b border-cyan-500/30">
                <div className="flex items-center justify-between">
                  <h3 
                    className="text-xl font-bold text-white"
                    style={{ fontFamily: 'Orbitron, monospace' }}
                  >
                    {selectedCity.name}
                  </h3>
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    selectedCity.status === 'active' 
                      ? 'bg-green-500/30 text-green-400 border border-green-500/50' 
                      : selectedCity.status === 'scanning'
                      ? 'bg-yellow-500/30 text-yellow-400 border border-yellow-500/50'
                      : 'bg-red-500/30 text-red-400 border border-red-500/50'
                  }`}>
                    {selectedCity.status.toUpperCase()}
                  </span>
                </div>
                <p className="text-cyan-400 text-sm mt-1" style={{ fontFamily: 'Share Tech Mono' }}>
                  {selectedCity.type === 'hub' ? 'MAJOR HUB' : 'NETWORK NODE'}
                </p>
              </div>

              {/* Stats */}
              <div className="p-4 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Revenue Generated</span>
                  <span className="text-green-400 font-bold" style={{ fontFamily: 'Orbitron' }}>
                    ${selectedCity.earnings.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Network Latency</span>
                  <span className="text-cyan-400 font-bold" style={{ fontFamily: 'Share Tech Mono' }}>
                    {Math.floor(Math.random() * 50 + 10)}ms
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Active Connections</span>
                  <span className="text-purple-400 font-bold" style={{ fontFamily: 'Share Tech Mono' }}>
                    {Math.floor(Math.random() * 100 + 20)}
                  </span>
                </div>
              </div>

              {/* Scan Button */}
              <div className="p-4 pt-0">
                <button
                  onClick={handleScan}
                  disabled={scanningCity?.name === selectedCity.name}
                  className={`w-full py-3 rounded-lg font-bold transition-all ${
                    scanningCity?.name === selectedCity.name
                      ? 'bg-yellow-500/30 text-yellow-400 cursor-wait'
                      : 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:from-cyan-400 hover:to-blue-400'
                  }`}
                  style={{ fontFamily: 'Orbitron' }}
                >
                  {scanningCity?.name === selectedCity.name ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      SCANNING... {scanProgress}%
                    </span>
                  ) : (
                    'INITIATE SCAN'
                  )}
                </button>
              </div>

              {/* Scan Results */}
              {scanResults && scanResults.city === selectedCity.name && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="border-t border-cyan-500/30 p-4 bg-cyan-500/10"
                >
                  <h4 className="text-cyan-400 font-bold mb-2" style={{ fontFamily: 'Orbitron' }}>
                    SCAN RESULTS
                  </h4>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Security Status:</span>
                      <span className="text-green-400 font-bold">{scanResults.status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Threat Level:</span>
                      <span className="text-green-400 font-bold">{scanResults.threat}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Active Nodes:</span>
                      <span className="text-cyan-400 font-bold">{scanResults.nodes}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Latency:</span>
                      <span className="text-cyan-400 font-bold">{scanResults.latency}ms</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Right Panel - Active Scans */}
      <AnimatePresence>
        {activeScans.length > 0 && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            className="absolute right-6 top-1/2 -translate-y-1/2 z-30 w-72"
          >
            <div className="bg-black/80 backdrop-blur-xl border border-cyan-500/30 rounded-lg p-4">
              <h3 className="text-cyan-400 font-bold mb-4" style={{ fontFamily: 'Orbitron' }}>
                ACTIVE SCANS
              </h3>
              <div className="space-y-3">
                {activeScans.slice(-5).map((scan, idx) => (
                  <div key={idx} className="flex items-center gap-3 text-sm">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-gray-400">{scan.city.name}</span>
                    <span className="text-cyan-400 text-xs">
                      {new Date(scan.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom Panel - Quick Stats */}
      <div className="absolute bottom-6 left-6 right-6 z-30">
        <div className="bg-black/60 backdrop-blur-md border border-cyan-500/30 rounded-lg p-4">
          <div className="grid grid-cols-4 gap-6">
            <div>
              <p className="text-gray-400 text-xs" style={{ fontFamily: 'Share Tech Mono' }}>GLOBAL REVENUE</p>
              <p className="text-2xl font-bold text-green-400" style={{ fontFamily: 'Orbitron' }}>
                ${totalEarnings.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-xs" style={{ fontFamily: 'Share Tech Mono' }}>ACTIVE NODES</p>
              <p className="text-2xl font-bold text-cyan-400" style={{ fontFamily: 'Orbitron' }}>
                {CITIES.filter(c => c.status === 'active').length}/{CITIES.length}
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-xs" style={{ fontFamily: 'Share Tech Mono' }}>NETWORK LATENCY</p>
              <p className="text-2xl font-bold text-purple-400" style={{ fontFamily: 'Orbitron' }}>
                24ms
              </p>
            </div>
            <div>
              <p className="text-gray-400 text-xs" style={{ fontFamily: 'Share Tech Mono' }}>THREAT LEVEL</p>
              <p className="text-2xl font-bold text-green-400" style={{ fontFamily: 'Orbitron' }}>
                NONE
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorldMapCyberpunk;
