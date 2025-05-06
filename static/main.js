async function loadSourceHosts() {
    try {
        const response = await fetch('/get_source_hosts');
        const sourceHosts = await response.json();

        const sourceHostsDropdown = document.getElementById('sourceHostsDropdown');
        const destinationHostsDropdown = document.getElementById('destinationHostsDropdown');
        sourceHostsDropdown.innerHTML = '<option value="" disabled selected>Select a host</option>';
        destinationHostsDropdown.innerHTML = '<option value="" disabled selected>Select a host</option>';

        sourceHosts.forEach(host => {
            const option = new Option(host, host);
            sourceHostsDropdown.appendChild(option);
            destinationHostsDropdown.appendChild(option.cloneNode(true));
        });
    } catch (error) {
        console.error('Error loading source hosts:', error);
    }
}

// Chart objects to store references for updating
let sourceVcpuChart = null;
let sourceRamChart = null;
let destVcpuChart = null;
let destRamChart = null;
let vcpuComparisonChart = null;
let ramComparisonChart = null;

// Flag to track if instances have been selected for moving
let instancesSelected = false;

// Function to reset all selections and clear instances
function resetSelection() {
    // Reset dropdowns
    document.getElementById('sourceHostsDropdown').selectedIndex = 0;
    document.getElementById('destinationHostsDropdown').selectedIndex = 0;

    // Clear instances to move
    clearInstancesToMove();

    // Reset flag
    instancesSelected = false;

    // Hide info message
    document.getElementById('infoMessage').classList.add('hidden');

    // Clear tables
    document.getElementById('sourceHost').innerHTML = '<thead><tr><th>Name</th><th>vCPU</th><th>RAM (GB)</th><th>Actions</th></tr></thead><tbody></tbody>';
    document.getElementById('destinationHost').innerHTML = '<thead><tr><th>Name</th><th>vCPU</th><th>RAM (GB)</th></tr></thead><tbody></tbody>';

    // Reset host info
    document.getElementById('sourceHostInfo').textContent = 'Host Information';
    document.getElementById('destinationHostInfo').textContent = 'Host Information';
    document.getElementById('sourceHostTitle').textContent = 'Instances';
    document.getElementById('destinationHostTitle').textContent = 'Current Instances';

    // Reset all host info values to 0
    // Source host
    document.getElementById('vcpusUsedSourceHost').textContent = '0';
    document.getElementById('totalVCPUsSourceHost').textContent = '0';
    document.getElementById('freeVCPUsSourceHost').textContent = '0';
    document.getElementById('ramUsedSourceHost').textContent = '0';
    document.getElementById('ramUsedGbSourceHost').textContent = '0';
    document.getElementById('ramTotalSourceHost').textContent = '0';
    document.getElementById('ramTotalGbSourceHost').textContent = '0';
    document.getElementById('ramFreeSourceHost').textContent = '0';
    document.getElementById('ramFreeGbSourceHost').textContent = '0';

    // Destination host
    document.getElementById('vcpusUsedHost').textContent = '0';
    document.getElementById('totalVCPUsHost').textContent = '0';
    document.getElementById('freeVCPUsHost').textContent = '0';
    document.getElementById('freeVCPUsAfter').textContent = '0';
    document.getElementById('totalVCPUsToMove').textContent = '0';
    document.getElementById('ramUsedHost').textContent = '0';
    document.getElementById('ramUsedGbHost').textContent = '0';
    document.getElementById('ramTotalHost').textContent = '0';
    document.getElementById('ramTotalGbHost').textContent = '0';
    document.getElementById('ramFreeHost').textContent = '0';
    document.getElementById('ramFreeGbHost').textContent = '0';
    document.getElementById('ramFreeAfter').textContent = '0';
    document.getElementById('ramFreeGbAfter').textContent = '0';
    document.getElementById('totalRamToMove').textContent = '0';
    document.getElementById('totalRamToMoveGb').textContent = '0';

    // Reset charts
    if (sourceVcpuChart) sourceVcpuChart.destroy();
    if (sourceRamChart) sourceRamChart.destroy();
    if (destVcpuChart) destVcpuChart.destroy();
    if (destRamChart) destRamChart.destroy();
    if (vcpuComparisonChart) vcpuComparisonChart.destroy();
    if (ramComparisonChart) ramComparisonChart.destroy();

    sourceVcpuChart = null;
    sourceRamChart = null;
    destVcpuChart = null;
    destRamChart = null;
    vcpuComparisonChart = null;
    ramComparisonChart = null;
}

