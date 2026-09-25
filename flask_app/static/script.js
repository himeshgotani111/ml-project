document.addEventListener("DOMContentLoaded", () => {
    // 1. Tab Navigation
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-tab");
            
            navButtons.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            document.getElementById(target).classList.add("active");
        });
    });

    // 2. Real-time BMI & Pulse Pressure Calculation
    const heightInput = document.getElementById("height");
    const weightInput = document.getElementById("weight");
    const apHiInput = document.getElementById("ap_hi");
    const apLoInput = document.getElementById("ap_lo");
    const liveBmi = document.getElementById("liveBmi");
    const livePulse = document.getElementById("livePulse");

    function updateLiveMetrics() {
        const h = parseFloat(heightInput.value) || 168;
        const w = parseFloat(weightInput.value) || 75;
        const hi = parseFloat(apHiInput.value) || 120;
        const lo = parseFloat(apLoInput.value) || 80;

        const bmiVal = (w / ((h / 100) ** 2)).toFixed(1);
        const pulseVal = Math.round(hi - lo);

        liveBmi.textContent = bmiVal;
        livePulse.textContent = `${pulseVal} mmHg`;
    }

    [heightInput, weightInput, apHiInput, apLoInput].forEach(input => {
        input.addEventListener("input", updateLiveMetrics);
    });
    updateLiveMetrics();

    // 3. Preset Profiles Menu
    const presetBtn = document.getElementById("presetBtn");
    const presetMenu = document.getElementById("presetMenu");
    let sampleProfiles = [];

    // Fetch sample patients from API
    fetch("/api/sample-patients")
        .then(res => res.json())
        .then(data => {
            if (data.samples) sampleProfiles = data.samples;
        })
        .catch(err => console.log("Could not load sample profiles:", err));

    presetBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        presetMenu.classList.toggle("show");
    });

    document.addEventListener("click", () => {
        presetMenu.classList.remove("show");
    });

    document.querySelectorAll(".preset-item").forEach(item => {
        item.addEventListener("click", () => {
            const idx = parseInt(item.getAttribute("data-sample"));
            if (sampleProfiles[idx]) {
                const p = sampleProfiles[idx];
                document.getElementById("age_years").value = p.age_years;
                document.getElementById("gender").value = p.gender;
                document.getElementById("height").value = p.height;
                document.getElementById("weight").value = p.weight;
                document.getElementById("ap_hi").value = p.ap_hi;
                document.getElementById("ap_lo").value = p.ap_lo;
                document.getElementById("cholesterol").value = p.cholesterol;
                document.getElementById("gluc").value = p.gluc;
                document.getElementById("smoke").value = p.smoke;
                document.getElementById("alco").value = p.alco;
                document.getElementById("active").value = p.active;
                updateLiveMetrics();
            }
        });
    });

    // 4. Form Submission & Prediction API
    const form = document.getElementById("predictionForm");
    const submitBtn = document.getElementById("submitBtn");
    const emptyState = document.getElementById("emptyState");
    const predictionView = document.getElementById("predictionView");
    const riskBadge = document.getElementById("riskBadge");
    const probNumber = document.getElementById("probNumber");
    const probCircle = document.getElementById("probCircle");
    const diagnosisText = document.getElementById("diagnosisText");
    const adviceText = document.getElementById("adviceText");
    const factorsList = document.getElementById("factorsList");
    const resBmi = document.getElementById("resBmi");
    const resPulse = document.getElementById("resPulse");
    const resMap = document.getElementById("resMap");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i data-lucide="loader-2" class="spin"></i> Analyzing Patient Vitals...`;
        lucide.createIcons();

        const payload = {
            age_years: parseFloat(document.getElementById("age_years").value),
            gender: parseInt(document.getElementById("gender").value),
            height: parseFloat(document.getElementById("height").value),
            weight: parseFloat(document.getElementById("weight").value),
            ap_hi: parseFloat(document.getElementById("ap_hi").value),
            ap_lo: parseFloat(document.getElementById("ap_lo").value),
            cholesterol: parseInt(document.getElementById("cholesterol").value),
            gluc: parseInt(document.getElementById("gluc").value),
            smoke: parseInt(document.getElementById("smoke").value),
            alco: parseInt(document.getElementById("alco").value),
            active: parseInt(document.getElementById("active").value)
        };

        try {
            const response = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok) {
                // Show Prediction view
                emptyState.classList.add("hidden");
                predictionView.classList.remove("hidden");

                // Update Risk Badge
                riskBadge.textContent = result.risk_level;
                riskBadge.style.backgroundColor = `${result.risk_color}22`;
                riskBadge.style.color = result.risk_color;
                riskBadge.style.border = `1px solid ${result.risk_color}`;

                // Update Probability Circle
                probNumber.textContent = `${result.disease_probability}%`;
                probNumber.style.color = result.risk_color;
                probCircle.style.borderColor = result.risk_color;

                // Diagnosis & Advice
                diagnosisText.textContent = result.prediction_label;
                diagnosisText.style.color = result.risk_color;
                adviceText.textContent = result.clinical_advice;

                // Contributing Factors
                factorsList.innerHTML = "";
                result.key_factors.forEach(factor => {
                    const li = document.createElement("li");
                    li.innerHTML = `<i data-lucide="chevron-right"></i> ${factor}`;
                    factorsList.appendChild(li);
                });

                // Derived Metrics
                resBmi.textContent = result.derived_metrics.bmi;
                resPulse.textContent = `${result.derived_metrics.pulse_pressure} mmHg`;
                resMap.textContent = `${result.derived_metrics.map_pressure} mmHg`;

                lucide.createIcons();
            } else {
                alert("Error: " + (result.error || "Failed to get prediction"));
            }
        } catch (err) {
            alert("Network error connecting to Flask API: " + err.message);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<i data-lucide="stethoscope"></i> Run AI Cardiovascular Assessment`;
            lucide.createIcons();
        }
    });

    // 5. Load Model Info & Feature Tags (Tab 2)
    fetch("/api/model-info")
        .then(res => res.json())
        .then(data => {
            if (data.accuracy) document.getElementById("mAccuracy").textContent = `${(data.accuracy * 100).toFixed(2)}%`;
            if (data.roc_auc) document.getElementById("mRocAuc").textContent = data.roc_auc.toFixed(4);
            if (data.precision) document.getElementById("mPrecision").textContent = `${(data.precision * 100).toFixed(2)}%`;
            if (data.recall) document.getElementById("mRecall").textContent = `${(data.recall * 100).toFixed(2)}%`;
            if (data.model_name) document.getElementById("mName").textContent = data.model_name;

            if (data.features) {
                const tagsContainer = document.getElementById("featureTags");
                tagsContainer.innerHTML = "";
                data.features.forEach(f => {
                    const tag = document.createElement("span");
                    tag.className = "tag";
                    tag.textContent = f;
                    tagsContainer.appendChild(tag);
                });
            }
        })
        .catch(err => console.log("Model metadata load error:", err));

    // 6. Load Dynamic EDA Statistics (Tab 3)
    fetch("/api/eda-stats")
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            // Update Total Records
            if (data.total_records) {
                const formattedCount = Number(data.total_records).toLocaleString();
                const recordPill = document.getElementById("edaRecordCount");
                if (recordPill) {
                    recordPill.innerHTML = `<i data-lucide="database"></i> ${formattedCount} Records Analyzed`;
                    lucide.createIcons();
                }
                const cardDesc = document.getElementById("edaCardDesc");
                if (cardDesc) {
                    cardDesc.textContent = `Insights computed across ${formattedCount} cleaned cardiovascular records.`;
                }
            }

            // Update Cholesterol vs Disease Rates
            if (data.cholesterol_disease_rate) {
                const rates = data.cholesterol_disease_rate;
                const r1 = rates[1] !== undefined ? rates[1] : rates["1"];
                const r2 = rates[2] !== undefined ? rates[2] : rates["2"];
                const r3 = rates[3] !== undefined ? rates[3] : rates["3"];

                const chol1 = document.getElementById("chol1Bar");
                if (chol1 && r1 !== undefined) {
                    const pct = (r1 * 100).toFixed(1);
                    chol1.style.width = `${pct}%`;
                    chol1.textContent = `${pct}%`;
                }
                const chol2 = document.getElementById("chol2Bar");
                if (chol2 && r2 !== undefined) {
                    const pct = (r2 * 100).toFixed(1);
                    chol2.style.width = `${pct}%`;
                    chol2.textContent = `${pct}%`;
                }
                const chol3 = document.getElementById("chol3Bar");
                if (chol3 && r3 !== undefined) {
                    const pct = (r3 * 100).toFixed(1);
                    chol3.style.width = `${pct}%`;
                    chol3.textContent = `${pct}%`;
                }
            }

            // Update Blood Pressure Averages
            if (data.bp_comparison) {
                const healthyBp = document.getElementById("edaHealthyBp");
                if (healthyBp && data.bp_comparison.healthy_ap_hi !== undefined) {
                    healthyBp.textContent = `${data.bp_comparison.healthy_ap_hi} mmHg`;
                }
                const diseaseBp = document.getElementById("edaDiseaseBp");
                if (diseaseBp && data.bp_comparison.disease_ap_hi !== undefined) {
                    diseaseBp.textContent = `${data.bp_comparison.disease_ap_hi} mmHg`;
                }
            }
        })
        .catch(err => console.log("EDA statistics load error:", err));
});
