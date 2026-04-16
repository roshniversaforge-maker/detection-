document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const urlInput = document.getElementById('url-input');
    const loader = document.getElementById('loader');
    const errorMsg = document.getElementById('error-msg');
    const resultsSection = document.getElementById('results-section');
    const reviewsList = document.getElementById('reviews-list');

    if (analyzeBtn && urlInput) {
        analyzeBtn.addEventListener('click', async () => {
            const url = urlInput.value.trim();
            
            if (!url) {
                showError("Please enter a valid product URL.");
                return;
            }

            // UI Reset
            loader.style.display = 'block';
            errorMsg.style.display = 'none';
            resultsSection.style.display = 'none';
            reviewsList.innerHTML = '';
            analyzeBtn.disabled = true;

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url: url })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "Failed to analyze reviews.");
                }

                // Update Stats
                document.getElementById('total-reviews').innerText = data.total;
                document.getElementById('genuine-pct').innerText = data.genuine_pct + '%';
                document.getElementById('fake-pct').innerText = data.fake_pct + '%';

                // Sort reviews so genuine appears prominently if needed, 
                // but usually we want to see all of them in order. Let's just render them.
                data.reviews.forEach(review => {
                    const card = document.createElement('div');
                    card.className = `review-card ${review.prediction.toLowerCase()}`;
                    
                    const badgePredClass = review.prediction === 'Genuine' ? 'pred-genuine' : 'pred-fake';
                    const badgeSentClass = `sent-${review.sentiment.toLowerCase()}`;
                    
                    let duplicateBadge = review.is_duplicate ? '<span class="badge duplicate"><i class="fa-solid fa-copy"></i> Duplicate Content</span>' : '';

                    card.innerHTML = `
                        <p style="margin-bottom: 10px;">"${review.text}"</p>
                        <div class="badge-container">
                            <span class="badge ${badgePredClass}">${review.prediction}</span>
                            <span class="badge ${badgeSentClass}">Sentiment: ${review.sentiment}</span>
                            ${duplicateBadge}
                        </div>
                    `;
                    reviewsList.appendChild(card);
                });

                resultsSection.style.display = 'block';
            } catch (err) {
                showError(err.message);
            } finally {
                loader.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        });
    }

    function showError(msg) {
        errorMsg.innerText = msg;
        errorMsg.style.display = 'block';
    }
});
