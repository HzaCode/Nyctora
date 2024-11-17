// Global variables
let currentExercise = null;
let currentBodyPart = null;
let currentUser = null;

// Check authentication status on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
    initializeTabNavigation();
    initializeModalHandlers();
});

// Authentication Functions
async function checkAuthStatus() {
    try {
        const response = await axios.get('/check_auth');
        if (response.data.authenticated) {
            currentUser = response.data.user;
            updateUIForAuthenticatedUser();
        } else {
            updateUIForUnauthenticatedUser();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        updateUIForUnauthenticatedUser();
    }
}

function updateUIForAuthenticatedUser() {
    document.getElementById('login-button').style.display = 'none';
    document.getElementById('profile-button').style.display = 'block';
    document.getElementById('logout-button').style.display = 'block';
    loadTrainingHistory();
    loadFavorites();
}

function updateUIForUnauthenticatedUser() {
    document.getElementById('login-button').style.display = 'block';
    document.getElementById('profile-button').style.display = 'none';
    document.getElementById('logout-button').style.display = 'none';
}

async function login() {
    const username = document.querySelector('#login-form input[name="username"]').value;
    const password = document.querySelector('#login-form input[name="password"]').value;

    try {
        const response = await axios.post('/login', { username, password });
        if (response.data.message) {
            showNotification(response.data.message, 'success');
            currentUser = response.data.user;
            closeAuthModal();
            updateUIForAuthenticatedUser();
        }
    } catch (error) {
        showNotification(error.response?.data?.error || 'Login failed', 'danger');
    }
}

async function register() {
    const username = document.querySelector('#register-form input[name="username"]').value;
    const email = document.querySelector('#register-form input[name="email"]').value;
    const password = document.querySelector('#register-form input[name="password"]').value;

    try {
        const response = await axios.post('/register', { username, email, password });
        showNotification(response.data.message, 'success');
        // Switch to login tab after successful registration
        switchAuthTab('login');
    } catch (error) {
        showNotification(error.response?.data?.error || 'Registration failed', 'danger');
    }
}

async function logout() {
    try {
        await axios.get('/logout');
        currentUser = null;
        updateUIForUnauthenticatedUser();
        showNotification('Logged out successfully', 'success');
    } catch (error) {
        showNotification('Logout failed', 'danger');
    }
}

// Training Plan Functions
async function generateTrainingPlan(bodyPart) {
    if (!currentUser) {
        showNotification('Please login to generate a training plan', 'warning');
        showAuthModal();
        return;
    }

    // Notify user if the free usage limit is about to be reached
    if (currentUser.usage_count >= 8 && currentUser.usage_count < 10) {
        showNotification(`You have ${10 - currentUser.usage_count} free uses left before a subscription is required.`, 'warning', 'free-limit-warning');
    } else if (currentUser.usage_count >= 10) {
        showNotification('Free access limit reached. Please subscribe to continue.', 'danger', 'free-limit-exceeded');
        return;
    }

    currentBodyPart = bodyPart;
    const trainingPlanDiv = document.getElementById("training-plan");
    trainingPlanDiv.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const response = await axios.get(`/get_training_plan?body_part=${bodyPart}`);
        const plan = response.data;
        displayTrainingPlan(plan, bodyPart);
    } catch (error) {
        showNotification('Failed to generate training plan', 'danger');
        trainingPlanDiv.innerHTML = `
            <div class="notification is-danger">
                Failed to generate training plan. Please try again.
            </div>
        `;
    }
}

function displayTrainingPlan(plan, bodyPart) {
    const trainingPlanDiv = document.getElementById("training-plan");
    trainingPlanDiv.innerHTML = "";

    const header = document.createElement('h2');
    header.className = 'title is-2 animate__animated animate__fadeIn';
    header.textContent = `${bodyPart.charAt(0).toUpperCase() + bodyPart.slice(1)} Training Plan`;
    trainingPlanDiv.appendChild(header);

    plan.forEach((exercise, index) => {
        setTimeout(() => {
            const exerciseDiv = createExerciseBox(exercise, bodyPart);
            trainingPlanDiv.appendChild(exerciseDiv);
        }, index * 200);
    });
}

function createExerciseBox(exercise, bodyPart) {
    const exerciseDiv = document.createElement("div");
    exerciseDiv.className = "exercise-box animate__animated animate__fadeInUp";

    const exerciseContent = `
        <div class="level">
            <div class="level-left">
                <h2>${exercise.name}</h2>
            </div>
            <div class="level-right">
                <button class="button is-primary mr-2" onclick="showRecordModal('${exercise.name}', '${bodyPart}')">
                    Record Training
                </button>
                <button class="button is-info" onclick="toggleFavorite('${exercise.name}', '${bodyPart}')">
                    <span class="icon">
                        <i class="fas fa-heart"></i>
                    </span>
                </button>
            </div>
        </div>
        <div class="exercise-details">
            <div class="exercise-description">
                ${exercise.description}
            </div>
            ${exercise.images ? createImageGallery(exercise.images) : ''}
        </div>
        <div class="progress-container">
            <div class="progress-bar" style="width: 0%"></div>
        </div>
    `;

    exerciseDiv.innerHTML = exerciseContent;

    // Animate progress bar
    setTimeout(() => {
        const progressBar = exerciseDiv.querySelector('.progress-bar');
        progressBar.style.width = `${Math.floor(Math.random() * 100)}%`;
    }, 100);

    return exerciseDiv;
}

function createImageGallery(images) {
    return `
        <div class="exercise-images">
            ${images.map(imageUrl => `
                <div class="image-wrapper">
                    <img src="${imageUrl}" class="exercise-image" alt="Exercise demonstration">
                </div>
            `).join('')}
        </div>
    `;
}

