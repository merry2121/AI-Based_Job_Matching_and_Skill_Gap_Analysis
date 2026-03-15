document.getElementById("matchBtn").addEventListener("click", async function() {
    const jobFile = document.getElementById("jobFile").files[0];
    const status = document.getElementById("status");
    const resultsDiv = document.getElementById("results");
    const resultsBody = document.getElementById("resultsBody");

    if (!jobFile) {
        alert("Please upload a job description!");
        return;
    }

    status.style.display = "block";
    status.className = "status info";
    status.innerHTML = "Finding matching candidates... please wait.";
    resultsDiv.style.display = "none";
    resultsBody.innerHTML = "";

    try {
        const formData = new FormData();
        formData.append("jobdesc", jobFile);

        const response = await fetch("/match-employer/", {
            method: "POST",
            body: formData
        });
        if (!response.ok) throw new Error("Request failed");
        const data = await response.json();

        data.candidates.forEach(candidate => {
            const row = resultsBody.insertRow();
            // Create a string of badge-styled missing skills
            const missingBadges = candidate.missing.map(skill =>
                `<span class="badge">${skill}</span>`
            ).join(" ");
            row.innerHTML = `
                <td>${candidate.rank}</td>
                <td>${candidate.name}</td>
                <td>${candidate.score}%</td>
                <td>${missingBadges}</td>
            `;
        });

        resultsDiv.style.display = "block";
        status.style.display = "none";
    } catch (error) {
        console.error("Error:", error);
        status.className = "status error";
        status.innerHTML = "An error occurred. Please try again.";
    }
});