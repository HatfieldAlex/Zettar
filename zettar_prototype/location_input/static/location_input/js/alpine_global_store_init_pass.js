console.log('💥 Global store script loaded');

document.addEventListener('DOMContentLoaded', () => {
    if (window.Alpine) {
        Alpine.store('app', {
            alpine_function() {
                console.log('✅ alpine_function was called');
                alert('generateInsights() called!');
            }
        });
    } else {
        console.error('❌ Alpine is not available on window');
    }
});
