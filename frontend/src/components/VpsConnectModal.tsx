import React, { useState, useRef } from 'react'

export type VpsConfig = {
  host: string
  username: string
  port: number
  sshKey: string
}

type Props = {
  onConnect: (config: VpsConfig) => void
}

export const VpsConnectModal: React.FC<Props> = ({ onConnect }) => {
  const [host, setHost] = useState('')
  const [username, setUsername] = useState('root')
  const [port, setPort] = useState('22')
  const [sshKey, setSshKey] = useState('')
  const [status, setStatus] = useState<'idle' | 'connecting' | 'done'>('idle')
  const [error, setError] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const handleKeyFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => setSshKey(ev.target?.result as string)
    reader.readAsText(file)
  }

  const handleConnect = async () => {
    if (!host.trim() || !sshKey.trim()) {
      setError('ホストとSSH秘密鍵は必須ニャ')
      return
    }
    setError('')
    setStatus('connecting')
    await new Promise(r => setTimeout(r, 1800))
    setStatus('done')
    await new Promise(r => setTimeout(r, 600))
    onConnect({ host: host.trim(), username: username.trim() || 'root', port: Number(port) || 22, sshKey })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)' }}>
      <div className="glass rounded-2xl p-8 w-full max-w-md mx-4 space-y-6 animate-slide-in" style={{ border: '1px solid rgba(99,102,241,0.3)' }}>
        {/* ヘッダー */}
        <div className="text-center space-y-1">
          <div className="text-4xl">🐱</div>
          <h2 className="text-xl font-bold text-white">VPSに接続するニャ</h2>
          <p className="text-gray-400 text-sm">インシデント対応を始める前に、守るべきVPSを教えてニャ</p>
        </div>

        {/* フォーム */}
        <div className="space-y-4">
          {/* ホスト */}
          <div className="space-y-1">
            <label className="text-xs text-gray-400 font-medium uppercase tracking-wider">ホスト / IP</label>
            <input
              type="text"
              className="w-full bg-black/30 border border-gray-700 rounded-xl px-4 py-2.5 text-sm font-mono text-gray-200 focus:outline-none focus:border-indigo-500 transition-colors"
              placeholder="192.168.1.1 または example.com"
              value={host}
              onChange={e => setHost(e.target.value)}
              disabled={status !== 'idle'}
            />
          </div>

          {/* ユーザー名 & ポート */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs text-gray-400 font-medium uppercase tracking-wider">ユーザー名</label>
              <input
                type="text"
                className="w-full bg-black/30 border border-gray-700 rounded-xl px-4 py-2.5 text-sm font-mono text-gray-200 focus:outline-none focus:border-indigo-500 transition-colors"
                placeholder="root"
                value={username}
                onChange={e => setUsername(e.target.value)}
                disabled={status !== 'idle'}
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs text-gray-400 font-medium uppercase tracking-wider">ポート</label>
              <input
                type="number"
                className="w-full bg-black/30 border border-gray-700 rounded-xl px-4 py-2.5 text-sm font-mono text-gray-200 focus:outline-none focus:border-indigo-500 transition-colors"
                placeholder="22"
                value={port}
                onChange={e => setPort(e.target.value)}
                disabled={status !== 'idle'}
              />
            </div>
          </div>

          {/* SSH秘密鍵 */}
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <label className="text-xs text-gray-400 font-medium uppercase tracking-wider">SSH 秘密鍵 <span className="text-gray-600 normal-case tracking-normal">（限定権限ユーザー推奨: nekoguard）</span></label>
              <button
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
                onClick={() => fileRef.current?.click()}
                disabled={status !== 'idle'}
              >
                ファイルから読み込む
              </button>
              <input ref={fileRef} type="file" className="hidden" accept=".pem,.key,.txt,*" onChange={handleKeyFile} />
            </div>
            <textarea
              className="w-full bg-black/30 border border-gray-700 rounded-xl px-4 py-3 text-xs font-mono text-gray-300 resize-none focus:outline-none focus:border-indigo-500 transition-colors"
              rows={5}
              placeholder={'-----BEGIN OPENSSH PRIVATE KEY-----\n...\n-----END OPENSSH PRIVATE KEY-----'}
              value={sshKey}
              onChange={e => setSshKey(e.target.value)}
              disabled={status !== 'idle'}
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}
        </div>

        {/* 接続ボタン */}
        <button
          className="w-full py-3.5 rounded-xl font-bold text-white transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          style={{ background: status === 'done' ? 'linear-gradient(135deg, #10b981, #34d399)' : 'linear-gradient(135deg, #6366f1, #818cf8)' }}
          onClick={handleConnect}
          disabled={status !== 'idle'}
        >
          {status === 'idle' && <><span>🔐</span> VPSに接続してNekoGuardを起動するニャ</>}
          {status === 'connecting' && (
            <>
              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              接続中...
            </>
          )}
          {status === 'done' && <><span>✅</span> 接続確立！NekoGuard起動中...</>}
        </button>

        <p className="text-center text-xs text-gray-600">
          秘密鍵はセッション中のみメモリに保持されます。ディスクには保存されません。<br />
          本番運用では限定権限の <code className="text-gray-500">nekoguard</code> ユーザーを推奨します。
        </p>
      </div>
    </div>
  )
}
