async function generateMCQs() {
    let formData = new FormData();
    let fileInput = document.getElementById("pdfFile");
    if (!fileInput.files.length) {
        alert("Please upload a PDF file.");
        return;
    }
    formData.append("pdf_file", fileInput.files[0]);

    document.getElementById("mcqContainer").innerHTML = "<p>Generating MCQs...</p>";

    let response = await fetch("/generate_mcqs", {
        method: "POST",
        body: formData
    });

    let data = await response.json();
    if (data.error) {
        document.getElementById("mcqContainer").innerHTML = "<p style='color:red;'>" + data.error + "</p>";
        return;
    }

    displayMCQs(data.mcqs);
}

function displayMCQs(mcqs) {
    let container = document.getElementById("mcqContainer");
    container.innerHTML = "";

    mcqs.forEach((mcq, index) => {
        let safeAnswer = mcq.answer.replace(/[()]/g, "").trim(); // Remove unwanted characters like (b)

        mcqElement = document.createElement("div");
        mcqElement.innerHTML = `
            <p><strong>Question:</strong> ${mcq.question}</p>
            <p><strong>Options:</strong></p>
            ${mcq.options.map((option, i) => `
                <label>
                    <input type="radio" name="q${index}" value="${option.trim()}">
                    ${String.fromCharCode(97 + i)}. ${option}
                </label><br>
            `).join("")}
            <button onclick="checkAnswer(${index}, '${safeAnswer}')">Submit</button>
            <p id="result${index}" style="color:blue;"></p>
            <hr>
        `;
        container.appendChild(mcqElement);
    });
}

function checkAnswer(index, correctAnswer) {
    let selectedOption = document.querySelector(`input[name="q${index}"]:checked`);
    let resultElement = document.getElementById(`result${index}`);

    if (!selectedOption) {
        resultElement.innerHTML = "<span style='color:red;'>Please select an answer.</span>";
        return;
    }

    let selectedValue = selectedOption.value.trim().toLowerCase();
    let formattedCorrectAnswer = correctAnswer.trim().toLowerCase();

    console.log(`Selected: "${selectedValue}" | Correct: "${formattedCorrectAnswer}"`); // Debugging log

    if (selectedValue === formattedCorrectAnswer) { 
        resultElement.innerHTML = "<span style='color:green;'>Correct!</span>";
    } else {
        resultElement.innerHTML = `<span style='color:red;'>Incorrect! The correct answer is: ${correctAnswer}</span>`;
    }
}
