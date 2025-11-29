// ========================================
// arXiv Collection Pro - JavaScript
// By Yassine Ait Mohamed
// ========================================

// Global State
let allArticles = [];
let filteredArticles = [];
let currentPage = 1;
const itemsPerPage = 50;
let currentCategory = 'all';
let currentYear = 'all';
let searchTerm = '';

// Particle Animation Variables
let canvas, ctx;
let particles = [];
let animationId;

// ========================================
// INITIALIZATION
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    initializeCanvas();
    loadArticles();
    setupEventListeners();
    populateYearFilter();
});

// ========================================
// DATA LOADING
// ========================================

async function loadArticles() {
    try {
        // Try to load from articles.json first
        const response = await fetch('articles.json');
        if (response.ok) {
            allArticles = await response.json();
        } else {
            // Load sample data if no JSON file exists
            allArticles = generateSampleData();
        }
        
        filteredArticles = [...allArticles];
        updateDisplay();
        updateHeaderStats();
    } catch (error) {
        console.log('Loading sample data...');
        allArticles = generateSampleData();
        filteredArticles = [...allArticles];
        updateDisplay();
        updateHeaderStats();
    }
}

function generateSampleData() {
    const categories = ['math.DG', 'math.SG', 'math-ph', 'math.AG', 'math.QA', 'math.RT'];
    const sampleArticles = [];
    
    for (let i = 0; i < 500; i++) {
        const year = 2000 + Math.floor(Math.random() * 25);
        const month = Math.floor(Math.random() * 12) + 1;
        const day = Math.floor(Math.random() * 28) + 1;
        const category = categories[Math.floor(Math.random() * categories.length)];
        
        sampleArticles.push({
            id: `${year}${String(month).padStart(2, '0')}${String(day).padStart(2, '0')}.${String(i).padStart(5, '0')}`,
            title: `Research Article ${i + 1}: Advanced Studies in ${category}`,
            authors: `Author ${i % 10 + 1}; Collaborator ${i % 5 + 1}; Researcher ${i % 3 + 1}`,
            abstract: `This paper explores fundamental aspects of ${category} with applications to modern mathematical physics. We present novel approaches and theoretical frameworks.`,
            category: category,
            published: `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
            link: `https://arxiv.org/abs/${year}${String(month).padStart(2, '0')}${String(day).padStart(2, '0')}.${String(i).padStart(5, '0')}`,
            pdf: `https://arxiv.org/pdf/${year}${String(month).padStart(2, '0')}${String(day).padStart(2, '0')}.${String(i).padStart(5, '0')}.pdf`
        });
    }
    
    return sampleArticles.sort((a, b) => b.published.localeCompare(a.published));
}

// ========================================
// EVENT LISTENERS
// ========================================

function setupEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    
    // Search
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });
    
    // Category filters
    document.querySelectorAll('.cat-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const category = e.target.dataset.category;
            setCategory(category);
        });
    });
    
    // Year filter
    document.getElementById('yearFilter').addEventListener('change', (e) => {
        setYear(e.target.value);
    });
    
    // Pagination - Top
    document.getElementById('firstPageTop').addEventListener('click', () => goToPage(1));
    document.getElementById('prevPageTop').addEventListener('click', () => goToPage(currentPage - 1));
    document.getElementById('nextPageTop').addEventListener('click', () => goToPage(currentPage + 1));
    document.getElementById('lastPageTop').addEventListener('click', goToLastPage);
    
    // Pagination - Bottom
    document.getElementById('firstPageBottom').addEventListener('click', () => goToPage(1));
    document.getElementById('prevPageBottom').addEventListener('click', () => goToPage(currentPage - 1));
    document.getElementById('nextPageBottom').addEventListener('click', () => goToPage(currentPage + 1));
    document.getElementById('lastPageBottom').addEventListener('click', goToLastPage);
    
    // Action buttons
    document.getElementById('statsBtn').addEventListener('click', showStats);
    document.getElementById('exportBtn').addEventListener('click', exportData);
    
    // Modal close buttons
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            e.target.closest('.modal').style.display = 'none';
        });
    });
    
    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// ========================================
// THEME TOGGLE
// ========================================

function toggleTheme() {
    const body = document.body;
    const themeBtn = document.getElementById('themeToggle');
    
    if (body.classList.contains('night-mode')) {
        body.classList.remove('night-mode');
        body.classList.add('day-mode');
        themeBtn.textContent = '🌙 Night Mode';
        startParticleAnimation();
    } else {
        body.classList.remove('day-mode');
        body.classList.add('night-mode');
        themeBtn.textContent = '☀️ Day Mode';
        stopParticleAnimation();
    }
}

// ========================================
// PARTICLE ANIMATION (Day Mode)
// ========================================

