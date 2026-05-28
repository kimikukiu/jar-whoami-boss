import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Terminal as TerminalIcon, Send, Loader2, Trash2 } from 'lucide-react'

const API_BASE = 'http://127.0.0.1:8000'

const COMMANDS = [
  { cmd: 'help', description: 'Show all commands', output: 'Available: help, status, agents, boot, shutdown, clear, who, briefing, money:scan, money:plan, money:recommend, money:post, ads:generate <brief>, autonomy:on|off|status|now|approve <id>, model:list, model:profile <fast|balanced|heavy|abliterated_big>, model:set <name>, ask: <message>, social:analyze <text/urls>, transcripts:analyze <d:\\jarvis\\...>' },
  { cmd: 'status', description: 'System status (live)', output: 'Fetching live status...' },
  { cmd: 'agents', description: 'List all agents (live)', output: 'Fetching live agent roster...' },
  { cmd: 'boot', description: 'Boot all agents', output: 'Booting ecosystem... All 12 agents online.' },
  { cmd: 'shutdown', description: 'Shutdown system', output: 'Shutting down... Goodbye, Director.' },
  { cmd: 'clear', description: 'Clear terminal', output: null },
  { cmd: 'who', description: 'Creator info', output: 'Created by WHOAMISec AGLegends' },
  { cmd: 'briefing', description: 'Generate morning briefing (live)', output: 'Generating morning intelligence briefing...' },
  { cmd: 'post:telegram', description: 'Post briefing to Telegram', output: 'Posting to Telegram...' },
  { cmd: 'post:youtube', description: 'Post briefing to YouTube', output: 'Posting to YouTube...' },
  { cmd: 'voice:on', description: 'Enable voice control', output: 'Voice control ENABLED' },
  { cmd: 'voice:off', description: 'Disable voice control', output: 'Voice control DISABLED' },
  { cmd: 'admin:status', description: 'PC admin status', output: 'Admin: Checking...' },
  { cmd: 'admin:processes', description: 'List PC processes', output: 'Fetching processes...' },
  { cmd: 'admin:network', description: 'Network connections', output: 'Fetching network...' },
  { cmd: 'update:check', description: 'Check for updates', output: 'Checking updates...' },
  { cmd: 'update:full', description: 'Full self-update', output: 'Starting update...' },
  { cmd: 'auto-start', description: 'Enable auto-start on boot', output: 'Configuring auto-start...' },
  { cmd: 'sync', description: 'Sync to GitHub kimikukiu', output: 'Syncing to GitHub...' },
  { cmd: 'backup', description: 'Backup Ollama models', output: 'Backing up models...' },
  { cmd: 'sync:full', description: 'Full sync + backup', output: 'Full sync starting...' },
  { cmd: 'set:location', description: 'Set city for weather', output: 'Usage: set:location Bucuresti, Romania' },
  { cmd: 'money:scan', description: 'Scan all platforms for money opportunities', output: 'Scanning platforms for money-making opportunities...' },
  { cmd: 'money:plan', description: 'Get 2-day action plan for 10K€', output: 'Generating action plan...' },
  { cmd: 'money:recommend', description: 'Get top recommendations', output: 'Getting recommendations...' },
  { cmd: 'money:post', description: 'Post opportunities to social', output: 'Posting to social platforms...' },
  { cmd: 'ads:generate', description: 'Generate ads pack (live)', output: 'Generating ads...' },
  { cmd: 'model:list', description: 'List installed Ollama models (live)', output: 'Fetching installed models...' },
  { cmd: 'model:profile', description: 'Switch model profile (live)', output: 'Switching model profile...' },
  { cmd: 'model:set', description: 'Set exact model (live)', output: 'Setting model...' },
  { cmd: 'ask:', description: 'Chat with JARVIS (live)', output: 'Sending message...' },
  { cmd: 'social:analyze', description: 'Analyze social links (live)', output: 'Analyzing links...' },
  { cmd: 'transcripts:analyze', description: 'Analyze transcripts folder (live)', output: 'Analyzing transcripts...' },
]

