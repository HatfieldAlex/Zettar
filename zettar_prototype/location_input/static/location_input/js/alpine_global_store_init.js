document.addEventListener('alpine:init', () => {
    console.log('✅ Alpine store initialized');

    Alpine.store('app', {
        showEstimate: false,
        connectionType: 'hello there!',
        location: { lat: 0.1, lng: 0.1 },
        result: 2,
        unformattedCost: null,
        GBPFormatCost: '',
        nearestSubstationName: null, // Needed for x-show to work

        generateInsights() {
            console.log('🔍 generateInsights() called');
            // Dummy logic for now
            this.nearestSubstationName = 'Dummy Substation A1';
        },

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
                    }, 200);
                });
            })
            .catch(error => {
                console.error('❌ Error fetching estimate:', error);
            });
        },

        
    });
});




// document.addEventListener('alpine:init', () => {
//     Alpine.store('app', {
//         // nearestSubstationName: 'Islington',
//         // demandApplicationSum: 0,
//         // demandCapacityMW: 0,
//         // generationApplicationSum: 0,
//         // generationCapacityMW: 0,

//         generateInsights() {
//             console.log('🧪 vvNasocTest() called - this is a very very nasoc test method');
//         },



//         // generateInsight1s() {
//         //     console.log('🚀 generateInsights() called');
//         //     console.log('📦 Sending to Django:', {
//         //         connection_type: this.connectionType,
//         //         location: this.location
//         //     });

//         //     fetch('/get-estimate/', {
//         //         method: 'POST',
//         //         headers: {
//         //             'Content-Type': 'application/json'
//         //         },
//         //         body: JSON.stringify({
//         //             connection_type: this.connectionType,
//         //             location: this.location
//         //         })
//         //     })
//         //     .then(response => {
//         //         if (!response.ok) {
//         //             throw new Error('Network response was not ok');
//         //         }
//         //         return response.json();
//         //     })
//         //     .then(data => {
//         //         console.log('💰 Connection application data received:', data);
//         //         this.nearestSubstationName = data.nearest_substation_name;
//         //         this.demandApplicationSum = data.demand_application_sum;
//         //         this.demandCapacityMW = data.demand_capacity_mw;
//         //         this.generationApplicationSum = data.generation_application_sum;
//         //         this.generationCapacityMW = data.generation_capacity_mw;

//         //         console.log('✅ Alpine store updated with estimate data:');


//         //         Alpine.nextTick(() => {
//         //             setTimeout(() => {
//         //                 window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
//         //             }, 200); 
//         //         });
                            

//         //     })
//         //     .catch(error => {
//         //         console.error('❌ Error fetching estimate:', error);
//         //     });
//         // }
//     });
// });