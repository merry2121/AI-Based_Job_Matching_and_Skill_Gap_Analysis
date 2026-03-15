// employer_script.js
document.getElementById("rankBtn").addEventListener("click", async function() {
    const jobFile = document.getElementById("jobdescFile").files[0];
    const candidateFiles = document.getElementById("candidateFiles").files;
    const status = document.getElementById("candidateStatus");
    const table = document.getElementById("rankingTable");
    const body = document.getElementById("rankingBody");

    if (!jobFile || candidateFiles.length === 0) {
        alert("Please upload a job description and at least one resume!");
        return;
    }

    status.innerHTML = "Ranking candidates... please wait.";
    body.innerHTML = "";
    table.style.display = "table";

    try {
        // Step 1: Upload job description
        const jobFormData = new FormData();
        jobFormData.append("jobdesc", jobFile);

        const jobResp = await fetch("http://127.0.0.1:8000/upload-job/", {
            method: "POST",
            body: jobFormData
        });
        if (!jobResp.ok) throw new Error("Job upload failed");
        const jobData = await jobResp.json();
        const jobId = jobData.job_id;

        // Step 2: Upload each resume with the jobId
        const promises = Array.from(candidateFiles).map(file => {
            const resumeFormData = new FormData();
            resumeFormData.append("resume", file);
            resumeFormData.append("job_id", jobId);
            return fetch("http://127.0.0.1:8000/match-candidate/", {
                method: "POST",
                body: resumeFormData
            }).then(res => res.json());
        });

        const results = await Promise.all(promises);

        // Sort by match score descending
        results.sort((a, b) => b.match_score - a.match_score);

        // Populate table
        results.forEach((candidate, index) => {
            const row = body.insertRow();
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${candidate.filename}</td>
                <td>${candidate.match_score}%</td>
                <td>${candidate.missing_skills.join(", ")}</td>
                <td>${candidate.recommendations.join(", ")}</td>
            `;
        });

        status.innerHTML = "Ranking complete!";
    } catch (error) {
        console.error("Error:", error);
        status.innerHTML = "An error occurred. Please try again.";
    }
});