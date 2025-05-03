/**
 * DataTables Extensions
 * Adds column resizing and text wrapping functionality to DataTables
 */

// Wait for document ready and then initialize after a delay
$(document).ready(function() {
    // Detect Chrome browser
    const isChrome = navigator.userAgent.indexOf("Chrome") !== -1 &&
                   navigator.userAgent.indexOf("Edg") === -1 && // Not Edge
                   navigator.userAgent.indexOf("OPR") === -1;   // Not Opera

    // Apply immediate basic styling to make tables look better while loading
    applyImmediateTableStyling();

    // Apply Chrome-specific fixes if needed
    if (isChrome) {
        applyChromeSpecificFixes();
    }

    // Wait a bit for DataTables to fully initialize
    setTimeout(function() {
        console.log('Initializing DataTables extensions...');

        // Make sure DataTables are properly initialized
        initializeDataTables();

        // Enable column resizing for all DataTables
        enableColumnResizing();

        // Enable text wrapping for all DataTables
        enableTextWrapping();

        // Load saved column widths
        loadSavedColumnWidths();

        // Apply additional Chrome-specific fixes after initialization if needed
        if (isChrome) {
            setTimeout(function() {
                applyChromeSpecificFixes();
            }, 500);
        }
    }, 1000); // Increased delay to ensure DataTables are fully initialized

    // Re-initialize when tabs are changed (for multi-tab interfaces)
    $('a[data-toggle="tab"]').on('shown.bs.tab', function() {
        setTimeout(function() {
            console.log('Tab changed, reinitializing DataTables extensions...');
            enableColumnResizing();
            enableTextWrapping();
            loadSavedColumnWidths();

            // Apply Chrome-specific fixes after tab change if needed
            if (isChrome) {
                applyChromeSpecificFixes();
            }
        }, 300);
    });

    // Watch for new DataTables being initialized
    $(document).on('init.dt', function(e) {
        const table = $(e.target).closest('table.dataTable');
        if (table.length) {
            console.log('New DataTable initialized:', table.attr('id') || 'unnamed');
            setTimeout(function() {
                enableColumnResizing();
                enableTextWrapping();
                loadSavedColumnWidths();

                // Apply Chrome-specific fixes for new tables if needed
                if (isChrome) {
                    applyChromeSpecificFixes();
                }
            }, 100);
        }
    });

    // Listen for DataTables events to reapply resizing after table updates
    $(document).on('draw.dt', function(e) {
        const table = $(e.target).closest('table.dataTable');
        if (table.length) {
            console.log('Table redrawn, reapplying column resizing:', table.attr('id') || 'unnamed');
            setTimeout(function() {
                // Temporarily add a class to prevent transitions during redraw
                table.addClass('dt-redrawing');

                // Add CSS to prevent transitions during redraw
                const tempStyle = document.createElement('style');
                tempStyle.innerHTML = `
                    .dt-redrawing,
                    .dt-redrawing th,
                    .dt-redrawing td {
                        transition: none !important;
                        animation: none !important;
                    }
                `;
                document.head.appendChild(tempStyle);

                // Reapply column widths from localStorage
                const pagePath = window.location.pathname;
                const tableId = table.attr('id') || 'dataTable-' + $('table.dataTable').index(table);
                const storageKey = 'dt_colwidths_' + pagePath + '_' + tableId;

                const savedWidths = localStorage.getItem(storageKey);
                if (savedWidths) {
                    try {
                        const widths = JSON.parse(savedWidths);
                        table.find('th').each(function(colIndex) {
                            if (widths[colIndex]) {
                                const width = parseInt(widths[colIndex]);
                                if (width && width > 0) {
                                    // Apply width with !important to prevent elastic effect
                                    $(this).attr('style', `width: ${width}px !important; min-width: ${width}px !important; max-width: ${width}px !important;`);

                                    // Apply to all cells in this column
                                    const colSelector = `.col-${colIndex}`;
                                    table.find(colSelector).attr('style', `width: ${width}px !important; min-width: ${width}px !important; max-width: ${width}px !important;`);
                                }
                            }
                        });

                        // Disable auto width if using DataTables
                        if ($.fn.dataTable.isDataTable(table)) {
                            try {
                                const dt = table.DataTable();
                                if (dt.settings) {
                                    dt.settings()[0].oFeatures.bAutoWidth = false;
                                }
                            } catch (err) {
                                console.error('Error configuring DataTable:', err);
                            }
                        }
                    } catch (e) {
                        console.error('Error reapplying column widths:', e);
                    }
                } else {
                    // If no saved widths, apply default column widths
                    applyDefaultColumnWidths(table);
                }

                // Make sure resize handles are present
                if (!table.find('.column-resize-handle').length) {
                    enableColumnResizing();
                }

                // Apply Chrome-specific fixes if needed
                if (isChrome) {
                    applyChromeSpecificFixes();
                }

                // Remove the temporary class after a short delay
                setTimeout(function() {
                    table.removeClass('dt-redrawing');
                    // Remove the temporary style element
                    if (tempStyle.parentNode) {
                        tempStyle.parentNode.removeChild(tempStyle);
                    }
                }, 100);
            }, 100);
        }
    });
});

