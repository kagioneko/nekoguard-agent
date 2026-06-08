import { useEffect, useRef } from 'react'

export type TerminalLine = {
  id: string
  text: string
  kind: 'command' | 'output' | 'success' | 'warning' | 'error'
}

type Props = {
  lines: TerminalLine[]
  active: boolean
}

const COLOR: Record<TerminalLine['kind'], string> = {
  command: 'text-emerald-400',
  output:  'text-gray-400',
  success: 'text-emerald-300',
  warning: 'text-yellow-400',
  error:   'text-red-400',
}

export const TerminalPanel: React.FC<Props> = ({ lines, active }) => {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [lines])

  return (
    <div className="rounded-xl overflow-hidden border border-gray-700/50" style={{ background: '#0d1117' }}>
      {/* タイトルバー */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-700/50" style={{ background: '#161b22' }}>
        <span className="w-3 h-3 rounded-full bg-red-500/70" />
        <span className="w-3 h-3 rounded-full bg-yellow-500/70" />
        <span className="w-3 h-3 rounded-full bg-green-500/70" />
        <span className="ml-2 text-xs text-gray-500 font-mono">agent@nekoguard — ssh session</span>
        {active && (
          <span className="ml-auto flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-emerald-500 font-mono">LIVE</span>
          </span>
        )}
      </div>

      {/* ターミナル本体 */}
      <div className="p-4 font-mono text-xs leading-relaxed overflow-y-auto max-h-64 space-y-0.5">
        {lines.map(line => (
          <div key={line.id} className={`${COLOR[line.kind]} whitespace-pre-wrap break-all`}>
            {line.kind === 'command' && <span className="text-gray-600 select-none">❯ </span>}
            {line.text}
          </div>
        ))}
        {active && lines.length > 0 && (
          <span className="inline-block w-2 h-3.5 bg-emerald-400 animate-pulse ml-0.5 align-middle" />
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
