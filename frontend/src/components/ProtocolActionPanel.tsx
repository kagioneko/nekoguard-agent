import React from 'react'

export type ActionStep = {
  id: string
  title: string
  desc: string
  status: 'pending' | 'running' | 'done' | 'skipped'
}

type Props = {
  protocol: string | null
  steps: ActionStep[]
  onConfirm: (id: string) => void
  onSkip: (id: string) => void
}

const STATUS_ICON: Record<ActionStep['status'], React.ReactNode> = {
  done:    <span className="text-emerald-400 text-lg">✅</span>,
  skipped: <span className="text-gray-500 text-lg">⏭</span>,
  running: <span className="text-indigo-400 text-lg animate-spin inline-block">⚙️</span>,
  pending: <span className="text-gray-600 text-lg">⭕</span>,
}

export const ProtocolActionPanel: React.FC<Props> = ({ protocol, steps, onConfirm, onSkip }) => {
  if (!protocol && steps.length === 0) {
    return (
      <div className="glass rounded-2xl p-5 flex items-center justify-center h-48">
        <div className="text-center text-gray-600">
          <p className="text-3xl mb-2">📋</p>
          <p className="text-sm">プロトコル待機中ニャ…</p>
        </div>
      </div>
    )
  }

  const isCat = protocol?.includes('CAT')

  return (
    <div className="glass rounded-2xl p-5 space-y-4">
      {/* プロトコルヘッダー */}
      {protocol && (
        <div className="flex items-center gap-3">
          <span className="text-2xl">{isCat ? '⚡' : '🛡️'}</span>
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-widest">Active Protocol</p>
            <p className={`font-bold text-sm ${isCat ? 'text-red-400' : 'text-amber-400'}`}>{protocol}</p>
          </div>
        </div>
      )}

      {/* ステップリスト */}
      <div className="space-y-2">
        {steps.map((step) => (
          <div
            key={step.id}
            className={`p-3 rounded-xl transition-all duration-500 action-step-entering ${
              step.status === 'done'    ? 'bg-emerald-500/10 border border-emerald-500/20' :
              step.status === 'skipped' ? 'bg-gray-800/60 border border-gray-600/40' :
              step.status === 'running' ? 'bg-indigo-500/10 border border-indigo-500/30' :
              'bg-gray-800/30 border border-gray-700/30'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">{STATUS_ICON[step.status]}</div>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-semibold ${
                  step.status === 'done'    ? 'text-emerald-300' :
                  step.status === 'skipped' ? 'text-gray-500 line-through' :
                  step.status === 'running' ? 'text-indigo-300' :
                  'text-gray-600'
                }`}>
                  {step.title}
                </p>
                {step.status !== 'pending' && (
                  <p className="text-xs text-gray-500 mt-0.5 font-mono leading-relaxed">{step.desc}</p>
                )}
                {step.status === 'skipped' && (
                  <p className="text-xs text-gray-600 mt-0.5">スキップされました</p>
                )}
              </div>
            </div>

            {/* ユーザー確認ボタン（runningのみ表示） */}
            {step.status === 'running' && (
              <div className="flex gap-2 mt-3 ml-9">
                <button
                  className="flex-1 py-2 rounded-lg text-sm font-bold text-white transition-all duration-200 hover:brightness-110 active:scale-95"
                  style={{ background: 'linear-gradient(135deg, #10b981, #34d399)' }}
                  onClick={() => onConfirm(step.id)}
                >
                  ✅ 完了した
                </button>
                <button
                  className="px-4 py-2 rounded-lg text-sm font-medium text-gray-400 border border-gray-600 hover:border-gray-500 hover:text-gray-300 transition-all duration-200 active:scale-95"
                  onClick={() => onSkip(step.id)}
                  title="まだ完了していないか不確かな場合にスキップ"
                >
                  ⏭ Skip
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
