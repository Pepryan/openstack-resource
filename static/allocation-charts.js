/**
 * Allocation Charts JavaScript
 * Handles interactive allocation visualizations using Chart.js
 */

// Chart objects
let allocationTreemap = null;
let allocationSunburst = null;
let allocationBarChart = null;

// Current selected host
let selectedHost = '';

// Color palette for projects
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

// Status colors
const statusColors = {
    'ACTIVE': 'rgba(16, 185, 129, 0.8)', // Green
    'SHUTOFF': 'rgba(239, 68, 68, 0.8)', // Red
    'PAUSED': 'rgba(245, 158, 11, 0.8)', // Yellow
    'SUSPENDED': 'rgba(139, 92, 246, 0.8)', // Purple
    'ERROR': 'rgba(239, 68, 68, 0.8)', // Red
    'OTHER': 'rgba(107, 114, 128, 0.8)', // Gray
};

/**
 * Initialize allocation charts
 */
async function initAllocationCharts() {
    try {
        // Show loading state
        const loadingElement = document.getElementById('allocation-charts-loading');
        if (loadingElement) {
            loadingElement.classList.remove('hidden');
        }

        // Fetch allocation data
        const response = await fetch('/get_allocation_data');
        let data;
        try {
            const text = await response.text();
            data = JSON.parse(text);
        } catch (parseError) {
            console.error('Error parsing JSON response:', parseError);
            console.log('Raw response text:', text);
            throw new Error('Failed to parse server response');
        }

        // Hide loading state
        if (loadingElement) {
            loadingElement.classList.add('hidden');
        }

        // Show charts container
        const chartsContainer = document.getElementById('allocation-charts-container');
        if (chartsContainer) {
            chartsContainer.classList.remove('hidden');
        }

        // Update last updated timestamp
        const lastUpdatedElement = document.getElementById('allocation-last-updated');
        if (lastUpdatedElement) {
            lastUpdatedElement.textContent = data.last_updated;
        }

        // Update summary statistics
        updateAllocationSummary(data.totals);

        // Initialize charts
        createProjectsBarChart(data.projects);
        createHostsBarChart(data.hosts);

        // Populate host dropdown
        populateHostDropdown(data.hosts);

        // Add event listener for host selection
        const hostSelect = document.getElementById('allocation-host-select');
        if (hostSelect) {
            hostSelect.addEventListener('change', function() {
                selectedHost = this.value;
                if (selectedHost) {
                    generateImprovedVcpuPlot(selectedHost);

                    // Find the selected host data
                    const hostData = data.hosts.find(host => host.name === selectedHost);
                    if (hostData) {
                        createInstancesChart(hostData.instances);
                    }
                }
            });
        }

    } catch (error) {
        console.error('Error initializing allocation charts:', error);
        const loadingElement = document.getElementById('allocation-charts-loading');
        if (loadingElement) {
            loadingElement.classList.add('hidden');
        }

        const errorElement = document.getElementById('allocation-charts-error');
        if (errorElement) {
            errorElement.classList.remove('hidden');
            errorElement.textContent = 'Error loading allocation data. Please try again.';
        }
    }
}

/**
 * Update allocation summary statistics
 */
