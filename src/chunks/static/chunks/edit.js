(function() {

    // is we admin?
    function showEditLinks() {
        $("a.admin-link").remove();

        $('span[data-edit]').each(function() {
            e = $(this).offset();
            a = $('<a class="admin-link" target="admin">\u270e</a>');
            a.attr('href', '/admin/' + $(this).attr('data-edit') + '/change/');
            a.offset(e);
            a.appendTo(document.body)
        });
    }

    $('.edit-links-toggle').on('click', function() {
        showEditLinks();
        return false;
    })
    
})()