// Function to create or update a donut chart
function createOrUpdateDonutChart(chartId, usedValue, totalValue, label, chartRef) {
    const ctx = document.getElementById(chartId).getContext('2d');
    const freeValue = totalValue - usedValue;
    // Calculate percentage for display in tooltip

    // Destroy existing chart if it exists
    if (chartRef) {
        chartRef.destroy();
    }

    // Create chart configuration
    const config = {
        type: 'doughnut',
        data: {
            labels: ['Used', 'Free'],
            datasets: [{
                data: [usedValue, freeValue],
                backgroundColor: ['#3b82f6', '#93c5fd'],
                borderWidth: 0,
                borderRadius: 4,
                hoverOffset: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 800
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: label,
                    position: 'bottom',
                    padding: {
                        top: 10,
                        bottom: 5
                    },
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const percentage = Math.round((value / (usedValue + freeValue)) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    };

    // Create new chart
    return new Chart(ctx, config);
}

// Function to create or update comparison chart
function createOrUpdateComparisonChart(chartId, sourceData, destData, label, chartRef) {
    const ctx = document.getElementById(chartId).getContext('2d');
    const sourceHost = document.getElementById('sourceHostsDropdown').value;
    const destHost = document.getElementById('destinationHostsDropdown').value;

    // Destroy existing chart if it exists
    if (chartRef) {
        chartRef.destroy();
    }

    // Create chart configuration
    const config = {
        type: 'bar',
        data: {
            labels: ['Used', 'Free'],
            datasets: [
                {
                    label: sourceHost,
                    data: [sourceData.used, sourceData.free],
                    backgroundColor: '#3b82f6',
                    borderWidth: 0,
                    borderRadius: 4,
                    hoverBackgroundColor: '#2563eb'
                },
                {
                    label: destHost,
                    data: [destData.used, destData.free],
                    backgroundColor: '#93c5fd',
                    borderWidth: 0,
                    borderRadius: 4,
                    hoverBackgroundColor: '#60a5fa'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            },
            plugins: {
                title: {
                    display: true,
                    text: label,
                    position: 'top',
                    padding: {
                        top: 10,
                        bottom: 20
                    },
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const hostName = context.dataset.label || '';
                            const category = context.label || '';
                            const value = context.raw || 0;

                            // Calculate total based on dataset
                            let total;
                            if (hostName === sourceHost) {
                                total = sourceData.used + sourceData.free;
                            } else {
                                total = destData.used + destData.free;
                            }

                            const percentage = Math.round((value / total) * 100);
                            return `${hostName} ${category}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(200, 200, 200, 0.2)'
                    }
                }
            }
        }
    };

    // Create new chart
    return new Chart(ctx, config);
}

async function loadInstances() {
    const selectedHost = document.getElementById('sourceHostsDropdown').value;

    // Check if instances have been selected for moving
    if (instancesSelected) {
        // Show info message
        document.getElementById('infoMessage').classList.remove('hidden');
        return;
    }

    if (selectedHost) {
        try {
            const response = await fetch(`/get_instances?host=${encodeURIComponent(selectedHost)}`);
            const { instances } = await response.json();

            const sourceHostTable = document.getElementById('sourceHost');
            sourceHostTable.innerHTML = '<tr><th class="px-4 py-2 bg-blue-500 text-white">Name</th><th class="px-4 py-2 bg-blue-500 text-white">vCPU</th><th class="px-4 py-2 bg-blue-500 text-white">RAM (GB)</th><th class="px-4 py-2 bg-blue-500 text-white">Actions</th></tr>';

            instances.forEach(async (instance, index) => {
                const row = sourceHostTable.insertRow();
                row.className = 'hover:bg-blue-200';
                // Store instance ID as data attribute
                row.setAttribute('data-instance-id', instance.ID);

                const cell1 = row.insertCell(0);
                cell1.textContent = instance.Name;

                const cell2 = row.insertCell(1);
                cell2.textContent = instance.CPU;
                cell2.className = "text-center";

                const cell3 = row.insertCell(2);
                // Use actual RAM value from API instead of estimation
                const ramGB = instance.RAM_GB ? parseFloat(instance.RAM_GB).toFixed(1) : "0.0";
                cell3.textContent = ramGB;
                cell3.className = "text-center";

                const moveButtonCell = row.insertCell(3);
                moveButtonCell.style.textAlign = 'center';
                moveButtonCell.className = 'py-1';

                const moveButton = document.createElement('button');
                moveButton.textContent = 'Move';
                moveButton.className = 'bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded transition duration-300 ease-in-out';
                moveButton.onclick = () => moveInstanceToDestination('sourceHostMoveBtn' + index);
                moveButtonCell.appendChild(moveButton);
                moveButton.id = 'sourceHostMoveBtn' + index;
            });

            document.getElementById('sourceHostTitle').textContent = 'Instances on ' + selectedHost;
            document.getElementById('sourceHostInfo').textContent = 'Info ' + selectedHost;

            const hostAllocationResponse = await fetch(`/get_host_allocation?host=${encodeURIComponent(selectedHost)}`);
            const hostAllocation = await hostAllocationResponse.json();

            // Update vCPU information
            document.getElementById('vcpusUsedSourceHost').textContent = hostAllocation.vcpus_used;
            document.getElementById('totalVCPUsSourceHost').textContent = hostAllocation.vcpus_total;
            document.getElementById('freeVCPUsSourceHost').textContent = hostAllocation.vcpus_free;

            // Update RAM information
            document.getElementById('ramUsedSourceHost').textContent = hostAllocation.ram_used;
            document.getElementById('ramTotalSourceHost').textContent = hostAllocation.ram_total;
            document.getElementById('ramFreeSourceHost').textContent = hostAllocation.ram_free;
            document.getElementById('ramUsedGbSourceHost').textContent = hostAllocation.ram_used_gb;
            document.getElementById('ramTotalGbSourceHost').textContent = hostAllocation.ram_total_gb;
            document.getElementById('ramFreeGbSourceHost').textContent = hostAllocation.ram_free_gb;

            // Create or update charts
            sourceVcpuChart = createOrUpdateDonutChart(
                'sourceVcpuChart',
                hostAllocation.vcpus_used,
                hostAllocation.vcpus_total,
                'vCPU Usage',
                sourceVcpuChart
            );

            sourceRamChart = createOrUpdateDonutChart(
                'sourceRamChart',
                hostAllocation.ram_used,
                hostAllocation.ram_total,
                'RAM Usage (MB)',
                sourceRamChart
            );

            // Update comparison charts if both hosts are selected
            updateComparisonCharts();
        } catch (error) {
            console.error('Error loading instances:', error);
        }
    }
}

async function loadDestinationHostInstances() {
    const selectedHost = document.getElementById('destinationHostsDropdown').value;

    // Check if instances have been selected for moving
    if (instancesSelected) {
        // Show info message
        document.getElementById('infoMessage').classList.remove('hidden');
        return;
    }

    if (selectedHost) {
        try {
            const response = await fetch(`/get_destination_host_instances?host=${encodeURIComponent(selectedHost)}`);
            const data = await response.json();

            const destinationHostTable = document.getElementById('destinationHost');
            destinationHostTable.innerHTML = '<tr><th class="px-4 py-2 bg-blue-500 text-white">Name</th><th class="px-4 py-2 bg-blue-500 text-white">vCPU</th><th class="px-4 py-2 bg-blue-500 text-white">RAM (GB)</th></tr>';

            if (data.instances) {
                data.instances.forEach(instance => {
                    const row = destinationHostTable.insertRow();
                    row.className = 'hover:bg-blue-200';

                    const cell1 = row.insertCell(0);
                    cell1.textContent = instance.Name;

                    const cell2 = row.insertCell(1);
                    cell2.textContent = instance.CPU;
                    cell2.className = "text-center py-1";

                    const cell3 = row.insertCell(2);
                    // Use actual RAM value from API instead of estimation
                    const ramGB = instance.RAM_GB ? parseFloat(instance.RAM_GB).toFixed(1) : "0.0";
                    cell3.textContent = ramGB;
                    cell3.className = "text-center py-1";
                    });
            }

            document.getElementById('destinationHostTitle').textContent = 'Instances on ' + selectedHost;
            document.getElementById('destinationHostInfo').textContent = 'Info ' + selectedHost;

            const hostAllocationResponse = await fetch(`/get_host_allocation?host=${encodeURIComponent(selectedHost)}`);
            const hostAllocation = await hostAllocationResponse.json();

            // Update vCPU information
            document.getElementById('vcpusUsedHost').textContent = hostAllocation.vcpus_used;
            document.getElementById('totalVCPUsHost').textContent = hostAllocation.vcpus_total;
            document.getElementById('freeVCPUsHost').textContent = hostAllocation.vcpus_free;

            // Update RAM information
            document.getElementById('ramUsedHost').textContent = hostAllocation.ram_used;
            document.getElementById('ramTotalHost').textContent = hostAllocation.ram_total;
            document.getElementById('ramFreeHost').textContent = hostAllocation.ram_free;
            document.getElementById('ramUsedGbHost').textContent = hostAllocation.ram_used_gb;
            document.getElementById('ramTotalGbHost').textContent = hostAllocation.ram_total_gb;
            document.getElementById('ramFreeGbHost').textContent = hostAllocation.ram_free_gb;

            // Initialize RAM after values
            document.getElementById('ramFreeAfter').textContent = hostAllocation.ram_free;
            document.getElementById('ramFreeGbAfter').textContent = hostAllocation.ram_free_gb;
            document.getElementById('totalRamToMove').textContent = '0';
            document.getElementById('totalRamToMoveGb').textContent = '0';

            // Create or update charts
            destVcpuChart = createOrUpdateDonutChart(
                'destVcpuChart',
                hostAllocation.vcpus_used,
                hostAllocation.vcpus_total,
                'vCPU Usage',
                destVcpuChart
            );

            destRamChart = createOrUpdateDonutChart(
                'destRamChart',
                hostAllocation.ram_used,
                hostAllocation.ram_total,
                'RAM Usage (MB)',
                destRamChart
            );

            // Update comparison charts if both hosts are selected
            updateComparisonCharts();
        } catch (error) {
            console.error('Error loading destination host instances:', error);
        }
    }
}

// Function to update comparison charts
function updateComparisonCharts() {
    const sourceHost = document.getElementById('sourceHostsDropdown').value;
    const destHost = document.getElementById('destinationHostsDropdown').value;

    // Only update if both hosts are selected
    if (!sourceHost || !destHost) {
        return;
    }

    // Get vCPU data
    const sourceVcpusUsed = parseInt(document.getElementById('vcpusUsedSourceHost').textContent) || 0;
    const sourceVcpusFree = parseInt(document.getElementById('freeVCPUsSourceHost').textContent) || 0;

    const destVcpusUsed = parseInt(document.getElementById('vcpusUsedHost').textContent) || 0;
    const destVcpusFree = parseInt(document.getElementById('freeVCPUsHost').textContent) || 0;

    // RAM data in MB tidak digunakan untuk chart, langsung gunakan data GB

    // Get RAM data in GB for display
    const sourceRamUsedGB = parseFloat(document.getElementById('ramUsedGbSourceHost').textContent) || 0;
    const sourceRamFreeGB = parseFloat(document.getElementById('ramFreeGbSourceHost').textContent) || 0;

    const destRamUsedGB = parseFloat(document.getElementById('ramUsedGbHost').textContent) || 0;
    const destRamFreeGB = parseFloat(document.getElementById('ramFreeGbHost').textContent) || 0;

    // Create or update vCPU comparison chart
    vcpuComparisonChart = createOrUpdateComparisonChart(
        'vcpuComparisonChart',
        { used: sourceVcpusUsed, free: sourceVcpusFree },
        { used: destVcpusUsed, free: destVcpusFree },
        'vCPU Comparison',
        vcpuComparisonChart
    );

    // Create or update RAM comparison chart
    ramComparisonChart = createOrUpdateComparisonChart(
        'ramComparisonChart',
        { used: sourceRamUsedGB, free: sourceRamFreeGB },
        { used: destRamUsedGB, free: destRamFreeGB },
        'RAM Comparison (GB)',
        ramComparisonChart
    );
}

async function moveInstanceToDestination(btnId) {
    const sourceRow = document.getElementById(btnId).parentNode.parentNode;
    const name = sourceRow.cells[0].textContent;
    const instanceId = sourceRow.getAttribute('data-instance-id');
    const selectedHost = document.getElementById('destinationHostsDropdown').value;

    // Set flag that instances have been selected
    instancesSelected = true;

    if (!selectedHost) {
        alert('Please select a destination host first.');
        clearInstancesToMove();
        return;
    }

    const sourceHostsDropdown = document.getElementById('sourceHostsDropdown');
    const destinationHostsDropdown = document.getElementById('destinationHostsDropdown');

    sourceHostsDropdown.disabled = true;
    destinationHostsDropdown.disabled = true;

    try {
        // Get instance vCPU and RAM information directly from the row
        const vcpus_used_instance = parseFloat(sourceRow.cells[1].textContent);
        const ram_gb_instance = parseFloat(sourceRow.cells[2].textContent);
        const ram_used_instance = ram_gb_instance * 1024; // Convert GB to MB

        // Get destination host allocation information
        const hostAllocationResponse = await fetch(`/get_host_allocation?host=${encodeURIComponent(selectedHost)}`);
        const hostAllocation = await hostAllocationResponse.json();

        // vCPU information
        const vcpus_used_host = parseFloat(hostAllocation.vcpus_used);
        const vcpus_total_host = parseFloat(hostAllocation.vcpus_total);
        const vcpus_free_host = parseFloat(hostAllocation.vcpus_free);

        // RAM information
        const ram_used_host = parseFloat(hostAllocation.ram_used);
        const ram_total_host = parseFloat(hostAllocation.ram_total);
        const ram_free_host = parseFloat(hostAllocation.ram_free);

        // Calculate total vCPUs and RAM to move
        const instancesToMoveTable = document.getElementById('instancesToMove');
        const rows = instancesToMoveTable.getElementsByTagName('tr');
        let totalVCPUsToMove = vcpus_used_instance;
        let totalRAMToMove = ram_used_instance;

        for (let i = 1; i < rows.length; i++) {
            const cells = rows[i].getElementsByTagName('td');
            const vcpuInstance = parseFloat(cells[1].textContent);
            let ramGBInstance = parseFloat(cells[2].textContent);

            // Make sure RAM value is not 0
            if (ramGBInstance === 0 || isNaN(ramGBInstance)) {
                // If RAM value is invalid, display "Invalid"
                cells[2].textContent = "Invalid";
                // Use 0 for calculations
                ramGBInstance = 0;
            }

            totalVCPUsToMove += vcpuInstance;
            totalRAMToMove += ramGBInstance * 1024; // Convert GB to MB
        }

        // Check if there's enough vCPU and RAM capacity
        const hasEnoughVCPU = totalVCPUsToMove <= vcpus_free_host && (vcpus_used_host + totalVCPUsToMove) <= vcpus_total_host;
        const hasEnoughRAM = totalRAMToMove <= ram_free_host && (ram_used_host + totalRAMToMove) <= ram_total_host;

        if (hasEnoughVCPU && hasEnoughRAM) {
            // Update vCPU information
            document.getElementById('totalVCPUsToMove').textContent = totalVCPUsToMove;
            const freeVCPUsAfter = vcpus_free_host - totalVCPUsToMove;
            document.getElementById('freeVCPUsAfter').textContent = freeVCPUsAfter;

            // Update RAM information
            document.getElementById('totalRamToMove').textContent = totalRAMToMove;
            document.getElementById('totalRamToMoveGb').textContent = (totalRAMToMove / 1024).toFixed(2);
            const freeRAMAfter = ram_free_host - totalRAMToMove;
            document.getElementById('ramFreeAfter').textContent = freeRAMAfter;
            document.getElementById('ramFreeGbAfter').textContent = (freeRAMAfter / 1024).toFixed(2);

            // Add instance to the move list
            const newRowToMove = instancesToMoveTable.insertRow();
            newRowToMove.insertCell(0).textContent = name;
            newRowToMove.insertCell(1).textContent = vcpus_used_instance;

            // Use the RAM value directly from the source row
            if (ram_gb_instance === 0 || isNaN(ram_gb_instance)) {
                newRowToMove.insertCell(2).textContent = "Invalid";
            } else {
                newRowToMove.insertCell(2).textContent = ram_gb_instance.toFixed(1);
            }

            // Store instance ID as data attribute on the new row
            newRowToMove.setAttribute('data-instance-id', instanceId);

            // Remove from source list
            sourceRow.parentNode.removeChild(sourceRow);
            document.getElementById('errorText').textContent = '';

            // Update charts
            updateComparisonCharts();

            // Update destination charts
            destVcpuChart = createOrUpdateDonutChart(
                'destVcpuChart',
                vcpus_used_host + totalVCPUsToMove,
                vcpus_total_host,
                'vCPU Usage (After)',
                destVcpuChart
            );

            destRamChart = createOrUpdateDonutChart(
                'destRamChart',
                ram_used_host + totalRAMToMove,
                ram_total_host,
                'RAM Usage (After)',
                destRamChart
            );
        } else if (!hasEnoughVCPU) {
            document.getElementById('errorText').textContent = 'Insufficient vCPUs on the destination host.';
            alert('Insufficient vCPUs on the destination host.');
        } else {
            document.getElementById('errorText').textContent = 'Insufficient RAM on the destination host.';
            alert('Insufficient RAM on the destination host.');
        }
    } catch (error) {
        console.error('Error moving instance to destination:', error);
    }
}

async function clearInstancesToMove() {
    const instancesToMoveTable = document.getElementById('instancesToMove');

    // Enable dropdowns
    const sourceHostsDropdown = document.getElementById('sourceHostsDropdown');
    const destinationHostsDropdown = document.getElementById('destinationHostsDropdown');
    sourceHostsDropdown.disabled = false;
    destinationHostsDropdown.disabled = false;

    // Reset flag and hide info message
    instancesSelected = false;
    document.getElementById('infoMessage').classList.add('hidden');

    // Reset vCPU and RAM counters
    document.getElementById('totalVCPUsToMove').textContent = '0';
    document.getElementById('freeVCPUsAfter').textContent = document.getElementById('freeVCPUsHost').textContent;
    document.getElementById('ramFreeAfter').textContent = document.getElementById('ramFreeHost').textContent;
    document.getElementById('ramFreeGbAfter').textContent = document.getElementById('ramFreeGbHost').textContent;
    document.getElementById('totalRamToMove').textContent = '0';
    document.getElementById('totalRamToMoveGb').textContent = '0';

    // Get destination host allocation to reset 'after' values
    const selectedHost = document.getElementById('destinationHostsDropdown').value;
    if (selectedHost) {
        try {
            const hostAllocationResponse = await fetch(`/get_host_allocation?host=${encodeURIComponent(selectedHost)}`);
            const hostAllocation = await hostAllocationResponse.json();

            // Reset vCPU and RAM 'after' values to original free values
            document.getElementById('freeVCPUsAfter').textContent = hostAllocation.vcpus_free;
            document.getElementById('ramFreeAfter').textContent = hostAllocation.ram_free;
            document.getElementById('ramFreeGbAfter').textContent = hostAllocation.ram_free_gb;

            // Update destination charts to original values
            destVcpuChart = createOrUpdateDonutChart(
                'destVcpuChart',
                hostAllocation.vcpus_used,
                hostAllocation.vcpus_total,
                'vCPU Usage',
                destVcpuChart
            );

            destRamChart = createOrUpdateDonutChart(
                'destRamChart',
                hostAllocation.ram_used,
                hostAllocation.ram_total,
                'RAM Usage (MB)',
                destRamChart
            );
        } catch (error) {
            console.error('Error resetting destination host values:', error);
        }
    }

    // Clear instances to move table
    if (instancesToMoveTable) {
        while (instancesToMoveTable.rows.length > 1) {
            instancesToMoveTable.deleteRow(1);
        }
    }

    // Clear error text
    const errorText = document.getElementById('errorText');
    if (errorText) {
        errorText.textContent = '';
    }

    // Reload instances and update comparison charts
    await loadInstances();
    updateComparisonCharts();
}

async function generateVcpuAllocationPlot() {
    const selectedDestinationHost = document.getElementById('destinationHostsDropdown').value;
    const selectedInstancesToMove = [];
    if (!selectedDestinationHost) {
        alert('Please select a destination host first.');
        // clearInstancesToMove();
        return;
    }

    const instancesToMoveTable = document.getElementById('instancesToMove');
    const rows = instancesToMoveTable.getElementsByTagName('tr');
    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        const instanceName = cells[0].textContent;
        selectedInstancesToMove.push(instanceName);
    }

    try {
        const response = await fetch(`/generate_vcpu_allocation_plot?destination_host=${encodeURIComponent(selectedDestinationHost)}`);
        const { image_path } = await response.json();
        displayVcpuAllocationPlot(image_path);
    } catch (error) {
        console.error('Error generating vCPU allocation plot:', error);
    }
}

function displayVcpuAllocationPlot(image_path) {
    const vcpuAllocationPlotDiv = document.getElementById('vcpuAllocationPlot');
    vcpuAllocationPlotDiv.innerHTML = `<img src="${image_path}" alt="vCPU Allocation Plot Generated">`;
}

async function getComputeWithFreeVCPUs() {
    const vcpuInput = document.getElementById('vcpuInput').value;

    if (vcpuInput <= 0) {
        alert('Masukkan jumlah VCPU yang valid (minimal 1).');
        return;
    }

    try {
        const response = await fetch(`/get_compute_with_free_vcpus?vcpu=${encodeURIComponent(vcpuInput)}`);
        const { compute_list } = await response.json();
        displayComputeWithFreeVCPUs(compute_list);
    } catch (error) {
        console.error('Error getting compute with free VCPUs:', error);
    }
}

function displayComputeWithFreeVCPUs(computeList) {
    const computeListDiv = document.getElementById('computeList');
    const vcpuInput = document.getElementById('vcpuInput').value;
    computeListDiv.innerHTML = `<h2>Compute dengan ${vcpuInput} free VCPU</h2>`;

    if (computeList.length === 0) {
        computeListDiv.innerHTML += `<p>Tidak ada compute yang memiliki ${vcpuInput} free VCPU.</p>`;
    } else {
        const uniqueComputeSet = new Set(computeList);
        const sortedUniqueCompute = Array.from(uniqueComputeSet).sort();

        const ul = document.createElement('ul');
        sortedUniqueCompute.forEach(compute => {
            const li = document.createElement('li');
            li.textContent = compute;
            ul.appendChild(li);
        });
        computeListDiv.appendChild(ul);
    }
}

window.onload = function () {
    loadSourceHosts();
}