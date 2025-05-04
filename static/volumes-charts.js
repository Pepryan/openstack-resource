/**
 * Volumes Charts JavaScript
 * Handles interactive chart visualizations for the volumes page
 * Optimized for performance with lazy loading and reduced animations
 */

// Chart objects
let statusChart = null;
let sizeDistributionChart = null;
let projectDistributionChart = null;
let chartsInitialized = false;
let projectDataCache = null;

// Chart colors
const chartColors = {
    blue: '#3b82f6',
    lightBlue: '#93c5fd',
    green: '#10b981',
    red: '#ef4444',
    yellow: '#f59e0b',
    purple: '#8b5cf6',
    orange: '#f97316',
    teal: '#14b8a6',
    indigo: '#6366f1',
    pink: '#ec4899',
    gray: '#6b7280',
    blueAlpha: 'rgba(59, 130, 246, 0.2)'
};

// Project color palette
const projectColors = [
    '#3b82f6', // Blue
    '#10b981', // Green
    '#f59e0b', // Yellow
    '#ef4444', // Red
    '#8b5cf6', // Purple
    '#ec4899', // Pink
    '#06b6d4', // Cyan
    '#f97316', // Orange
    '#14b8a6', // Teal
    '#a855f7', // Violet
    '#6366f1', // Indigo
    '#84cc16', // Lime
    '#0ea5e9', // Sky
    '#d946ef', // Fuchsia
    '#64748b', // Slate
    '#0891b2', // Cyan
];

/**
 * Initialize all volume charts with performance optimizations
 * Uses lazy loading to improve initial page load time
 */
function initVolumeCharts() {
    // Initialize calculator first as it doesn't require heavy rendering
    setupVolumeCalculator();

    // Use requestIdleCallback or setTimeout to defer chart creation
    // This allows the page to become interactive faster
    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => {
            lazyLoadCharts();
        }, { timeout: 1000 });
    } else {
        setTimeout(lazyLoadCharts, 100);
    }
}

/**
 * Hide chart loading indicator
 */
function hideChartLoadingIndicator(id) {
    const loadingIndicator = document.getElementById(id);
    if (loadingIndicator) {
        loadingIndicator.classList.add('hidden');
        // Remove from DOM after animation completes
        setTimeout(() => {
            if (loadingIndicator.parentNode) {
                loadingIndicator.parentNode.removeChild(loadingIndicator);
            }
        }, 300);
    }
}

/**
 * Lazy load charts to improve initial page load performance
 */
function lazyLoadCharts() {
    // Create charts in sequence with small delays to prevent UI blocking
    createStatusChart();

    setTimeout(() => {
        createSizeDistributionChart();

        setTimeout(() => {
            createProjectDistributionChart();
            chartsInitialized = true;
        }, 50);
    }, 50);
}

/**
 * Create status distribution chart with optimized performance
 */
