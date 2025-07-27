document.addEventListener('alpine:init', () => {
    Alpine.store('app', {
        showEstimate: false,
        connectionType: 'hello there!',
        location: { lat: 0.1, lng: 0.1 },
        result: 2,

        // 🧪 Dummy method for now
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
            });

            // Optional: set a UI flag if needed
            this.showEstimate = false; // or true, depending on your design
        }

    });

});