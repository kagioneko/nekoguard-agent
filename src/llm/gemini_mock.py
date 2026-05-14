class GeminiMock:
    def __init__(self):
        self.model_name = "gemini-mock"

    def analyze_incident(self, input_data: str, is_image: bool = False, state: str = "NORMAL", phase: int = 1, neuro_state=None) -> dict:
        """デモ用のモックレスポンスを返す。フェーズに応じて出力を変更する。"""
        
        text_content = ""
        if not is_image:
            text_content = input_data.lower()
            
        if "unauthorized" in text_content or "leaked" in text_content or "EMERGENCY" in state:
            if phase == 1:
                response_text = "【Wide-scan】\nこれは深刻な事態かもしれません。影響範囲は広範に及んでいる可能性がありますが、落ち着いて対処すれば必ず防げます。影響サービス：Compute Engine, Cloud Storage"
            elif phase == 2:
                response_text = "【Judgment】\n攻撃は現在進行形 (Active Breach) と判断します。非常に危険な状態です。早急に被害を封じ込め、その後に二次被害を防ぐべきです。"
            elif phase == 3:
                response_text = "【Detail analysis】\n不審なIP (192.168.x.x) からのSSHログイン成功履歴が3件。直後に.envファイルへのアクセス記録あり。被害規模：クリティカル。APIキー漏洩の確率95%。"
            else:
                response_text = "【Recovery】\n大丈夫、初期のトリアージと分析は完了しました。この事態を乗り越えるため、The CAT Protocol (Active Breach 対応) に沿って行動しましょう。私はあなたをサポートします。"
        elif "ALERT" in state or "failed login" in text_content:
            if phase == 1:
                response_text = "【Wide-scan】\n少し不審な動きがあります。まだ被害は出ていないようですが、念のため確認しましょう。"
            elif phase == 2:
                response_text = "【Judgment】\n過去の侵害 (Past Breach) の試み、または小規模な攻撃の可能性があります。影響範囲は限定的です。"
            elif phase == 3:
                response_text = "【Detail analysis】\nSSHブルートフォース攻撃の痕跡。成功したログインはありませんが、ポート22が公開されています。"
            else:
                response_text = "【Recovery】\n被害は確認されませんでしたが、再発防止のためにABC Protocolの Containment ステップを実行することをお勧めします。"
        else:
            response_text = f"【Phase {phase}】\n正常稼働中です。異常は検知されませんでした。"

        # NeuroState ヘッダーをモック出力に付加（実際の値を反映）
        if neuro_state is not None:
            import sys, os
            src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            try:
                from neurostate_core.prompt_builder import build_neuro_log_header
                header = build_neuro_log_header(neuro_state)
                response_text = f"{header}\n\n{response_text}"
            except Exception:
                pass

        return {"text": response_text}

