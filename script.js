// Function to show specific page and hide others
function showPage(pageId) {
    const pages = ["landing-page", "login-page", "register-page", "main-page"];
    pages.forEach(page => {
        document.getElementById(page).classList.add("hidden");
    });
    document.getElementById(pageId).classList.remove("hidden");
}

// Function to handle user registration
function register() {
    const username = document.getElementById("reg-username").value.trim();
    const password = document.getElementById("reg-password").value.trim();

    // Basic validation
    if (username.length < 4 || password.length < 4) {
        alert("Username and password must be at least 4 characters long.");
        return;
    }

    // Store user credentials in local storage
    localStorage.setItem("username", username);
    localStorage.setItem("password", password);

    alert("Account created successfully! Please log in.");
    showPage("login-page"); // Redirect to login page
}

// Function to handle login
function login() {
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value.trim();

    // Get stored credentials
    const storedUsername = localStorage.getItem("username");
    const storedPassword = localStorage.getItem("password");

    // Check if the entered credentials match the stored ones
    if (username === storedUsername && password === storedPassword) {
        alert("Login successful!");
        showPage("main-page"); // Redirect to main page
    } else {
        alert("Invalid username or password. Please try again.");
    }
}

// Function to process safe route (Placeholder)
function processRoute() {
    const currentLocation = document.getElementById("current-location").value;
    const destination = document.getElementById("destination").value;

    if (currentLocation && destination) {
        document.getElementById("output").innerText = `Finding the safest route from ${currentLocation} to ${destination}...`;
    } else {
        alert("Please enter both locations.");
    }
}

// Function to logout
function logout() {
    alert("Logged out successfully!");
    showPage("landing-page");
}
