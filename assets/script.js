let top_domains_file = './outputs/output_most_viewed_domains.json'
let similarity_file = './outputs/output_similarity.json'
let peers_file = './outputs/output_peers.json'

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

fetch(peers_file)
    .then(response => response.json())
    .then(peers => {
        const activeBadge = document.querySelector('.active-badge');
        activeBadge.textContent = `${peers.length} Active Learners`;
    })
    .catch(error => console.error('Error loading peers:', error));


let similarityData = null;
fetch(similarity_file)
    .then(response => response.json())
    .then(data => {
        similarityData = data;
        setupSearch();
    })
    .catch(error => console.error('Error loading similarity data:', error));

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
    searchInput.placeholder = "Search your email...  ";

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            renderResults(e.target.value.trim());
            console.log(e.target.value.trim());
        }
    });

    renderResults('');
}