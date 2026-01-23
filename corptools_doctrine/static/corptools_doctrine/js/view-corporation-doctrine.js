/* global aaCorptoolsDoctrineSettings, DataTable, populateCategoryFilter, filterDoctrineItems, ClipboardJS, fetchGet, _bootstrapTooltip, _bootstrapPopover */

// Global variables for cross-file access
window.allTableData = [];
window.tableSkilllist = null;

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
                            render: function (data, type, row) {
                                if (type === 'display') {
                                    let infoIcon = '';

                                    if (row.alts && row.alts.length > 0) {
                                        const altsContent = row.alts.map(alt =>
                                            `<div class="d-flex align-items-center mb-1">
                                            <img width="24" height="24" class="rounded-circle me-2" src="https://images.evetech.net/characters/${alt.character_id}/portrait?size=256">
                                            <span>${alt.character_name}</span>
                                        </div>`
                                        ).join('');

                                        // Escape HTML properly for data attribute
                                        const escapedContent = altsContent.replace(/"/g, '&quot;').replace(/'/g, '&#39;');

                                        infoIcon = `<i class="fa-solid fa-info-circle"
                                                data-character-id="${data.character_id}"
                                                data-bs-toggle="popover"
                                                data-bs-popover="aa-corptools-doctrine"
                                                data-bs-trigger="hover"
                                                data-bs-html="true"
                                                data-bs-content="${escapedContent}"
                                                title="Included Alts"
                                                style="cursor: pointer;"></i>`;
                                    }

                                    return `
                                    <img width="32" height="32" class="rounded-circle" src="https://images.evetech.net/characters/${data.character_id}/portrait?size=256">
                                    ${data.character_name}
                                    ${infoIcon}
                                `;
                                }
                                // For sorting/filtering, return character name and alt names
                                const altNames = row.alts ? row.alts.map(alt => alt.character_name).join(' ') : '';
                                return `${data.character_name} ${altNames}`;
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
                        _bootstrapPopover({selector: '#doctrine-table' });

                        // Store all data for category filtering using jQuery data
                        doctrineTable.data('originalData', data);

                        // Populate category filter dropdown
                        populateCategoryFilter(data, dt);
                    },
                    drawCallback: function () {
                        _bootstrapTooltip({selector: '#doctrine-table' });
                        _bootstrapPopover({selector: '#doctrine-table' });
                        // Replace clipboard icons after each draw
                        $('.fa-copy').removeClass('fa-copy').addClass('fa-xmark');

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
