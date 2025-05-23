from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ResponseRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 各質問の個別カラム（q1〜q27）
    q1 = db.Column(db.Text)
    q2 = db.Column(db.Text)
    q3 = db.Column(db.Text)
    q4 = db.Column(db.Text)
    q5 = db.Column(db.Text)
    q6 = db.Column(db.Text)
    q7 = db.Column(db.Text)
    q8 = db.Column(db.Text)
    q9 = db.Column(db.Text)
    q10 = db.Column(db.Text)
    q11 = db.Column(db.Text)
    q12 = db.Column(db.Text)
    q13 = db.Column(db.Text)
    q14 = db.Column(db.Text)
    q15 = db.Column(db.Text)
    q16 = db.Column(db.Text)
    q17 = db.Column(db.Text)
    q18 = db.Column(db.Text)
    q19 = db.Column(db.Text)
    q20 = db.Column(db.Text)
    q21 = db.Column(db.Text)
    q22 = db.Column(db.Text)
    q23 = db.Column(db.Text)
    q24 = db.Column(db.Text)
    q25 = db.Column(db.Text)
    q26 = db.Column(db.Text)
    q27 = db.Column(db.Text)
    
    # AI応答
    prompt_text = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)

    # followup
    selected_plan = db.Column(db.String(10), nullable=True)
    followup_prompt = db.Column(db.Text, nullable=True)
    followup_response = db.Column(db.Text, nullable=True)
