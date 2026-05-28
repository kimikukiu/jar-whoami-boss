import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageSquare, Send, Users, Shield, Cpu, Database, Code, Bug, Palette, Rocket } from 'lucide-react'

const AGENTS = [
  { id: 'director_fury', name: 'Director Fury', tier: 0, color: '#ff4444' },
  { id: 'heimdall', name: 'Heimdall', tier: 1, color: '#44ff44' },
  { id: 'john_kramer', name: 'John Kramer', tier: 2, color: '#ffaa00' },
  { id: 'morpheus', name: 'Morpheus', tier: 2, color: '#aa44ff' },
  { id: 'sherlock_holmes', name: 'Sherlock', tier: 2, color: '#44aaff' },
  { id: 'data', name: 'Data', tier: 2, color: '#00ffff' },
  { id: 'saul_goodman', name: 'Saul', tier: 3, color: '#ff8800' },
  { id: 'jarvis_build', name: 'JARVIS', tier: 3, color: '#4a9eff' },
  { id: 'ripley', name: 'Ripley', tier: 3, color: '#ff0044' },
  { id: 'da_vinci', name: 'Da Vinci', tier: 3, color: '#ff44aa' },
  { id: 'john_wick', name: 'John Wick', tier: 3, color: '#ffffff' },
]

const INITIAL_MESSAGES = [
  { id: 1, from: 'director_fury', to: 'heimdall', content: 'Heimdall, validate incoming request for Project Nexus.', timestamp: '10:42:15', type: 'direct' },
  { id: 2, from: 'heimdall', to: 'director_fury', content: 'Request validated. No security threats detected. Forwarding to John Kramer.', timestamp: '10:42:18', type: 'direct' },
  { id: 3, from: 'heimdall', to: '*', content: 'All agents: New mission incoming. Prepare for deployment.', timestamp: '10:42:20', type: 'broadcast' },
  { id: 4, from: 'john_kramer', to: 'director_fury', content: 'Mission decomposed into 6 actionable steps. Plan ready for approval.', timestamp: '10:42:45', type: 'direct' },
  { id: 5, from: 'ripley', to: '*', content: 'Bug detected in auth module: critical severity. Investigating.', timestamp: '10:43:02', type: 'alert' },
  { id: 6, from: 'jarvis_build', to: '*', content: 'Build validation passed. Quality score: 94%. Ready for deployment.', timestamp: '10:43:30', type: 'broadcast' },
]

