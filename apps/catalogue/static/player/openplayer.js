(function($) {
    $(function() {



$('.open-player').click(function(event) {
    event.preventDefault();
    window.open($(this).attr('href'),
        'player',
        'width=422, height=500, scrollbars=1'
        );
});



    });
})(jQuery);

