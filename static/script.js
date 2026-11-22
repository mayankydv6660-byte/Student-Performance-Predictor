const form = document.getElementById("predictionForm");

const resultPlaceholder = document.getElementById("resultPlaceholder");
const resultContent = document.getElementById("resultContent");
const loading = document.getElementById("loading");
const errorMessage = document.getElementById("errorMessage");

const gradeValue = document.getElementById("gradeValue");
const performanceValue = document.getElementById("performanceValue");
const modelValue = document.getElementById("modelValue");

// Multi-Outcome elements
const dropoutRiskValue = document.getElementById("dropoutRiskValue");
const placementValue = document.getElementById("placementValue");
const remedialValue = document.getElementById("remedialValue");
const topFactorsList = document.getElementById("topFactorsList");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    // Hide previous messages
    resultPlaceholder.classList.add("hidden");
    resultContent.classList.add("hidden");
    errorMessage.classList.add("hidden");

    // Show loading
    loading.classList.remove("hidden");

    // Collect 15 exact questions data
    const student = {
        student_name: document.getElementById("student_name").value.trim() || "Anonymous",
        cgpa: parseFloat(document.getElementById("cgpa").value),
        attendance: parseFloat(document.getElementById("attendance").value),
        quiz_score: parseFloat(document.getElementById("quiz_score").value),
        backlogs: parseInt(document.getElementById("backlogs").value, 10),
        entrance_score: parseFloat(document.getElementById("entrance_score").value),
        study_hours: parseFloat(document.getElementById("study_hours").value),
        lms_usage: parseInt(document.getElementById("lms_usage").value, 10),
        class_participation: parseInt(document.getElementById("class_participation").value, 10),
        extra_activities: parseFloat(document.getElementById("extra_activities").value),
        study_style: parseInt(document.getElementById("study_style").value, 10),
        sleep_hours: parseFloat(document.getElementById("sleep_hours").value),
        screen_time: parseFloat(document.getElementById("screen_time").value),
        stress_level: parseInt(document.getElementById("stress_level").value, 10),
        procrastination: parseInt(document.getElementById("procrastination").value, 10),
        health_status: parseInt(document.getElementById("health_status").value, 10)
    };

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(student)
        });

        const result = await response.json();

        if (!response.ok || result.status !== "success") {
            throw new Error(result.message || "Prediction failed.");
        }

        loading.classList.add("hidden");

        const prediction = result.prediction;

        // Display Grade, Level, and Model Name
        gradeValue.textContent = Number(prediction.predicted_grade).toFixed(2);
        performanceValue.textContent = prediction.performance_level;
        modelValue.textContent = prediction.model_name;

        // Multi-Outcome predictions
        if (prediction.outcomes) {
            if (dropoutRiskValue) {
                dropoutRiskValue.textContent = prediction.outcomes.dropout_risk;
                dropoutRiskValue.style.color = prediction.outcomes.dropout_risk === "High" ? "#dc2626" : (prediction.outcomes.dropout_risk === "Moderate" ? "#d97706" : "#16a34a");
            }
            if (placementValue) {
                placementValue.textContent = prediction.outcomes.placement_readiness;
            }
            if (remedialValue) {
                remedialValue.textContent = prediction.outcomes.remedial_needs;
            }
        }

        // Top Factors List
        if (topFactorsList && prediction.top_factors) {
            topFactorsList.innerHTML = "";
            prediction.top_factors.forEach(f => {
                const li = document.createElement("li");
                li.innerHTML = `<span>${f.feature}</span> <strong>${(f.importance * 100).toFixed(1)}%</strong>`;
                topFactorsList.appendChild(li);
            });
        }

        resultContent.classList.remove("hidden");

        // Dynamic Grade Color
        if (prediction.performance_level === "Excellent" || prediction.performance_level === "Good") {
            performanceValue.style.color = "#16a34a";
        } else if (prediction.performance_level === "Needs Improvement") {
            performanceValue.style.color = "#d97706";
        } else {
            performanceValue.style.color = "#dc2626";
        }

    } catch (error) {
        loading.classList.add("hidden");
        errorMessage.textContent = "Prediction Error: " + error.message;
        errorMessage.classList.remove("hidden");
        resultPlaceholder.classList.remove("hidden");
    }
});
