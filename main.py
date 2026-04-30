from fastapi import FastAPI
import psycopg2
import time

app = FastAPI()

# 🔥 DATABASE (تأكد من USER الصحيح من Supabase)
DATABASE_CONFIG = {
  host:
aws-1-ap-northeast-1.pooler.supabase.com

port:
6543

database:
postgres

user:
postgres.ffrjmkgzhbkhiksrvlcp

}

def get_db():
    return psycopg2.connect(DATABASE_URL)

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

    if any(x in ua.lower() for x in ["python", "curl", "bot"]):
        score += 50
        reasons.append("bad user agent")

    now = time.time()

    if ip not in requests_log:
        requests_log[ip] = []

    requests_log[ip].append(now)

    recent = [t for t in requests_log[ip] if now - t < 10]

    if len(recent) > 10:
        score += 40
        reasons.append("too many requests")

    result = "human"
    if score >= 70:
        result = "bot"
    elif score >= 40:
        result = "medium"

    # 💾 save
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
