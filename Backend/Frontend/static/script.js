let mediaRecorder;
let audioChunks = [];

const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const output = document.getElementById("output");

recordBtn.onclick = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log("Microphone access granted");

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            console.log("Recording stopped. Chunks:", audioChunks.length);
            if (audioChunks.length === 0) {
                output.value = "No audio recorded!";
                return;
            }

            const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
            console.log("Audio blob size:", audioBlob.size);

            const formData = new FormData();
            formData.append("file", audioBlob, "recording.webm"); 

            output.value = "Transcribing...";

            try {
                const response = await fetch("/transcribe", {
                    method: "POST",
                    body: formData
                });
                const data = await response.json();
                console.log("Server response:", data);
                if (data.error){
                    output.value = "❌ Error: " + data.error;
                }
                else{
                    const topEmotion = data.emotion[0][0];
                    const emotion = topEmotion.label;
                    const score = (topEmotion.score * 100).toFixed(1);

                    let emoji = "😐";

                    if(emotion==="joy") emoji="😊";
                    else if(emotion==="anger") emoji="😡";
                    else if(emotion==="sadness") emoji="😢";
                    else if(emotion==="fear") emoji="😨";
                    else if(emotion==="surprise") emoji="😲";
                    else if(emotion==="disgust") emoji="🤢";
                    else if(emotion==="neutral") emoji="😐";

                    output.value = `📝 Text:
${data.text.trim()}

🎭 Emotion:
${emoji} ${emotion}

📊 Confidence:
${score}%`;
                    }
            } catch (err) {
                output.value = "Network error: " + err;
            }
        };

        mediaRecorder.start();
        console.log("Recording started");

        recordBtn.textContent = "🔴 Recording...";
        recordBtn.disabled = true;
        stopBtn.disabled = false;
    } catch (err) {
        console.error("Microphone error:", err);
        output.value = "Error accessing microphone: " + err;
    }
};

stopBtn.onclick = () => {
    if (!mediaRecorder) return;
    mediaRecorder.stop();

    stopBtn.disabled = true;
    recordBtn.disabled = false;
    recordBtn.textContent = "🎙 Start Recording";
};
