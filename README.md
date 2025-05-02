# 育休プラン提案Webアプリ（OpenAI連携）開発中

このアプリは、日本の育児休業制度と給付金制度に詳しいChatGPT（GPT-4o）を活用し、ユーザーの入力に基づいて育児休業の取得プランを自動提案するWebアプリです。

現在は基本機能が実装されたベータ版であり、今後さらなる機能追加・UI改善・本番環境へのデプロイなどを予定しています。

---

## 使用技術

- Python（Flask）
- OpenAI API（gpt-4o）
- HTML / CSS（Jinja2テンプレート）
- Markdown形式の出力表示
- JavaScript（日付計算）

---

## ローカル実行手順

1. 仮想環境の作成（任意）

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合：venv\Scripts\activate
```

2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

3. `.env` ファイルを作成して、以下のようにOpenAI APIキーを記述：

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

4. Flaskアプリを起動

```bash
python app.py
```

5. ブラウザで `http://localhost:5000` にアクセス

---

## 注意事項

- 本アプリは現在**開発中**です。予告なく機能や構成が変更される可能性があります。
- `.env` にはAPIキーなど機密情報を記載するため、**絶対に公開しないでください**。
- 制度の詳細は厚生労働省などの公式情報をご確認ください。

---

## ライセンス

MIT License
