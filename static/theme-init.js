/**
 * Early Theme Initialization
 * This script runs before the page content is rendered to prevent flash of wrong theme
 */
(function() {
    // Get saved theme or use system preference
    const savedTheme = localStorage.getItem('theme');
    const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const preferredTheme = savedTheme || (systemDarkMode ? 'dark' : 'light');
    
    // Apply theme immediately before any content is rendered
    document.documentElement.setAttribute('data-theme', preferredTheme);
    
    // Add a class to disable all transitions during initial load
    document.documentElement.classList.add('theme-init');
    
    // Remove theme-init class after a short delay to enable smooth transitions
    setTimeout(() => {
        document.documentElement.classList.remove('theme-init');
    }, 100);
})();