function CommsPanel() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES)
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [newMessage, setNewMessage] = useState('')
  const [filter, setFilter] = useState('all')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = () => {
    if (newMessage.trim()) {
      const message = {
        id: Date.now(),
        from: 'director_fury',
        to: selectedAgent || '*',
        content: newMessage,
        timestamp: new Date().toLocaleTimeString(),
        type: selectedAgent ? 'direct' : 'broadcast'
      }
      setMessages(prev => [...prev, message])
      setNewMessage('')
    }
  }

  const getAgentInfo = (agentId) => AGENTS.find(a => a.id === agentId) || { name: agentId, color: '#888' }

  const filteredMessages = messages.filter(msg => {
    if (filter === 'all') return true
    if (filter === 'direct') return msg.type === 'direct'
    if (filter === 'broadcast') return msg.type === 'broadcast'
    if (filter === 'alerts') return msg.type === 'alert'
    return true
  })

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="h-full flex gap-6"
    >
      <div className="w-64 flex flex-col">
        <h3 className="text-lg font-bold text-[#4a9eff] mb-4 flex items-center gap-2">
          <Users size={20} className="text-[#00d4ff]" />
          AGENTS
        </h3>

        <div className="flex-1 overflow-y-auto space-y-2">
          <button
            onClick={() => setSelectedAgent(null)}
            className={`w-full p-3 rounded-lg text-left transition-all ${
              selectedAgent === null
                ? 'bg-[#4a9eff]/20 border border-[#4a9eff]'
                : 'bg-[#1a1a2e] border border-transparent hover:border-[#4a9eff]/30'
            }`}
          >
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-[#4a9eff]/20 flex items-center justify-center">
                <MessageSquare size={14} className="text-[#4a9eff]" />
              </div>
              <div>
                <div className="text-white text-sm font-medium">Broadcast</div>
                <div className="text-xs text-[#666]">All agents</div>
              </div>
            </div>
          </button>

          {AGENTS.map((agent) => (
            <button
              key={agent.id}
              onClick={() => setSelectedAgent(agent.id)}
              className={`w-full p-3 rounded-lg text-left transition-all ${
                selectedAgent === agent.id
                  ? 'bg-[#4a9eff]/20 border border-[#4a9eff]'
                  : 'bg-[#1a1a2e] border border-transparent hover:border-[#4a9eff]/30'
              }`}
            >
              <div className="flex items-center gap-2">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: `${agent.color}20`, border: `1px solid ${agent.color}` }}
                >
                  {agent.tier === 0 && <Shield size={14} style={{ color: agent.color }} />}
                  {agent.tier === 1 && <Shield size={14} style={{ color: agent.color }} />}
                  {agent.tier === 2 && <Cpu size={14} style={{ color: agent.color }} />}
                  {agent.tier === 3 && <Rocket size={14} style={{ color: agent.color }} />}
                </div>
                <div>
                  <div className="text-white text-sm font-medium">{agent.name}</div>
                  <div className="text-xs text-[#666]">Tier {agent.tier}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col rpg-panel">
        <div className="p-4 border-b border-[#4a9eff]/20">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-[#4a9eff] flex items-center gap-2">
              <MessageSquare size={20} className="text-[#00d4ff]" />
              {selectedAgent ? `Chat with ${getAgentInfo(selectedAgent).name}` : 'Broadcast Channel'}
            </h3>
            <div className="flex gap-2">
              {['all', 'direct', 'broadcast', 'alerts'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1 rounded text-xs capitalize transition-all ${
                    filter === f
                      ? 'bg-[#4a9eff] text-white'
                      : 'bg-[#1a1a2e] text-[#888] hover:text-white'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <AnimatePresence>
            {filteredMessages.map((msg) => {
              const agent = getAgentInfo(msg.from)
              return (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${msg.from === 'director_fury' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] p-3 rounded-lg ${
                      msg.type === 'broadcast'
                        ? 'bg-[#9b59ff]/10 border border-[#9b59ff]/30'
                        : msg.type === 'alert'
                        ? 'bg-[#ff4444]/10 border border-[#ff4444]/30'
                        : 'bg-[#1a1a2e] border border-[#4a9eff]/30'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <div
                        className="w-5 h-5 rounded flex items-center justify-center"
                        style={{ backgroundColor: `${agent.color}20` }}
                      >
                        {agent.tier === 0 && <Shield size={10} style={{ color: agent.color }} />}
                        {agent.tier === 1 && <Shield size={10} style={{ color: agent.color }} />}
                        {agent.tier === 2 && <Cpu size={10} style={{ color: agent.color }} />}
                        {agent.tier === 3 && <Rocket size={10} style={{ color: agent.color }} />}
                      </div>
                      <span className="text-xs font-bold" style={{ color: agent.color }}>
                        {msg.from === 'director_fury' ? 'You' : agent.name}
                      </span>
                      {msg.type === 'broadcast' && (
                        <span className="px-1.5 py-0.5 rounded text-[8px] bg-[#9b59ff]/30 text-[#9b59ff]">
                          BROADCAST
                        </span>
                      )}
                      {msg.type === 'alert' && (
                        <span className="px-1.5 py-0.5 rounded text-[8px] bg-[#ff4444]/30 text-[#ff4444]">
                          ALERT
                        </span>
                      )}
                      <span className="text-[10px] text-[#666]">{msg.timestamp}</span>
                    </div>
                    <p className="text-sm text-white/90">{msg.content}</p>
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>

        <div className="p-4 border-t border-[#4a9eff]/20">
          <div className="flex gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder={selectedAgent ? `Message ${getAgentInfo(selectedAgent).name}...` : 'Broadcast to all agents...'}
              className="flex-1 bg-[#0a0a0f] border border-[#4a9eff]/30 rounded-lg px-4 py-2 text-white placeholder-[#666] focus:outline-none focus:border-[#4a9eff]"
            />
            <button
              onClick={sendMessage}
              className="px-6 py-2 rounded-lg bg-[#4a9eff] text-white font-medium flex items-center gap-2 hover:bg-[#00d4ff] transition-colors"
            >
              <Send size={16} />
              Send
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default CommsPanel