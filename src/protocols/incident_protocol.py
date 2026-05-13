from protocols.cat_protocol import CATProtocol
from protocols.abc_protocol import ABCProtocol

class IncidentResponseProtocol:
    """
    インシデントレスポンスのルータークラス。
    侵害が現在進行形(Active)か過去のもの(Past)かによって、
    CATプロトコルまたはABCプロトコルにルーティングする。
    """
    def __init__(self, demo_mode=False):
        self.demo_mode = demo_mode

    def execute(self, breach_status="active"):
        """
        breach_status: 'active' (現在進行形) または 'past' (事後)
        """
        print("\n=======================================================")
        print("🚨 NekoGuard プロトコルルーター起動！")
        print("   深呼吸してニャ。ボクがしっかりサポートするから大丈夫だよ。")
        print("=======================================================\n")
        
        if breach_status == "active":
            print("👉 [状況判断] 現在進行形の侵害 (Active Breach) を検知しました。")
            print("👉 CATプロトコルへ移行します。")
            protocol = CATProtocol(demo_mode=self.demo_mode)
            protocol.execute()
        elif breach_status == "past":
            print("👉 [状況判断] 過去の侵害 (Past Breach) を検知しました。")
            print("👉 ABCプロトコルへ移行します。")
            protocol = ABCProtocol(demo_mode=self.demo_mode)
            protocol.execute()
        else:
            print("❌ 不明な侵害ステータスです。プロトコルを停止します。")