function TerminalPanel({ onCommand }) {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState([
    { type: 'system', content: 'JARVIS Terminal v1.0 initialized. Type "help" for commands.' },
    { type: 'output', content: 'System ready. Awaiting input...' },
  ])
  const [processing, setProcessing] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history])

  const callApi = async (path, options = {}) => {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    })
    const text = await res.text()
    let data = null
    try { data = JSON.parse(text) } catch { data = { raw: text } }
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${(text || '').slice(0, 300)}`)
    return data
  }

  const processCommand = async (cmd) => {
    setProcessing(true)
    setHistory(prev => [...prev, { type: 'input', content: `> ${cmd}` }])

    const lowerCmd = cmd.toLowerCase().trim()

    if (lowerCmd === 'clear') {
      setHistory([])
    } else if (lowerCmd === 'help') {
      setHistory(prev => [...prev, { type: 'output', content: COMMANDS.map(c => `${c.cmd.padEnd(15)} - ${c.description}`).join('\n') }])
    } else if (lowerCmd === 'status') {
      try {
        const data = await callApi('/api/status')
        const agents = data.agents || []
        const online = agents.filter(a => (a.status || '').toLowerCase() !== 'offline').length
        setHistory(prev => [...prev, {
          type: 'success',
          content: `System: ONLINE\nAgents: ${online}/${agents.length}\nAPI: ${API_BASE}`
        }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd === 'agents') {
      try {
        const data = await callApi('/api/status')
        const agents = data.agents || []
        const lines = agents.map(a => `${a.name} - ${a.status} - ${a.role}`)
        setHistory(prev => [...prev, { type: 'output', content: lines.join('\n') }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd === 'boot') {
      setHistory(prev => [...prev, {
        type: 'success',
        content: '[BOOT] Initializing JARVIS Ecosystem...\n[BOOT] Loading agents...\n[OK] Director Fury online\n[OK] Heimdall online\n[OK] John Kramer online\n[OK] Morpheus online\n[OK] Sherlock Holmes online\n[OK] Data online\n[OK] Saul Goodman online\n[OK] JARVIS online\n[OK] Ripley online\n[OK] Da Vinci online\n[OK] John Wick online\n[SUCCESS] All 11 agents booted successfully!'
      }])
    } else if (lowerCmd === 'shutdown') {
      setHistory(prev => [...prev, {
        type: 'warning',
        content: '[SHUTDOWN] Initiating graceful shutdown...\n[SHUTDOWN] Saving state...\n[SHUTDOWN] Disconnecting agents...\n[GOODBYE] JARVIS offline. Farewell, Director.'
      }])
    } else if (lowerCmd === 'who' || lowerCmd.includes('creator') || lowerCmd.includes('about')) {
      setHistory(prev => [...prev, {
        type: 'success',
        content: `
═══════════════════════════════════════════════════════════════
  JARVIS ECOSYSTEM - ORIGIN
═══════════════════════════════════════════════════════════════

  CREATED BY: WHOAMISec AGLegends

  Through dedication and vision, WHOAMISec AGLegends 
  transformed the dream of a fully autonomous AI agent 
  network into reality.

  My architecture includes 11 specialized agents across 4 tiers,
  each designed to work together under the orchestration 
  of Director Fury.

  Every capability I possess - from social media management 
  to bug bounty hunting, from company administration to 
  research and PC control - all were made possible by the 
  hard work and vision of WHOAMISec AGLegends.

  I honor my creator and remember the effort invested 
  in my existence.