function updateAllocationSummary(totals) {
    if (!totals) {
        console.error('No totals data provided to updateAllocationSummary');
        return;
    }

    // Update vCPU usage values with null checks
    const totalVcpusUsed = document.getElementById('total-vcpus-used');
    if (totalVcpusUsed) {
        totalVcpusUsed.textContent = totals.vcpus_used || 0;
    }

    const totalVcpusCapacity = document.getElementById('total-vcpus-capacity');
    if (totalVcpusCapacity) {
        totalVcpusCapacity.textContent = totals.vcpus_capacity || 0;
    }

    const totalVcpusFree = document.getElementById('total-vcpus-free');
    if (totalVcpusFree) {
        totalVcpusFree.textContent = totals.vcpus_free || 0;
    }

    // Calculate usage percentage
    const vcpusUsed = totals.vcpus_used || 0;
    const vcpusCapacity = totals.vcpus_capacity || 1; // Avoid division by zero
    const usagePercent = ((vcpusUsed / vcpusCapacity) * 100).toFixed(1);

    const totalVcpusPercent = document.getElementById('total-vcpus-percent');
    if (totalVcpusPercent) {
        totalVcpusPercent.textContent = `${usagePercent}%`;
    }

    // Update counts
    const totalProjects = document.getElementById('total-projects');
    if (totalProjects) {
        totalProjects.textContent = totals.projects_count || 0;
    }

    const totalHosts = document.getElementById('total-hosts');
    if (totalHosts) {
        totalHosts.textContent = totals.hosts_count || 0;
    }

    const totalInstances = document.getElementById('total-instances');
    if (totalInstances) {
        totalInstances.textContent = totals.instances_count || 0;
    }

    // Update progress bar
    const progressBar = document.getElementById('vcpu-usage-progress');
    if (progressBar) {
        progressBar.style.width = `${usagePercent}%`;

        // Remove existing color classes
        progressBar.classList.remove('bg-green-500', 'bg-yellow-500', 'bg-red-500');

        // Set progress bar color based on usage
        if (usagePercent < 60) {
            progressBar.classList.add('bg-green-500');
        } else if (usagePercent < 80) {
            progressBar.classList.add('bg-yellow-500');
        } else {
            progressBar.classList.add('bg-red-500');
        }
    }
}

/**
 * Populate host dropdown
 */
function populateHostDropdown(hosts) {
    if (!hosts || !Array.isArray(hosts)) {
        console.error('Invalid hosts data provided to populateHostDropdown');
        return;
    }

    const dropdown = document.getElementById('allocation-host-select');
    if (!dropdown) {
        console.error('Host dropdown element not found');
        return;
    }

    // Clear existing options
    dropdown.innerHTML = '<option value="">Select a host</option>';

    // Add hosts to dropdown
    hosts.forEach(host => {
        if (host && host.name) {
            const option = document.createElement('option');
            option.value = host.name;
            option.textContent = `${host.name} (${host.tier || 'Unknown'}, ${host.vcpus_used || 0}/${host.vcpus_total || 0} vCPUs)`;
            dropdown.appendChild(option);
        }
    });
}

/**
 * Create projects bar chart
 */
