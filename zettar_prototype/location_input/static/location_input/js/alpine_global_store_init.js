document.addEventListener('alpine:init', () => {
    Alpine.store('app', {
        showEstimate: false,
        connectionType: 'hello there!',
        location: { lat: 0.1, lng: 0.1 },
        result: 2,
        connectionCost: null,  // ✅ New variable, initially null

        submitEstimate() {
            console.log('🚀 submitEstimate() called');
            console.log('📦 Sending to Django:', {
                connection_type: this.connectionType,
                location: this.location
            });

            fetch('/get-estimate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    connection_type: this.connectionType,
                    location: this.location
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('💰 Cost estimate received from Django:', data.cost_estimate);
                this.result = data.cost_estimate;
                this.connectionCost = data.cost_estimate;  // ✅ Set connectionCost here
                this.showEstimate = true;
            })
            .catch(error => {
                console.error('❌ Error fetching estimate:', error);
            });
        }
    });
});
