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


        $('.book-list-index').click(function(){
            $('.book-list-show-index').hide('slow');
            if($(this).parent().next('ul:not(:hidden)').length == 0){
		$(this).parent().next('ul').toggle('slow');
	    }
            return false;
        });


    });
})(jQuery)

