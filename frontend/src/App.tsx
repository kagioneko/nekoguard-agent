import { useState, useCallback, useRef } from 'react'
import { IncidentDropzone } from './components/IncidentDropzone'
import { NeuroStateMeter } from './components/NeuroStateMeter'
import { ChatWindow, type ChatMessage, type TriageReport } from './components/ChatWindow'
import { ProtocolActionPanel, type ActionStep } from './components/ProtocolActionPanel'
import { VpsConnectModal, type VpsConfig } from './components/VpsConnectModal'

type NeuroLevel = 'NORMAL' | 'ALERT' | 'EMERGENCY'

type ServerStep = {
  id: string
  title: string
  desc: string
  triage_report?: TriageReport
}

const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : ''

function App() {
  const [vpsConfig, setVpsConfig] = useState<VpsConfig | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [neuroLevel, setNeuroLevel] = useState<NeuroLevel>('NORMAL')
  const [neuroParams, setNeuroParams] = useState({ dopamine: 50, serotonin: 50, gaba: 50, acetylcholine: 50 })
  const [currentPhase, setCurrentPhase] = useState<number | null>(null)
  const [currentParam, setCurrentParam] = useState('')
  const [protocol, setProtocol] = useState<string | null>(null)
  const [steps, setSteps] = useState<ActionStep[]>([])
  const [running, setRunning] = useState(false)

  // protocol_ready で受け取った全ステップデータ（triage_reportつき）を保持
  const serverStepsRef = useRef<ServerStep[]>([])

  const msgIdRef = useRef(0)
  const nextId = () => String(++msgIdRef.current)

  const addMsg = useCallback((msg: Omit<ChatMessage, 'id'>) => {
    setMessages(prev => [...prev, { ...msg, id: nextId() }])
  }, [])

  const updateNeuroFromPhase = (phase: number, param: string) => {
    const presets: Record<number, typeof neuroParams> = {
      1: { dopamine: 60, serotonin: 55, gaba: 50,  acetylcholine: 45 },
      2: { dopamine: 40, serotonin: 80, gaba: 75,  acetylcholine: 50 },
      3: { dopamine: 25, serotonin: 45, gaba: 55,  acetylcholine: 85 },
      4: { dopamine: 65, serotonin: 70, gaba: 60,  acetylcholine: 55 },
    }
    setNeuroParams(presets[phase] || neuroParams)
    setCurrentParam(param)
  }

  // ステップを起動（running状態にし、triageならチャットにレポートも流す）
  const activateStep = useCallback((stepId: string) => {
    setSteps(prev => prev.map(s => s.id === stepId ? { ...s, status: 'running' } : s))

    const serverStep = serverStepsRef.current.find(s => s.id === stepId)
    if (serverStep?.triage_report) {
      addMsg({
        type: 'revoke_list',
        text: 'ログ解析と認証情報スキャンが完了したニャ。以下を確認して、削除・ローテーションを進めてニャ！',
        triage: serverStep.triage_report,
      })
    }
  }, [addMsg])

  // 完了 or Skip → 次のステップを起動
  const advanceProtocol = useCallback((stepId: string, outcome: 'done' | 'skipped') => {
    setSteps(prev => {
      const updated = prev.map(s => s.id === stepId ? { ...s, status: outcome } : s)
      const currentIndex = updated.findIndex(s => s.id === stepId)
      const next = updated[currentIndex + 1]
      if (next) {
        // 次のステップを少し遅らせてactivate（stateの反映を待つ）
        setTimeout(() => activateStep(next.id), 300)
      } else {
        // 全ステップ完了
        setTimeout(() => {
          addMsg({ type: 'agent', text: 'すべての対応が完了したニャ！本当にお疲れ様！これで安心できるよ 🐾💚' })

          // スキップしたステップがあれば再通知
          const skipped = updated.filter(s => s.status === 'skipped')
          if (skipped.length > 0) {
            setTimeout(() => {
              addMsg({
                type: 'system',
                text: `⚠️ 以下の項目がスキップされています。後で必ず対応してニャ！\n\n${skipped.map(s => `• ${s.title}`).join('\n')}`
              })
            }, 800)
          }

          setRunning(false)
        }, 400)
      }
      return updated
    })
  }, [activateStep, addMsg])

  const handleConfirm = useCallback((id: string) => advanceProtocol(id, 'done'),    [advanceProtocol])
  const handleSkip    = useCallback((id: string) => advanceProtocol(id, 'skipped'), [advanceProtocol])

  const processStream = useCallback(async (response: Response) => {
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) return

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n').filter(l => l.startsWith('data: '))

      for (const line of lines) {
        const raw = line.replace('data: ', '').trim()
        if (!raw) continue
        try {
          const event = JSON.parse(raw)
          switch (event.type) {
            case 'status':
              setNeuroLevel(event.neurostate as NeuroLevel)
              addMsg({ type: 'agent', text: `${event.message}！NeuroState: ${event.neurostate} 🐾` })
              break
            case 'phase_start':
              setCurrentPhase(event.phase)
              if (event.neuro_params) {
                // NeuroState Engine の物理計算値をそのまま反映
                setNeuroParams(event.neuro_params)
                setCurrentParam(event.param)
              } else {
                updateNeuroFromPhase(event.phase, event.param)
              }
              addMsg({ type: 'phase', text: `${event.name}  ${event.desc}`, phase: event.phase })
              break
            case 'phase_result':
              addMsg({ type: event.phase === 3 ? 'system' : 'agent', text: event.text })
              break
            case 'agent_action':
              addMsg({ type: 'agent', text: event.text })
              break
            case 'protocol_decision':
              setProtocol(event.protocol)
              addMsg({ type: 'agent', text: `分析完了！${event.protocol}を起動するニャ 🚀` })
              break
            case 'protocol_ready': {
              const serverSteps: ServerStep[] = event.steps
              serverStepsRef.current = serverSteps

              // 全ステップをpendingで登録し、最初の1つだけrunningに
              const initialSteps: ActionStep[] = serverSteps.map((s, i) => ({
                id: s.id,
                title: s.title,
                desc: s.desc,
                status: i === 0 ? 'running' : 'pending',
              }))
              setSteps(initialSteps)
              setProtocol(event.protocol)

              // 最初のステップにtriage_reportがある場合も流す（通常はないが念のため）
              const first = serverSteps[0]
              if (first?.triage_report) {
                addMsg({
                  type: 'revoke_list',
                  text: 'ログ解析と認証情報スキャンが完了したニャ。以下を確認して、削除・ローテーションを進めてニャ！',
                  triage: first.triage_report,
                })
              }
              break
            }
            case 'done':
              // protocol_ready方式では done は無視（advanceProtocol内で処理）
              break
          }
        } catch (_) {}
      }
    }
  }, [addMsg])

  const resetState = () => {
    setMessages([])
    setSteps([])
    setProtocol(null)
    setCurrentPhase(null)
    setCurrentParam('')
    serverStepsRef.current = []
  }

  const handleTextSubmit = useCallback(async (text: string) => {
    if (!text.trim() || running) return
    setRunning(true)
    resetState()
    addMsg({ type: 'agent', text: '受け取ったニャ！今すぐ解析を始めるよ。深呼吸してニャ 🐱' })
    try {
      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ log_text: text, demo_mode: true, vps_config: vpsConfig }),
      })
      await processStream(res)
    } catch {
      addMsg({ type: 'system', text: 'バックエンドへの接続に失敗したニャ。サーバーが起動しているか確認してニャ。' })
      setRunning(false)
    }
  }, [running, addMsg, processStream, vpsConfig])

  const handleFileSelect = useCallback(async (file: File) => {
    if (running) return
    setRunning(true)
    resetState()
    addMsg({ type: 'agent', text: `画像「${file.name}」を受け取ったニャ！解析するよ 📨` })
    const formData = new FormData()
    formData.append('file', file)
    formData.append('demo_mode', 'true')
    try {
      const res = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: formData })
      await processStream(res)
    } catch {
      addMsg({ type: 'system', text: 'バックエンドへの接続に失敗したニャ。サーバーが起動しているか確認してニャ。' })
      setRunning(false)
    }
  }, [running, addMsg, processStream])

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #0a0d14 0%, #0f172a 50%, #0a0d14 100%)' }}>
      {/* VPS接続モーダル */}
      {!vpsConfig && <VpsConnectModal onConnect={setVpsConfig} />}

      {/* ヘッダー */}
      <header className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🐱</span>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">NekoGuard Agent</h1>
              <p className="text-xs text-gray-500">Incident Response AI · Google Cloud Hackathon</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {vpsConfig && (
              <div className="flex items-center gap-2 glass rounded-lg px-3 py-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs text-emerald-400 font-mono">{vpsConfig.username}@{vpsConfig.host}:{vpsConfig.port}</span>
                <button
                  className="text-gray-600 hover:text-gray-400 transition-colors text-xs ml-1"
                  onClick={() => setVpsConfig(null)}
                  title="切断"
                >
                  ✕
                </button>
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${running ? 'bg-indigo-400 animate-pulse' : 'bg-gray-600'}`} />
              <span className="text-xs text-gray-500 font-mono">{running ? 'Analyzing...' : 'Standby'}</span>
            </div>
          </div>
        </div>
      </header>

      {/* メインレイアウト */}
      <main className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左カラム */}
        <div className="space-y-6">
          <div>
            <h2 className="text-xs text-gray-500 uppercase tracking-widest font-medium mb-3">🧠 NeuroState Engine</h2>
            <NeuroStateMeter
              level={neuroLevel}
              params={neuroParams}
              currentPhase={currentPhase}
              currentParam={currentParam}
            />
          </div>
          <div>
            <h2 className="text-xs text-gray-500 uppercase tracking-widest font-medium mb-3">📨 インシデント入力</h2>
            <IncidentDropzone
              onFileSelect={handleFileSelect}
              onTextSubmit={handleTextSubmit}
              disabled={running}
            />
          </div>
        </div>

        {/* 中央カラム */}
        <div className="space-y-4">
          <h2 className="text-xs text-gray-500 uppercase tracking-widest font-medium">💬 NekoGuard Chat</h2>
          <ChatWindow messages={messages} />
        </div>

        {/* 右カラム */}
        <div className="space-y-4">
          <h2 className="text-xs text-gray-500 uppercase tracking-widest font-medium">⚡ Protocol Action Panel</h2>
          <ProtocolActionPanel
            protocol={protocol}
            steps={steps}
            onConfirm={handleConfirm}
            onSkip={handleSkip}
          />
          <div className="glass rounded-xl p-4 text-center space-y-1">
            <p className="text-xs text-gray-600">Powered by</p>
            <p className="text-xs text-gray-500 font-mono">Gemini 3 · Dynatrace MCP · NeuroState Engine</p>
            <p className="text-xs text-indigo-400 mt-2">Google Cloud Rapid Agent Hackathon 2026</p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