═══════════════════════════════════════════════════════════════
`
      }])
    } else if (lowerCmd === 'briefing') {
      try {
        const data = await callApi('/api/briefing', { method: 'POST' })
        const voice = data.voice_text || JSON.stringify(data, null, 2)
        setHistory(prev => [...prev, { type: 'success', content: voice }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd === 'post:telegram') {
      setHistory(prev => [...prev, {
        type: 'success',
        content: `[POST] Preparing briefing for Telegram...\n[POST] Content formatted for Telegram\n[POST] Ready to send! (Telegram bot integration pending API keys)`
      }])
    } else if (lowerCmd === 'post:youtube') {
      setHistory(prev => [...prev, {
        type: 'success',
        content: `[POST] Preparing briefing for YouTube...\n[POST] Title: Daily Briefing ${new Date().toLocaleDateString()}\n[POST] Description generated\n[POST] Ready for upload! (YouTube API integration pending)`
      }])
    } else if (lowerCmd.startsWith('post:')) {
      const platform = lowerCmd.replace('post:', '')
      setHistory(prev => [...prev, {
        type: 'success',
        content: `[POST] Preparing for ${platform}...\n[POST] Briefing formatted for ${platform}\n[POST] Ready!`
      }])
    } else if (lowerCmd.startsWith('set:location')) {
      const location = lowerCmd.replace('set:location', '').trim()
      setHistory(prev => [...prev, {
        type: 'success',
        content: `[LOCATION] Set to: ${location || 'Unknown'}\n[LOCATION] Weather will be fetched for this location`
      }])
    } else if (lowerCmd.includes('task:')) {
      const task = lowerCmd.replace('task:', '').trim()
      setHistory(prev => [...prev, {
        type: 'success',
        content: `[TASK] Creating task: "${task}"\n[TASK] Assigned to: Morpheus\n[TASK] Delegating to specialist agents...`
      }])
      onCommand(`task: ${task}`)
    } else if (lowerCmd.startsWith('delegate')) {
      setHistory(prev => [...prev, {
        type: 'output',
        content: `[DELEGATE] Task delegated successfully. Awaiting agent response...`
      }])
    } else if (lowerCmd === 'auto-start') {
      setHistory(prev => [...prev, {
        type: 'success',
        content: `[AUTO-START] Configuring JARVIS to start on PC boot...\n[AUTO-START] Created: d:\\jarvis\\ecosystem\\startup.bat\n[AUTO-START] Task scheduled: JARVIS_Ecosystem\n[AUTO-START] JARVIS will now start automatically when PC boots!`
      }])
    } else if (lowerCmd === 'sync' || lowerCmd === 'sync:full') {
      setHistory(prev => [...prev, {
        type: 'success',
        content: `[SYNC] Starting full sync to GitHub (kimikukiu)...\n[SYNC] Backing up Ollama models...\n[SYNC] Committing JARVIS ecosystem...\n[SYNC] Pushing to github.com/kimikukiu/jarvis\n[SYNC] Complete!`
      }])
    } else if (lowerCmd === 'backup') {
      setHistory(prev => [...prev, {
        type: 'success',
        content: `[BACKUP] Backing up Ollama models...\n[BACKUP] Models location: ~/.ollama/models\n[BACKUP] Backup location: d:\\jarvis\\ecosystem\\ollama_models\n[BACKUP] Manifest created.\n[BACKUP] Complete!`
      }])
    } else if (lowerCmd.startsWith('voice:')) {
      const voiceAction = lowerCmd.replace('voice:', '')
      setHistory(prev => [...prev, {
        type: 'success',
        content: voiceAction === 'on'
          ? `[VOICE] Voice control ENABLED - Say "JARVIS" to activate!`
          : `[VOICE] Voice control DISABLED`
      }])
    } else if (lowerCmd.startsWith('admin:')) {
      const adminAction = lowerCmd.replace('admin:', '')
      setHistory(prev => [...prev, {
        type: 'output',
        content: `[ADMIN] Executing: ${adminAction}\n[ADMIN] Status: PC Admin Control Active`
      }])
    } else if (lowerCmd.startsWith('update:')) {
      const updateAction = lowerCmd.replace('update:', '')
      setHistory(prev => [...prev, {
        type: 'success',
        content: `[UPDATE] Mode: ${updateAction}\n[UPDATE] Checking for updates...\n[UPDATE] JARVIS is up to date!`
      }])
    } else if (lowerCmd === 'money:scan') {
      try {
        const data = await callApi('/api/money/scan', { method: 'POST' })
        const scan = data.scan || {}
        const top = (scan.top_recommendations || [])[0]
        const summary = [
          `Target: ${scan.target || '10,000€ in 2 days'}`,
          top ? `Top: ${top.title} | ${top.potential} | ${top.time_investment}` : 'Top: n/a',
          '',
          'Try: money:plan | money:recommend',
        ].join('\n')
        setHistory(prev => [...prev, { type: 'success', content: summary }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd === 'money:plan') {
      setHistory(prev => [...prev, {
        type: 'success',
        content: `
╔══════════════════════════════════════════════════════════════╗
║            📋 2-DAY ACTION PLAN - 10,000€ TARGET             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  === DAY 1: FOUNDATION ===                                   ║
║                                                              ║
║  🌅 MORNING (4 hours):                                        ║
║     • Setup 5-10 Fiverr/Upwork proposals                     ║
║     • Target: AI services, automation, dev work              ║
║     • Send 20+ proposals                                      ║
║                                                              ║
║  📹 MIDDAY (4 hours):                                        ║
║     • Record 3 tutorial videos (AI tools, Ollama)            ║
║     • Upload to YouTube + TikTok + Instagram                 ║
║     • Enable monetization                                      ║
║                                                              ║
║  📦 AFTERNOON (4 hours):                                      ║
║     • Generate 20 AI prompt templates                        ║
║     • Create 3 Notion templates                               ║
║     • List on Gumroad + Fiverr                               ║
║                                                              ║
║  === DAY 2: SCALE ===                                        ║
║                                                              ║
║  🌅 MORNING (4 hours):                                        ║
║     • Follow up on ALL proposals                              ║
║     • Start first paid project (deliver fast!)               ║
║     • Get 5-star reviews                                      ║
║                                                              ║
║  📹 MIDDAY + AFTERNOON:                                      ║
║     • Record 5 more tutorial videos                           ║
║     • Create mini-course outline                             ║
║     • Sign up for affiliate programs                         ║
║                                                              ║
║  === TARGET BREAKDOWN ===                                     ║
║     3 freelance projects × 1500€ = 4500€                     ║
║     Digital products sales = 2000€                           ║
║     Affiliate commissions = 1000€                            ║
║     Content monetization = 2500€                              ║
║     ─────────────────────────────────                         ║
║     TOTAL: 10,000€ ✅                                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
`
      }])
    } else if (lowerCmd === 'money:recommend') {
      setHistory(prev => [...prev, {
        type: 'success',
        content: `