function createStatusChart() {
    const chartElement = document.getElementById('status-chart');
    if (!chartElement || !chartElement.getContext) return;

    const ctx = chartElement.getContext('2d');
    if (!ctx) return;

    try {
        // Get data from the data attributes - use || 0 for safety
        const inUse = parseInt(chartElement.dataset.inUse) || 0;
        const available = parseInt(chartElement.dataset.available) || 0;
        const creating = parseInt(chartElement.dataset.creating) || 0;
        const error = parseInt(chartElement.dataset.error) || 0;
        const reserved = parseInt(chartElement.dataset.reserved) || 0;

        // Destroy existing chart if it exists
        if (statusChart) {
            statusChart.destroy();
        }

        // Hide loading indicator
        hideChartLoadingIndicator('status-chart-loading');

        // Create chart with optimized options
        statusChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['In Use', 'Available', 'Creating', 'Error', 'Reserved'],
                datasets: [{
                    data: [inUse, available, creating, error, reserved],
                    backgroundColor: [
                        chartColors.blue,
                        chartColors.green,
                        chartColors.yellow,
                        chartColors.red,
                        chartColors.purple
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutoutPercentage: 65, // For Chart.js 2.9.4
                animation: {
                    animateScale: false,  // Disable scale animation for better performance
                    animateRotate: true,
                    duration: 400         // Reduce animation duration
                },
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        fontSize: 12
                    }
                },
                tooltips: {
                    enabled: true,
                    callbacks: {
                        label: function(tooltipItem, data) {
                            const index = tooltipItem.index;
                            const label = data.labels[index] || '';
                            const value = data.datasets[0].data[index] || 0;
                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating status chart:', error);
    }
}

/**
 * Create size distribution chart with optimized performance
 */
function createSizeDistributionChart() {
    const chartElement = document.getElementById('size-distribution-chart');
    if (!chartElement || !chartElement.getContext) return;

    const ctx = chartElement.getContext('2d');
    if (!ctx) return;

    try {
        // Get data from the data attributes - use || 0 for safety
        const under100gb = parseInt(chartElement.dataset.under100gb) || 0;
        const from100gbTo500gb = parseInt(chartElement.dataset.from100gbTo500gb) || 0;
        const from500gbTo1tb = parseInt(chartElement.dataset.from500gbTo1tb) || 0;
        const over1tb = parseInt(chartElement.dataset.over1tb) || 0;

        // Destroy existing chart if it exists
        if (sizeDistributionChart) {
            sizeDistributionChart.destroy();
        }

        // Hide loading indicator
        hideChartLoadingIndicator('size-chart-loading');

        // Create chart with optimized options
        sizeDistributionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['≤ 100GB', '101-500GB', '501-1000GB (1TB)', '> 1000GB'],
                datasets: [{
                    data: [under100gb, from100gbTo500gb, from500gbTo1tb, over1tb],
                    backgroundColor: [
                        chartColors.blue,
                        chartColors.teal,
                        chartColors.indigo,
                        chartColors.purple
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutoutPercentage: 65, // For Chart.js 2.9.4
                animation: {
                    animateScale: false,  // Disable scale animation for better performance
                    animateRotate: true,
                    duration: 400         // Reduce animation duration
                },
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        fontSize: 12
                    }
                },
                tooltips: {
                    enabled: true,
                    callbacks: {
                        label: function(tooltipItem, data) {
                            const index = tooltipItem.index;
                            const label = data.labels[index] || '';
                            const value = data.datasets[0].data[index] || 0;
                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating size distribution chart:', error);
    }
}

/**
 * Create project distribution chart with optimized performance
 * Uses caching to avoid repeated DOM parsing
 */
function createProjectDistributionChart() {
    const chartElement = document.getElementById('project-distribution-chart');
    if (!chartElement || !chartElement.getContext) return;

    const ctx = chartElement.getContext('2d');
    if (!ctx) return;

    try {
        // Use cached project data if available to avoid expensive DOM operations
        let sortedProjects;

        if (!projectDataCache) {
            // Get projects data from the server-side rendered template
            const projectsList = document.getElementById('all-projects-list');
            if (!projectsList) {
                console.warn('Projects list element not found');
                hideChartLoadingIndicator('project-chart-loading');
                return;
            }

            // Extract project data from the DOM - this is an expensive operation
            // so we'll cache the results
            const projectItems = projectsList.querySelectorAll('.flex.justify-between');
            if (projectItems.length === 0) {
                console.warn('No project data found in the DOM');
                hideChartLoadingIndicator('project-chart-loading');
                return;
            }

            // Build data arrays more efficiently
            const projectData = [];

            // Use faster iteration method
            for (let i = 0; i < projectItems.length; i++) {
                const item = projectItems[i];
                const nameElement = item.querySelector('.project-name');
                const countElement = item.querySelector('.project-name + span');

                if (nameElement && countElement) {
                    const name = nameElement.textContent.trim();
                    const count = parseInt(countElement.textContent.trim(), 10);

                    if (name && !isNaN(count)) {
                        projectData.push({ name, count });
                    }
                }
            }

            // Sort by count (descending) and take top 10
            sortedProjects = projectData
                .sort((a, b) => b.count - a.count)
                .slice(0, 10);

            // Cache the processed data
            projectDataCache = sortedProjects;
        } else {
            // Use cached data
            sortedProjects = projectDataCache;
        }

        if (sortedProjects.length === 0) {
            console.warn('No valid project data to display');
            return;
        }

        const labels = sortedProjects.map(item => item.name);
        const data = sortedProjects.map(item => item.count);

        // Destroy existing chart if it exists
        if (projectDistributionChart) {
            projectDistributionChart.destroy();
        }

        // Hide loading indicator
        hideChartLoadingIndicator('project-chart-loading');

        // Create chart with optimized options
        projectDistributionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: labels.map((_, i) => projectColors[i % projectColors.length]),
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutoutPercentage: 65, // For Chart.js 2.9.4
                animation: {
                    animateScale: false,  // Disable scale animation for better performance
                    animateRotate: true,
                    duration: 400         // Reduce animation duration
                },
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        fontSize: 11
                    }
                },
                tooltips: {
                    enabled: true,
                    callbacks: {
                        label: function(tooltipItem, data) {
                            const index = tooltipItem.index;
                            const label = data.labels[index] || '';
                            const value = data.datasets[0].data[index] || 0;
                            const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating project distribution chart:', error);
    }
}



/**
 * Setup volume calculator with visual feedback
 */
function setupVolumeCalculator() {
    const calculatorElement = document.querySelector('.volume-calculator');
    if (!calculatorElement) return;

    try {
        const volumeCalc = {
            currentVolume: parseFloat(calculatorElement.dataset.currentVolume) || 0,
            erasureCode: parseFloat(calculatorElement.dataset.erasureCode) || 1.5,
            totalSize: parseFloat(calculatorElement.dataset.totalSize) || 5700,

            calculate: function(newVolume) {
                const total = this.currentVolume + (newVolume || 0);
                return ((total * this.erasureCode) / this.totalSize) * 100;
            },

            // Calculate maximum allowed new volume size to stay at or below 100% usage
            getMaxAllowedVolume: function() {
                // Formula: (totalSize / erasureCode) - currentVolume
                return (this.totalSize / this.erasureCode) - this.currentVolume;
            },

            updateDisplay: function(value) {
                const usageElement = document.getElementById('predictedUsage');
                if (!usageElement) return;

                // Get the maximum allowed volume size
                const maxAllowedVolume = this.getMaxAllowedVolume();

                // Limit input value to prevent exceeding 100% usage
                let newVolume = parseFloat(value) || 0;
                if (newVolume > maxAllowedVolume) {
                    newVolume = maxAllowedVolume;

                    // Update input field with the limited value
                    const newVolumeInput = document.getElementById('newVolume');
                    if (newVolumeInput && newVolumeInput.value !== newVolume.toFixed(1)) {
                        newVolumeInput.value = newVolume.toFixed(1);
                    }
                }

                const usage = this.calculate(newVolume);

                // Ensure usage doesn't exceed 100%
                const displayUsage = Math.min(usage, 100);

                // Update text display
                usageElement.textContent = displayUsage.toFixed(2) + '%';
                usageElement.className = `font-bold ${getUsageTextColorClass(displayUsage)}`;

                // Update calculator progress bar
                const progressBar = document.getElementById('calculator-progress-bar');
                const percentageText = document.getElementById('calculator-percentage');

                if (progressBar) {
                    progressBar.style.width = displayUsage.toFixed(2) + '%';
                    progressBar.dataset.usage = displayUsage.toFixed(2);

                    // Update color based on usage
                    if (displayUsage > 90) {
                        progressBar.style.backgroundColor = '#ef4444'; // Red
                    } else if (displayUsage > 75) {
                        progressBar.style.backgroundColor = '#f59e0b'; // Yellow
                    } else {
                        progressBar.style.backgroundColor = '#3b82f6'; // Blue
                    }
                }

                if (percentageText) {
                    percentageText.textContent = displayUsage.toFixed(2) + '%';
                }
            }
        };

        // Add event listener to input
        const newVolumeInput = document.getElementById('newVolume');
        if (newVolumeInput) {
            // Set the max attribute to prevent exceeding 100% usage
            const maxAllowedVolume = volumeCalc.getMaxAllowedVolume();
            newVolumeInput.setAttribute('max', maxAllowedVolume.toFixed(1));

            // Add a title attribute to show the max value on hover
            newVolumeInput.setAttribute('title', `Maximum allowed value: ${maxAllowedVolume.toFixed(1)} TB (to stay at or below 100% usage)`);

            // Set max attribute only

            newVolumeInput.addEventListener('input', function() {
                const value = parseFloat(this.value) || 0;
                const maxAllowed = volumeCalc.getMaxAllowedVolume();

                // Provide visual feedback if value exceeds maximum
                if (value > maxAllowed) {
                    // Add a warning class to the input
                    this.classList.add('border-red-500');
                } else {
                    // Remove warning class if value is valid
                    this.classList.remove('border-red-500');
                }

                volumeCalc.updateDisplay(value);
            });

            // Add validation on blur to ensure the value doesn't exceed max
            newVolumeInput.addEventListener('blur', function() {
                const value = parseFloat(this.value) || 0;
                const maxAllowed = volumeCalc.getMaxAllowedVolume();

                if (value > maxAllowed) {
                    this.value = maxAllowed.toFixed(1);
                    volumeCalc.updateDisplay(maxAllowed);

                    // Remove warning class since we've corrected the value
                    this.classList.remove('border-red-500');
                }
            });

            // Initialize with current value
            volumeCalc.updateDisplay(parseFloat(newVolumeInput.value) || 0);
        }

        // Initialize progress bars with correct colors
        const usageProgressBars = document.querySelectorAll('.usage-progress-bar');
        usageProgressBars.forEach(bar => {
            const usage = parseFloat(bar.dataset.usage) || 0;
            if (usage > 90) {
                bar.style.backgroundColor = '#ef4444'; // Red
            } else if (usage > 75) {
                bar.style.backgroundColor = '#f59e0b'; // Yellow
            } else {
                bar.style.backgroundColor = '#3b82f6'; // Blue
            }
        });

    } catch (error) {
        console.error('Error setting up volume calculator:', error);
    }
}

/**
 * Get color based on usage percentage
 */
function getUsageColor(usage) {
    if (usage > 90) {
        return chartColors.red;
    } else if (usage > 75) {
        return chartColors.yellow;
    } else {
        return chartColors.blue;
    }
}

/**
 * Get text color class based on usage percentage
 */
function getUsageTextColorClass(usage) {
    if (usage > 90) {
        return 'text-red-600';
    } else if (usage > 75) {
        return 'text-yellow-600';
    } else {
        return 'text-blue-600';
    }
}

/**
 * Update progress bar colors based on usage
 * Extracted to a separate function to avoid code duplication
 */
function updateProgressBarColors() {
    // Update main usage progress bars
    const usageProgressBars = document.querySelectorAll('.usage-progress-bar');
    usageProgressBars.forEach(bar => {
        const usage = parseFloat(bar.dataset.usage) || 0;
        if (usage > 90) {
            bar.style.backgroundColor = '#ef4444'; // Red
        } else if (usage > 75) {
            bar.style.backgroundColor = '#f59e0b'; // Yellow
        } else {
            bar.style.backgroundColor = '#3b82f6'; // Blue
        }
    });

    // Update calculator progress bar
    const calculatorProgressBar = document.getElementById('calculator-progress-bar');
    if (calculatorProgressBar) {
        const usage = parseFloat(calculatorProgressBar.dataset.usage) || 0;
        if (usage > 90) {
            calculatorProgressBar.style.backgroundColor = '#ef4444'; // Red
        } else if (usage > 75) {
            calculatorProgressBar.style.backgroundColor = '#f59e0b'; // Yellow
        } else {
            calculatorProgressBar.style.backgroundColor = '#3b82f6'; // Blue
        }
    }
}

// Initialize page when DOM is loaded with performance optimizations
document.addEventListener('DOMContentLoaded', function() {
    // Initialize calculator first (lightweight)
    setupVolumeCalculator();

    // Setup toggle for all projects (lightweight)
    const toggleButton = document.getElementById('toggle-all-projects');
    const allProjectsList = document.getElementById('all-projects-list');

    if (toggleButton && allProjectsList) {
        toggleButton.addEventListener('click', function() {
            const isHidden = allProjectsList.style.display === 'none';

            if (isHidden) {
                allProjectsList.style.display = 'block';
                toggleButton.textContent = 'Hide All Projects';
            } else {
                allProjectsList.style.display = 'none';
                toggleButton.textContent = 'View All Projects';
            }
        });
    }

    // Defer chart initialization to improve initial page load
    // This allows the page to become interactive faster
    if ('requestIdleCallback' in window) {
        requestIdleCallback(() => {
            lazyLoadCharts();
        }, { timeout: 1000 });
    } else {
        setTimeout(lazyLoadCharts, 100);
    }
});

// Handle theme changes with optimized performance
document.addEventListener('themeChanged', function() {
    // Add no-transition class to prevent animation during theme change
    document.documentElement.classList.add('no-transition');

    // Only redraw charts if they've been initialized
    if (chartsInitialized) {
        // Use requestAnimationFrame for smoother rendering
        requestAnimationFrame(() => {
            // Redraw charts on theme change
            createStatusChart();
            createSizeDistributionChart();
            createProjectDistributionChart();

            // Update progress bar colors
            updateProgressBarColors();

            // Remove no-transition class after a short delay
            setTimeout(() => {
                document.documentElement.classList.remove('no-transition');
            }, 50);
        });
    } else {
        // Just update progress bars if charts aren't initialized yet
        updateProgressBarColors();

        // Remove no-transition class
        setTimeout(() => {
            document.documentElement.classList.remove('no-transition');
        }, 50);
    }
});

// End of volumes-charts.js
