(function () {
    const chatContainer = document.createElement("div");
    chatContainer.innerHTML = `
        <div class="chat-toggle" onclick="toggleChat()">💬</div>
        <div class="chat-container" id="chatContainer">
            <div class="chat-header">Hỏi đáp cùng Nikkie</div>
            <div class="chat-body" id="chatBody">
                <div class="bot-message">Xin chào! Tôi là Nikkie, chatbot sẽ giúp bạn trả lời câu hỏi về thuốc trong nhi khoa.</div>
            </div>
            <div class="chat-input">
                <input type="text" id="chatInput" placeholder="Nhập câu hỏi..." onkeypress="if(event.key === 'Enter') sendMessage()">
                <button onclick="sendMessage()">Gửi</button>
            </div>
        </div>
    `;
    document.body.appendChild(chatContainer);

    const style = document.createElement("style");
    style.textContent = `
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap');
        .chat-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            max-height: 500px;
            background: #ffffff;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: none;
            flex-direction: column;
            z-index: 1000;
            font-family: 'Roboto', sans-serif;
            border: 1px solid #e0e0e0;
        }
        .chat-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: #28a745;
            color: #fff;
            border-radius: 50%;
            display: flex -webkit-flex;
            align-items: center;
kii            justify-content: center;
            cursor: pointer;
            font-size: 24, sans-serif;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
            z-index: 1001;
            transition: background 0.3s;
        }
        .chat-toggle:hover {
            background: #218838;
        }
        .chat-header {
            background: #28a745;
            color: #fff;
            padding: 12px;
            border-radius: 15px 15px 0 0;
            font-size: 16px;
            font-weight: 500;
            text-align: center;
        }
        .chat-body {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            max-height: 400px;
            background: #f9f9f9;
        }
        .user-message {
            background: #28a745;
            color: #fff;
            padding: 10px 14px;
            border-radius: 15px 15px 0 15px;
            margin: 8px 10px 8px 50px;
            max-width: 80%;
            word-wrap: break-word;
            align-self: flex-end;
            white-space: pre-wrap;
            line-height: 1.5;
            font-size: 14px;
        }
        .bot-message {
            background: #ffffff;
            color: #333;
            padding: 10px 14px;
            border-radius: 15px 15px 15px 0;
            margin: 8px 50px 8px 10px;
            max-width: 80%;
            word-wrap: break-word;
            align-self: flex-start;
            white-space: pre-wrap;
            line-height: 1.5;
            font-size: 14px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        .bot-message::before {
            content: "• ";
            color: #28a745;
            font-weight: bold;
        }
        .chat-input {
            display: flex;
            padding: 10px;
            border-top: 1px solid #e0e0e0;
            background: #fff;
            border-radius: 0 0 15px 15px;
        }
        .chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
            font-size: 14px;
            font-family: 'Roboto', sans-serif;
        }
        .chat-input button {
            margin-left: 10px;
            padding: 10px 20px;
            background: #28a745;
            color: #fff;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        .chat-input button:hover {
            background: #218838;
        }
        @media (max-width: 400px) {
            .chat-container {
                width: 90%;
                bottom: 10px;
                right: 10px;
            }
        }
    `;
    document.head.appendChild(style);

    window.toggleChat = function () {
        const container = document.getElementById("chatContainer");
        const toggle = document.querySelector(".chat-toggle");
        if (container.style.display === "flex") {
            container.style.display = "none";
            toggle.style.display = "flex";
        } else {
            container.style.display = "flex";
            toggle.style.display = "none";
        }
    };

    window.sendMessage = async function () {
        const input = document.getElementById("chatInput");
        const chatBody = document.getElementById("chatBody");
        const query = input.value.trim();

        if (!query) return;

        const userMsg = document.createElement("div");
        userMsg.className = "user-message";
        userMsg.textContent = query;
        chatBody.appendChild(userMsg);

        input.value = "";
        chatBody.scrollTop = chatBody.scrollHeight;

        try {
            const response = await fetch("http://localhost:5000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });
            const data = await response.json();

            const botMsg = document.createElement("div");
            botMsg.className = "bot-message";
            botMsg.textContent = data.response || data.error || "Không có thông tin phù hợp.";
            chatBody.appendChild(botMsg);
        } catch (error) {
            const botMsg = document.createElement("div");
            botMsg.className = "bot-message";
            botMsg.textContent = "Lỗi kết nối, vui lòng thử lại.";
            chatBody.appendChild(botMsg);
        }

        chatBody.scrollTop = chatBody.scrollHeight;
    };
})();