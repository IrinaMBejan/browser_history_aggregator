let top_domains_file = './outputs/output_most_viewed_domains.json'
let similarity_file = './outputs/output_similarity.json'
let peers_file = './outputs/output_peers.json'
let top_papers_list = './outputs/output_top_papers.json'

fetch(top_domains_file)
    .then(response => response.json())
    .then(data => {
        const platformData = {
            labels: data.map(item => item[0].replace('www.', '')), // Remove www. from domain names
            datasets: [{
                label: 'Visits',
                data: data.map(item => item[1]),
                backgroundColor: '#3b82f6',
                borderRadius: 6
            }]
        };

        const ctx = document.getElementById('platformChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: platformData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#e5e7eb'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Most Visited Domains',
                        color: '#e5e7eb',
                        font: {
                            size: 16
                        }
                    }
                },
                scales: {
                    y: {
                        grid: {
                            color: '#374151'
                        },
                        ticks: {
                            color: '#9ca3af'
                        },
                        title: {
                            display: true,
                            text: 'Number of Visits',
                            color: '#9ca3af'
                        }
                    },
                    x: {
                        grid: {
                            color: '#374151'
                        },
                        ticks: {
                            color: '#9ca3af'
                        }
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Error loading the JSON file:', error);
        document.getElementById('platformChart').innerHTML = 'Error loading chart data';
    });

fetch(peers_file)
    .then(response => response.json())
    .then(peers => {
        const activeBadge = document.querySelector('.active-badge');
        activeBadge.textContent = `${peers.length} Active Learners`;
    })
    .catch(error => console.error('Error loading peers:', error));

fetch(top_papers_list)
    .then(response => response.json())
    .then(data => {
        const filteredData = data.filter(([url]) => !url.includes('profile'));
        
        const container = document.createElement('div');
        const header = document.createElement('div');
        header.className = 'flex justify-between items-center mb-4';
        
        const title = document.createElement('h2');
        title.className = 'text-xl font-semibold text-white';
        title.textContent = 'Top Research Papers';
        
        const badge = document.createElement('div');
        badge.className = 'papers-badge badge';
        badge.textContent = `${filteredData.length} Papers`;
        
        header.appendChild(title);
        header.appendChild(badge);

        const list = document.createElement('ul');
        list.className = 'space-y-2';

        filteredData.forEach(([url, count]) => {
            if (!url) return;
            
            const li = document.createElement('li');
            li.className = 'learner-card hover:bg-gray-700 transition-all';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'flex justify-between items-center gap-4';
            
            const leftSection = document.createElement('div');
            leftSection.className = 'flex flex-col min-w-0 flex-1'; 
            
            const link = document.createElement('a');
            link.href = `https://${url}`;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.className = 'hover:text-blue-400 transition-colors truncate'; 
            
            const domain = url.split('/')[0];
            const domainSpan = document.createElement('span');
            domainSpan.className = 'font-medium text-white truncate'; 
            domainSpan.textContent = domain;
            
            const path = '/' + url.split('/').slice(1).join('/');
            const pathSpan = document.createElement('span');
            pathSpan.className = 'text-muted text-sm mt-1 truncate'; 
            pathSpan.textContent = path;
            
            const countBadge = document.createElement('span');
            countBadge.className = 'badge match-badge whitespace-nowrap';
            countBadge.textContent = `${count} visits`;
            
            link.appendChild(domainSpan);
            link.appendChild(pathSpan);
            leftSection.appendChild(link);
            
            contentDiv.appendChild(leftSection);
            contentDiv.appendChild(countBadge);
            li.appendChild(contentDiv);
            list.appendChild(li);
        });

        container.appendChild(header);
        container.appendChild(list);

        const papersList = document.getElementById('papersList');
        if (papersList) {
            papersList.appendChild(container);
        }
    })
    .catch(error => {
        console.error('Error loading the papers data:', error);
        const papersList = document.getElementById('papersList');
        if (papersList) {
            const errorContainer = document.createElement('div');
            errorContainer.className = 'max-w-4xl mx-auto p-6';
            errorContainer.innerHTML = `
                <div class="card mb-6">
                    <div class="text-red-500">Error loading papers list</div>
                </div>
            `;
            papersList.parentNode.replaceChild(errorContainer, papersList);
        }
    });

let similarityData = null;

function findSimilarUsers(email) {
    if (!similarityData || !similarityData[email]) {
        console.log("No similar users found for", email);
        return [];
    }
    
    return similarityData[email]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([email, similarity]) => ({
            email: email,
            similarity: Math.round(similarity * 100)
        }));
}

function renderResults(searchTerm) {
    const learnersContainer = document.getElementById('learnersList');
    
    if (!learnersContainer) {
        console.error('Learners list container not found');
        return;
    }
    
    learnersContainer.innerHTML = '';

    if (!searchTerm) {
        learnersContainer.innerHTML = '<div class="text-gray-400 p-4">Enter email and press Enter to search</div>';
        return;
    }

    if (!similarityData || !similarityData[searchTerm]) {
        learnersContainer.innerHTML = '<div class="text-gray-400 p-4">No similar users found</div>';
        return;
    }

    const similarUsers = findSimilarUsers(searchTerm);
    similarUsers.forEach(user => {
        const userElement = document.createElement('div');
        userElement.className = 'learner-card flex justify-between items-center';
        userElement.innerHTML = `
            <div class="flex items-center gap-4">
                <div class="text-2xl">👤</div>
                <div>
                    <h3 class="font-medium text-white">${user.email}</h3>
                </div>
            </div>
            <span class="badge match-badge">${user.similarity}% match</span>
        `;
        learnersContainer.appendChild(userElement);
    });
}

function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    
    if (!searchInput) {
        console.error('Search input not found');
        return;
    }
    
    searchInput.placeholder = "Search your email...";

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const searchTerm = e.target.value.trim();
            renderResults(searchTerm);
            console.log('Searching for:', searchTerm);
        }
    });

    renderResults('');
}

document.addEventListener('DOMContentLoaded', () => {
    fetch(similarity_file)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            similarityData = data;
            setupSearch();
            console.log('Similarity data loaded');
        })
        .catch(error => {
            console.error('Error loading similarity data:', error);
            const learnersContainer = document.getElementById('learnersList');
            if (learnersContainer) {
                learnersContainer.innerHTML = '<div class="text-red-500 p-4">Error loading similarity data</div>';
            }
        });
});