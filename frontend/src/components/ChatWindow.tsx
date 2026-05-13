import React, { useEffect, useRef } from 'react'

export type RevokeItem = {
  type: string
  masked_key: string
  location: string
  reason: string
}

export type TriageReport = {
  attacker_ips: string[]
  log_findings: string[]
  revoke_list: RevokeItem[]
}

export type ChatMessage = {
  id: string
  type: 'agent' | 'system' | 'phase' | 'revoke_list'
  text: string
  phase?: number
  triage?: TriageReport
}

type Props = {
  messages: ChatMessage[]
}

const PHASE_ICONS: Record<number, string> = { 1: '🔍', 2: '⚖️', 3: '🔬', 4: '💚' }

export const ChatWindow: React.FC<Props> = ({ messages }) => {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="glass rounded-2xl p-4 h-80 overflow-y-auto space-y-3">
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-600">
            <p className="text-4xl mb-2">🐱</p>
            <p className="text-sm">NekoGuardがスタンバイ中ニャ…</p>
            <p className="text-xs mt-1">上からインシデントを投げ込んでみてニャ！</p>
          </div>
        </div>
      )}
      {messages.map((msg) => (
        <div key={msg.id} className="animate-slide-in">
          {msg.type === 'phase' ? (
            <div className="flex items-center gap-2 my-2">
              <div className="flex-1 h-px bg-gray-700" />
              <span className="text-xs text-indigo-400 font-mono px-2 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10">
                {msg.phase && PHASE_ICONS[msg.phase]} Phase {msg.phase}: {msg.text}
              </span>
              <div className="flex-1 h-px bg-gray-700" />
            </div>
          ) : msg.type === 'agent' ? (
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-sm flex-shrink-0 mt-0.5">🐱</div>
              <div className="chat-bubble-agent rounded-2xl rounded-tl-sm px-4 py-3 max-w-xs">
                <p className="text-sm text-gray-200 whitespace-pre-wrap leading-relaxed">{msg.text}</p>
              </div>
            </div>
          ) : msg.type === 'revoke_list' && msg.triage ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-sm flex-shrink-0">🐱</div>
                <div className="chat-bubble-agent rounded-2xl rounded-tl-sm px-4 py-3">
                  <p className="text-sm text-gray-200">{msg.text}</p>
                </div>
              </div>
              {/* 攻撃者IP */}
              {msg.triage.attacker_ips.length > 0 && (
                <div className="ml-11 rounded-xl border border-red-500/30 bg-red-500/5 p-3 space-y-1">
                  <p className="text-xs text-red-400 font-bold uppercase tracking-widest">⚠ 攻撃者IP</p>
                  {msg.triage.attacker_ips.map((ip, i) => (
                    <p key={i} className="text-xs font-mono text-red-300">{ip}</p>
                  ))}
                </div>
              )}
              {/* ログ抜粋 */}
              {msg.triage.log_findings.length > 0 && (
                <div className="ml-11 rounded-xl border border-gray-700 bg-black/40 p-3 space-y-1">
                  <p className="text-xs text-gray-500 font-bold uppercase tracking-widest">📄 ログ抜粋</p>
                  {msg.triage.log_findings.map((line, i) => (
                    <p key={i} className="text-xs font-mono text-gray-400">{line}</p>
                  ))}
                </div>
              )}
              {/* 削除推奨リスト */}
              {msg.triage.revoke_list.length > 0 && (
                <div className="ml-11 rounded-xl border border-amber-500/30 bg-amber-500/5 p-3 space-y-2">
                  <p className="text-xs text-amber-400 font-bold uppercase tracking-widest">🗑 削除・ローテーション推奨リスト</p>
                  {msg.triage.revoke_list.map((item, i) => (
                    <div key={i} className="rounded-lg border border-amber-500/20 bg-black/30 px-3 py-2 space-y-0.5">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-amber-300 font-semibold">{item.type}</span>
                        <span className="text-xs font-mono text-gray-500">{item.location}</span>
                      </div>
                      <p className="text-xs font-mono text-gray-400">{item.masked_key}</p>
                      <p className="text-xs text-gray-500">{item.reason}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="chat-bubble-system rounded-xl px-3 py-2">
              <p className="text-xs text-gray-400 font-mono whitespace-pre-wrap">{msg.text}</p>
            </div>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