/**
 * Makes sure DataTables are properly initialized
 */
function initializeDataTables() {
    // Force DataTables to adjust columns for all tables
    $('table.dataTable').each(function() {
        const table = $(this);
        if ($.fn.dataTable.isDataTable(table)) {
            try {
                const dt = table.DataTable();

                // Configure DataTable for better resizing support
                if (dt.settings) {
                    const settings = dt.settings()[0];

                    // Always disable auto width to prevent elastic effect
                    settings.oFeatures.bAutoWidth = false;

                    // Disable column auto-sizing
                    if (settings.aoColumns) {
                        settings.aoColumns.forEach(function(column) {
                            column.sWidth = column.sWidth || column._sManualType || null;
                            column.bAutoWidth = false;
                        });
                    }

                    // Get saved widths or apply defaults
                    const pagePath = window.location.pathname;
                    const tableId = table.attr('id') || 'dataTable-' + $('table.dataTable').index(table);
                    const storageKey = 'dt_colwidths_' + pagePath + '_' + tableId;
                    const savedWidths = localStorage.getItem(storageKey);

                    if (savedWidths) {
                        // Apply saved widths
                        try {
                            const widths = JSON.parse(savedWidths);
                            table.find('th').each(function(colIndex) {
                                if (widths[colIndex]) {
                                    const width = parseInt(widths[colIndex]);
                                    if (width && width > 0) {
                                        $(this).css('width', width + 'px');

                                        // Set width in DataTables settings to prevent auto-adjustment
                                        if (settings.aoColumns && settings.aoColumns[colIndex]) {
                                            settings.aoColumns[colIndex].sWidth = width + 'px';
                                        }
                                    }
                                }
                            });
                        } catch (e) {
                            console.error('Error applying saved widths:', e);
                            // Fall back to default widths
                            applyDefaultColumnWidths(table);
                        }
                    } else {
                        // Apply default column widths for better initial appearance
                        applyDefaultColumnWidths(table);
                    }
                }

                // Add column classes for easier selection
                table.find('tr').each(function() {
                    $(this).find('th, td').each(function(cellIndex) {
                        $(this).addClass(`col-${cellIndex}`);
                    });
                });

                console.log('Initialized DataTable:', table.attr('id') || 'unnamed');
            } catch (err) {
                console.error('Error initializing DataTable:', err);
            }
        } else {
            console.log('Table is not a DataTable:', table.attr('id') || 'unnamed');
        }
    });
}

/**
 * Applies default column widths for better initial appearance
 */
function applyDefaultColumnWidths(table) {
    // Skip on allocation page
    // if (window.location.pathname === '/allocation') {
    //     return;
    // }

    console.log('Applying default column widths for table:', table.attr('id') || 'unnamed');

    // Default widths based on column type/content
    const defaultWidths = {};

    // Set default widths based on page type
    if (window.location.pathname.includes('instances') || window.location.pathname === '/list-all-instances') {
        // Instances page default column widths
        defaultWidths[0] = 150; // Project
        defaultWidths[1] = 200; // ID
        defaultWidths[2] = 150; // Name
        defaultWidths[3] = 80;  // Status
        defaultWidths[4] = 80;  // Power State
        defaultWidths[5] = 150; // Networks
        defaultWidths[6] = 150; // Image Name
        defaultWidths[7] = 150; // Flavor Name
        defaultWidths[8] = 80;  // Host
        defaultWidths[9] = 60;  // Tier
        defaultWidths[10] = 60; // vCPU
        defaultWidths[11] = 60; // RAM
        defaultWidths[12] = 300; // Attached Volumes
        defaultWidths[13] = 100; // Total Disk
    } else if (window.location.pathname.includes('volumes') || window.location.pathname === '/volumes') {
        // Volumes page default column widths
        defaultWidths[0] = 200; // ID
        defaultWidths[1] = 150; // Name
        defaultWidths[2] = 80;  // Status
        defaultWidths[3] = 80;  // Size
        defaultWidths[4] = 300; // Attached to
    } else if (window.location.pathname.includes('flavors') || window.location.pathname === '/list-all-flavors') {
        // Flavors page default column widths
        defaultWidths[0] = 150; // ID
        defaultWidths[1] = 150; // Name
        defaultWidths[2] = 80;  // vCPUs
        defaultWidths[3] = 80;  // RAM
        defaultWidths[4] = 80;  // Disk
        defaultWidths[5] = 80;  // Ephemeral
        defaultWidths[6] = 80;  // Swap
        defaultWidths[7] = 80;  // RX/TX Factor
        defaultWidths[8] = 80;  // Public
    }

    // Get DataTable instance and settings if available
    let dt = null;
    let settings = null;
    if ($.fn.dataTable.isDataTable(table)) {
        try {
            dt = table.DataTable();
            if (dt.settings) {
                settings = dt.settings()[0];
            }
        } catch (err) {
            console.error('Error getting DataTable instance:', err);
        }
    }

    // Apply default widths with !important to prevent elastic effect
    table.find('th').each(function(index) {
        const th = $(this);
        if (defaultWidths[index]) {
            const width = defaultWidths[index];

            // Apply width with !important to header
            th.attr('style', `width: ${width}px !important; min-width: ${width}px !important; max-width: ${width}px !important;`);

            // Apply to all cells in this column with !important
            const colSelector = `.col-${index}`;
            table.find(colSelector).attr('style', `width: ${width}px !important; min-width: ${width}px !important; max-width: ${width}px !important;`);

            // Set width in DataTables settings to prevent auto-adjustment
            if (settings && settings.aoColumns && settings.aoColumns[index]) {
                settings.aoColumns[index].sWidth = width + 'px';
                settings.aoColumns[index].bAutoWidth = false;
            }
        }
    });

    // Disable column auto-adjustment to prevent elastic effect
    if (dt) {
        try {
            // Prevent DataTables from adjusting columns automatically
            dt.settings()[0].oFeatures.bAutoWidth = false;

            // Apply the changes without triggering elastic effect
            dt.columns.adjust().draw(false);
        } catch (err) {
            console.error('Error applying column settings:', err);
        }
    }

    // Save these widths to localStorage to maintain consistency
    saveColumnWidths(table);
}

