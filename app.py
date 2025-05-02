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

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

@app.template_filter('markdown')
def markdown_filter(text):
    return Markup(markdown(text, extensions=["extra", "tables", "fenced_code"]))

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        responses = {}

        # q1〜q23（単一回答・テキスト）
        for i in range(1, 24):
            key = f"q{i}"
            responses[key] = request.form.get(key, "")

        # チェックボックス＋その他対応（q11, q25, q26）
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

        # MarkdownをHTMLに変換して保存
        session["step1_prompt"] = prompt_text
        session["step1_response"] = Markup(markdown(ai_response, extensions=["extra", "tables", "fenced_code"]))
        session["step1_response_plain"] = ai_response  # プレーンテキストも保存

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

    return render_template(
        "result.html",
        step1_prompt=session.get("step1_prompt"),
        step1_response=session.get("step1_response"),
        step2_prompt=followup_prompt,
        step2_response=Markup(markdown(followup_response, extensions=["extra", "tables", "fenced_code"])),
    )

# 日付自動計算用のエンドポイント（JavaScriptから呼ばれる）
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
    app.run(debug=True, port=5000)