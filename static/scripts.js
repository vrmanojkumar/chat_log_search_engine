document.addEventListener("DOMContentLoaded", function () {
  const searchForm = document.getElementById("searchForm");
  const uploadForm = document.getElementById("uploadForm");
  const messagesList = document.getElementById("messagesList");

  searchForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const query = document.getElementById("searchQuery").value;
    const sender = document.getElementById("senderFilter").value;
    const chatroom = document.getElementById("chatroomFilter").value;
    const date = document.getElementById("dateFilter").value;

    try {
      const response = await fetch(
        `/search_messages?query=${encodeURIComponent(
          query
        )}&sender=${encodeURIComponent(sender)}&chatroom=${encodeURIComponent(
          chatroom
        )}&date=${encodeURIComponent(date)}`
      );

      if (response.ok) {
        const messages = await response.json();
        displayMessages(messages);
      }
    } catch (error) {
      console.error("Error:", error);
      showError("Failed to search messages");
    }
  });

  uploadForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const fileInput = document.getElementById("jsonFile");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
      const response = await fetch("/upload_json", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        showSuccess("Chat logs uploaded successfully");
        searchForm.dispatchEvent(new Event("submit")); // Refresh results
      } else {
        showError("Failed to upload file");
      }
    } catch (error) {
      console.error("Error:", error);
      showError("Network error occurred");
    }
  });

  function displayMessages(messages) {
    messagesList.innerHTML = "";

    if (messages.length === 0) {
      messagesList.innerHTML = `
            <div class="message-item">
                <div class="message-content">No messages found matching your search criteria.</div>
            </div>
        `;
      return;
    }

    messages.forEach((message) => {
      const messageDiv = document.createElement("div");
      messageDiv.className = "message-item";
      messageDiv.innerHTML = `
            <div class="message-header">
                <span class="sender">From: ${message.sender}</span>
                <span class="chatroom">Room: ${message.chatroom}</span>
                <span class="timestamp">Time: ${message.timestamp}</span>
            </div>
            <div class="message-content">
                ${message.highlighted_content}
            </div>
            <div class="message-metadata">
                <span class="relevance">Relevance Score: ${message.relevance_score}</span>
            </div>
        `;
      messagesList.appendChild(messageDiv);
    });
  }

  function showSuccess(message) {
    const alert = document.createElement("div");
    alert.className = "alert alert-success";
    alert.innerHTML = `<i class="fas fa-check-circle"></i>${message}`;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 3500);
  }

  function showError(message) {
    const alert = document.createElement("div");
    alert.className = "alert alert-error";
    alert.innerHTML = `<i class="fas fa-exclamation-triangle"></i>${message}`;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 3500);
  }
});