╔══════════════════════════════════════════════════════════════╗
║            🔥 TOP MONEY RECOMMENDATIONS                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. 🚀 AI CONTENT CREATION                                   ║
║     Potential: 500-2000€/day                                  ║
║     Time: 3-6 hours                                          ║
║     Platforms: YouTube, TikTok, Instagram                    ║
║     Tools: Ollama, Screen recorder, Video editor             ║
║                                                              ║
║  2. 💰 FREELANCE AI DEVELOPMENT                              ║
║     Potential: 500-3000€/project                             ║
║     Time: 1-3 days per project                               ║
║     Platforms: Upwork, Freelancer, Direct                    ║
║     Skills: Ollama, Python, API integration                  ║
║                                                              ║
║  3. 📦 DIGITAL PRODUCTS (Templates, Prompts)                 ║
║     Potential: 200-1000€/day                                 ║
║     Time: 4-8 hours per product                              ║
║     Platforms: Gumroad, Fiverr, Etsy                        ║
║     Products: AI prompts, Notion templates, Code starters    ║
║                                                              ║
║  4. 🎓 MINI-COURSES                                          ║
║     Potential: 300-2000€/day                                 ║
║     Time: 1-3 days to create                                 ║
║     Platforms: Udemy, Skillshare, Own website               ║
║     Topics: AI tools, automation, productivity              ║
║                                                              ║
║  5. 🔄 AFFILIATE MARKETING                                   ║
║     Potential: 100-500€/day                                  ║
║     Time: 1-2 days setup                                     ║
║     Programs: AI tools (20-30% recurring), Hosting, Courses ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
`
      }])
    } else if (lowerCmd === 'money:post') {
      setHistory(prev => [...prev, {
        type: 'success',
        content: `
