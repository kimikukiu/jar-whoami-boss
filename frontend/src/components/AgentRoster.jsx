import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Eye, Cpu, Database, Code, Bug, Palette, Rocket, Power, ChevronDown, ChevronUp } from 'lucide-react'

const TIER_CONFIG = {
  0: { name: 'TIER 0 - DIRECTOR', color: '#ff4444', icon: Shield, description: 'Chief of Staff' },
  1: { name: 'TIER 1 - GATEKEEPER', color: '#44ff44', icon: Eye, description: 'Security & Validation' },
  2: { name: 'TIER 2 - SPECIALISTS', color: '#ffaa00', icon: Cpu, description: 'Analysis & Planning' },
  3: { name: 'TIER 3 - EXECUTORS', color: '#4a9eff', icon: Rocket, description: 'Implementation' },
}

const AGENTS_BY_TIER = [
  {
    tier: 0,
    agents: [
      { id: 'director_fury', name: 'Director Fury', role: 'Chief of Staff', status: 'active', capabilities: ['Command Parsing', 'Delegation', 'Reporting'] }
    ]
  },
  {
    tier: 1,
    agents: [
      { id: 'heimdall', name: 'Heimdall', role: 'Gatekeeper', status: 'active', capabilities: ['Security Validation', 'Input Filtering', 'Threat Detection'] }
    ]
  },
  {
    tier: 2,
    agents: [
      { id: 'john_kramer', name: 'John Kramer', role: 'Planner', status: 'active', capabilities: ['Task Decomposition', 'Strategic Planning', 'Risk Assessment'] },
      { id: 'morpheus', name: 'Morpheus', role: 'Dispatcher', status: 'active', capabilities: ['Task Routing', 'Agent Matching', 'Load Balancing'] },
      { id: 'sherlock_holmes', name: 'Sherlock Holmes', role: 'Repo Inspector', status: 'active', capabilities: ['Code Analysis', 'Bug Detection', 'Vulnerability Scanning'] },
      { id: 'data', name: 'Data', role: 'Archivist', status: 'active', capabilities: ['Memory Storage', 'Context Management', 'Cross-Referencing'] },
    ]
  },
  {
    tier: 3,
    agents: [
      { id: 'saul_goodman', name: 'Saul Goodman', role: 'Patch Agent', status: 'busy', capabilities: ['Patch Application', 'Hotfix Execution', 'Refactoring'] },
      { id: 'jarvis_build', name: 'JARVIS', role: 'Build Validator', status: 'active', capabilities: ['Type Checking', 'Linting', 'Quality Gates'] },
      { id: 'ripley', name: 'Ripley', role: 'Bug Hunter', status: 'active', capabilities: ['Bug Hunting', 'Stack Trace Analysis', 'Debugging'] },
      { id: 'da_vinci', name: 'Da Vinci', role: 'UI Agent', status: 'active', capabilities: ['UI Design', 'Component Building', 'Responsive Design'] },
      { id: 'john_wick', name: 'John Wick', role: 'Final Implementation', status: 'standby', capabilities: ['Full-Stack', 'Deployment', 'Integration'] },
    ]
  }
]

