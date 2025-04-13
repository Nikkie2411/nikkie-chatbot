from flask import Flask, request, render_template, jsonify, redirect
from chatbot import answer_query, load_data
import os

app = Flask(__name__)

@app.route("/")
def index():
    if request.method == "POST":
        query = request.form["query"]
        response = answer_query(query)
        return render_template("index.html", response=response, query=query)
    return render_template("index.html", response="", query="")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        query = data.get("query", "")
        refresh = data.get("refresh", False)  # Lấy tham số refresh từ request
        if not query:
            return jsonify({"error": "Query không được để trống"}), 400
        response = answer_query(query, refresh_data=refresh)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Debug - Lỗi API /chat: {e}")
        return jsonify({"error": "Lỗi xử lý yêu cầu"}), 500

@app.route("/chat-widget")
def chat_widget():
    return render_template("chat.html")

@app.route("/refresh", methods=["POST"])
def refresh():
    try:
        load_data()  # Tải lại dữ liệu từ Google Drive
        return jsonify({"message": "Dữ liệu đã được làm mới."})
    except Exception as e:
        print(f"Debug - Lỗi làm mới dữ liệu: {e}")
        return jsonify({"error": "Lỗi làm mới dữ liệu."}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)