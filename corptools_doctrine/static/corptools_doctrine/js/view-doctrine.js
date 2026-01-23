/* global aaCorptoolsDoctrineSettings, populateCategoryFilter, ClipboardJS, fetchGet, _bootstrapTooltip, _bootstrapPopover, DataTable */

$(document).ready(function() {
    /**
     * Table :: IDs
     */
    const doctrineTable = $('#doctrine-table');

    /**
     * Modal :: IDs
     */
    const modalRequestDoctrineSkills = $('#corptools-request-doctrine-skills');

    fetchGet({
        url: aaCorptoolsDoctrineSettings.url.Doctrine,
    })
        .then((data) => {
            if (data) {
                /**
                 * Table :: Doctrine
                 * Initialize DataTable for Doctrine Table
                 * @type {*|jQuery}
                 */
                const doctrineDataTable = new DataTable(doctrineTable, {
                    data: data,
                    language: aaCorptoolsDoctrineSettings.dataTables.language,
                    layout: aaCorptoolsDoctrineSettings.dataTables.layout,
                    ordering: aaCorptoolsDoctrineSettings.dataTables.ordering,
                    columnControl: aaCorptoolsDoctrineSettings.dataTables.columnControl,
                    order: [[0, 'asc']],
                    pageLength: 25,
                    columnDefs: [
                        {
                            orderable: false,
                            targets: [0],
                            columnControl: [
                                {target: 0, content: []},
                                {target: 1, content: []}
                            ]
                        },
                    ],
                    columns: [
                        {
                            data: 'character',
                            render: function (data, type) {
                                if (type === 'display') {
                                    return `<img width="32" height="32" class="rounded-circle" src="https://images.evetech.net/characters/${data.character_id}/portrait?size=256"> ${data.character_name}`;
                                }
                                return data.character_name;
                            }
                        },
                        {
                            data: 'doctrines',
                            render: function (data, type, row) {
                                if (type === 'display') {
                                    // Convert doctrines object to array and sort by order
                                    const doctrineArray = Object.entries(data).map(([doctrineName, doctrine]) => ({
                                        name: doctrineName,
                                        doctrine: doctrine,
                                        order: doctrine.order || 999 // Default high order for items without order
                                    }));

                                    // Sort by order (ascending)
                                    doctrineArray.sort((a, b) => a.order - b.order);

                                    // Render sorted doctrines as a list of divs with flex layout
                                    let html = '<div class="d-flex flex-wrap gap-2">';
                                    doctrineArray.forEach(({ name, doctrine }) => {
                                        // Add category information to the HTML if it exists
                                        let doctrineHtml = doctrine.html || name;
                                        if (doctrine.category) {
                                            doctrineHtml = doctrineHtml.replace(
                                                'data-doctrine="' + name + '"',
                                                'data-doctrine="' + name + '" data-category="' + doctrine.category + '"'
                                            );
                                        }
                                        html += doctrineHtml;
                                    });
                                    html += '</div>';
                                    return html;
                                }
                                return Object.keys(data).join(' ');
                            }
                        },
                    ],
                    initComplete: function() {
                        const dt = doctrineTable.DataTable();
                        _bootstrapTooltip({selector: '#doctrine-table' });

                        // Store all data for category filtering using jQuery data
                        doctrineTable.data('originalData', data);

                        // Populate category filter dropdown
                        populateCategoryFilter(data, dt);
                    },
                    drawCallback: function () {
                        const dt = doctrineTable.DataTable();
                        _bootstrapTooltip({selector: '#doctrine-table' });

                        // Add clipboard functionality for missing skills (red buttons)
                        setTimeout(() => {
                            $('.doctrine-item').each(function() {
                                const doctrineDiv = $(this);
                                const copyButton = doctrineDiv.find('button[id^="copy-"]');

                                if (copyButton.length && copyButton.hasClass('btn-danger')) {
                                    const doctrineName = doctrineDiv.attr('data-doctrine');

                                    // Find the doctrine data from the table row
                                    const row = doctrineDiv.closest('tr');
                                    const rowData = dt.row(row).data();

                                    if (rowData && rowData.doctrines && rowData.doctrines[doctrineName]) {
                                        const doctrine = rowData.doctrines[doctrineName];
                                        const missingSkills = [];

                                        if (doctrine.skills) {
                                            Object.keys(doctrine.skills).forEach(skillName => {
                                                const skillLevel = doctrine.skills[skillName];
                                                missingSkills.push(`${skillName} ${skillLevel}`);
                                            });
                                        }

                                        const clipboardText = missingSkills.join('\n');
                                        copyButton.attr('data-clipboard-text', clipboardText);

                                        // Initialize ClipboardJS if not already initialized
                                        if (!copyButton.data('clipboard-initialized')) {
                                            new ClipboardJS(copyButton[0]).on('success', function(e) {
                                                const originalIcon = copyButton.html();
                                                const originalClass = copyButton.attr('class');

                                                copyButton.html('<i class="fa-solid fa-check"></i>');
                                                copyButton.removeClass('btn-danger').addClass('btn-success');

                                                setTimeout(() => {
                                                    copyButton.html(originalIcon);
                                                    copyButton.attr('class', originalClass);
                                                }, 1500);

                                                e.clearSelection();
                                            });

                                            copyButton.data('clipboard-initialized', true);
                                        }
                                    }
                                }
                            });
                        }, 100);
                    },
                });
            }
        })
        .catch((error) => {
            console.error('Error fetching doctrine data:', error);
        });

    /**
     * Modal :: Skilllist
     * Open Skilllist Modal for Skills Viewing
     * On Open send a request to the API Endpoint and load the content
     */
    modalRequestDoctrineSkills.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');

        // Load content via Fetch API
        const content = modalRequestDoctrineSkills.find('#modal-ajax-content');
        fetchGet({
            url: url,
            responseIsJson: false,
        })
            .then((data) => {
                if (data) {
                    content.html(data);
                }
            })
            .catch((error) => {
                console.error('Error fetching missing skills data:', error);
                content.html('<div class="alert alert-danger" role="alert">An error occurred while loading the missing skills.</div>');
            });
    }).on('hide.bs.modal', () => {
        modalRequestDoctrineSkills.find('#modal-button-cancel-request').unbind('click');
    });
});
