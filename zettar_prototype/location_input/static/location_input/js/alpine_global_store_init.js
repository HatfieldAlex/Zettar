document.addEventListener('alpine:init', () => {
    Alpine.store('app', {
        showEstimate: false,
        connectionType: 'hello there!',
        location: { lat: 0.1, lng: 0.1 },
        result: 2,
        unformattedCost: null,
        GBPFormatCost: '',

        formatGBP(value) {
            return new Intl.NumberFormat('en-UK', {
                style: 'currency',
                currency: 'GBP'
            }).format(value);
        },

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
                this.unformattedCost = data.cost_estimate;
                this.GBPFormatCost = this.formatGBP(data.cost_estimate);
                this.showEstimate = true;

                Alpine.nextTick(() => {
                    setTimeout(() => {
                        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                    }, 200); // wait for transition + rendering
                });
                            



            })
            .catch(error => {
                console.error('❌ Error fetching estimate:', error);
            });
        }
    });
});