/**
 * Loads saved column widths from localStorage except on allocation page
 */
function loadSavedColumnWidths() {
    // Skip loading saved widths on allocation page
    // if (window.location.pathname === '/allocation') {
    //     console.log('Skipping loading saved column widths on allocation page');
    //     return;
    // }

    console.log('Loading saved column widths...');

    // Get current page path to use as part of the storage key
    const pagePath = window.location.pathname;

    // Apply to all tables
    $('table.dataTable').each(function(tableIndex) {
        const table = $(this);
        const tableId = table.attr('id') || 'dataTable-' + tableIndex;
        const storageKey = 'dt_colwidths_' + pagePath + '_' + tableId;

        console.log('Loading widths for table:', tableId, 'with key:', storageKey);

        // Try to get saved widths
        const savedWidths = localStorage.getItem(storageKey);
        if (savedWidths) {
            try {
                const widths = JSON.parse(savedWidths);
                console.log('Found saved widths:', widths);

                // First, add column classes to all cells for easier selection
                table.find('tr').each(function() {
                    $(this).find('th, td').each(function(cellIndex) {
                        $(this).addClass(`col-${cellIndex}`);
                    });
                });

                // Get DataTable instance and settings if available
                let dt = null;
                let settings = null;
                if ($.fn.dataTable.isDataTable(table)) {
                    try {
                        dt = table.DataTable();
                        if (dt.settings) {
                            settings = dt.settings()[0];
                            // Disable auto width to prevent elastic effect
                            settings.oFeatures.bAutoWidth = false;
                        }
                    } catch (err) {
                        console.error('Error getting DataTable instance:', err);
                    }
                }

                // Apply saved widths with !important to prevent DataTables from overriding
                table.find('th').each(function(colIndex) {
                    if (widths[colIndex]) {
                        const width = parseInt(widths[colIndex]);
                        if (width && width > 0) {
                            // Apply to header and all cells in this column with !important
                            const colSelector = `.col-${colIndex}`;
                            table.find(colSelector).attr('style', `width: ${width}px !important; min-width: ${width}px !important; max-width: ${width}px !important;`);

                            // Set width in DataTables settings to prevent auto-adjustment
                            if (settings && settings.aoColumns && settings.aoColumns[colIndex]) {
                                settings.aoColumns[colIndex].sWidth = width + 'px';
                                settings.aoColumns[colIndex].bAutoWidth = false;
                            }
                        }
                    }
                });

                // Apply the changes without triggering elastic effect
                if (dt) {
                    try {
                        // Use draw(false) to prevent full redraw which can cause elastic effect
                        dt.columns.adjust().draw(false);
                    } catch (err) {
                        console.error('Error applying column settings:', err);
                    }
                }
            } catch (e) {
                console.error('Error loading saved column widths:', e);
                // Fall back to default widths
                applyDefaultColumnWidths(table);
            }
        } else {
            console.log('No saved widths found for table:', tableId);
            // Apply default column widths for better initial appearance
            applyDefaultColumnWidths(table);
        }
    });
}

/**
 * Resets all column widths to their default values
 */