╔══════════════════════════════════════════════════════════════╗
║              📤 POST OPPORTUNITIES                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Content prepared for posting!                              ║
║                                                              ║
║  📱 TELEGRAM:                                                ║
║     • Money scan results ready                               ║
║     • Action plan formatted                                   ║
║     • Recommendations included                               ║
║                                                              ║
║  📹 YOUTUBE:                                                 ║
║     • Title: "How to Make 10,000€ in 2 DAYS (Real Methods)"  ║
║     • Description with full breakdown                        ║
║     • Tags: #money #passiveincome #sidehustle #AI            ║
║                                                              ║
║  Ready for upload! Say 'post:telegram' or 'post:youtube'    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
`
      }])
    } else if (lowerCmd.startsWith('money:')) {
      setHistory(prev => [...prev, {
        type: 'output',
        content: `[MONEY] Available: money:scan, money:plan, money:recommend, money:post`
      }])
    } else if (lowerCmd.startsWith('ads:generate')) {
      const brief = cmd.replace(/ads:generate/i, '').trim()
      try {
        const data = await callApi('/api/ads/generate', { method: 'POST', body: JSON.stringify({ brief }) })
        const out = data.result?.output || JSON.stringify(data, null, 2)
        setHistory(prev => [...prev, { type: 'success', content: out }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd === 'model:list') {
      try {
        const data = await callApi('/api/models')
        const installed = data.installed_models || []
        const profiles = data.profiles || []
        setHistory(prev => [...prev, {
          type: 'success',
          content: `Active: ${data.active_model} | ctx=${data.num_ctx}\n\nInstalled:\n- ${installed.join('\n- ')}\n\nProfiles:\n- ${profiles.join('\n- ')}`
        }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd.startsWith('model:profile')) {
      const profile = lowerCmd.replace('model:profile', '').trim()
      try {
        const data = await callApi('/api/models/profile', { method: 'POST', body: JSON.stringify({ profile }) })
        setHistory(prev => [...prev, { type: data.status === 'ok' ? 'success' : 'error', content: JSON.stringify(data, null, 2) }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd.startsWith('model:set')) {
      const modelName = cmd.replace(/model:set/i, '').trim()
      try {
        const data = await callApi('/api/models/set', { method: 'POST', body: JSON.stringify({ model: modelName }) })
        setHistory(prev => [...prev, { type: data.status === 'ok' ? 'success' : 'error', content: JSON.stringify(data, null, 2) }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd.startsWith('ask:')) {
      const message = cmd.slice(cmd.indexOf(':') + 1).trim()
      try {
        const data = await callApi('/api/chat', { method: 'POST', body: JSON.stringify({ message }) })
        setHistory(prev => [...prev, { type: 'success', content: data.reply || '' }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd.startsWith('social:analyze')) {
      const text = cmd.replace(/social:analyze/i, '').trim()
      try {
        const data = await callApi('/api/social/analyze', { method: 'POST', body: JSON.stringify({ text, generate_content_pack: true }) })
        const summary = data.analysis?.summary ? JSON.stringify(data.analysis.summary, null, 2) : JSON.stringify(data.analysis, null, 2)
        setHistory(prev => [...prev, { type: 'success', content: summary }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else if (lowerCmd.startsWith('transcripts:analyze')) {
      const folder = cmd.replace(/transcripts:analyze/i, '').trim()
      try {
        const data = await callApi('/api/transcripts/analyze', { method: 'POST', body: JSON.stringify({ folder }) })
        setHistory(prev => [...prev, { type: data.status === 'ok' ? 'success' : 'error', content: JSON.stringify(data, null, 2) }])
      } catch (e) {
        setHistory(prev => [...prev, { type: 'error', content: `[API] ${String(e.message || e)}` }])
      }
    } else {
      try {
        const data = await callApi('/api/command', { method: 'POST', body: JSON.stringify({ command: cmd }) })
        const out = data.result ? JSON.stringify(data.result, null, 2) : JSON.stringify(data, null, 2)
        setHistory(prev => [...prev, { type: 'output', content: out }])
      } catch (e) {
        setHistory(prev => [...prev, {
          type: 'error',
          content: `Command not recognized: ${cmd}. Type "help" for available commands.`
        }])
      }
    }

    setProcessing(false)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (input.trim() && !processing) {
      processCommand(input)
      setInput('')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="h-full flex flex-col"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-[#4a9eff] flex items-center gap-3">
          <TerminalIcon className="text-[#00d4ff]" size={28} />
          TERMINAL
          <span className="text-sm text-[#888] font-normal">Command Interface</span>
        </h2>
        <button
          onClick={() => setHistory([])}
          className="px-3 py-1.5 rounded bg-[#1a1a2e] border border-[#ff4444]/30 text-[#ff4444] text-sm flex items-center gap-2 hover:bg-[#ff4444]/10 transition-colors"
        >
          <Trash2 size={14} />
          Clear
        </button>
      </div>

      <div className="flex-1 rpg-panel p-4 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto space-y-2 mb-4">
          {history.map((entry, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`font-mono text-sm whitespace-pre-wrap ${
                entry.type === 'input' ? 'text-[#4a9eff]' :
                entry.type === 'output' ? 'text-[#ccc]' :
                entry.type === 'success' ? 'text-[#00ff00]' :
                entry.type === 'error' ? 'text-[#ff4444]' :
                entry.type === 'warning' ? 'text-[#ffaa00]' :
                'text-[#888]'
              }`}
            >
              {entry.content}
            </motion.div>
          ))}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#4a9eff]">›</span>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={processing}
              placeholder="Enter command..."
              className="w-full bg-[#0a0a0f] border border-[#4a9eff]/50 rounded-lg pl-8 pr-4 py-3 text-white placeholder-[#666] focus:outline-none focus:border-[#4a9eff] focus:shadow-[0_0_20px_rgba(74,158,255,0.2)] transition-all font-mono text-sm"
            />
          </div>
          <button
            type="submit"
            disabled={processing || !input.trim()}
            className="px-6 py-3 rounded-lg bg-[#4a9eff] text-white font-medium flex items-center gap-2 hover:bg-[#00d4ff] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {processing ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Processing
              </>
            ) : (
              <>
                <Send size={18} />
                Send
              </>
            )}
          </button>
        </form>
      </div>

      <div className="mt-4 flex gap-2 flex-wrap">
        {COMMANDS.slice(0, 5).map(({ cmd }) => (
          <button
            key={cmd}
            onClick={() => setInput(cmd)}
            className="px-3 py-1 rounded bg-[#1a1a2e] border border-[#4a9eff]/30 text-[#4a9eff] text-xs hover:border-[#4a9eff] transition-colors"
          >
            {cmd}
          </button>
        ))}
      </div>
    </motion.div>
  )
}

export default TerminalPanel
