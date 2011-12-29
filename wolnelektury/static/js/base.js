(function($) {
    $(function() {


$('#themes-list-toggle').click(function(event) {
    event.preventDefault();
    $('#themes-list').toggle('slow');
});


$('.open-player').click(function(event) {
    event.preventDefault();
    window.open($(this).attr('href'),
        'player',
        'width=420, height=500'
        );
});


    });
})(jQuery)

