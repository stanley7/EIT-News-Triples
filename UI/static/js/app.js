/**
 * SOCIOTYPER - Main Application JavaScript
 */

// =============================================================================
// STATE
// =============================================================================

const state = {
    text: '',
    triplets: [],
    validatedTriplets: [],
    isExtracting: false,
    apiUrl: localStorage.getItem('sociotyper_api_url') || '',
};

// =============================================================================
// TAB NAVIGATION
// =============================================================================

document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Update active tab
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update active content
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(tab.dataset.tab).classList.add('active');
    });
});

// =============================================================================
// FILE UPLOAD
// =============================================================================

document.getElementById('fileInput').addEventListener('change', async (e) => {
    const files = e.target.files;
    const fileList = document.getElementById('fileList');
    const textPreview = document.getElementById('textPreview');

    fileList.innerHTML = '';
    let combinedText = '';

    for (const file of files) {
        // Add to file list
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span>${file.name}</span>
            <button onclick="this.parentElement.remove()">×</button>
        `;
        fileList.appendChild(fileItem);

        // Read file content
        const text = await file.text();
        combinedText += text + '\n\n';
    }

    state.text = combinedText.trim();
    textPreview.value = state.text;
    updateCharCount();
});

document.getElementById('textPreview').addEventListener('input', (e) => {
    state.text = e.target.value;
    updateCharCount();
});

function updateCharCount() {
    document.getElementById('charCount').textContent = state.text.length.toLocaleString();
}

// =============================================================================
// URL SCRAPING
// =============================================================================

async function scrapeUrl() {
    const url = document.getElementById('urlInput').value.trim();
    if (!url) {
        alert('Please enter a URL');
        return;
    }

    const apiUrl = getApiUrl();
    if (!apiUrl) {
        alert('Please configure the API URL in the Configure tab');
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/scrape_url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url }),
        });

        const data = await response.json();

        if (data.error) {
            alert('Error scraping URL: ' + data.error);
            return;
        }

        state.text = data.text;
        document.getElementById('textPreview').value = state.text;
        updateCharCount();

    } catch (error) {
        alert('Failed to scrape URL: ' + error.message);
    }
}

// =============================================================================
// API CONNECTION
// =============================================================================

function getApiUrl() {
    const urlInput = document.getElementById('apiUrl');
    if (urlInput.value) {
        state.apiUrl = urlInput.value.trim().replace(/\/$/, '');
        localStorage.setItem('sociotyper_api_url', state.apiUrl);
    }
    return state.apiUrl;
}

async function testConnection() {
    const apiUrl = getApiUrl();
    const status = document.getElementById('connectionStatus');

    if (!apiUrl) {
        status.textContent = 'Please enter API URL';
        status.className = 'error';
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/models`);
        const data = await response.json();

        if (data.models) {
            status.textContent = '✓ Connected';
            status.className = 'success';
        } else {
            status.textContent = '✗ Invalid response';
            status.className = 'error';
        }
    } catch (error) {
        status.textContent = '✗ Connection failed';
        status.className = 'error';
    }
}

// Load saved API URL on page load
document.addEventListener('DOMContentLoaded', () => {
    if (state.apiUrl) {
        document.getElementById('apiUrl').value = state.apiUrl;
    }
});

// =============================================================================
// EXTRACTION
// =============================================================================

