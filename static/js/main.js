// CropSenseAI - Main JavaScript Functions

// Global state
let currentCropData = [];
let selectedDistrict = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    loadCropsList();
    loadLocationsList();
    setupEventListeners();
    console.log('✅ CropSenseAI initialized');
}

// Load crops from API
async function loadCropsList() {
    try {
        const response = await fetch('/api/crops');
        const data = await response.json();
        
        const selects = document.querySelectorAll('select[id*="Crop"]');
        selects.forEach(select => {
            data.crops.forEach(crop => {
                const option = document.createElement('option');
                option.value = crop;
                option.textContent = capitalizeFirst(crop);
                select.appendChild(option);
            });
        });
    } catch (error) {
        console.error('Error loading crops:', error);
    }
}

// Load locations from API
async function loadLocationsList() {
    try {
        const response = await fetch('/api/locations');
        const locations = await response.json();
        
        // Store for autocomplete
        window.locationData = locations;
        console.log('Loaded locations for', Object.keys(locations).length, 'states');
    } catch (error) {
        console.error('Error loading locations:', error);
    }
}

// Setup all event listeners
function setupEventListeners() {
    // File upload preview
    const fileInput = document.getElementById('fileUpload');
    if (fileInput) {
        fileInput.addEventListener('change', handleFilePreview);
    }

    // Form submissions
    setupFormSubmit('diseaseForm', '/disease-diagnosis', displayDiseaseResult);
    setupFormSubmit('yieldForm', '/yield-prediction', displayYieldResult, true);
    setupFormSubmit('recommendationForm', '/crop-recommendation', displayRecommendationResult, true);
    setupFormSubmit('farmForm', '/farm-report', displayFarmReport, true);
}

// Handle file preview
function handleFilePreview(event) {
    const file = event.target.files[0];
    if (file) {
        // Check file size
        if (file.size > 4 * 1024 * 1024) {
            alert('File size exceeds 4MB limit');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('previewImg');
            const previewContainer = document.getElementById('imagePreview');
            
            preview.src = e.target.result;
            previewContainer.classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
}

// Generic form submit handler
function setupFormSubmit(formId, endpoint, resultHandler, isJSON = false) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        showLoading(formId);

        try {
            let response;
            
            if (isJSON) {
                const formData = getFormDataAsJSON(formId);
                response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
            } else {
                const formData = new FormData(this);
                response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });
            }

            const result = await response.json();
            
            if (response.ok) {
                resultHandler(result);
            } else {
                showError(result.error || 'An error occurred');
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        } finally {
            hideLoading(formId);
        }
    });
}

// Get form data as JSON object
function getFormDataAsJSON(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input, select, textarea');
    const data = {};

    inputs.forEach(input => {
        if (input.id) {
            const key = input.id.replace(formId.replace('Form', ''), '').toLowerCase();
            data[key] = input.value;
        }
    });

    return data;
}

