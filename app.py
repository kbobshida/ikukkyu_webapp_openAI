# app.py
from flask import Flask, render_template, request, session, jsonify
from flask_session import Session
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
from markdown import markdown
from markupsafe import Markup
from datetime import datetime, timedelta
from models import db, ResponseRecord

# 環境変数とOpenAI初期化
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Flask設定
app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///responses.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 拡張機能初期化
db.init_app(app)
Session(app)

with app.app_context():
    db.create_all()

# Markdownフィルター
@app.template_filter('markdown')
def markdown_filter(text):
    return Markup(markdown(text, extensions=["extra", "tables", "fenced_code"]))

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        responses = {}

        for i in range(1, 24):
            key = f"q{i}"
            responses[key] = request.form.get(key, "")

        def handle_checkboxes(base_key, other_key):
            selected = request.form.getlist(base_key)
            other_val = request.form.get(other_key, "").strip()
            if any("その他" in s for s in selected) and other_val:
                selected.append(f"（内容：{other_val}）")
            return "、".join(selected)

        responses["q11"] = handle_checkboxes("q11", "q11_other")
        responses["q25"] = handle_checkboxes("q25", "q25_other")
        responses["q26"] = handle_checkboxes("q26", "q26_other")
        responses["q24"] = request.form.get("q24", "")
        responses["q27"] = request.form.get("q27", "")

        prompt_text = render_template("prompt_template.txt", responses=responses)
        system_content = render_template("system_template.txt")

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7
        )
        ai_response = response.choices[0].message.content.strip()

        session["step1_prompt"] = prompt_text
        session["step1_response"] = Markup(markdown(ai_response, extensions=["extra", "tables", "fenced_code"]))
        session["step1_response_plain"] = ai_response

        record = ResponseRecord(
            q1=responses["q1"], q2=responses["q2"], q3=responses["q3"], q4=responses["q4"],
            q5=responses["q5"], q6=responses["q6"], q7=responses["q7"], q8=responses["q8"],
            q9=responses["q9"], q10=responses["q10"], q11=responses["q11"], q12=responses["q12"],
            q13=responses["q13"], q14=responses["q14"], q15=responses["q15"], q16=responses["q16"],
            q17=responses["q17"], q18=responses["q18"], q19=responses["q19"], q20=responses["q20"],
            q21=responses["q21"], q22=responses["q22"], q23=responses["q23"], q24=responses["q24"],
            q25=responses["q25"], q26=responses["q26"], q27=responses["q27"],
            prompt_text=prompt_text,
            ai_response=ai_response
        )
        db.session.add(record)
        db.session.commit()
        session["record_id"] = record.id

        return render_template(
            "result.html",
            step1_prompt=session["step1_prompt"],
            step1_response=session["step1_response"],
            step2_prompt=None,
            step2_response=None
        )

    return render_template("form.html")

@app.route("/followup", methods=["POST"])
def followup():
    selected_plan = request.form.get("selected_plan", "①")
    followup_prompt = render_template("followup_template.txt", selected_plan=selected_plan)
    system_content = render_template("system_template.txt")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": session.get("step1_prompt", "")},
            {"role": "assistant", "content": session.get("step1_response_plain", "")},
            {"role": "user", "content": followup_prompt}
        ],
        temperature=0.7
    )
    followup_response = response.choices[0].message.content.strip()

    record_id = session.get("record_id")
    if record_id:
        record = ResponseRecord.query.get(record_id)
        if record:
            record.selected_plan = selected_plan
            record.followup_prompt = followup_prompt
            record.followup_response = followup_response
            db.session.commit()

    return render_template(
        "result.html",
        step1_prompt=session.get("step1_prompt"),
        step1_response=session.get("step1_response"),
        step2_prompt=followup_prompt,
        step2_response=Markup(markdown(followup_response, extensions=["extra", "tables", "fenced_code"])),
    )

@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    due_date_str = data.get("due_date")
    is_multiple = data.get("is_multiple")

    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return jsonify({"error": "無効な日付形式です"}), 400

    pre_days = 98 if is_multiple else 42
    pre_start = due_date - timedelta(days=pre_days)
    pre_end = due_date
    post_start = due_date + timedelta(days=1)
    post_end = due_date + timedelta(weeks=8)

    return jsonify({
        "産前休業開始日": pre_start.strftime("%Y-%m-%d"),
        "産前休業終了日": pre_end.strftime("%Y-%m-%d"),
        "産後休業開始日": post_start.strftime("%Y-%m-%d"),
        "産後休業終了日": post_end.strftime("%Y-%m-%d")
    })

if __name__ == "__main__":
    app.run(debug=True, port=4000)
