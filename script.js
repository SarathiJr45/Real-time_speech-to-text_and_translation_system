const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const video = document.getElementById("video");
const originalText = document.getElementById("original");
const translatedText = document.getElementById("translation");

let mediaRecorder;
let socket;

// Access camera and microphone
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
  .then(stream => {
    video.srcObject = stream;

    startBtn.addEventListener("click", () => {
      mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorder.start();
      startBtn.disabled = true;
      stopBtn.disabled = false;

      // Open WebSocket connection
      socket = new WebSocket("ws://localhost:8000/ws");

      // Send audio data to the backend
      mediaRecorder.ondataavailable = (event) => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(event.data);
        }
      };

      // Display transcription and translation
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        originalText.textContent = data.transcription;
        translatedText.textContent = data.translation;
      };

      // Handle WebSocket errors
      socket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      socket.onclose = () => {
        console.log("WebSocket connection closed.");
      };
    });

    stopBtn.addEventListener("click", () => {
      mediaRecorder.stop();
      startBtn.disabled = false;
      stopBtn.disabled = true;
      socket.close();
    });
  })
  .catch(error => console.error("Error accessing media devices:", error));
