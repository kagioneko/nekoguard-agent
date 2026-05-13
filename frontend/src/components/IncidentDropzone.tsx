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
        <p className="text-gray-300 font-medium">怖いアラートのスクショやログをここに投げるニャ</p>
        <p className="text-gray-500 text-sm mt-1">PNG / JPG / .log / .txt 対応</p>
      </div>

      {/* テキスト入力 */}
      <div className="glass rounded-2xl p-4 space-y-3">
        <p className="text-gray-400 text-sm font-medium">または、テキストで直接貼り付けるニャ</p>
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
          🚀 NekoGuardに解析してもらうニャ！
        </button>
      </div>
    </div>
  )
}
