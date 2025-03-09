// 1. PAGE NAVIGATION
function showPage(pageId) {
    const pages = ["landing-page", "login-page", "register-page", "main-page"];
    pages.forEach(page => {
        document.getElementById(page).classList.add("hidden");
    });
    document.getElementById(pageId).classList.remove("hidden");
}

function showTab(tabId) {
    const tabs = document.querySelectorAll(".tab-content");
    tabs.forEach(tab => {
        tab.classList.add("hidden");
    });
    document.getElementById(tabId).classList.remove("hidden");
}

// 2. USER REGISTRATION
function register() {
    const username = document.getElementById("reg-username").value.trim();
    const password = document.getElementById("reg-password").value.trim();

    if (username.length < 4 || password.length < 4) {
        alert("Username and password must be at least 4 characters long.");
        return;
    }

    localStorage.setItem("username", username);
    localStorage.setItem("password", password);

    alert("Account created successfully! Please log in.");
    showPage("login-page");
}

// 3. USER LOGIN
function login() {
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value.trim();

    const storedUsername = localStorage.getItem("username");
    const storedPassword = localStorage.getItem("password");

    if (username === storedUsername && password === storedPassword) {
        alert("Login successful!");
        showPage("main-page");
        showTab("crime-prediction");  // Default tab
    } else {
        alert("Invalid username or password. Please try again.");
    }
}

// 4. CRIME PREDICTION
function processPrediction() {
    const state = document.getElementById("prediction-state").value;
    const district = document.getElementById("prediction-district").value;

    if (state && district) {
        const data = {
            state_ut: state.toUpperCase(),
            district: district.toUpperCase(),
            year: 2022,
            // Dummy values for other columns
            murder: 0,
            attempt_to_murder: 0,
            culpable_homicide: 0,
            rape: 0,
            custodial_rape: 0,
            other_rape: 0,
            kidnap_abduction: 0,
            kidnap_women_girls: 0,
            kidnap_others: 0,
            dacoity: 0,
            prep_dacoity: 0,
            robbery: 0,
            burglary: 0,
            theft: 0,
            auto_theft: 0,
            other_theft: 0,
            riots: 0,
            criminal_breach_of_trust: 0,
            cheating: 0,
            counterfieting: 0,
            arson: 0,
            grievous_hurt: 0,
            dowry_deaths: 0,
            assault_women: 0,
            insult_to_modesty_of_women: 0,
            cruelty_by_husband: 0,
            import_girls_foreign: 0,
            death_by_negligence: 0,
            other_ipc_crimes: 0
        };

        document.getElementById("prediction-output").innerText = "Calculating prediction...";

        fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            document.getElementById("prediction-output").innerText = 
                `Predicted Total IPC Crimes: ${result.predicted_total_ipc_crimes}`;
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById("prediction-output").innerText = "Error predicting crime.";
        });
    } else {
        alert("Please enter both state and district.");
    }
}

// 5. SAFE PATH RECOMMENDATION
function processSafePath() {
    const currentLocation = document.getElementById("route-current-location").value;
    const destination = document.getElementById("route-destination").value;

    if (currentLocation && destination) {
        const data = {
            current_location,
            destination
        };

        document.getElementById("route-output").innerText = "Calculating safe route...";

        fetch("http://127.0.0.1:5000/safe_path", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            document.getElementById("route-output").innerText = `Recommended Safe Route: ${result.safe_route}`;
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById("route-output").innerText = "Error finding safe route.";
        });
    } else {
        alert("Please enter both current location and destination.");
    }
}

// 6. EMERGENCY TAP
function emergencyTap() {
    // For demonstration, we just ask for user location in a prompt.
    // In a real app, you'd use HTML5 geolocation or user profile data.
    const userLocation = prompt("Enter your current location (optional):", "Unknown");
    const userId = localStorage.getItem("username") || "Guest";

    fetch("http://127.0.0.1:5000/emergency", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location: userLocation, user_id: userId })
    })
    .then(response => response.json())
    .then(result => {
        alert(result.status);
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Error triggering emergency.");
    });
}

// 7. LOGOUT
function logout() {
    alert("Logged out successfully!");
    showPage("landing-page");
}
