function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('alpine:init', () => {

    Alpine.store('app', {
        nearestSubstationName: '',
        nearestSubstationType: '',
        demandApplicationSum: 0,
        demandCapacityMW: 0,
        generationApplicationSum: 0,
        generationCapacityMW: 0,
        showInsights: false,

        generateInsights() {
            console.log('generateInsights() called');
            console.log('Sending to Django:', {
                connection_type: this.connectionType,
                location: this.location
            });

            fetch('/get_nearby_application_data/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') 
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
                console.log('💰 Connection application data received:', data);
                this.nearestSubstationName = data.nearest_substation_name;
                this.nearestSubstationType = data.nearest_substation_type;
                this.demandApplicationSum = data.demand_application_sum;
                this.demandCapacityMW = data.demand_capacity_mw;
                this.generationApplicationSum = data.generation_application_sum;
                this.generationCapacityMW = data.generation_capacity_mw;
                this.showInsights = true;

                Alpine.nextTick(() => {
                    setTimeout(() => {
                        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                    }, 200); 
                });
                            
            })
            .catch(error => {
                console.error('Error fetching estimate:', error);
            });
        }
        
    })
    
});