function resetAllColumnWidths(table) {
    console.log('Resetting all column widths for table:', table.attr('id') || 'unnamed');

    // Temporarily add a class to prevent transitions during reset
    table.addClass('dt-resetting');

    // Add CSS to prevent transitions during reset
    const style = document.createElement('style');
    style.innerHTML = `
        .dt-resetting,
        .dt-resetting th,
        .dt-resetting td {
            transition: none !important;
            animation: none !important;
        }
    `;
    document.head.appendChild(style);

    // Find all columns by their class
    for (let i = 0; i < 100; i++) { // Assuming no more than 100 columns
        const colSelector = `.col-${i}`;
        const colElements = table.find(colSelector);

        if (colElements.length > 0) {
            // Remove inline styles that set width
            colElements.removeAttr('style');
        } else {
            // No more columns found
            break;
        }
    }

    // Clear saved widths from localStorage
    const pagePath = window.location.pathname;
    const tableId = table.attr('id') || 'dataTable-' + $('table.dataTable').index(table);
    const storageKey = 'dt_colwidths_' + pagePath + '_' + tableId;
    localStorage.removeItem(storageKey);

    // Get DataTable instance if available
    let dt = null;
    if ($.fn.dataTable.isDataTable(table)) {
        try {
            dt = table.DataTable();

            // Disable auto width to prevent elastic effect
            if (dt.settings) {
                dt.settings()[0].oFeatures.bAutoWidth = false;
            }
        } catch (err) {
            console.error('Error getting DataTable instance:', err);
        }
    }

    // Apply default column widths for better appearance
    applyDefaultColumnWidths(table);

    // Apply the changes without triggering elastic effect
    if (dt) {
        try {
            // Use draw(false) to prevent full redraw which can cause elastic effect
            dt.columns.adjust().draw(false);
        } catch (err) {
            console.error('Error applying column settings:', err);
        }
    }

    // Force browser reflow
    void table[0].offsetHeight;

    // Remove the temporary class after a short delay
    setTimeout(function() {
        table.removeClass('dt-resetting');
        // Remove the temporary style element
        if (style.parentNode) {
            style.parentNode.removeChild(style);
        }
    }, 100);
}

/**
 * Enables column resizing for all DataTables except on allocation page
 */