// Training Record Functions
function showRecordModal(exerciseName, bodyPart) {
    currentExercise = { name: exerciseName, bodyPart: bodyPart };
    document.getElementById('record-modal').classList.add('is-active');
}

function closeRecordModal() {
    document.getElementById('record-modal').classList.remove('is-active');
    currentExercise = null;
}

async function saveTrainingRecord() {
    if (!currentExercise) return;

    const recordData = {
        exercise_name: currentExercise.name,
        body_part: currentExercise.bodyPart,
        sets: document.getElementById('sets').value,
        reps: document.getElementById('reps').value,
        weight: document.getElementById('weight').value,
        notes: document.getElementById('notes').value
    };

    try {
        const response = await axios.post('/save_training', recordData);
        showNotification('Training record saved successfully', 'success');
        closeRecordModal();
        // Refresh training history if we're on that tab
        if (document.getElementById('training-history-content').style.display !== 'none') {
            loadTrainingHistory();
        }
    } catch (error) {
        showNotification('Failed to save training record', 'danger');
    }
}

// Training History Functions
async function loadTrainingHistory(page = 1) {
    const bodyPart = document.getElementById('history-filter').value;
    try {
        const response = await axios.get(`/get_training_history?page=${page}&body_part=${bodyPart}`);
        displayTrainingHistory(response.data);
    } catch (error) {
        showNotification('Failed to load training history', 'danger');
    }
}

function displayTrainingHistory(historyData) {
    const tableContainer = document.getElementById('training-history-table');
    
    const table = `
        <table class="table is-fullwidth is-striped">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Exercise</th>
                    <th>Body Part</th>
                    <th>Sets</th>
                    <th>Reps</th>
                    <th>Weight (kg)</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                ${historyData.records.map(record => `
                    <tr>
                        <td>${new Date(record.training_date).toLocaleDateString()}</td>
                        <td>${record.exercise_name}</td>
                        <td>${record.body_part}</td>
                        <td>${record.sets}</td>
                        <td>${record.reps}</td>
                        <td>${record.weight || '-'}</td>
                        <td>${record.notes || '-'}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    tableContainer.innerHTML = table;
    updatePagination(historyData.current_page, historyData.total_pages);
}

// Favorites Functions
async function toggleFavorite(exerciseName, bodyPart) {
    try {
        const response = await axios.post('/toggle_favorite', {
            exercise_name: exerciseName,
            body_part: bodyPart
        });
        showNotification(response.data.message, 'success');
        if (document.getElementById('favorites-content').style.display !== 'none') {
            loadFavorites();
        }
    } catch (error) {
        showNotification('Failed to update favorites', 'danger');
    }
}

async function loadFavorites() {
    try {
        const response = await axios.get('/get_favorites');
        displayFavorites(response.data);
    } catch (error) {
        showNotification('Failed to load favorites', 'danger');
    }
}

function displayFavorites(favorites) {
    const container = document.getElementById('favorites-list');
    container.innerHTML = favorites.map(favorite => `
        <div class="column is-one-third">
            <div class="favorite-card">
                <h3 class="title is-4">${favorite.exercise_name}</h3>
                <p class="subtitle is-6">${favorite.body_part}</p>
                <button class="button is-danger is-small" 
                        onclick="toggleFavorite('${favorite.exercise_name}', '${favorite.body_part}')">
                    Remove from Favorites
                </button>
            </div>
        </div>
    `).join('');
}

// UI Helper Functions
function showNotification(message, type = 'info', customClass = '') {
    const notification = document.createElement('div');
    notification.className = `notification is-${type} ${customClass}`;
    notification.innerHTML = `
        <button class="delete"></button>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    // Add event listener for the delete button
    notification.querySelector('.delete').addEventListener('click', () => {
        notification.remove();
    });

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function initializeTabNavigation() {
    const tabs = document.querySelectorAll('.tabs li');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const contentId = tab.getAttribute('data-content');
            switchTab(contentId);
        });
    });
}

function switchTab(contentId) {
    // Update tab active states
    document.querySelectorAll('.tabs li').forEach(tab => {
        tab.classList.remove('is-active');
    });
    document.querySelector(`[data-content="${contentId}"]`).classList.add('is-active');

    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
    });
    document.getElementById(`${contentId}-content`).style.display = 'block';

    // Load content if needed
    if (contentId === 'training-history') {
        loadTrainingHistory();
    } else if (contentId === 'favorites') {
        loadFavorites();
    }
}

function initializeModalHandlers() {
    // Close modal when background or delete button is clicked
    document.querySelectorAll('.modal-background, .modal .delete, .modal .cancel').forEach(element => {
        element.addEventListener('click', () => {
            document.querySelectorAll('.modal').forEach(modal => {
                modal.classList.remove('is-active');
            });
        });
    });
}

function showAuthModal() {
    document.getElementById('auth-modal').classList.add('is-active');
}

function closeAuthModal() {
    document.getElementById('auth-modal').classList.remove('is-active');
}

function switchAuthTab(tab) {
    document.querySelectorAll('.auth-form').forEach(form => {
        form.style.display = 'none';
    });
    document.getElementById(`${tab}-form`).style.display = 'block';

    document.querySelectorAll('.tabs li').forEach(li => {
        li.classList.remove('is-active');
    });
    document.querySelector(`[data-tab="${tab}"]`).parentElement.classList.add('is-active');
}

// Event Listeners
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
        const focused = document.activeElement;
        if (focused.classList.contains('option')) {
            focused.click();
        }
    }
});

// Initialize history filter
document.getElementById('history-filter')?.addEventListener('change', () => {
    loadTrainingHistory(1);
});