async function startExtraction() {
    if (!state.text) {
        alert('Please upload or enter text first');
        return;
    }

    const apiUrl = getApiUrl();
    if (!apiUrl) {
        alert('Please configure the API URL in the Configure tab');
        return;
    }

    state.isExtracting = true;
    document.getElementById('startExtraction').disabled = true;
    document.getElementById('stopExtraction').disabled = false;

    const model = document.getElementById('modelSelect').value;
    const userPrompt = document.getElementById('userPrompt').value;
    const maxTriplets = parseInt(document.getElementById('maxTriplets').value) || 50;

    const log = document.getElementById('extractionLog');
    log.innerHTML = '';
    addLog('Starting extraction...');
    addLog(`Model: ${model}`);
    addLog(`Max triplets: ${maxTriplets}`);

    updateProgress(0, 'Sending request...');

    try {
        const response = await fetch(`${apiUrl}/extract_triplets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: state.text,
                model: model,
                user_prompt: userPrompt,
                max_triplets: maxTriplets,
            }),
        });

        const data = await response.json();

        if (data.error) {
            addLog(`Error: ${data.error}`, 'error');
            return;
        }

        state.triplets = data.triplets || [];
        addLog(`Extracted ${state.triplets.length} triplets`, 'success');

        updateProgress(100, `Complete! ${state.triplets.length} triplets extracted`);

        // Show triplets in log
        state.triplets.forEach((t, i) => {
            const { role, practice, counterrole } = t.extracted;
            addLog(`${i + 1}. ${role} → ${practice} → ${counterrole}`);
        });

        // Update validation tab
        updateValidationTab();
        updateResultsTab();

    } catch (error) {
        addLog(`Error: ${error.message}`, 'error');
    } finally {
        state.isExtracting = false;
        document.getElementById('startExtraction').disabled = false;
        document.getElementById('stopExtraction').disabled = true;
    }
}

function stopExtraction() {
    state.isExtracting = false;
    addLog('Extraction stopped by user', 'error');
}

function addLog(message, type = '') {
    const log = document.getElementById('extractionLog');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type ? 'log-' + type : ''}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;
}

function updateProgress(percent, text) {
    document.getElementById('progressFill').style.width = `${percent}%`;
    document.getElementById('progressText').textContent = text;
}

// =============================================================================
// VALIDATION
// =============================================================================

function updateValidationTab() {
    const list = document.getElementById('validationList');
    list.innerHTML = '';

    document.getElementById('totalTriplets').textContent = state.triplets.length;
    updateValidationCounts();

    state.triplets.forEach((triplet, index) => {
        const card = document.createElement('div');
        card.className = 'triplet-card';
        card.dataset.index = index;

        const { role, practice, counterrole } = triplet.extracted;

        card.innerHTML = `
            <div class="triplet-content">
                <span class="triplet-role">${role}</span>
                <span class="triplet-practice">→ ${practice} →</span>
                <span class="triplet-counterrole">${counterrole}</span>
                <div class="triplet-context">"${triplet.text}"</div>
            </div>
            <div class="triplet-actions">
                <button class="accept-btn" onclick="validateTriplet(${index}, true)">Accept</button>
                <button class="reject-btn" onclick="validateTriplet(${index}, false)">Reject</button>
            </div>
        `;

        list.appendChild(card);
    });
}

function validateTriplet(index, accepted) {
    state.triplets[index].validated = accepted;

    const card = document.querySelector(`.triplet-card[data-index="${index}"]`);
    card.classList.remove('accepted', 'rejected');
    card.classList.add(accepted ? 'accepted' : 'rejected');

    updateValidationCounts();
}

function updateValidationCounts() {
    const accepted = state.triplets.filter(t => t.validated === true).length;
    const rejected = state.triplets.filter(t => t.validated === false).length;

    document.getElementById('acceptedTriplets').textContent = accepted;
    document.getElementById('rejectedTriplets').textContent = rejected;
}

// =============================================================================
// NETWORK VISUALIZATION
// =============================================================================

function updateNetworkVisualization(filter = 'all') {
    const container = document.getElementById('networkContainer');
    container.innerHTML = '';

    const width = container.clientWidth;
    const height = 500;

    // Filter triplets
    let filteredTriplets = state.triplets.filter(t => t.validated !== false);
    if (filter !== 'all') {
        filteredTriplets = filteredTriplets.filter(t =>
            t.extracted.practice.toLowerCase().includes(filter)
        );
    }

    if (filteredTriplets.length === 0) {
        container.innerHTML = '<p style="padding: 2rem; text-align: center;">No triplets to display</p>';
        return;
    }

    // Build nodes and links
    const nodeSet = new Set();
    const links = [];

    filteredTriplets.forEach(t => {
        const role = t.extracted.role;
        const counterrole = t.extracted.counterrole;
        nodeSet.add(role);
        nodeSet.add(counterrole);
        links.push({
            source: role,
            target: counterrole,
            practice: t.extracted.practice,
        });
    });

    const nodes = Array.from(nodeSet).map(name => ({ id: name }));

    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    // Create simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(150))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .enter()
        .append('line')
        .attr('stroke', '#999')
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.6);

    // Draw nodes
    const node = svg.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter()
        .append('circle')
        .attr('r', 8)
        .attr('fill', '#0f62fe')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add labels
    const label = svg.append('g')
        .selectAll('text')
        .data(nodes)
        .enter()
        .append('text')
        .text(d => d.id)
        .attr('font-size', 10)
        .attr('dx', 12)
        .attr('dy', 4);

    // Update positions
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });

    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
}

function filterNetwork(filter) {
    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(filter) ||
            (filter === 'all' && btn.textContent === 'All')) {
            btn.classList.add('active');
        }
    });

    updateNetworkVisualization(filter);
}

// Update network when switching to tab
document.querySelector('[data-tab="network"]').addEventListener('click', () => {
    setTimeout(() => updateNetworkVisualization('all'), 100);
});

// =============================================================================
// RESULTS & EXPORT
// =============================================================================

function updateResultsTab() {
    const summary = document.getElementById('resultsSummary');
    const preview = document.getElementById('tripletsPreview');

    const accepted = state.triplets.filter(t => t.validated === true);
    const rejected = state.triplets.filter(t => t.validated === false);
    const pending = state.triplets.filter(t => t.validated === null);

    summary.innerHTML = `
        <p>Total triplets: ${state.triplets.length}</p>
        <p>Accepted: ${accepted.length}</p>
        <p>Rejected: ${rejected.length}</p>
        <p>Pending validation: ${pending.length}</p>
    `;

    preview.innerHTML = '';
    state.triplets.slice(0, 20).forEach(t => {
        const div = document.createElement('div');
        div.className = 'triplet-card';
        const { role, practice, counterrole } = t.extracted;
        div.innerHTML = `
            <span class="triplet-role">${role}</span>
            <span class="triplet-practice">→ ${practice} →</span>
            <span class="triplet-counterrole">${counterrole}</span>
        `;
        preview.appendChild(div);
    });
}

function exportJSON() {
    const data = {
        exported_at: new Date().toISOString(),
        total_triplets: state.triplets.length,
        triplets: state.triplets,
    };

    downloadFile(
        JSON.stringify(data, null, 2),
        'sociotyper_triplets.json',
        'application/json'
    );
}

function exportCSV() {
    let csv = 'ID,Role,Practice,Counterrole,Context,Confidence,Validated\n';

    state.triplets.forEach(t => {
        const { role, practice, counterrole } = t.extracted;
        csv += `${t.id},"${role}","${practice}","${counterrole}","${t.text.replace(/"/g, '""')}",${t.confidence},${t.validated}\n`;
    });

    downloadFile(csv, 'sociotyper_triplets.csv', 'text/csv');
}

function exportNetwork() {
    const nodeSet = new Set();
    const links = [];

    state.triplets.filter(t => t.validated !== false).forEach(t => {
        nodeSet.add(t.extracted.role);
        nodeSet.add(t.extracted.counterrole);
        links.push({
            source: t.extracted.role,
            target: t.extracted.counterrole,
            practice: t.extracted.practice,
        });
    });

    const data = {
        nodes: Array.from(nodeSet).map(id => ({ id })),
        links,
    };

    downloadFile(
        JSON.stringify(data, null, 2),
        'sociotyper_network.json',
        'application/json'
    );
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
