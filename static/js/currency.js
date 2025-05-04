document.querySelectorAll('.buy-button').forEach(button => {
    button.addEventListener('click', () => {
        const amount = button.dataset.amount;

        fetch('/get_currency', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() if csrf_token else "" }}'
            },
            body: JSON.stringify({ amount: amount })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Successfully got $${data.amount}!`);
                document.querySelector('.currency').textContent = `$${Number(data.new_balance).toLocaleString()}`;
            } else {
                alert(data.message || 'Purchase failed.');
            }
        });
    });
});
