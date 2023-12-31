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

async function loadInstances() {
    const selectedHost = document.getElementById('sourceHostsDropdown').value;

    if (selectedHost) {
        try {
            const response = await fetch(`/get_instances?host=${encodeURIComponent(selectedHost)}`);
            const { instances } = await response.json();

            const sourceHostTable = document.getElementById('sourceHost');
            sourceHostTable.innerHTML = '<tr><th class="px-4 py-2 bg-blue-500 text-white">Name</th><th class="px-4 py-2 bg-blue-500 text-white">vCPU</th><th class="px-4 py-2 bg-blue-500 text-white">Actions</th></tr>';

            instances.forEach(async (instance, index) => {
                const row = sourceHostTable.insertRow();
                row.className = 'hover:bg-blue-200';

                const cell1 = row.insertCell(0);
                cell1.textContent = instance.Name;

                const cell2 = row.insertCell(1);
                cell2.textContent = instance.CPU;
                cell2.className = "text-center";

                const moveButtonCell = row.insertCell(2);
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

            document.getElementById('vcpusUsedSourceHost').textContent = hostAllocation.vcpus_used;
            document.getElementById('totalVCPUsSourceHost').textContent = hostAllocation.vcpus_total;
            document.getElementById('freeVCPUsSourceHost').textContent = hostAllocation.vcpus_free;
        } catch (error) {
            console.error('Error loading instances:', error);
        }
    }
}

async function loadDestinationHostInstances() {
    const selectedHost = document.getElementById('destinationHostsDropdown').value;

    if (selectedHost) {
        try {
            const response = await fetch(`/get_destination_host_instances?host=${encodeURIComponent(selectedHost)}`);
            const data = await response.json();

            const destinationHostTable = document.getElementById('destinationHost');
            destinationHostTable.innerHTML = '<tr><th class="px-4 py-2 bg-blue-500 text-white">Name</th><th class="px-4 py-2 bg-blue-500 text-white">vCPU</th></tr>';

            if (data.instances) {
                data.instances.forEach(instance => {
                    const row = destinationHostTable.insertRow();
                    row.className = 'hover:bg-blue-200';

                    const cell1 = row.insertCell(0);
                    cell1.textContent = instance.Name;

                    const cell2 = row.insertCell(1);
                    cell2.textContent = instance.CPU;
                    cell2.className = "text-center py-1";
                    });
            }

            document.getElementById('destinationHostTitle').textContent = 'Instances on ' + selectedHost;
            document.getElementById('destinationHostInfo').textContent = 'Info ' + selectedHost;

            const hostAllocationResponse = await fetch(`/get_host_allocation?host=${encodeURIComponent(selectedHost)}`);
            const hostAllocation = await hostAllocationResponse.json();

            document.getElementById('vcpusUsedHost').textContent = hostAllocation.vcpus_used;
            document.getElementById('totalVCPUsHost').textContent = hostAllocation.vcpus_total;
            document.getElementById('freeVCPUsHost').textContent = hostAllocation.vcpus_free;
        } catch (error) {
            console.error('Error loading destination host instances:', error);
        }
    }
}

async function moveInstanceToDestination(btnId) {
    const sourceRow = document.getElementById(btnId).parentNode.parentNode;
    // console.log('btnId:', btnId);
    // console.log('sourceRow:', sourceRow);
    // console.log('sourceRow.parentNode (tbody):', sourceRow.parentNode);
    // console.log('sourceRow.parentNode.parentNode (table):', sourceRow.parentNode.parentNode);

    const name = sourceRow.cells[0].textContent;
    const cpu = sourceRow.cells[1].textContent;
    const selectedHost = document.getElementById('destinationHostsDropdown').value;

    const vcpusFreeElement = document.getElementById('freeVCPUsHost');
    // console.log(vcpusFreeElement)
    const vcpus_free = vcpusFreeElement ? parseFloat(vcpusFreeElement.textContent) : 0;

    const sourceHostsDropdown = document.getElementById('sourceHostsDropdown');
    const destinationHostsDropdown = document.getElementById('destinationHostsDropdown');

    sourceHostsDropdown.disabled = true;
    destinationHostsDropdown.disabled = true;

    if (!selectedHost) {
        alert('Please select a destination host first.');
        clearInstancesToMove();
        return;
    }

    try {
        const instanceVcpusResponse = await fetch(`/get_instance_vcpus_used?name=${encodeURIComponent(name)}`);
        const vcpus_used_instance = parseFloat(await instanceVcpusResponse.json());

        const hostAllocationResponse = await fetch(`/get_host_allocation?host=${encodeURIComponent(selectedHost)}`);
        const hostAllocation = await hostAllocationResponse.json();
        const vcpus_used_host = parseFloat(hostAllocation.vcpus_used);
        const vcpus_total_host = parseFloat(hostAllocation.vcpus_total);
        const vcpus_free_host = parseFloat(hostAllocation.vcpus_free);

        const instancesToMoveTable = document.getElementById('instancesToMove');
        const rows = instancesToMoveTable.getElementsByTagName('tr');
        let totalVCPUsToMove = vcpus_used_instance;

        for (let i = 1; i < rows.length; i++) {
            const cells = rows[i].getElementsByTagName('td');
            const vcpuInstance = parseFloat(cells[1].textContent);
            totalVCPUsToMove += vcpuInstance;
        }

        if (totalVCPUsToMove <= vcpus_free_host && (vcpus_used_host + totalVCPUsToMove) <= vcpus_total_host) {
            if (vcpus_free_host - totalVCPUsToMove >= 0) {
                document.getElementById('totalVCPUsToMove').textContent = totalVCPUsToMove;

                const freeVCPUsAfter = vcpus_free_host - totalVCPUsToMove;
                document.getElementById('freeVCPUsAfter').textContent = freeVCPUsAfter;

                const newRowToMove = instancesToMoveTable.insertRow();
                newRowToMove.insertCell(0).textContent = name;
                newRowToMove.insertCell(1).textContent = vcpus_used_instance;

                sourceRow.parentNode.removeChild(sourceRow);
                vcpusFreeElement.textContent = vcpus_free_host;
                document.getElementById('errorText').textContent = '';
            } else {
                document.getElementById('errorText').textContent = 'Insufficient vcpus_free on the destination host.';
            }
        } else {
            // document.getElementById('errorText').textContent = 'Total vCPU of the destination host will exceed the limit.';
            // document.getElementById('errorText').textContent = 'Insufficient vcpus_free on the destination host.';
            alert('Insufficient vcpus_free on the destination host.')
        }
    } catch (error) {
        console.error('Error moving instance to destination:', error);
    }
}

async function clearInstancesToMove() {
const instancesToMoveTable = document.getElementById('instancesToMove');
const sourceHostTable = document.getElementById('sourceHost');
let vcpus_free = 0; // Change const to let for reassignment

const sourceHostsDropdown = document.getElementById('sourceHostsDropdown');
const destinationHostsDropdown = document.getElementById('destinationHostsDropdown');

sourceHostsDropdown.disabled = false;
destinationHostsDropdown.disabled = false;

document.getElementById('totalVCPUsToMove').textContent = 0;
document.getElementById('freeVCPUsAfter').textContent = 0;

    if (instancesToMoveTable) {
        const rows = instancesToMoveTable.getElementsByTagName('tr');
        for (let i = 1; i < rows.length; i++) {
            const cells = rows[i].getElementsByTagName('td');
            const vcpuInstance = parseFloat(cells[1].textContent);
            vcpus_free += vcpuInstance;
        }

        while (instancesToMoveTable.rows.length > 1) {
            instancesToMoveTable.deleteRow(1);
        }
    }

    const vcpusFreeElement = document.getElementById('vcpusFree');
    if (vcpusFreeElement) {
        vcpusFreeElement.textContent = vcpus_free;
    }

    const errorText = document.getElementById('errorText');
    if (errorText) {
        errorText.textContent = '';
    }

    await loadInstances();
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