console.log('💥 Global store script loaded');

document.addEventListener('alpine:init', () => {

    Alpine.store('app', {
        name: 'Alex',

    

        

        generateInsights() {
            console.log('✅ generateInsights was called');
            this.name = 'Hatfield';
            alert('generateInsights() called!');
        }
    });

});