function initializeCanvas() {
    canvas = document.getElementById('particleCanvas');
    ctx = canvas.getContext('2d');
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
}

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

function createParticles() {
    particles = [];
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 2 + 1,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            color: `rgba(74, 155, 142, ${Math.random() * 0.5 + 0.2})`
        });
    }
}

function animateParticles() {
    if (!document.body.classList.contains('day-mode')) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    particles.forEach(particle => {
        particle.x += particle.vx;
        particle.y += particle.vy;
        
        if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
        
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        ctx.fillStyle = particle.color;
        ctx.fill();
    });
    
    // Draw connections
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 150) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(74, 155, 142, ${0.2 * (1 - distance / 150)})`;
                ctx.lineWidth = 1;
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
            }
        }
    }
    
    animationId = requestAnimationFrame(animateParticles);
}

function startParticleAnimation() {
    createParticles();
    animateParticles();
}

function stopParticleAnimation() {
    if (animationId) {
        cancelAnimationFrame(animationId);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
}

// ========================================
// FILTERING & SEARCH
// ========================================

function performSearch() {
    searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    currentPage = 1;
    applyFilters();
}

function setCategory(category) {
    currentCategory = category;
    currentPage = 1;
    
    // Update button states
    document.querySelectorAll('.cat-btn').forEach(btn => {
        if (btn.dataset.category === category) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    applyFilters();
}

function setYear(year) {
    currentYear = year;
    currentPage = 1;
    applyFilters();
}

function applyFilters() {
    filteredArticles = allArticles.filter(article => {
        // Search filter
        if (searchTerm) {
            const matchesSearch = 
                article.title.toLowerCase().includes(searchTerm) ||
                article.abstract.toLowerCase().includes(searchTerm);
            if (!matchesSearch) return false;
        }
        
        // Category filter
        if (currentCategory !== 'all' && article.category !== currentCategory) {
            return false;
        }
        
        // Year filter
        if (currentYear !== 'all' && !article.published.startsWith(currentYear)) {
            return false;
        }
        
        return true;
    });
    
    updateDisplay();
}

// ========================================
// DISPLAY UPDATE
// ========================================

function updateDisplay() {
    const tbody = document.getElementById('articlesTableBody');
    tbody.innerHTML = '';
    
    const totalPages = Math.ceil(filteredArticles.length / itemsPerPage);
    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageArticles = filteredArticles.slice(start, end);
    
    pageArticles.forEach(article => {
        const row = createArticleRow(article);
        tbody.appendChild(row);
    });
    
    updatePagination();
}

function createArticleRow(article) {
    const tr = document.createElement('tr');
    
    // Get first author
    const authors = article.authors.split(';');
    let firstAuthor = authors[0].trim();
    if (authors.length > 1) {
        firstAuthor += ' et al.';
    }
    
    // Get year
    const year = article.published.substring(0, 4);
    
    tr.innerHTML = `
        <td class="article-title">${article.title}</td>
        <td class="article-authors">${firstAuthor}</td>
        <td class="article-year">${year}</td>
        <td><span class="article-category">${article.category}</span></td>
        <td class="action-links">
            <a href="#" class="action-link" title="View Details" onclick="showArticleDetails('${article.id}'); return false;">📄</a>
            <a href="${article.link}" class="action-link" target="_blank" title="Open on arXiv">🔗</a>
            <a href="${article.pdf}" class="action-link" target="_blank" title="Download PDF">📥</a>
        </td>
    `;
    
    return tr;
}

function updatePagination() {
    const totalPages = Math.ceil(filteredArticles.length / itemsPerPage);
    const pageInfo = `Page ${currentPage}/${totalPages || 1} | ${filteredArticles.length.toLocaleString()} articles`;
    
    document.getElementById('pageInfoTop').textContent = pageInfo;
    document.getElementById('pageInfoBottom').textContent = pageInfo;
    
    // Enable/disable buttons
    const firstButtons = [document.getElementById('firstPageTop'), document.getElementById('firstPageBottom')];
    const prevButtons = [document.getElementById('prevPageTop'), document.getElementById('prevPageBottom')];
    const nextButtons = [document.getElementById('nextPageTop'), document.getElementById('nextPageBottom')];
    const lastButtons = [document.getElementById('lastPageTop'), document.getElementById('lastPageBottom')];
    
    firstButtons.forEach(btn => btn.disabled = currentPage === 1);
    prevButtons.forEach(btn => btn.disabled = currentPage === 1);
    nextButtons.forEach(btn => btn.disabled = currentPage >= totalPages);
    lastButtons.forEach(btn => btn.disabled = currentPage >= totalPages);
}

function goToPage(page) {
    const totalPages = Math.ceil(filteredArticles.length / itemsPerPage);
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        updateDisplay();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function goToLastPage() {
    const totalPages = Math.ceil(filteredArticles.length / itemsPerPage);
    goToPage(totalPages);
}

// ========================================
// STATISTICS
// ========================================

function updateHeaderStats() {
    const stats = calculateStats();
    const statsText = `📊 Total: ${stats.total.toLocaleString()} articles | 📂 ${stats.categories.length} categories | 📅 ${stats.yearRange}`;
    document.getElementById('headerStats').textContent = statsText;
}

function calculateStats() {
    const total = allArticles.length;
    
    // Categories
    const categoryCount = {};
    allArticles.forEach(article => {
        categoryCount[article.category] = (categoryCount[article.category] || 0) + 1;
    });
    
    // Years
    const years = allArticles.map(a => parseInt(a.published.substring(0, 4))).filter(y => !isNaN(y));
    const minYear = Math.min(...years);
    const maxYear = Math.max(...years);
    
    // Year distribution
    const yearCount = {};
    years.forEach(year => {
        yearCount[year] = (yearCount[year] || 0) + 1;
    });
    
    return {
        total,
        categories: Object.entries(categoryCount).sort((a, b) => b[1] - a[1]),
        yearRange: `${minYear}-${maxYear}`,
        yearDistribution: Object.entries(yearCount).sort((a, b) => b[0] - a[0])
    };
}

function showStats() {
    const stats = calculateStats();
    const modal = document.getElementById('statsModal');
    const body = document.getElementById('statsBody');
    
    let html = '<h2>📊 Collection Statistics</h2>';
    
    // Overview
    html += '<div class="stats-grid">';
    html += `<div class="stat-card">
        <h4>Total Articles</h4>
        <div class="stat-value">${stats.total.toLocaleString()}</div>
    </div>`;
    html += `<div class="stat-card">
        <h4>Categories</h4>
        <div class="stat-value">${stats.categories.length}</div>
    </div>`;
    html += `<div class="stat-card">
        <h4>Year Range</h4>
        <div class="stat-value">${stats.yearRange}</div>
    </div>`;
    html += '</div>';
    
    // By Category
    html += '<h3>📂 By Category</h3>';
    stats.categories.forEach(([cat, count]) => {
        const percent = (count / stats.total * 100).toFixed(1);
        html += `
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span><strong>${cat}</strong></span>
                    <span>${count.toLocaleString()} (${percent}%)</span>
                </div>
                <div class="stat-bar">
                    <div class="stat-bar-fill" style="width: ${percent}%"></div>
                </div>
            </div>
        `;
    });
    
    // By Year
    html += '<h3>📅 By Year (Recent)</h3>';
    stats.yearDistribution.slice(0, 10).forEach(([year, count]) => {
        const maxCount = Math.max(...stats.yearDistribution.map(y => y[1]));
        const percent = (count / maxCount * 100).toFixed(0);
        html += `
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span><strong>${year}</strong></span>
                    <span>${count.toLocaleString()}</span>
                </div>
                <div class="stat-bar">
                    <div class="stat-bar-fill" style="width: ${percent}%"></div>
                </div>
            </div>
        `;
    });
    
    body.innerHTML = html;
    modal.style.display = 'block';
}

// ========================================
// ARTICLE DETAILS
// ========================================

function showArticleDetails(articleId) {
    const article = allArticles.find(a => a.id === articleId);
    if (!article) return;
    
    const modal = document.getElementById('detailsModal');
    const body = document.getElementById('modalBody');
    
    const html = `
        <h2>📄 ${article.title}</h2>
        
        <h3>✍️ Authors</h3>
        <p>${article.authors.split(';').join(', ')}</p>
        
        <h3>🏷️ Metadata</h3>
        <p><strong>Category:</strong> ${article.category}</p>
        <p><strong>Published:</strong> ${article.published}</p>
        <p><strong>arXiv ID:</strong> ${article.id}</p>
        
        <h3>🔗 Links</h3>
        <p>
            <a href="${article.link}" target="_blank">View on arXiv →</a><br>
            <a href="${article.pdf}" target="_blank">Download PDF →</a>
        </p>
        
        <h3>📝 Abstract</h3>
        <p>${article.abstract}</p>
    `;
    
    body.innerHTML = html;
    modal.style.display = 'block';
}

// ========================================
// EXPORT DATA
// ========================================

function exportData() {
    const dataStr = JSON.stringify(filteredArticles, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `arxiv_export_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
}

// ========================================
// YEAR FILTER POPULATION
// ========================================

function populateYearFilter() {
    const select = document.getElementById('yearFilter');
    const currentYear = new Date().getFullYear();
    
    for (let year = currentYear; year >= 2000; year--) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        select.appendChild(option);
    }
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

// Make showArticleDetails available globally
window.showArticleDetails = showArticleDetails;