function enableColumnResizing() {
    // Skip resizing on allocation page
    // if (window.location.pathname === '/allocation') {
    //     console.log('Skipping column resizing on allocation page');
    //     return;
    // }

    console.log('Enabling column resizing...');

    // Add CSS for resizable columns
    const style = document.createElement('style');
    style.innerHTML = `
        /* Force table layout to be fixed for resizing to work properly */
        table.dataTable.resizable {
            table-layout: fixed !important;
            width: 100% !important;
            border-collapse: separate !important;
            border-spacing: 0 !important;
        }

        /* Prevent DataTables from overriding our column widths */
        table.dataTable.resizable th,
        table.dataTable.resizable td {
            box-sizing: border-box !important;
        }

        /* Ensure table container allows horizontal scrolling */
        .dataTables_wrapper {
            overflow-x: auto !important;
        }

        /* Header styling */
        table.dataTable.resizable th {
            position: relative;
            overflow: visible !important;
            min-width: 50px;
            box-sizing: border-box;
        }

        /* Cell styling */
        table.dataTable.resizable td {
            overflow: hidden;
            text-overflow: ellipsis;
            word-wrap: break-word;
            box-sizing: border-box;
        }

        /* Resize handle */
        .column-resize-handle {
            position: absolute;
            top: 0;
            right: 0;
            width: 10px;
            height: 100%;
            cursor: col-resize;
            z-index: 100;
        }

        /* Show a subtle indicator on hover */
        .column-resize-handle:after {
            content: '';
            position: absolute;
            top: 0;
            right: 4px;
            width: 2px;
            height: 100%;
            background-color: transparent;
            transition: background-color 0.2s;
        }

        .column-resize-handle:hover,
        .column-resize-handle.resizing {
            background-color: rgba(0, 0, 0, 0.05);
        }

        .column-resize-handle:hover:after,
        .column-resize-handle.resizing:after {
            background-color: var(--primary-light);
        }

        [data-theme='dark'] .column-resize-handle:hover,
        [data-theme='dark'] .column-resize-handle.resizing {
            background-color: rgba(255, 255, 255, 0.1);
        }

        [data-theme='dark'] .column-resize-handle:hover:after,
        [data-theme='dark'] .column-resize-handle.resizing:after {
            background-color: var(--primary-light);
        }

        .column-resize-handle.resizing {
            height: 100vh;
            position: fixed;
        }
    `;
    document.head.appendChild(style);

    // Apply to all DataTables
    $('table.dataTable').each(function() {
        const table = $(this);
        const tableId = table.attr('id') || 'dataTable';
        console.log('Processing table:', tableId);

        // Add resizable class
        table.addClass('resizable');

        // Remove any existing resize handles to avoid duplicates
        table.find('.column-resize-handle').remove();

        // Add reset button if it doesn't exist
        const tableWrapper = table.closest('.dataTables_wrapper');
        if (tableWrapper.length && !tableWrapper.find('.dt-reset-columns').length) {
            // Create reset button
            const resetButton = $('<button class="dt-reset-columns btn btn-sm btn-outline-secondary" title="Fix or reset column widths">Fix/Reset Columns</button>');

            // Add button to the table controls
            const buttonContainer = tableWrapper.find('.dataTables_filter');
            if (buttonContainer.length) {
                resetButton.css({
                    'margin-right': '10px',
                    'float': 'right'
                });
                buttonContainer.prepend(resetButton);
            } else {
                // If no filter exists, create a container
                const container = $('<div class="dt-buttons"></div>');
                container.css({
                    'margin-bottom': '10px',
                    'text-align': 'right'
                });
                container.append(resetButton);
                tableWrapper.prepend(container);
            }

            // Add click handler
            resetButton.on('click', function(e) {
                e.preventDefault();
                resetAllColumnWidths(table);
            });
        }

        // Add resize handles to all table headers
        table.find('th').each(function(index) {
            const th = $(this);
            const columnIndex = index;

            // Create resize handle with updated hover text
            const handle = $('<div class="column-resize-handle" title="Drag to resize column width"></div>');
            th.append(handle);

            // Drag to resize column
            handle.on('mousedown', function(e) {
                e.stopPropagation();
                e.preventDefault();

                // Get initial width and position
                const startX = e.pageX;
                const startWidth = th.outerWidth();

                console.log('Resize started:', columnIndex, 'Initial width:', startWidth);

                // Add resizing class
                handle.addClass('resizing');

                // Create overlay to capture mouse events
                const overlay = $('<div class="resize-overlay" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; cursor: col-resize;"></div>');
                $('body').append(overlay);

                // Handle mouse move
                overlay.on('mousemove', function(e) {
                    // Calculate new width
                    const diff = e.pageX - startX;
                    const newWidth = startWidth + diff;

                    // Apply minimum width
                    if (newWidth >= 50) {
                        // Force column width with !important to prevent DataTables from overriding
                        th.attr('style', `width: ${newWidth}px !important; min-width: ${newWidth}px !important; max-width: ${newWidth}px !important;`);

                        // Apply to all cells in this column to maintain consistency
                        if ($.fn.dataTable.isDataTable(table)) {
                            try {
                                // Get all cells in this column and set their width
                                const colSelector = `.col-${columnIndex}`;

                                // Add class to cells if not already present
                                if (!table.find(`td${colSelector}`).length) {
                                    table.find('tr').each(function() {
                                        $(this).find(`td:eq(${columnIndex}), th:eq(${columnIndex})`).addClass(`col-${columnIndex}`);
                                    });
                                }

                                // Set width on all cells in this column with !important
                                table.find(colSelector).attr('style', `width: ${newWidth}px !important; min-width: ${newWidth}px !important; max-width: ${newWidth}px !important;`);

                                // Get DataTable instance and settings
                                const dt = table.DataTable();
                                if (dt.settings) {
                                    const settings = dt.settings()[0];

                                    // Disable auto width to prevent elastic effect
                                    settings.oFeatures.bAutoWidth = false;

                                    // Set width in DataTables settings to prevent auto-adjustment
                                    if (settings.aoColumns && settings.aoColumns[columnIndex]) {
                                        settings.aoColumns[columnIndex].sWidth = newWidth + 'px';
                                        settings.aoColumns[columnIndex].bAutoWidth = false;
                                    }
                                }
                            } catch (err) {
                                console.error('Error setting column width:', err);
                            }
                        }
                    }
                });

                // Add keyboard escape handler to cancel resize
                $(document).on('keydown.resize', function(e) {
                    if (e.key === 'Escape') {
                        handle.removeClass('resizing');
                        overlay.remove();
                        $(document).off('keydown.resize');
                    }
                });

                // Handle mouse up - attach to document to ensure it catches all mouse up events
                $(document).on('mouseup.resize', function() {
                    // Clean up all event handlers
                    $(document).off('mousemove.resize mouseup.resize keydown.resize');

                    // Remove resizing class and overlay
                    handle.removeClass('resizing');
                    overlay.remove();

                    // Save column widths
                    saveColumnWidths(table);

                    // Disable auto width for this table
                    if ($.fn.dataTable.isDataTable(table)) {
                        try {
                            const dt = table.DataTable();

                            // Disable auto width
                            if (dt.settings) {
                                dt.settings()[0].oFeatures.bAutoWidth = false;
                            }

                            // Prevent DataTables from adjusting this column
                            dt.columns.adjust().draw(false);
                        } catch (err) {
                            console.error('Error adjusting columns:', err);
                        }
                    }

                    console.log('Resize completed:', columnIndex, 'New width:', th.outerWidth());

                    // Force browser reflow to ensure changes are applied
                    void table[0].offsetHeight;
                });

                // Also handle mouse leave on the overlay as a backup
                overlay.on('mouseleave', function() {
                    $(document).trigger('mouseup.resize');
                });
            });
        });
    });
}

