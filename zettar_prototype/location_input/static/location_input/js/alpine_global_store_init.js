document.addEventListener('alpine:init', () => {
  Alpine.store('app', {
    showEstimate: false,
    connectionType: 'hello there!',
    location: { lat: 0.1, lng: 0.1 },
    result: 2
  });
});

console.log('🔍 [Alpine Store: app]', Alpine.store('app'));
