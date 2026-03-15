document.getElementById("matchBtn").addEventListener("click", async function() {
    const cvFile = document.getElementById("cvFile").files[0];
    const status = document.getElementById("status");
    const resultsDiv = document.getElementById("results");
    const resultsBody = document.getElementById("resultsBody");

    if (!cvFile) {
        alert("Please upload your CV!");
        return;
    }

    status.innerHTML = "Finding matching jobs... please wait.";
    resultsDiv.style.display = "none";
    resultsBody.innerHTML = "";

    try {
        const formData = new FormData();
        formData.append("cv", cvFile);

        const response = await fetch("/match-seeker/", {
            method: "POST",
            body: formData
        });
        if (!response.ok) throw new Error("Request failed");
        const data = await response.json();

        data.jobs.forEach(job => {
            const row = resultsBody.insertRow();
            row.innerHTML = `
                <td>${job.rank}</td>
                <td>${job.title}</td>
                <td>${job.company}</td>
                <td>${job.location}</td>
                <td>${job.score}%</td>
                <td>${job.missing.join(", ")}</td>
                <td>${job.recommendations.join(", ")}</td>
            `;
        });

        resultsDiv.style.display = "block";
        status.innerHTML = "Matching complete!";
    } catch (error) {
        console.error("Error:", error);
        status.innerHTML = "An error occurred. Please try again.";
    }
});