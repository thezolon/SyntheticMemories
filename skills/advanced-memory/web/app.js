// Use relative URLs so browser calls the same host it loaded the page from
const API_BASE = '';

let currentMemories = [];
let currentQuery = '';
let currentPage = 1;
let perPage = 25;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadHealth();
    loadAllMemories();
    
    // Event listeners
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('clearBtn').addEventListener('click', clearSearch);
    document.getElementById('addBtn').addEventListener('click', openAddModal);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
    
    document.getElementById('tierFilter').addEventListener('change', applyFilters);
    document.getElementById('importanceFilter').addEventListener('change', applyFilters);
    document.getElementById('sortBy').addEventListener('change', applySort);
    document.getElementById('perPageSelect').addEventListener('change', changePerPage);
    document.getElementById('prevPage').addEventListener('click', prevPage);
    document.getElementById('nextPage').addEventListener('click', nextPage);
    
    document.getElementById('addMemoryForm').addEventListener('submit', saveMemory);
});

async function loadHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const health = await response.json();
        
        document.getElementById('totalCount').textContent = health.memory_count;
        document.getElementById('modelName').textContent = health.embedding_model;
        
        const indicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        
        if (health.ollama_connected) {
            indicator.className = 'status-indicator healthy';
            statusText.textContent = 'Connected to Ollama';
        } else {
            indicator.className = 'status-indicator unhealthy';
            statusText.textContent = 'Ollama disconnected';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        document.getElementById('statusIndicator').className = 'status-indicator unhealthy';
        document.getElementById('statusText').textContent = 'Service unavailable';
    }
}

async function loadAllMemories() {
    try {
        // Fetch with high limit to get all, then paginate client-side
        const response = await fetch(`${API_BASE}/recall?query=*&limit=1000`);
        const data = await response.json();
        
        currentMemories = data.results || [];
        currentQuery = '';
        currentPage = 1;
        renderMemories();
    } catch (error) {
        console.error('Failed to load memories:', error);
        showError('Failed to load memories');
    }
}

async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        loadAllMemories();
        return;
    }
    
    try {
        const tierFilter = document.getElementById('tierFilter').value;
        const importanceFilter = document.getElementById('importanceFilter').value;
        
        let url = `${API_BASE}/recall?query=${encodeURIComponent(query)}&limit=1000`;
        if (tierFilter) url += `&tier=${tierFilter}`;
        if (importanceFilter) url += `&min_importance=${importanceFilter}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        currentMemories = data.results || [];
        currentQuery = query;
        currentPage = 1;
        renderMemories();
    } catch (error) {
        console.error('Search failed:', error);
        showError('Search failed');
    }
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('tierFilter').value = '';
    document.getElementById('importanceFilter').value = '';
    currentPage = 1;
    loadAllMemories();
}

function applyFilters() {
    if (currentQuery) {
        performSearch();
    } else {
        loadAllMemories();
    }
}

function applySort() {
    const sortBy = document.getElementById('sortBy').value;
    
    switch (sortBy) {
        case 'recent':
            currentMemories.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            break;
        case 'importance':
            currentMemories.sort((a, b) => b.importance - a.importance);
            break;
        case 'similarity':
            currentMemories.sort((a, b) => (a.similarity || 999) - (b.similarity || 999));
            break;
    }
    
    renderMemories();
}

function renderMemories() {
    const container = document.getElementById('memoriesContainer');
    
    if (currentMemories.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No memories found</h3>
                <p>Start by adding your first memory or try a different search.</p>
            </div>
        `;
        updatePageInfo();
        return;
    }
    
    // Calculate pagination
    const totalItems = currentMemories.length;
    const totalPages = Math.ceil(totalItems / perPage);
    const startIdx = (currentPage - 1) * perPage;
    const endIdx = Math.min(startIdx + perPage, totalItems);
    const pageItems = currentMemories.slice(startIdx, endIdx);
    
    container.innerHTML = `
        <div class="memories-grid">
            ${pageItems.map(renderMemoryCard).join('')}
        </div>
    `;
    
    updatePageInfo();
    
    // Update pagination buttons
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage >= totalPages;
}

function updatePageInfo() {
    const totalItems = currentMemories.length;
    const startIdx = (currentPage - 1) * perPage + 1;
    const endIdx = Math.min(currentPage * perPage, totalItems);
    
    const pageInfo = document.getElementById('pageInfo');
    if (totalItems === 0) {
        pageInfo.textContent = 'Showing 0 of 0';
    } else {
        pageInfo.textContent = `Showing ${startIdx}-${endIdx} of ${totalItems}`;
    }
}

function changePerPage() {
    perPage = parseInt(document.getElementById('perPageSelect').value);
    currentPage = 1;
    renderMemories();
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        renderMemories();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function nextPage() {
    const totalPages = Math.ceil(currentMemories.length / perPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderMemories();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function renderMemoryCard(memory) {
    const date = new Date(memory.timestamp);
    const dateStr = date.toLocaleString();
    
    const importanceClass = memory.importance >= 7 ? 'high' : memory.importance >= 5 ? 'medium' : 'low';
    
    const similarityBadge = memory.similarity !== undefined 
        ? `<span class="similarity">Match: ${(1000 - memory.similarity).toFixed(0)}</span>`
        : '';
    
    return `
        <div class="memory-card">
            <div class="memory-header">
                <div class="memory-meta">
                    <span class="badge tier-${memory.tier}">${memory.tier}</span>
                    <span class="importance ${importanceClass}">Importance: ${memory.importance}</span>
                    ${similarityBadge}
                </div>
            </div>
            <div class="memory-content">${escapeHtml(memory.content)}</div>
            <div class="memory-footer">
                <span class="timestamp">${dateStr}</span>
                <span class="memory-id">${memory.id}</span>
            </div>
        </div>
    `;
}

function openAddModal() {
    document.getElementById('addModal').classList.add('active');
}

function closeModal() {
    document.getElementById('addModal').classList.remove('active');
    document.getElementById('addMemoryForm').reset();
}

async function saveMemory(e) {
    e.preventDefault();
    
    const content = document.getElementById('memoryContent').value.trim();
    const tier = document.getElementById('memoryTier').value;
    const importance = document.getElementById('memoryImportance').value;
    
    if (!content) return;
    
    try {
        const payload = {
            content,
            tier,
            user_id: 'default'
        };
        
        if (importance) {
            payload.importance = parseInt(importance);
        }
        
        const response = await fetch(`${API_BASE}/store`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        
        if (result.success) {
            closeModal();
            loadHealth(); // Refresh count
            if (currentQuery) {
                performSearch();
            } else {
                loadAllMemories();
            }
        } else {
            showError('Failed to save memory');
        }
    } catch (error) {
        console.error('Save failed:', error);
        showError('Failed to save memory');
    }
}

function showError(message) {
    const container = document.getElementById('memoriesContainer');
    container.innerHTML = `
        <div class="empty-state">
            <h3>❌ Error</h3>
            <p>${message}</p>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal on outside click
document.getElementById('addModal').addEventListener('click', (e) => {
    if (e.target.id === 'addModal') {
        closeModal();
    }
});