/**
 * Saves column widths to localStorage
 */
function saveColumnWidths(table) {
    // Get current page path to use as part of the storage key
    const pagePath = window.location.pathname;
    const tableId = table.attr('id') || 'dataTable-' + $('table.dataTable').index(table);
    const storageKey = 'dt_colwidths_' + pagePath + '_' + tableId;

    console.log('Saving widths for table:', tableId, 'with key:', storageKey);

    // Get all column widths
    const widths = [];
    table.find('th').each(function(index) {
        // Try to get width from style attribute first (most accurate for resized columns)
        let width;
        const style = $(this).attr('style');
        if (style && style.includes('width:')) {
            // Extract width from style attribute
            const match = style.match(/width:\s*(\d+)px/i);
            if (match && match[1]) {
                width = parseInt(match[1]);
            }
        }

        // If no width in style, get the actual width
        if (!width) {
            width = $(this).outerWidth();
        }

        widths.push(width);
        console.log('Column', index, 'width:', width);
    });

    // Save to localStorage
    try {
        localStorage.setItem(storageKey, JSON.stringify(widths));
        console.log('Saved column widths:', widths);
    } catch (e) {
        console.error('Error saving column widths:', e);
    }
}

/**
 * Applies immediate styling to tables before DataTables fully initializes
 * This helps prevent the initial unstyled flash of content
 */
