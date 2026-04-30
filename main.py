from fastapi import FastAPI
import psycopg2
import time

app = FastAPI()

# 🔥 DATABASE URL (جاهز من بياناتك)
DATABASE_URL = "postgresql://postgres.ffrjmkgzhbkhiksrvlcp:11223344mmddmM%40%40@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

def get_db():
    return psycopg2.connect(DATABASE_URL)

def safe_close(cur=None, db=None):
    try:
        if cur:
            cur.close()
        if db:
            db.close()
    except:
        pass

# 🧠 تخزين مؤقت (RAM)
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

    # 🧠 User-Agent detection
    if any(x in ua.lower() for x in ["python", "curl", "bot", "scraper"]):
        score += 50
        reasons.append("suspicious user-agent")

    # ⚡ Speed detection
    now = time.time()

    if ip not in requests_log:
        requests_log[ip] = []

    requests_log[ip].append(now)

    recent = [t for t in requests_log[ip] if now - t < 10]

    if len(recent) > 10:
        score += 40
        reasons.append("high request rate")

    # 🎯 النتيجة
    if score >= 70:
        result = "bot"
    elif score >= 40:
        result = "medium"
    else:
        result = "human"

    # 💾 حفظ في الداتابيس
    cur = None
    db = None

    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("""
            INSERT INTO bot_logs (ip, user_agent, path, score, result)
            VALUES (%s, %s, %s, %s, %s)
        """, (ip, ua, path, score, result))

        db.commit()

    except Exception as e:
        print("🔥 DB ERROR:", e)

    finally:
        safe_close(cur, db)

    return {


        @app.get("/stats")
def stats():
    db = None
    cur = None
    try:
        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT COUNT(*) FROM bot_logs WHERE result='human'")
        human = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM bot_logs WHERE result='medium'")
        medium = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM bot_logs WHERE result='bot'")
        bot = cur.fetchone()[0]

        return {
            "human": human,
            "medium": medium,
            "bot": bot
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if cur:
            cur.close()
        if db:
            db.close()
        "result": result,
        "score": score,
        "reasons": reasons
    }
