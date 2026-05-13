# NekoGuard Dynamic Protocol & NeuroState Upgrade Tasks

- [ ] 1. プロトコルクラスの刷新 (Protocols Layer)
  - [ ] `src/protocols/cat_protocol.py` の新規作成 (Active Breach用)
  - [ ] `src/protocols/abc_protocol.py` の新規作成 (Past Breach用)
  - [ ] `src/protocols/incident_protocol.py` をルーターとして改修
- [ ] 2. エージェントメインフローの改修 (`nekoguard.py`)
  - [ ] デモモードでもユーザーから画像/ログ入力を受け取るように変更
  - [ ] NeuroStateによる4フェーズ遷移（Wide-scan, Judgment, Detail analysis, Recovery）のループ処理実装
  - [ ] CAT/ABCプロトコルの動的選択処理
- [ ] 3. LLMレイヤーの改修 (`gemini_client.py`, `gemini_mock.py`)
  - [ ] プロンプトにフェーズとNeuroStateパラメーターを注入する仕組みの追加
  - [ ] モックにおける各フェーズごとの応答パターン追加
- [ ] 4. 実行テスト
  - [ ] `--demo` モードでの一連の動作確認

## Web Dashboard Tasks
- [x] 1. バックエンド (FastAPI) の構築
  - [x] `src/api/server.py` の作成 (CORS設定, エンドポイント)
  - [x] `nekoguard.py` から分析フェーズをAPI向けに切り出す
  - [x] 依存ライブラリ (`fastapi`, `uvicorn`, `python-multipart` 等) の追加
- [x] 2. フロントエンド (Vite + React) のセットアップ
  - [x] `npx create-vite` コマンドの確認と実行 (`frontend` ディレクトリ)
  - [x] TailwindCSS v3 のセットアップ
- [x] 3. フロントエンド UI コンポーネントの実装
  - [x] NeuroState Meterの実装
  - [x] Chat UI の実装
  - [x] Incident Dropzone の実装
  - [x] Protocol Action Panel の実装
- [x] 4. バックエンドとフロントエンドの結合テスト
  - [x] サーバーとフロントエンドを起動し、正常動作を確認