// Display disease diagnosis result
function displayDiseaseResult(result) {
    const resultDiv = document.getElementById('diseaseResult');
    
    resultDiv.innerHTML = `
        <div class="result-card bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-xl p-6 shadow-lg">
            <div class="flex items-center gap-3 mb-4">
                <span class="text-4xl">🔬</span>
                <h3 class="text-2xl font-bold text-green-800">Analysis Complete</h3>
            </div>
            
            <div class="grid md:grid-cols-2 gap-4">
                <div>
                    <p class="mb-2"><strong>🦠 Disease Detected:</strong></p>
                    <p class="text-xl font-semibold text-red-600">${result.disease}</p>
                    
                    <p class="mt-4 mb-2"><strong>📊 Confidence Level:</strong></p>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${result.confidence * 100}%"></div>
                    </div>
                    <p class="text-sm mt-1">${(result.confidence * 100).toFixed(1)}%</p>
                    
                    <p class="mt-4 mb-2"><strong>💚 Eco-Friendly Remedy:</strong></p>
                    <p class="text-gray-700 bg-white p-3 rounded-lg">${result.remedy}</p>
                </div>
                
                <div>
                    <p class="mb-2"><strong>📷 Analyzed Image:</strong></p>
                    <img src="${result.image_url}" class="rounded-lg shadow-md w-full" alt="Analyzed crop" />
                </div>
            </div>
        </div>
    `;
    
    resultDiv.classList.remove('hidden');
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display yield prediction result
function displayYieldResult(result) {
    const resultDiv = document.getElementById('yieldResult');
    
    const stressColor = result.rainfall_stress > 0.5 ? 'red' : result.rainfall_stress > 0.3 ? 'yellow' : 'green';
    
    resultDiv.innerHTML = `
        <div class="result-card bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 shadow-lg">
            <div class="flex items-center gap-3 mb-4">
                <span class="text-4xl">📈</span>
                <h3 class="text-2xl font-bold text-blue-800">Yield Prediction Results</h3>
            </div>
            
            <div class="bg-white rounded-lg p-6 mb-4 text-center">
                <p class="text-gray-600 mb-2">Predicted Yield</p>
                <p class="text-5xl font-bold text-blue-900">${result.predicted_yield_per_hectare}</p>
                <p class="text-xl text-gray-600">${result.unit} per hectare</p>
            </div>
            
            <div class="grid md:grid-cols-2 gap-4">
                <div class="bg-white rounded-lg p-4">
                    <p class="font-semibold mb-2">🌾 Crop Information</p>
                    <p><strong>Crop:</strong> ${capitalizeFirst(result.crop)}</p>
                    <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(0)}%</p>
                </div>
                
                <div class="bg-white rounded-lg p-4">
                    <p class="font-semibold mb-2">⚠️ Stress Analysis</p>
                    <p><strong>Stress Level:</strong> <span class="text-${stressColor}-600 font-bold">${(result.rainfall_stress * 100).toFixed(0)}%</span></p>
                    <div class="progress-bar mt-2">
                        <div class="progress-fill bg-${stressColor}-500" style="width: ${result.rainfall_stress * 100}%"></div>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-lg p-4 mt-4">
                <p class="font-semibold mb-3">💡 Recommendations:</p>
                <ul class="space-y-2">
                    ${result.recommendations.map(rec => `
                        <li class="flex items-start gap-2">
                            <span class="text-green-600 mt-1">✓</span>
                            <span>${rec}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        </div>
    `;
    
    resultDiv.classList.remove('hidden');
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display crop recommendations
function displayRecommendationResult(result) {
    const resultDiv = document.getElementById('recommendationResult');
    
    resultDiv.innerHTML = `
        <div class="result-card">
            <h3 class="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span>🌱</span> Top Recommended Crops
            </h3>
            
            <div class="space-y-3">
                ${result.map((item, idx) => `
                    <div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div class="flex items-center justify-between">
                            <div class="flex-1">
                                <h4 class="text-lg font-bold text-green-800 flex items-center gap-2">
                                    <span class="bg-green-600 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm">${idx + 1}</span>
                                    ${item.crop.toUpperCase()}
                                </h4>
                                
                                <div class="mt-2 grid grid-cols-2 gap-2 text-sm">
                                    <div>
                                        <p class="text-gray-600">Suitability Score</p>
                                        <p class="font-bold text-green-700">${(item.suitability_score * 100).toFixed(1)}%</p>
                                    </div>
                                    <div>
                                        <p class="text-gray-600">Avg Rainfall Needed</p>
                                        <p class="font-bold">${item.requirements.rainfall_avg.toFixed(0)}mm</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="text-right">
                                <div class="progress-bar w-24" style="transform: rotate(-90deg);">
                                    <div class="progress-fill" style="width: ${item.suitability_score * 100}%"></div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3 pt-3 border-t border-green-200">
                            <p class="text-xs text-gray-600">
                                <strong>Temp:</strong> ${item.requirements.temperature_avg.toFixed(1)}°C | 
                                <strong>pH:</strong> ${item.requirements.ph_avg.toFixed(1)} | 
                                <strong>N-P-K:</strong> ${item.requirements.N_avg.toFixed(0)}-${item.requirements.P_avg.toFixed(0)}-${item.requirements.K_avg.toFixed(0)}
                            </p>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    resultDiv.classList.remove('hidden');
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display farm report
function displayFarmReport(result) {
    const resultDiv = document.getElementById('farmResult');
    
    const crops = result.recommended_crops.map(c => capitalizeFirst(c.crop)).join(', ');
    
    resultDiv.innerHTML = `
        <div class="result-card bg-gradient-to-br from-yellow-50 to-green-50 border border-yellow-300 rounded-xl p-6 shadow-lg">
            <div class="flex items-center gap-3 mb-6">
                <span class="text-4xl">📊</span>
                <h3 class="text-3xl font-bold text-green-800">Comprehensive Farm Report</h3>
            </div>
            
            <!-- Location Analysis -->
            <div class="bg-white rounded-lg p-5 mb-4 shadow-sm">
                <h4 class="font-bold text-lg mb-3 flex items-center gap-2">
                    <span>📍</span> Location Analysis
                </h4>
                <div class="grid md:grid-cols-3 gap-4">
                    <div>
                        <p class="text-gray-600 text-sm">District</p>
                        <p class="font-bold text-lg">${result.location_analysis.district}</p>
                    </div>
                    <div>
                        <p class="text-gray-600 text-sm">State</p>
                        <p class="font-bold text-lg">${result.location_analysis.state}</p>
                    </div>
                    <div>
                        <p class="text-gray-600 text-sm">Annual Rainfall</p>
                        <p class="font-bold text-lg text-blue-600">${result.location_analysis.annual_rainfall}mm</p>
                    </div>
                </div>
            </div>
            
            <!-- Recommended Crops -->
            <div class="bg-white rounded-lg p-5 mb-4 shadow-sm">
                <h4 class="font-bold text-lg mb-3 flex items-center gap-2">
                    <span>🌾</span> Recommended Crops
                </h4>
                <div class="flex flex-wrap gap-2">
                    ${result.recommended_crops.map(c => `
                        <span class="crop-badge">${capitalizeFirst(c.crop)}</span>
                    `).join('')}
                </div>
            </div>
            
            <!-- Seasonal Planning -->
            <div class="bg-white rounded-lg p-5 mb-4 shadow-sm">
                <h4 class="font-bold text-lg mb-3 flex items-center gap-2">
                    <span>📅</span> Seasonal Planning
                </h4>
                <div class="grid md:grid-cols-3 gap-4">
                    ${Object.entries(result.seasonal_planning).map(([season, data]) => `
                        <div class="border border-green-200 rounded-lg p-3">
                            <p class="font-bold text-green-700 capitalize">${season} Season</p>
                            <p class="text-sm text-gray-600">${data.months}</p>
                            <p class="text-sm mt-2"><strong>Rainfall:</strong> ${data.rainfall.toFixed(0)}mm</p>
                            <p class="text-xs mt-1 text-gray-500">${data.suitable_crops.slice(0, 3).join(', ')}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <!-- Irrigation Advice -->
            <div class="bg-white rounded-lg p-5 mb-4 shadow-sm">
                <h4 class="font-bold text-lg mb-3 flex items-center gap-2">
                    <span>💧</span> Irrigation Recommendations
                </h4>
                <p class="mb-2"><strong>Category:</strong> <span class="text-blue-600">${result.irrigation_advice.category}</span></p>
                <p class="text-gray-700">${result.irrigation_advice.advice}</p>
                <p class="mt-2 text-sm"><strong>Water Conservation:</strong> ${result.irrigation_advice.water_conservation} Priority</p>
            </div>
            
            <!-- Soil Management -->
            <div class="bg-white rounded-lg p-5 shadow-sm">
                <h4 class="font-bold text-lg mb-3 flex items-center gap-2">
                    <span>🌱</span> Soil Management
                </h4>
                <div class="space-y-2">
                    <p><strong>NPK Recommendation:</strong></p>
                    <ul class="list-disc list-inside text-sm text-gray-700 ml-4">
                        <li>${result.soil_management.npk_recommendation.N}</li>
                        <li>${result.soil_management.npk_recommendation.P}</li>
                        <li>${result.soil_management.npk_recommendation.K}</li>
                    </ul>
                    <p class="mt-3"><strong>Organic Matter:</strong> ${result.soil_management.organic_matter}</p>
                    <p><strong>pH Management:</strong> ${result.soil_management.ph_management}</p>
                </div>
            </div>
            
            <div class="mt-6 text-center">
                <button onclick="window.print()" class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors">
                    🖨️ Print Report
                </button>
            </div>
        </div>
    `;
    
    resultDiv.classList.remove('hidden');
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Utility functions
function showLoading(formId) {
    const form = document.getElementById(formId);
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    button.innerHTML = '<div class="spinner"></div> Processing...';
}

function hideLoading(formId) {
    const form = document.getElementById(formId);
    const button = form.querySelector('button[type="submit"]');
    button.disabled = false;
    
    // Reset button text based on form
    const buttonTexts = {
        'diseaseForm': '🔍 Get Diagnosis',
        'yieldForm': '📊 Predict Yield',
        'recommendationForm': '🌱 Get Recommendations',
        'farmForm': '📄 Generate Report'
    };
    
    button.innerHTML = buttonTexts[formId] || 'Submit';
}

function showError(message) {
    alert('❌ Error: ' + message);
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Export for use in HTML
window.CropSenseAI = {
    showLoading,
    hideLoading,
    showError,
    capitalizeFirst
};
