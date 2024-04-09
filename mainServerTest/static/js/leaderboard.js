document.addEventListener('DOMContentLoaded', () => {
    const tiers = {
        'Bronze': { minPoints: 0, logo: '', users: [] },
        'Silver': { minPoints: 1000, logo: 'S', users: [] },
        'Gold': { minPoints: 2000, logo: 'G', users: [] },
        'Platinum': { minPoints: 3000, logo: 'P', users: [] },
        // Add more tiers as needed
    };

    // Expanded example users
    const users = [
        { name: 'User 1', points: 850 },
        { name: 'User 2', points: 1200 },
        { name: 'User 3', points: 2500 },
        { name: 'User 4', points: 500 },
        { name: 'User 5', points: 3500 },
        { name: 'User 6', points: 450 },
        { name: 'User 7', points: 1500 },
        { name: 'User 8', points: 2200 },
        // Add more users as needed
    ];

    function updateLeaderboard() {
        // Clear previous tiers
        document.getElementById('tiers').innerHTML = '';

        // Assign users to tiers based on points
        for (const user of users) {
            for (const [tierName, tier] of Object.entries(tiers).reverse()) {
                if (user.points >= tier.minPoints) {
                    tier.users.push(user);
                    break; // Stop checking once the correct tier is found
                }
            }
        }

        // Generate HTML for each tier
        for (const [tierName, tier] of Object.entries(tiers)) {
            if (tier.users.length > 0) {
                const tierElement = document.createElement('div');
                tierElement.className = 'tier';
                tierElement.innerHTML = `
                    <div class="tier-header">
                        <div class="tier-logo">${tier.logo}</div>
                        <div class="tier-name">${tierName} Tier</div>
                    </div>
                `;
                const userList = document.createElement('div');
                for (const user of tier.users) {
                    const userElement = document.createElement('div');
                    userElement.className = 'user';
                    userElement.innerHTML = `<div class="username">${user.name}</div><div class="points">${user.points} Points</div>`;
                    userList.appendChild(userElement);
                }
                tierElement.appendChild(userList);
                document.getElementById('tiers').appendChild(tierElement);
            }

            // Clear users for next update
            tier.users = [];
        }
    }

    updateLeaderboard();
});
document.getElementById('back-to-quiz').addEventListener('click', function() {
    window.location.href = 'generate_mcqs.html'; // Assuming your quiz application file is named 'index.html'
});