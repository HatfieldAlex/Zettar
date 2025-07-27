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

        fetch('/estimate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                connection_type: this.connectionType,
                location: this.location
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('✅ Response from server:', data);
            this.result = data.estimate ?? 'No estimate returned';
            this.showEstimate = true;
        })
        .catch(error => {
            console.error('❌ Server error:', error);
            this.result = 'Error generating estimate';
            this.showEstimate = true;
        });
    }

    });

    console.log('🔍 [Alpine Store: app]', Alpine.store('app'));
});
