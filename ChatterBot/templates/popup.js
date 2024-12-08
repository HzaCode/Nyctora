document.addEventListener("DOMContentLoaded", function() {
    const userInput = document.getElementById("user-input");
    const chatMessages = document.getElementById("chat-messages");

    userInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            const message = userInput.value;
            if (message) {
                appendMessage("user", message);
                userInput.value = "";
                setTimeout(() => {
                    appendMessage("bot", "You said: " + message);
                }, 500);
            }
        }
    });

    function appendMessage(sender, text) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
