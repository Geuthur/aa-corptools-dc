/* global aaCorptoolsDoctrineSettings, fetchGet, _bootstrapTooltip, _bootstrapPopover, DataTable, fetchPost */

$(document).ready(function() {
    /**
     * Table :: IDs
     */
    const manageTable = $('#manage-table');
    /**
     * Modal :: IDs
     */
    const modalRequestDoctrineSkills = $('#corptools-request-doctrine-skills');
    const modalRequestApprove = $('#corptools-request-skillplan-accept-delete');

    fetchGet({
        url: aaCorptoolsDoctrineSettings.url.Manage,
    })
        .then((data) => {
            if (data) {
                /**
                 * Table :: Manage
                 * Initialize DataTable for Manage Table
                 * @type {*|jQuery}
                 */
                const manageDataTable = new DataTable(manageTable, {
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
                            targets: [1, 5],
                            columnControl: [
                                {target: 0, content: []},
                                {target: 1, content: []}
                            ]
                        },
                    ],
                    columns: [
                        {
                            data: {
                                display: (data) => data.name.html,
                                sort: (data) => data.name.sort,
                                filter: (data) => data.name.sort,
                            }
                        },
                        {
                            data: {
                                display: (data) => data.skills.html,
                                sort: (data) => data.skills.sort,
                                filter: (data) => data.skills.sort,
                            }
                        },
                        {
                            data: {
                                display: (data) => data.active.html,
                                sort: (data) => data.active.sort,
                                filter: (data) => data.active.sort,
                            }
                        },
                        {
                            data: {
                                display: (data) => data.ordering.html,
                                sort: (data) => data.ordering.sort,
                                filter: (data) => data.ordering.sort,
                            }
                        },
                        {
                            data: {
                                display: (data) => data.category.html,
                                sort: (data) => data.category.sort,
                                filter: (data) => data.category.sort,
                            }
                        },
                        {
                            data: {
                                display: (data) => data.actions,
                                sort: (data) => data.actions,
                                filter: (data) => data.actions,
                            }
                        },
                    ],
                    initComplete: function() {
                        _bootstrapTooltip({selector: '#manage-table' });
                    },
                    drawCallback: function () {
                        _bootstrapTooltip({selector: '#manage-table' });
                        _initializeEditTable();
                    }
                });
            }
        })
        .catch((error) => {
            console.error('Error fetching manage data:', error);
        });

    /**
     * Table :: Manage :: Helper Function :: Initialize EditTable
     * Handle initialization of x-editable elements in Manage DataTable
     * @private
     */
    function _initializeEditTable() {
        $('.editable').editable({
            mode: 'inline',
            emptytext: 'Click to edit',
            ajaxOptions: {
                type: 'POST',
                beforeSend: function(xhr, settings) {
                    // Set CSRF token in header
                    xhr.setRequestHeader('X-CSRFToken', aaCorptoolsDoctrineSettings.csrfToken);
                },
                complete: function(xhr, textStatus) {
                    console.log('Response:', xhr.responseText);
                }
            },
            success: function(response, newValue) {
                fetchGet({
                    url: aaCorptoolsDoctrineSettings.url.Manage,
                })
                    .then((newData) => {
                        if (newData) {
                            _reloadManageDataTable(newData);
                        }
                    })
                    .catch((error) => {
                        console.error('Error fetching updated manage data:', error);
                    });
            },
            error: function(xhr, status, error) {
                // Parse JSON response to get the message
                let errorMessage = 'Update failed';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.message || 'Update failed';
                } catch (e) {
                    errorMessage = xhr.responseText || error;
                }

                return errorMessage;
            }
        });

        // Initialize boolean editable (active/inactive)
        $('.editable-boolean').editable({
            mode: 'inline',
            emptytext: 'Click to edit',
            ajaxOptions: {
                type: 'POST',
                beforeSend: function(xhr, settings) {
                    // Set CSRF token in header
                    xhr.setRequestHeader('X-CSRFToken', aaCorptoolsDoctrineSettings.csrfToken);
                },
                complete: function(xhr, textStatus) {
                    fetchGet({
                        url: aaCorptoolsDoctrineSettings.url.Manage,
                    })
                        .then((newData) => {
                            if (newData) {
                                _reloadManageDataTable(newData);
                            }
                        })
                        .catch((error) => {
                            console.error('Error fetching updated manage data:', error);
                        });
                }
            },
            success: function(response, newValue) {
                console.log('Updated active status:', newValue);
                fetchGet({
                    url: aaCorptoolsDoctrineSettings.url.Manage,
                })
                    .then((newData) => {
                        if (newData) {
                            _reloadManageDataTable(newData);
                        }
                    })
                    .catch((error) => {
                        console.error('Error fetching updated manage data:', error);
                    });
            },
            error: function(xhr, status, error) {
                // Parse JSON response to get the message
                let errorMessage = 'Update failed';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMessage = response.message || 'Update failed';
                } catch (e) {
                    errorMessage = xhr.responseText || error;
                }

                return errorMessage;
            }
        });
    }

    /**
     * Table :: Manage :: Helper Function :: Reload DataTable
     * Handle reloading of Manage DataTable with new data
     * @param {Array} newData
     * @private
     */
    function _reloadManageDataTable(newData) {
        const dtManage = manageTable.DataTable();
        dtManage.clear().rows.add(newData).draw();
    }

    /**
     * Modal :: Skilllist Delete
     * Open Confirmation Modal for Skilllist Deletion
     * On Confirmation send a request to the API Endpoint and close the modal
     */
    modalRequestApprove.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('action');

        modalRequestApprove.find('#modal-button-confirm-delete-request').on('click', () => {
            fetchPost({
                url: url,
                csrfToken: aaCorptoolsDoctrineSettings.csrfToken,
            })
                .then((data) => {
                    console.log('Delete response:', data);
                    if (data) {
                        fetchGet({
                            url: aaCorptoolsDoctrineSettings.url.Manage,
                        })
                            .then((newData) => {
                                if (newData) {
                                    _reloadManageDataTable(newData);
                                }
                            })
                            .catch((error) => {
                                console.error('Error fetching updated manage data:', error);
                            });
                        modalRequestApprove.modal('hide');
                    }
                })
                .catch((error) => {
                    console.error(`Error posting delete request: ${error.message}`);
                });
        });
    }).on('hide.bs.modal', () => {
        modalRequestApprove.find('#modal-button-confirm-delete-request').unbind('click');
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