function AgentCard({ agent, tierConfig }) {
  const [expanded, setExpanded] = useState(false)
  const Icon = tierConfig.icon

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="agent-card relative"
    >
      <div
        className="p-4 rounded-xl bg-gradient-to-br from-[#12121a] to-[#1a1a2e] border-2 cursor-pointer transition-all duration-300 hover:shadow-[0_0_30px_rgba(74,158,255,0.3)]"
        style={{ borderColor: agent.status === 'active' ? tierConfig.color : agent.status === 'busy' ? '#ffaa00' : '#666' }}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: `${tierConfig.color}20`, border: `1px solid ${tierConfig.color}` }}
            >
              <Icon size={20} style={{ color: tierConfig.color }} />
            </div>
            <div>
              <h3 className="text-white font-bold">{agent.name}</h3>
              <p className="text-xs text-[#888]">{agent.role}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full animate-pulse"
              style={{
                backgroundColor: agent.status === 'active' ? '#00ff00' : agent.status === 'busy' ? '#ffaa00' : '#666'
              }}
            />
            <span className="text-xs uppercase tracking-wider" style={{ color: tierConfig.color }}>
              {agent.status}
            </span>
          </div>
        </div>

        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mt-4 pt-4 border-t border-[#4a9eff]/20"
            >
              <div className="text-xs text-[#4a9eff] mb-2">CAPABILITIES</div>
              <div className="flex flex-wrap gap-2">
                {agent.capabilities.map((cap, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 rounded text-xs bg-[#0a0a0f] text-[#888] border border-[#4a9eff]/20"
                  >
                    {cap}
                  </span>
                ))}
              </div>
              <div className="flex gap-2 mt-4">
                <button className="flex-1 px-3 py-2 rounded bg-[#4a9eff]/20 border border-[#4a9eff] text-[#4a9eff] text-xs hover:bg-[#4a9eff]/30 transition-colors">
                  Activate
                </button>
                <button className="flex-1 px-3 py-2 rounded bg-[#ff4444]/20 border border-[#ff4444] text-[#ff4444] text-xs hover:bg-[#ff4444]/30 transition-colors">
                  Standby
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {expanded ? (
          <ChevronUp className="absolute bottom-2 right-2 text-[#4a9eff]" size={16} />
        ) : (
          <ChevronDown className="absolute bottom-2 right-2 text-[#666]" size={16} />
        )}
      </div>
    </motion.div>
  )
}

function AgentRoster() {
  const [selectedTier, setSelectedTier] = useState(null)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="h-full"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-[#4a9eff] flex items-center gap-3">
          <Users size={28} className="text-[#00d4ff]" />
          AGENT ROSTER
          <span className="text-sm text-[#888] font-normal">11 Agents Active</span>
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedTier(null)}
            className={`px-4 py-2 rounded-lg text-sm transition-all ${
              selectedTier === null
                ? 'bg-[#4a9eff] text-white'
                : 'bg-[#1a1a2e] text-[#888] border border-[#4a9eff]/30 hover:border-[#4a9eff]'
            }`}
          >
            All Tiers
          </button>
          {[0, 1, 2, 3].map((tier) => (
            <button
              key={tier}
              onClick={() => setSelectedTier(tier)}
              className={`px-4 py-2 rounded-lg text-sm transition-all ${
                selectedTier === tier
                  ? 'bg-[#4a9eff] text-white'
                  : 'bg-[#1a1a2e] text-[#888] border border-[#4a9eff]/30 hover:border-[#4a9eff]'
              }`}
            >
              Tier {tier}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-8 overflow-y-auto h-[calc(100%-80px)] pr-2">
        {AGENTS_BY_TIER.filter(t => selectedTier === null || t.tier === selectedTier).map(({ tier, agents }) => {
          const tierConfig = TIER_CONFIG[tier]
          const Icon = tierConfig.icon
          return (
            <div key={tier}>
              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: `${tierConfig.color}20`, border: `1px solid ${tierConfig.color}` }}
                >
                  <Icon size={16} style={{ color: tierConfig.color }} />
                </div>
                <div>
                  <h3 className="text-lg font-bold" style={{ color: tierConfig.color }}>
                    {tierConfig.name}
                  </h3>
                  <p className="text-xs text-[#888]">{tierConfig.description}</p>
                </div>
                <div className="ml-auto text-sm text-[#888]">
                  {agents.filter(a => a.status === 'active').length}/{agents.length} active
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {agents.map((agent) => (
                  <AgentCard key={agent.id} agent={agent} tierConfig={tierConfig} />
                ))}
              </div>
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}

export default AgentRoster