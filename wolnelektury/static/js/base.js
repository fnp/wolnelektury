(function($) {
    $(function() {
        $.fn.toggle_slide = function(p) {
            cont = $(this);
            short_el = p['short_el'] || $(':first-child', this);
            long_el = p['long_el'] || short_el.next();
            button = p['button'];
            short_text = p['short_text'],
            long_text = p['long_text'];

            var toggle_fun = function(cont, short_el, long_el, button, short_text, long_text) {
                var toggle = function() {
                    if (cont.hasClass('short')) {
                        cont.animate({"height": long_el.attr("cont_h")+'px'}, {duration: "fast" }).removeClass('short');
                        short_el.hide();
                        long_el.show();
                        if (button && long_text) button.html(long_text);
                    } else {
                        cont.animate({"height": short_el.attr("cont_h")+'px'}, {duration: "fast" }).addClass('short');
                        long_el.hide();
                        short_el.show();
                        if (button && short_text) button.html(short_text);
                    }
                    return false;
                }
                return toggle;
            }
            if (long_el.html().length <= short_el.html().length)
                return;

            // ensure long element shown first
            long_el.show();short_el.hide();
            long_el.attr("cont_h", $(this).height()).hide();
            short_el.show().attr("cont_h", $(this).height());
            $(this).addClass('short');

            if (button && short_text) button.html(short_text);
            if (button) button.hover(
                function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
                function() { $(this).css({background: '#EEE'}); }
            ).click(toggle_fun(cont, short_el, long_el, button, short_text, long_text));
            short_el.hover(
                function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
                function() { $(this).css({background: '#FFF'}); }
            ).click(toggle_fun(cont, short_el, long_el, button, short_text, long_text));
            long_el.hover(
                function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
                function() { $(this).css({background: '#FFF'}); }
            ).click(toggle_fun(cont, short_el, long_el, button, short_text, long_text));
        };


        // Fragments
        $('.fragment-short-text').each(function() {
            var fragment = $(this).closest('.fragment');
            fragment.toggle_slide({
                short_el: $(this),
                long_el: fragment.find('.fragment-text')
            })
        });






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