function applyImmediateTableStyling() {
    console.log('Applying immediate table styling...');

    // Detect Chrome browser - using a more modern approach
    const isChrome = navigator.userAgent.indexOf("Chrome") !== -1 &&
                   navigator.userAgent.indexOf("Edg") === -1 && // Not Edge
                   navigator.userAgent.indexOf("OPR") === -1;   // Not Opera
    console.log('Browser detection - Chrome:', isChrome);

    // Add CSS for immediate table styling
    const style = document.createElement('style');
    style.innerHTML = `
        /* Immediate table styling to prevent unstyled flash and elastic effect */
        table.dataTable {
            table-layout: fixed !important;
            width: 100% !important;
            transition: none !important;
            ${isChrome ? 'contain: layout style size !important;' : ''}
        }

        /* Prevent elastic effect by disabling transitions and animations */
        table.dataTable,
        table.dataTable th,
        table.dataTable td {
            transition: none !important;
            animation: none !important;
            ${isChrome ? 'contain: layout style size !important;' : ''}
        }

        /* Prevent DataTables from adjusting column widths automatically */
        .dataTables_wrapper {
            overflow-x: auto !important;
            transition: none !important;
            ${isChrome ? 'contain: layout style !important;' : ''}
        }

        /* Ensure table headers don't resize after initial render */
        table.dataTable thead th {
            position: relative;
            box-sizing: border-box !important;
            transition: none !important;
            ${isChrome ? 'contain: layout style size !important;' : ''}
        }

        /* Chrome-specific fixes for elastic effect */
        ${isChrome ? `
        /* Force Chrome to use a specific layout algorithm */
        table.dataTable {
            contain: layout style size !important;
            transform: translateZ(0) !important;
            backface-visibility: hidden !important;
            perspective: 1000px !important;
            will-change: transform !important;
        }

        /* Prevent Chrome from recalculating layout */
        .dataTables_wrapper {
            contain: layout style !important;
            transform: translateZ(0) !important;
        }

        /* Force Chrome to respect fixed widths */
        table.dataTable th,
        table.dataTable td {
            contain: layout style size !important;
            transform: translateZ(0) !important;
            backface-visibility: hidden !important;
        }
        ` : ''}

        /* Default column widths for common pages */
        /* Instances page */
        body[data-page="instances"] table.dataTable th:nth-child(1),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(1) {
            width: 150px !important; /* Project */
        }
        body[data-page="instances"] table.dataTable th:nth-child(2),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(2) {
            width: 200px !important; /* ID */
        }
        body[data-page="instances"] table.dataTable th:nth-child(3),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(3) {
            width: 150px !important; /* Name */
        }
        body[data-page="instances"] table.dataTable th:nth-child(4),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(4) {
            width: 80px !important; /* Status */
        }
        body[data-page="instances"] table.dataTable th:nth-child(5),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(5) {
            width: 80px !important; /* Power State */
        }
        body[data-page="instances"] table.dataTable th:nth-child(6),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(6) {
            width: 150px !important; /* Networks */
        }
        body[data-page="instances"] table.dataTable th:nth-child(7),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(7) {
            width: 150px !important; /* Image Name */
        }
        body[data-page="instances"] table.dataTable th:nth-child(8),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(8) {
            width: 150px !important; /* Flavor Name */
        }
        body[data-page="instances"] table.dataTable th:nth-child(9),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(9) {
            width: 80px !important; /* Host */
        }
        body[data-page="instances"] table.dataTable th:nth-child(10),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(10) {
            width: 60px !important; /* vCPU */
        }
        body[data-page="instances"] table.dataTable th:nth-child(11),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(11) {
            width: 60px !important; /* RAM */
        }
        body[data-page="instances"] table.dataTable th:nth-child(12),
        body[data-page="list-all-instances"] table.dataTable th:nth-child(12) {
            width: 300px !important; /* Attached Volumes */
        }

        /* Volumes page */
        body[data-page="volumes"] table.dataTable th:nth-child(1) {
            width: 200px !important; /* ID */
        }
        body[data-page="volumes"] table.dataTable th:nth-child(2) {
            width: 150px !important; /* Name */
        }
        body[data-page="volumes"] table.dataTable th:nth-child(3) {
            width: 80px !important; /* Status */
        }
        body[data-page="volumes"] table.dataTable th:nth-child(4) {
            width: 80px !important; /* Size */
        }
        body[data-page="volumes"] table.dataTable th:nth-child(5) {
            width: 300px !important; /* Attached to */
        }

        /* Flavors page */
        body[data-page="flavors"] table.dataTable th:nth-child(1),
        body[data-page="list-all-flavors"] table.dataTable th:nth-child(1) {
            width: 150px !important; /* ID */
        }
        body[data-page="flavors"] table.dataTable th:nth-child(2),
        body[data-page="list-all-flavors"] table.dataTable th:nth-child(2) {
            width: 150px !important; /* Name */
        }
        body[data-page="flavors"] table.dataTable th:nth-child(3),
        body[data-page="list-all-flavors"] table.dataTable th:nth-child(3) {
            width: 80px !important; /* vCPUs */
        }
        body[data-page="flavors"] table.dataTable th:nth-child(4),
        body[data-page="list-all-flavors"] table.dataTable th:nth-child(4) {
            width: 80px !important; /* RAM */
        }
        body[data-page="flavors"] table.dataTable th:nth-child(5),
        body[data-page="list-all-flavors"] table.dataTable th:nth-child(5) {
            width: 80px !important; /* Disk */
        }
        body[data-page="flavors"] table.dataTable th:nth-child(6),
        body[data-page="list-all-flavors"] table.dataTable th:nth-child(6) {
            width: 80px !important; /* Ephemeral */
        }
        body[data-page="flavors"] table.dataTable th:nth-child(7),
        body[data-page="list-all-flavors"] table.dataTable th:nth-child(7) {
            width: 80px !important; /* Swap */
        }
        body[data-page="flavors"] table.dataTable th:nth-child(8),
        body[data-page="list-all-flavors"] table.dataTable th:nth-child(8) {
            width: 80px !important; /* RX/TX Factor */
        }
        body[data-page="flavors"] table.dataTable th:nth-child(9),
        body[data-page="list-all-flavors"] table.dataTable th:nth-child(9) {
            width: 80px !important; /* Public */
        }
    `;
    document.head.appendChild(style);

    // Add data-page attribute to body for CSS targeting
    const path = window.location.pathname;
    let pageName = '';

    if (path.includes('instances') || path === '/list-all-instances') {
        pageName = path === '/list-all-instances' ? 'list-all-instances' : 'instances';
    } else if (path.includes('volumes') || path === '/volumes') {
        pageName = 'volumes';
    } else if (path.includes('flavors') || path === '/list-all-flavors') {
        pageName = path === '/list-all-flavors' ? 'list-all-flavors' : 'flavors';
    }

    if (pageName) {
        document.body.setAttribute('data-page', pageName);
    }
}

/**
 * Applies Chrome-specific fixes to prevent elastic effect
 */
