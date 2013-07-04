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
            if (button) button.click(toggle_fun(cont, short_el, long_el, button, short_text, long_text));
        };


        // Fragments
        $('.fragment-with-short').each(function() {
            $(this).toggle_slide({
                short_el: $('.fragment-short-text', this),
                long_el: $('.fragment-long-text', this),
                button: $('.toggle', this)
            })
        });
        $('#description').each(function() {
            $(this).toggle_slide({
                short_el: $('#description-short', this),
                long_el: $('#description-long', this),
                button: $(this)
            })
        });



		(function() {
			var $current = null;
            var menu_loaded = false;
			$('.hidden-box-wrapper').each(function() {
				var $hidden = $('.hidden-box', this);
				$('.hidden-box-trigger', this).click(function(event) {
					event.preventDefault();
					if ($current == $hidden) {
						$current = null;
						$hidden.hide('fast');
					} else {
						$current && $current.hide('fast');
						$hidden.show('fast');
						$current = $hidden;
                        if ($(this).hasClass('load-menu') && !menu_loaded) {
                            $.ajax({
                                url: '/katalog/',
                                dataType: "json",
                            }).done(function(data) {
                                $.each(data, function(index, value) {
                                    $('#menu-' + index).html(value);
                                });
                                menu_loaded = true;
                            });
                        }
					} 
				});
			});
			$('body').click(function(e) {
				if ($current == null) return;
				var p = $(e.target);
				while (p.length) {
					if (p == $current)
						return;
					if (p.hasClass('hidden-box-trigger'))
						return;
					p = p.parent();
				}
				$current.hide('fast');
				$current = null;
			});
		})();
		

$('#show-menu').click(function(event) {
    event.preventDefault();
    $('#menu').toggle('slow');
});


$('#themes-list-toggle').click(function(event) {
    event.preventDefault();
    $('#themes-list').toggle('slow');
});


        $('.book-list-index').click(function(){
            $('.book-list-show-index').hide('slow');
            if($(this).parent().next('ul:not(:hidden)').length == 0){
		$(this).parent().next('ul').toggle('slow');
	    }
            return false;
        });

	$('.hoverclick').click(function() {$(this).closest('.hoverget').toggleClass('hover');});

	$(function(){
	    $("#search").search();});

    });
})(jQuery);