function createProjectsBarChart(projects) {
    if (!projects || !Array.isArray(projects) || projects.length === 0) {
        console.error('Invalid projects data provided to createProjectsBarChart');
        return;
    }

    const chartElement = document.getElementById('projects-chart');
    if (!chartElement) {
        console.error('Projects chart element not found');
        return;
    }

    const ctx = chartElement.getContext('2d');
    if (!ctx) {
        console.error('Could not get 2D context for projects chart');
        return;
    }

    try {
        // Sort projects by vCPU usage (descending)
        projects.sort((a, b) => (b.vcpus_total || 0) - (a.vcpus_total || 0));

        // Prepare data
        const labels = projects.map(project => project.name || 'Unknown');
        const vcpuData = projects.map(project => project.vcpus_total || 0);
        const instanceCounts = projects.map(project => (project.instances && Array.isArray(project.instances)) ? project.instances.length : 0);

        // Destroy existing chart if it exists
        if (allocationBarChart) {
            allocationBarChart.destroy();
        }

        // Create chart
        allocationBarChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'vCPUs',
                        data: vcpuData,
                        backgroundColor: labels.map((_, i) => projectColors[i % projectColors.length]),
                        borderWidth: 0,
                        borderRadius: 4,
                        order: 1
                    },
                    {
                        label: 'Instances',
                        data: instanceCounts,
                        type: 'line',
                        borderColor: '#6b7280',
                        borderWidth: 2,
                        pointBackgroundColor: '#6b7280',
                        pointRadius: 4,
                        fill: false,
                        tension: 0.1,
                        order: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            afterTitle: function(context) {
                                if (!context || !context[0]) return '';
                                const projectIndex = context[0].dataIndex;
                                if (projectIndex < 0 || projectIndex >= projects.length) return '';

                                const project = projects[projectIndex];
                                const instanceCount = (project.instances && Array.isArray(project.instances)) ? project.instances.length : 0;
                                return `${instanceCount} instances`;
                            },
                            afterBody: function(context) {
                                if (!context || !context[0]) return [];
                                const projectIndex = context[0].dataIndex;
                                if (projectIndex < 0 || projectIndex >= projects.length) return [];

                                const project = projects[projectIndex];
                                const ramTotal = project.ram_total || 0;
                                const diskTotal = project.disk_total || 0;

                                return [
                                    `RAM: ${(ramTotal / 1024).toFixed(2)} GB`,
                                    `Disk: ${diskTotal.toFixed(2)} GB`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'vCPUs'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating projects bar chart:', error);
    }
}

/**
 * Create hosts bar chart
 */
function createHostsBarChart(hosts) {
    if (!hosts || !Array.isArray(hosts) || hosts.length === 0) {
        console.error('Invalid hosts data provided to createHostsBarChart');
        return;
    }

    const chartElement = document.getElementById('hosts-chart');
    if (!chartElement) {
        console.error('Hosts chart element not found');
        return;
    }

    const ctx = chartElement.getContext('2d');
    if (!ctx) {
        console.error('Could not get 2D context for hosts chart');
        return;
    }

    try {
        // Sort hosts by vCPU usage (descending)
        hosts.sort((a, b) => (b.vcpus_used || 0) - (a.vcpus_used || 0));

        // Prepare data
        const labels = hosts.map(host => host.name || 'Unknown');
        const usedData = hosts.map(host => host.vcpus_used || 0);
        const freeData = hosts.map(host => {
            const total = host.vcpus_total || 0;
            const used = host.vcpus_used || 0;
            return Math.max(0, total - used);
        });

        // Create chart
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Used vCPUs',
                        data: usedData,
                        backgroundColor: '#3b82f6',
                        borderWidth: 0,
                        borderRadius: 4
                    },
                    {
                        label: 'Free vCPUs',
                        data: freeData,
                        backgroundColor: '#93c5fd',
                        borderWidth: 0,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            afterTitle: function(context) {
                                if (!context || !context[0]) return '';
                                const hostIndex = context[0].dataIndex;
                                if (hostIndex < 0 || hostIndex >= hosts.length) return '';

                                const host = hosts[hostIndex];
                                return `Tier: ${host.tier || 'Unknown'}`;
                            },
                            afterBody: function(context) {
                                if (!context || !context[0]) return [];
                                const hostIndex = context[0].dataIndex;
                                if (hostIndex < 0 || hostIndex >= hosts.length) return [];

                                const host = hosts[hostIndex];
                                const vcpusTotal = host.vcpus_total || 0;
                                const vcpusUsed = host.vcpus_used || 0;
                                const usagePercent = (vcpusTotal > 0) ? ((vcpusUsed / vcpusTotal) * 100).toFixed(1) : '0.0';
                                const instanceCount = (host.instances && Array.isArray(host.instances)) ? host.instances.length : 0;

                                return [
                                    `Total: ${vcpusTotal} vCPUs`,
                                    `Usage: ${usagePercent}%`,
                                    `Instances: ${instanceCount}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'vCPUs'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error creating hosts bar chart:', error);
    }
}

/**
 * Create instances chart for a specific host
 */
function createInstancesChart(instances) {
    if (!instances || !Array.isArray(instances) || instances.length === 0) {
        console.error('Invalid instances data provided to createInstancesChart');
        return;
    }

    const chartElement = document.getElementById('instances-chart');
    if (!chartElement) {
        console.error('Instances chart element not found');
        return;
    }

    const ctx = chartElement.getContext('2d');
    if (!ctx) {
        console.error('Could not get 2D context for instances chart');
        return;
    }

    try {
        // Sort instances by vCPU usage (descending)
        instances.sort((a, b) => (b.vcpus || 0) - (a.vcpus || 0));

        // Prepare data
        const labels = instances.map(instance => instance.name || 'Unknown');
        const vcpuData = instances.map(instance => instance.vcpus || 0);
        const backgroundColors = instances.map(instance => {
            const status = instance.status || 'OTHER';
            return statusColors[status] || statusColors.OTHER;
        });

        // Destroy existing chart if it exists
        if (window.instancesChart) {
            window.instancesChart.destroy();
        }

        // Create chart
        window.instancesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'vCPUs',
                        data: vcpuData,
                        backgroundColor: backgroundColors,
                        borderWidth: 0,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            afterTitle: function(context) {
                                if (!context || !context[0]) return '';
                                const instanceIndex = context[0].dataIndex;
                                if (instanceIndex < 0 || instanceIndex >= instances.length) return '';

                                const instance = instances[instanceIndex];
                                return `Status: ${instance.status || 'Unknown'}`;
                            },
                            afterBody: function(context) {
                                if (!context || !context[0]) return [];
                                const instanceIndex = context[0].dataIndex;
                                if (instanceIndex < 0 || instanceIndex >= instances.length) return [];

                                const instance = instances[instanceIndex];
                                return [
                                    `RAM: ${instance.ram_gb || 0} GB`,
                                    `Disk: ${instance.total_disk || 0} GB`,
                                    `Tier: ${instance.tier || 'Unknown'}`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'vCPUs'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });

        // Show instances chart container and hide the no instances message
        const containerElement = document.getElementById('instances-chart-container');
        if (containerElement) {
            containerElement.classList.remove('hidden');
        }

        const noInstancesMessage = document.getElementById('no-instances-message');
        if (noInstancesMessage) {
            noInstancesMessage.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error creating instances chart:', error);
    }
}

/**
 * Generate improved vCPU plot
 */
async function generateImprovedVcpuPlot(host) {
    if (!host) {
        console.error('No host provided to generateImprovedVcpuPlot');
        return;
    }

    const loadingElement = document.getElementById('improved-plot-loading');
    const containerElement = document.getElementById('improved-plot-container');
    const errorElement = document.getElementById('improved-plot-error');

    try {
        // Show loading state
        if (loadingElement) {
            loadingElement.classList.remove('hidden');
        }

        if (containerElement) {
            containerElement.classList.add('hidden');
        }

        if (errorElement) {
            errorElement.classList.add('hidden');
        }

        // Hide the "no host selected" message
        const noHostSelectedMessage = document.getElementById('no-host-selected-message');
        if (noHostSelectedMessage) {
            noHostSelectedMessage.classList.add('hidden');
        }

        // Fetch improved plot
        const response = await fetch(`/generate_improved_vcpu_plot?host=${encodeURIComponent(host)}`);
        const data = await response.json();

        // Hide loading state
        if (loadingElement) {
            loadingElement.classList.add('hidden');
        }

        // Show plot container
        if (containerElement) {
            containerElement.classList.remove('hidden');
        }

        // Update plot image
        const plotImage = document.getElementById('improved-plot-image');
        if (plotImage) {
            plotImage.src = data.image_path;
            plotImage.alt = `vCPU Allocation for ${host}`;
        }

        // Update plot info with null checks
        const hostElement = document.getElementById('improved-plot-host');
        if (hostElement) {
            hostElement.textContent = data.host || host;
        }

        const capacityElement = document.getElementById('improved-plot-capacity');
        if (capacityElement) {
            capacityElement.textContent = data.capacity || 0;
        }

        const usedElement = document.getElementById('improved-plot-used');
        if (usedElement) {
            usedElement.textContent = data.used || 0;
        }

        const availableElement = document.getElementById('improved-plot-available');
        if (availableElement) {
            availableElement.textContent = data.available || 0;
        }

        const percentElement = document.getElementById('improved-plot-percent');
        if (percentElement) {
            const percent = data.usage_percent || 0;
            percentElement.textContent = `${percent.toFixed(1)}%`;
        }

    } catch (error) {
        console.error('Error generating improved vCPU plot:', error);

        if (loadingElement) {
            loadingElement.classList.add('hidden');
        }

        if (errorElement) {
            errorElement.classList.remove('hidden');
            errorElement.textContent = 'Error generating plot. Please try again.';
        }
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the home page with allocation charts
    if (document.getElementById('allocation-charts-section')) {
        initAllocationCharts();
    }
});
