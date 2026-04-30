from fastapi import FastAPI
import time
import psycopg2

app = FastAPI()

# 🔥 انسخ هذا من Supabase (Connect → Transaction pooler)
DATABASE_URL = "postgresql://postgres.xxxxx:PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"

def get_db():
    return psycopg2.connect(DATABASE_URL)

# RAM storage
requests_log = {}

@app.get("/")
def home():
    return {"message": "Bot Detector Running 🤖"}

@app.post("/detect")
def detect(data: dict):

    ip = data.get("ip")
    ua = data.get("user_agent", "")
    path = data.get("path", "/")

    score = 0
    reasons = []

    # 🧠 User-Agent check
    if any(bot in ua.lower() for bot in ["python", "curl", "bot", "scraper"]):
        score += 50
        reasons.append("suspicious user-agent")

    # ⚡ Speed check
    now = time.time()

    if ip not in requests_log:
        requests_log[ip] = []

    requests_log[ip].append(now)

    recent = [t for t in requests_log[ip] if now - t < 10]

    if len(recent) > 10:
        score += 40
        reasons.append("high request rate")

    # 🎯 result
    if score >= 70:
        result = "bot"
    elif score >= 40:
        result = "medium"
    else:
        result = "human"

    # 💾 SAVE TO DATABASE
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO bot_logs (ip, user_agent, path, score, result)
            VALUES (%s, %s, %s, %s, %s)
        """, (ip, ua, path, score, result))

        db.commit()

        cur.close()
        db.close()

    except Exception as e:
        print("DB ERROR:", e)

    return {
        "result": result,
        "score": score,
        "reasons": reasons
    }
