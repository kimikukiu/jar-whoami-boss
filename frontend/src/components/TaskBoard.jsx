import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, GripVertical, Clock, User, AlertCircle, CheckCircle, XCircle } from 'lucide-react'

const INITIAL_TASKS = {
  todo: [
    { id: '1', title: 'Validate Project Nexus build', priority: 'critical', assignee: 'JARVIS', created: '2m ago' },
    { id: '2', title: 'Scan for security vulnerabilities', priority: 'high', assignee: 'Sherlock', created: '5m ago' },
    { id: '3', title: 'Design new dashboard UI', priority: 'medium', assignee: 'Da Vinci', created: '10m ago' },
  ],
  in_progress: [
    { id: '4', title: 'Fix critical bug in auth module', priority: 'critical', assignee: 'Ripley', created: '1m ago' },
    { id: '5', title: 'Deploy updates to staging', priority: 'high', assignee: 'John Wick', created: '3m ago' },
  ],
  done: [
    { id: '6', title: 'Code review for API endpoints', priority: 'medium', assignee: 'Sherlock', created: '15m ago' },
    { id: '7', title: 'Update dependencies', priority: 'low', assignee: 'Saul', created: '20m ago' },
  ]
}

const PRIORITY_COLORS = {
  critical: '#ff4444',
  high: '#ffaa00',
  medium: '#4a9eff',
  low: '#888'
}

function TaskCard({ task, column }) {
  const [dragging, setDragging] = useState(false)

  return (
    <motion.div
      layout
      draggable
      onDragStart={() => setDragging(true)}
      onDragEnd={() => setDragging(false)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9 }}
      whileHover={{ scale: 1.02, boxShadow: '0 0 30px rgba(74,158,255,0.3)' }}
      className={`p-4 rounded-lg bg-[#0a0a0f] border border-[#4a9eff]/30 cursor-grab active:cursor-grabbing ${
        dragging ? 'opacity-50 rotate-2' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <GripVertical size={14} className="text-[#666]" />
          <span
            className="px-2 py-0.5 rounded text-xs font-bold uppercase"
            style={{
              backgroundColor: `${PRIORITY_COLORS[task.priority]}20`,
              color: PRIORITY_COLORS[task.priority],
              border: `1px solid ${PRIORITY_COLORS[task.priority]}40`
            }}
          >
            {task.priority}
          </span>
        </div>
        <div className="flex items-center gap-1 text-xs text-[#666]">
          <Clock size={12} />
          {task.created}
        </div>
      </div>

      <h4 className="text-white font-medium mb-3 pl-5">{task.title}</h4>

      <div className="flex items-center justify-between pl-5">
        <div className="flex items-center gap-1 text-xs text-[#888]">
          <User size={12} />
          {task.assignee}
        </div>
        {column === 'done' && (
          <CheckCircle size={16} className="text-[#00ff00]" />
        )}
        {column === 'todo' && (
          <AlertCircle size={16} className="text-[#4a9eff]" />
        )}
      </div>
    </motion.div>
  )
}

function Column({ title, color, tasks, icon: Icon }) {
  return (
    <div className="flex-1 min-w-[300px]">
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${color}20`, border: `1px solid ${color}` }}
        >
          <Icon size={16} style={{ color }} />
        </div>
        <h3 className="text-lg font-bold" style={{ color }}>{title}</h3>
        <span className="px-2 py-0.5 rounded-full text-xs bg-[#1a1a2e] text-[#888]">
          {tasks.length}
        </span>
      </div>

      <div className="space-y-3 min-h-[400px] p-2 rounded-lg bg-[#0a0a0f]/50 border border-[#4a9eff]/10">
        <AnimatePresence mode="popLayout">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} column={title.toLowerCase().replace(' ', '_')} />
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}

function TaskBoard() {
  const [tasks, setTasks] = useState(INITIAL_TASKS)
  const [newTask, setNewTask] = useState({ title: '', priority: 'medium', assignee: '' })

  const handleAddTask = () => {
    if (newTask.title.trim()) {
      const task = {
        id: Date.now().toString(),
        title: newTask.title,
        priority: newTask.priority,
        assignee: newTask.assignee || 'Unassigned',
        created: 'just now'
      }
      setTasks(prev => ({
        ...prev,
        todo: [...prev.todo, task]
      }))
      setNewTask({ title: '', priority: 'medium', assignee: '' })
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="h-full flex flex-col"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-[#4a9eff] flex items-center gap-3">
          <Activity size={28} className="text-[#00d4ff]" />
          TASK BOARD
          <span className="text-sm text-[#888] font-normal">Kanban View</span>
        </h2>
      </div>

      <div className="flex-1 flex gap-6 overflow-x-auto pb-4">
        <Column
          title="To Do"
          color="#4a9eff"
          icon={AlertCircle}
          tasks={tasks.todo}
        />
        <Column
          title="In Progress"
          color="#ffaa00"
          icon={Clock}
          tasks={tasks.in_progress}
        />
        <Column
          title="Done"
          color="#00ff00"
          icon={CheckCircle}
          tasks={tasks.done}
        />
      </div>

      <div className="mt-4 p-4 rounded-lg bg-[#1a1a2e] border border-[#4a9eff]/30">
        <h4 className="text-[#4a9eff] text-sm font-bold mb-3">CREATE NEW TASK</h4>
        <div className="flex gap-3">
          <input
            type="text"
            value={newTask.title}
            onChange={(e) => setNewTask(prev => ({ ...prev, title: e.target.value }))}
            placeholder="Task description..."
            className="flex-1 bg-[#0a0a0f] border border-[#4a9eff]/30 rounded px-4 py-2 text-white placeholder-[#666] focus:outline-none focus:border-[#4a9eff]"
          />
          <select
            value={newTask.priority}
            onChange={(e) => setNewTask(prev => ({ ...prev, priority: e.target.value }))}
            className="bg-[#0a0a0f] border border-[#4a9eff]/30 rounded px-4 py-2 text-white focus:outline-none"
          >
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            value={newTask.assignee}
            onChange={(e) => setNewTask(prev => ({ ...prev, assignee: e.target.value }))}
            className="bg-[#0a0a0f] border border-[#4a9eff]/30 rounded px-4 py-2 text-white focus:outline-none"
          >
            <option value="">Select Agent</option>
            <option value="Director Fury">Director Fury</option>
            <option value="Heimdall">Heimdall</option>
            <option value="John Kramer">John Kramer</option>
            <option value="Morpheus">Morpheus</option>
            <option value="Sherlock">Sherlock</option>
            <option value="Data">Data</option>
            <option value="Saul">Saul</option>
            <option value="JARVIS">JARVIS</option>
            <option value="Ripley">Ripley</option>
            <option value="Da Vinci">Da Vinci</option>
            <option value="John Wick">John Wick</option>
          </select>
          <button
            onClick={handleAddTask}
            className="px-6 py-2 rounded bg-[#4a9eff] text-white font-medium flex items-center gap-2 hover:bg-[#00d4ff] transition-colors"
          >
            <Plus size={18} />
            Add
          </button>
        </div>
      </div>
    </motion.div>
  )
}

export default TaskBoard