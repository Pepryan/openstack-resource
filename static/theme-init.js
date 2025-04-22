/**
 * Early Theme Initialization
 * This script runs before the page content is rendered to prevent flash of wrong theme
 */
(function() {
    // Get saved theme or use system preference
    const savedTheme = localStorage.getItem('theme');
    const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const prefersDark = savedTheme === 'dark' || (!savedTheme && systemDarkMode);
    
    // Apply theme immediately before any content is rendered
    if (prefersDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
        // Add a class to disable all transitions during initial load
        document.documentElement.classList.add('theme-init');
    }
})();
