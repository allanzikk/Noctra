import jwt
from datetime import datetime, timezone, timedelta
import os
from models import Session
from extensions import db
from utils import success, error
from datetime import datetime, date
from uuid import UUID
from sqlalchemy import text
from flask import jsonify

SESSION_SECRET = os.getenv("SESSION_SECRET")

MAX_TOKEN_AGE_MINUTES = 30
MIN_DURATION_MINUTES = int(os.getenv("MIN_DURATION_MINUTES"))

class sessionFunctions():
    def create_session_token(user_id):
        payload = {
            "user_id": user_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=MAX_TOKEN_AGE_MINUTES),
            "type": "session_token",
        }
        return jwt.encode(payload, SESSION_SECRET, algorithm="HS256")

    
    def verify_session_token(token):
        payload = jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
        if payload.get("type") != "session_token":
            raise ValueError("invalid token for this context.")
        return payload

    def complete_session(self, data, user_id):
        token = data.get("session_token")
        if not token:
            return error(code="TOKEN_INVALID_DATA", message="session_token is required.")
        
        try:
            payload = self.verify_session_token(token)

        except jwt.InvalidSignatureError:
            return error(code="TOKEN_INVALID", message="invalid session_token.")
        
        except jwt.ExpiredSignatureError:
            return error(code="EXPIRED_TOKEN", message="session_token expired.")
        
        if str(payload.get("user_id")) != user_id:
            return error(code="UNAUTHORIZED_TOKEN", message="this token does not belong to current user.")
        
        started_at = datetime.fromisoformat(payload["started_at"])
        elapsed = datetime.now(timezone.utc) - started_at
        if elapsed.total_seconds() < MIN_DURATION_MINUTES * 60:
            return error(code="SESSION_TOO_SHORT", message=f"session can't be lower than {MIN_DURATION_MINUTES} min.")
        
            
        session = Session(user_id=user_id)
        db.session.add(session)
        db.session.commit()
        return success(data={
            "id": session.id,
            "completed_at": session.completed_at,
            "duration_minutes": session.duration_minutes,
            "user_id": session.user_id
        })
    
    def get_sessions(before_cursor, limit, user_id):
        user_id = UUID(user_id)
        try:
            limit = int(limit)
            if not 1 <= limit <= 14 :
                limit = 7
            before_cursor = datetime.strptime(before_cursor, "%Y-%m-%d")
            before_cursor = before_cursor.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            limit = 7
            before_cursor = None
        if before_cursor:
            rows = db.session.execute(text("""
        SELECT DATE(completed_at) AS day, COUNT(*) AS count
        FROM session
        WHERE user_id = :user_id AND DATE(completed_at) < :before_cursor
        GROUP BY DATE(completed_at)
        ORDER BY DATE(completed_at) DESC
        LIMIT :limit
        ;
"""), {"user_id": user_id, "before_cursor": before_cursor, "limit": limit+1}).fetchall()
        else:
            rows = db.session.execute(text("""
        SELECT DATE(completed_at) AS day, COUNT(*) AS count
        FROM session
        WHERE user_id = :user_id
        GROUP BY DATE(completed_at)
        ORDER BY DATE(completed_at) DESC
        LIMIT :limit
        ;
"""), {"user_id": user_id, "limit": limit+1}).fetchall()

        next_cursor = None
        if len(rows) > limit:
            next_cursor = str(rows[limit-1].day)
        rows = rows[:limit]
        days = {}
        for i in rows:
            days[str(i.day)] = i.count
        print(days, flush=True)
        return jsonify({"data": days, "next_cursor": next_cursor}), 200
    
    def total_sessions(user_id):
        user_id = UUID(user_id)
        total = db.session.execute(text("""
        SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE DATE(completed_at) = CURRENT_DATE) AS today
        FROM session
        WHERE user_id = :user_id
        ;
"""), {"user_id": user_id}).fetchall()
        days_streak = db.session.execute(text("""
        SELECT DISTINCT DATE(completed_at) AS day
        FROM session
        WHERE user_id = :user_id
        ORDER BY DATE(completed_at) DESC
        ;
"""), {"user_id": user_id}).fetchall()
        
        streak = 0
        today = date.today()
        if days_streak:
            if (today - days_streak[0].day).days <= 1: 
                streak += 1
                for i, item in enumerate(days_streak):
                    if i == len(days_streak)-1:
                        break
                    if (item.day - days_streak[i+1].day).days <= 1:
                        streak += 1
                    else:
                        break
        
        
        return success(data={
            "total": total[0].total,
            "streak": streak,
            "today": total[0].today
        })