function applyChromeSpecificFixes() {
    console.log('Applying Chrome-specific fixes to prevent elastic effect...');

    // Add Chrome-specific CSS
    const style = document.createElement('style');
    style.innerHTML = `
        /* Chrome-specific fixes for elastic effect */
        table.dataTable {
            contain: layout style size !important;
            transform: translateZ(0) !important;
            backface-visibility: hidden !important;
            perspective: 1000px !important;
            will-change: transform !important;
            table-layout: fixed !important;
        }

        /* Prevent Chrome from recalculating layout */
        .dataTables_wrapper {
            contain: layout style !important;
            transform: translateZ(0) !important;
            overflow-x: auto !important;
        }

        /* Force Chrome to respect fixed widths */
        table.dataTable th,
        table.dataTable td {
            contain: layout style size !important;
            transform: translateZ(0) !important;
            backface-visibility: hidden !important;
            box-sizing: border-box !important;
        }

        /* Prevent layout shifts */
        table.dataTable thead,
        table.dataTable tbody,
        table.dataTable tr {
            contain: layout style !important;
        }

        /* Disable animations and transitions */
        table.dataTable *,
        .dataTables_wrapper * {
            animation: none !important;
            transition: none !important;
        }
    `;
    document.head.appendChild(style);

    // Apply hardware acceleration to tables
    $('table.dataTable').each(function() {
        const table = $(this);

        // Force hardware acceleration
        table.css({
            'transform': 'translateZ(0)',
            'backface-visibility': 'hidden',
            'perspective': '1000px',
            'will-change': 'transform',
            'table-layout': 'fixed'
        });

        // Disable auto width if using DataTables
        if ($.fn.dataTable.isDataTable(table)) {
            try {
                const dt = table.DataTable();
                if (dt.settings) {
                    dt.settings()[0].oFeatures.bAutoWidth = false;

                    // Disable column auto-sizing
                    if (dt.settings()[0].aoColumns) {
                        dt.settings()[0].aoColumns.forEach(function(column) {
                            column.bAutoWidth = false;
                        });
                    }
                }
            } catch (err) {
                console.error('Error applying Chrome-specific fixes:', err);
            }
        }
    });

    // Force browser reflow
    void document.body.offsetHeight;
}

/**
 * Enables text wrapping for all DataTables
 */
function enableTextWrapping() {
    console.log('Enabling text wrapping...');

    // Special handling for allocation page (text wrapping only, no resizing)
    const isAllocationPage = window.location.pathname === '/allocation';

    // Apply different styling for allocation page if needed
    if (isAllocationPage) {
        console.log('Applying allocation-specific text wrapping');
    }

    // Add CSS for text wrapping
    const style = document.createElement('style');
    style.innerHTML = `
        /* Text wrapping styles */
        table.dataTable td {
            white-space: normal;
            word-break: break-word;
            transition: none !important;
        }

        table.dataTable th {
            white-space: nowrap;
            transition: none !important;
        }

        table.dataTable th.narrow-column {
            white-space: normal;
            word-break: break-word;
            transition: none !important;
        }

        /* Ensure text doesn't overflow */
        .dataTables_wrapper .dataTables_scroll {
            overflow: visible;
            transition: none !important;
        }

        /* Ensure horizontal scrolling works */
        .dataTables_wrapper .dataTables_scrollBody {
            overflow-x: auto !important;
            transition: none !important;
        }

        /* Prevent elastic effect during rendering */
        .dataTable * {
            animation: none !important;
            transition: none !important;
        }

        /* Reset button styling */
        .dt-reset-columns {
            font-size: 0.8rem;
            padding: 0.25rem 0.5rem;
            margin-right: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .dt-reset-columns:hover {
            background-color: var(--primary-light);
            color: var(--text-on-primary);
        }

        [data-theme='dark'] .dt-reset-columns {
            border-color: var(--border-color);
            color: var(--text-primary);
        }

        [data-theme='dark'] .dt-reset-columns:hover {
            background-color: var(--primary-light);
            color: var(--text-on-primary);
            border-color: var(--primary-light);
        }
    `;
    document.head.appendChild(style);

    // Add event listener to update column classes based on width
    $(window).on('resize.dt-text-wrap', function() {
        $('table.dataTable th').each(function() {
            const th = $(this);
            if (th.outerWidth() < 80) {
                th.addClass('narrow-column');
            } else {
                th.removeClass('narrow-column');
            }
        });
    });

    // Initial check
    $('table.dataTable th').each(function() {
        const th = $(this);
        if (th.outerWidth() < 80) {
            th.addClass('narrow-column');
        }
    });

    // Re-check after a short delay to ensure all tables are fully rendered
    setTimeout(function() {
        $(window).trigger('resize.dt-text-wrap');
    }, 500);

    // Handle theme changes
    $(document).on('themeChanged', function() {
        console.log('Theme changed, updating DataTables styling...');

        // Add theme-init class to disable transitions during theme change
        document.documentElement.classList.add('theme-init');

        // Refresh all tables immediately without transitions
        $('table.dataTable').each(function() {
            const table = $(this);
            table.addClass('dt-redrawing');

            if ($.fn.dataTable.isDataTable(table)) {
                try {
                    // Disable auto width to prevent elastic effect
                    const dt = table.DataTable();
                    if (dt.settings) {
                        dt.settings()[0].oFeatures.bAutoWidth = false;
                    }

                    // Adjust columns without animations
                    dt.columns.adjust();
                } catch (err) {
                    console.error('Error adjusting columns after theme change:', err);
                }
            }
        });

        // Re-enable transitions after a short delay
        setTimeout(function() {
            document.documentElement.classList.remove('theme-init');
            $('table.dataTable').removeClass('dt-redrawing');
        }, 100);
    });
}
