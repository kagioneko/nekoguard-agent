import React from 'react'

type NeuroParams = {
  dopamine: number
  serotonin: number
  gaba: number
  acetylcholine: number
}

type Props = {
  level: 'NORMAL' | 'ALERT' | 'EMERGENCY'
  params: NeuroParams
  currentPhase: number | null
  currentParam: string
}

const LEVEL_CONFIG = {
  NORMAL: { label: 'NORMAL', color: 'text-emerald-400', bg: 'bg-emerald-400', border: 'border-emerald-400', glow: 'state-normal', icon: '😸' },
  ALERT: { label: 'ALERT', color: 'text-amber-400', bg: 'bg-amber-400', border: 'border-amber-400', glow: 'state-alert', icon: '😾' },
  EMERGENCY: { label: 'EMERGENCY', color: 'text-red-400', bg: 'bg-red-400', border: 'border-red-400', glow: 'state-emergency', icon: '🙀' },
}

const PHASE_LABELS: Record<number, string> = {
  1: 'Wide-scan',
  2: 'Judgment',
  3: 'Detail analysis',
  4: 'Recovery',
}

export const NeuroStateMeter: React.FC<Props> = ({ level, params, currentPhase, currentParam }) => {
  const cfg = LEVEL_CONFIG[level]

  const bars = [
    { label: 'Dopamine', key: 'dopamine', val: params.dopamine, cls: 'neuro-bar-dopamine', color: '#6366f1' },
    { label: 'Serotonin', key: 'serotonin', val: params.serotonin, cls: 'neuro-bar-serotonin', color: '#10b981' },
    { label: 'GABA', key: 'gaba', val: params.gaba, cls: 'neuro-bar-gaba', color: '#3b82f6' },
    { label: 'Acetylcholine', key: 'acetylcholine', val: params.acetylcholine, cls: 'neuro-bar-acetylcholine', color: '#f59e0b' },
  ]

  return (
    <div className={`glass rounded-2xl border-2 p-5 transition-all duration-700 ${cfg.border} ${cfg.glow}`}>
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-gray-500 text-xs uppercase tracking-widest font-medium">NeuroState</p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-2xl">{cfg.icon}</span>
            <span className={`text-xl font-bold font-mono ${cfg.color}`}>{cfg.label}</span>
            {level === 'EMERGENCY' && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${cfg.bg} text-black font-bold animate-pulse`}>ACTIVE</span>
            )}
          </div>
        </div>
        {currentPhase && (
          <div className="text-right">
            <p className="text-gray-500 text-xs uppercase tracking-widest">Phase</p>
            <p className="text-indigo-300 font-mono font-bold text-lg">{currentPhase}</p>
            <p className="text-gray-400 text-xs">{PHASE_LABELS[currentPhase]}</p>
          </div>
        )}
      </div>

      {/* 注入パラメーター */}
      {currentParam && (
        <div className="mb-4 px-3 py-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
          <p className="text-xs text-indigo-300 font-mono">💉 {currentParam}</p>
        </div>
      )}

      {/* 神経伝達物質バー */}
      <div className="space-y-3">
        {bars.map(bar => (
          <div key={bar.key}>
            <div className="flex justify-between mb-1">
              <span className="text-gray-400 text-xs">{bar.label}</span>
              <span className="text-gray-300 text-xs font-mono">{bar.val}</span>
            </div>
            <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000`}
                style={{ width: `${bar.val}%`, background: `linear-gradient(90deg, ${bar.color}88, ${bar.color})` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
