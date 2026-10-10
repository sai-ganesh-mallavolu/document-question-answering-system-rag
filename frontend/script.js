const fileInput = document.getElementById("fileInput");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");
const chatMessages = document.getElementById("chatMessages");

const BACKEND_URL = "https://document-question-answering-system-rag.onrender.com";





/* Upload document */

uploadButton.addEventListener("click", async () => {

    const file = fileInput.files[0];

    if (!file) {

        uploadStatus.innerHTML =
            "⚠️ <strong>Please select a PDF or TXT file.</strong>";

        uploadStatus.style.color = "#dc2626";
        uploadStatus.style.background = "#fef2f2";
        uploadStatus.style.display = "block";

        return;
    }

    const fileName = file.name.toLowerCase();

    const allowedTypes = [
        ".pdf",
        ".txt"
    ];

    const isAllowed = allowedTypes.some(
        type => fileName.endsWith(type)
    );

    if (!isAllowed) {

        uploadStatus.innerHTML =
            "❌ <strong>Only PDF and TXT files are allowed.</strong>";

        uploadStatus.style.color = "#dc2626";
        uploadStatus.style.background = "#fef2f2";
        uploadStatus.style.display = "block";

        return;
    }

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    uploadButton.disabled = true;

    uploadButton.textContent =
        "Processing...";

    uploadStatus.innerHTML =
        "⏳ <strong>Processing document...</strong><br>Please wait...";

    uploadStatus.style.color =
        "#2563eb";

    uploadStatus.style.background =
        "#eff6ff";

    uploadStatus.style.display =
        "block";

    try {

        const response = await fetch(
            `${BACKEND_URL}/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const data =
            await response.json();

        if (!response.ok) {

            uploadStatus.innerHTML =
                `❌ <strong>${data.error || "Upload failed."}</strong>`;

            uploadStatus.style.color =
                "#dc2626";

            uploadStatus.style.background =
                "#fef2f2";

            uploadStatus.style.display =
                "block";

            return;
        }


        /* Save uploaded filename */




        /* Show upload success */

        uploadStatus.innerHTML =
            `📄 <strong>${data.file_name}</strong> uploaded successfully.<br>
            You can now ask questions.`;

        uploadStatus.style.color =
            "#166534";

        uploadStatus.style.background =
            "#f0fdf4";

        uploadStatus.style.display =
            "block";

    } catch (error) {

        console.error(
            "Upload error:",
            error
        );

        uploadStatus.innerHTML =
            "❌ <strong>Could not connect to the backend.</strong><br>" +
            "Make sure Flask is running.";

        uploadStatus.style.color =
            "#dc2626";

        uploadStatus.style.background =
            "#fef2f2";

        uploadStatus.style.display =
            "block";

    } finally {

        uploadButton.disabled = false;

        uploadButton.textContent =
            "Upload Document";
    }
});


/* Ask question */

askButton.addEventListener(
    "click",
    askQuestion
);


/* Ask question using Enter */

questionInput.addEventListener(
    "keydown",
    event => {

        if (event.key === "Enter") {

            event.preventDefault();

            askQuestion();
        }
    }
);


/* Send question to backend */

async function askQuestion() {

    const question =
        questionInput.value.trim();

    if (!question) {

        return;
    }

    addMessage(
        question,
        "user"
    );

    questionInput.value = "";

    askButton.disabled = true;

    questionInput.disabled = true;

    askButton.textContent =
        "Thinking...";

    const thinkingMessage =
        addMessage(
            "⏳ Thinking...",
            "assistant"
        );

    try {

        const response =
            await fetch(
                `${BACKEND_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })
                }
            );

        const data =
            await response.json();

        thinkingMessage.remove();

        if (!response.ok) {

            addMessage(
                `❌ ${data.error || "Something went wrong."}`,
                "assistant"
            );

            return;
        }

        let sourceText = "";

        if (data.source) {

            sourceText =
                `<br><br><strong>Source:</strong> ${data.source}`;
        }

        addMessage(
            `${data.answer}${sourceText}`,
            "assistant"
        );

    } catch (error) {

        console.error(
            "Chat error:",
            error
        );

        thinkingMessage.remove();

        addMessage(
            "❌ Could not connect to the backend. " +
            "Make sure Flask is running.",
            "assistant"
        );

    } finally {

        askButton.disabled = false;

        questionInput.disabled = false;

        askButton.textContent =
            "Ask";

        questionInput.focus();
    }
}


/* Add message to chat */

function addMessage(
    text,
    type
) {

    const message =
        document.createElement("div");

    message.classList.add(
        "message",
        type
    );

    message.innerHTML =
        text;

    chatMessages.appendChild(
        message
    );

    chatMessages.scrollTop =
        chatMessages.scrollHeight;

    return message;
}