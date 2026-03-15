async function analyze() {
    // 1. Get the files from the HTML inputs
    const resumeFile = document.getElementById("resumeFile").files[0];
    const jobFile = document.getElementById("jobFile").files[0];
    
    // 2. Get the places on the screen where we will show results
    const scoreElement = document.getElementById("score");
    const skillsElement = document.getElementById("skills");
    const recElement = document.getElementById("recommendations");
    const statusElement = document.getElementById("status-message");

    // 3. Simple check: Did the user upload both files?
    if (!resumeFile || !jobFile) {
        alert("Please upload both Resume and Job Description PDFs!");
        return;
    }

    // Show a loading message
    statusElement.innerText = "Analyzing your profile... please wait.";
    statusElement.style.color = "blue";

    // 4. Prepare the files to be sent to Python
    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("job", jobFile);

    try {
        // 5. Send the files to your Python Backend (Uvicorn)
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Backend connection failed.");

        // 6. Receive the calculation from Python
        const data = await response.json();

        // 7. Update the Dashboard with the results
        scoreElement.innerText = data.match_score + "%";
        skillsElement.innerText = data.missing_skills.join(", ");
        recElement.innerText = data.recommendations;
        
        // 8. Call our helper function to show the course links
        displayCourses(data.missing_skills);

        statusElement.innerText = "Analysis Complete!";
        statusElement.style.color = "green";

    } catch (error) {
        console.error("Error:", error);
        statusElement.innerText = "Error: Make sure your Python Terminal is running (cd backend -> uvicorn).";
        statusElement.style.color = "red";
    }
}

// Helper function to create the clickable course list
function displayCourses(missingSkills) {
    const list = document.getElementById("course-links");
    list.innerHTML = ""; // Clear any old links
    
    // If no skills are missing, show a success message
    if (!missingSkills || missingSkills[0] === "None") {
        let li = document.createElement("li");
        li.innerText = "🎉 Excellent! You have all the key skills for this role.";
        list.appendChild(li);
        return;
    }
    
    // Create a clickable link for every missing skill found by the AI
    missingSkills.forEach(skill => {
        let li = document.createElement("li");
        li.innerHTML = `<a href="https://www.coursera.org/search?query=${skill}" target="_blank" style="color: #0056b3; font-weight: bold;">
            Master ${skill} on Coursera →
        </a>`;
        list.appendChild(li);
    });
}