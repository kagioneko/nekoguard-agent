# NekoGuard エージェント 使い方メモ 🐾

NekoGuardエージェントの起動と、本格的な6段階インシデント対応デモの体験方法ニャ！

## 🚀 1. 起動方法 (デモモード)

VSCodeの下部ターミナル、またはコマンドプロンプト（PowerShell）を開いて、NekoGuardのルートディレクトリ（`d:\nekoguard-agent`）に移動してから、以下のコマンドを実行してね！

```bash
python src/agents/nekoguard.py
```
*(※ `--demo` を付けなくても、デフォルトでデモモードとして起動します)*

## 🐾 2. デモの体験フロー

1. コマンドを実行すると、NekoGuardが起動し、自動的に `demo/sample_alert.log` のダミーログを読み込みます。
2. LLM（Geminiモック）がログを解析し、深刻なインシデント（EMERGENCY）を検知します。
3. 画面に **本格的な6段階の対応計画 (6-Phase Incident Response)** が出力されます。
4. 以下の承認プロンプトが表示されたら、`y`（または `yes`）と入力してEnterを押してね！
   ```text
   ❓ 提案された対応計画を実行しますか？ (Y/n): 
   ```
5. その後は、Phase 1 から Phase 6 まで、NekoGuardが優しくナビゲートしてくれます。
   *(※ 途中で手動操作をお願いする場面があるので、終わったらEnterを押して進めてね)*

## 🌐 3. 本番環境 (REALモード) で動かす場合

実際に本物の **Gemini API** と **Dynatrace MCP** を使って動かしたい時は、`.env` ファイルにAPIキー等の情報を設定した上で、以下のコマンドで起動してニャ！

```bash
python src/agents/nekoguard.py --real
```
*(※ こちらは実際のログ監視とGemini 3系での分析が走るガチモードです)*

---
明日、VSCodeのターミナルから試してみてね！お疲れ様でしたニャン！😼✨
