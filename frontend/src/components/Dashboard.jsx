import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Activity, Users, Cpu, Database, Clock, TrendingUp, AlertCircle } from 'lucide-react'

const AGENT_STATS = [
  { name: 'Director Fury', status: 'active', task: 'Coordinating mission', tier: 0 },
  { name: 'Heimdall', status: 'active', task: 'Validating requests', tier: 1 },
  { name: 'John Kramer', status: 'active', task: 'Planning operations', tier: 2 },
  { name: 'Morpheus', status: 'active', task: 'Routing tasks', tier: 2 },
  { name: 'Sherlock Holmes', status: 'active', task: 'Analyzing code', tier: 2 },
  { name: 'Data', status: 'active', task: 'Memory operations', tier: 2 },
  { name: 'Saul Goodman', status: 'busy', task: 'Applying patches', tier: 3 },
  { name: 'JARVIS', status: 'active', task: 'Validating builds', tier: 3 },
  { name: 'Ripley', status: 'active', task: 'Hunting bugs', tier: 3 },
  { name: 'Da Vinci', status: 'active', task: 'Designing UI', tier: 3 },
  { name: 'John Wick', status: 'standby', task: 'Awaiting deployment', tier: 3 },
]

function Dashboard({ agents }) {
  const [stats, setStats] = useState({
    totalAgents: 11,
    active: 10,
    busy: 1,
    standby: 0,
    tasksCompleted: 247,
    uptime: '99.9%',
    cpu: 23,
    memory: 45,
  })

  const [recentActivity, setRecentActivity] = useState([
    { agent: 'JARVIS', action: 'Build validated', time: '2s ago', status: 'success' },
    { agent: 'Ripley', action: 'Bug found: critical', time: '15s ago', status: 'warning' },
    { agent: 'Director Fury', action: 'Mission assigned', time: '32s ago', status: 'info' },
    { agent: 'Heimdall', action: 'Request validated', time: '1m ago', status: 'success' },
    { agent: 'John Wick', action: 'Deployment ready', time: '2m ago', status: 'success' },
  ])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="h-full grid grid-cols-3 gap-6"
    >
      <div className="col-span-2 space-y-6">
        <div className="rpg-panel p-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[#4a9eff]/5 to-transparent" />
          <h2 className="text-xl font-bold text-[#4a9eff] mb-4 flex items-center gap-2">
            <Activity className="text-[#00d4ff]" size={20} />
            SYSTEM STATUS
          </h2>
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Agents Online', value: `${stats.active}/${stats.totalAgents}`, icon: Users, color: '#4a9eff' },
              { label: 'Tasks Done', value: stats.tasksCompleted, icon: TrendingUp, color: '#00ff00' },
              { label: 'Uptime', value: stats.uptime, icon: Clock, color: '#ffaa00' },
              { label: 'Active Tasks', value: '7', icon: Activity, color: '#ff4444' },
            ].map(({ label, value, icon: Icon, color }) => (
              <motion.div
                key={label}
                whileHover={{ scale: 1.05, boxShadow: `0 0 30px ${color}40` }}
                className="p-4 rounded-lg bg-[#0a0a0f]/80 border border-[#4a9eff]/30 text-center"
              >
                <Icon size={24} style={{ color }} className="mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">{value}</div>
                <div className="text-xs text-[#888] uppercase tracking-wider">{label}</div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="rpg-panel p-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[#9b59ff]/5 to-transparent" />
          <h2 className="text-xl font-bold text-[#9b59ff] mb-4 flex items-center gap-2">
            <Cpu className="text-[#9b59ff]" size={20} />
            AGENT ACTIVITY
          </h2>
          <div className="space-y-3 max-h-64 overflow-y-auto pr-2">
            {recentActivity.map((activity, i) => (
              <motion.div
                key={i}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center justify-between p-3 rounded-lg bg-[#0a0a0f]/80 border border-[#4a9eff]/20"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'success' ? 'bg-[#00ff00]' :
                    activity.status === 'warning' ? 'bg-[#ffaa00]' :
                    'bg-[#4a9eff]'
                  }`} />
                  <div>
                    <div className="text-white font-medium">{activity.agent}</div>
                    <div className="text-xs text-[#888]">{activity.action}</div>
                  </div>
                </div>
                <span className="text-xs text-[#4a9eff]">{activity.time}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="rpg-panel p-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[#00d4ff]/5 to-transparent" />
          <h2 className="text-xl font-bold text-[#00d4ff] mb-4 flex items-center gap-2">
            <Database className="text-[#00d4ff]" size={20} />
            SYSTEM RESOURCES
          </h2>
          <div className="space-y-4">
            {[
              { label: 'CPU', value: stats.cpu, color: '#4a9eff' },
              { label: 'Memory', value: stats.memory, color: '#9b59ff' },
              { label: 'Network', value: 12, color: '#00d4ff' },
            ].map(({ label, value, color }) => (
              <div key={label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-[#888]">{label}</span>
                  <span style={{ color }}>{value}%</span>
                </div>
                <div className="h-2 bg-[#0a0a0f] rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                    className="h-full rounded-full"
                    style={{ backgroundColor: color, boxShadow: `0 0 10px ${color}` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rpg-panel p-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-[#ff4444]/5 to-transparent" />
          <h2 className="text-xl font-bold text-[#ff4444] mb-4 flex items-center gap-2">
            <AlertCircle className="text-[#ff4444]" size={20} />
            BRIEFING
          </h2>
          <div className="space-y-3">
            <p className="text-[#00ff00] text-sm">
              Good morning, Director. All systems operational.
            </p>
            <p className="text-[#888] text-xs">
              11 agents online. 1 mission in progress.
              Awaiting your command.
            </p>
            <div className="p-3 rounded bg-[#0a0a0f]/80 border border-[#4a9eff]/30">
              <div className="text-xs text-[#4a9eff] mb-1">PRIORITY</div>
              <div className="text-[#ffaa00]">Code validation for Project Nexus</div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default Dashboard