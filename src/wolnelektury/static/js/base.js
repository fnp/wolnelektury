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
                };
                return toggle;
            };
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
                                url: '/katalog/' + LANGUAGE_CODE + '.json',
                                dataType: "json",
                            }).done(function(data) {
                                $.each(data, function(index, value) {
                                    var $menuitem = $('#menu-' + index);
                                    $menuitem.html(value);
                                    var $minisearch = $("<input class='mini-search' style='margin-bottom: 1em' />");
                                    $minisearch.keyup(function() {
                                        var s = $(this).val().toLowerCase();
                                        if (s) {
                                            $("li", $menuitem).each(function() {
                                                if ($("a", this).text().toLowerCase().indexOf(s) != -1)
                                                    $(this).show();
                                                else $(this).hide();
                                            });
                                        }
                                        else {
                                            $("li", $menuitem).css("display", "");
                                        }
                                    });
                                    $menuitem.prepend($minisearch);
                                });
                                menu_loaded = true;
                            });
                        }
					}
				});
			});
		    /* this kinda breaks the whole page. */
			$('body').click(function(e) {
				if ($current == null) return;
				var p = $(e.target);
				while (p.length) {
					if (p == $current)
						return;
					if (p.hasClass('hidden-box-trigger')
					    || p.hasClass('simple-toggler')
                        || p.hasClass('mini-search'))
						return;
					p = p.parent();
				}
				$current.hide('fast');
				$current = null;
			});
		})();


$('#show-menu').click(function(event) {
    event.preventDefault();
    //$('#menu').toggle('slow');
    $('body').toggleClass('menu-on');
});


$('#book-list-nav h2').click(function(event) {
    event.preventDefault();
    $('#book-list-nav-index').toggle();
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

      $('body').on('click', '.simple-toggler' , function(ev) {
	ev.preventDefault();
	var scope = $(this).closest('.simple-toggler-scope');
	scope.find('.simple-hidden-box').each(function(){
	  var $this = $(this);
	  if ($this.is(':hidden')) {
	    $this.show();
	  } else {
	    $this.hide();
	  }
	  });
      });


    $('.tabbed-filter').each(function() {
        var tf = this;
        $('.tab').click(function() {
            if ($(this).hasClass('active')) {
                $(this).removeClass('active');
                $('#' + $(this).attr('data-id')).hide();
            }
            else {
                var $active = $('.active', tf);
                $active.removeClass('active');
                $('#' + $active.attr('data-id')).hide();
                $(this).addClass('active');
                $('#' + $(this).attr('data-id')).show();
            }
        });
    });


    $('.plain-list-paged').each(function() {
        // should change on resize?
        var $plc = $(this);
        var $pl = $('.plain-list', this);

        var $items = $('p', $pl);

        if ($items.length > 40) {
            $items.hide();
            var prev = [0, 0];

            $('.pager', $plc).paging($items.length, {
                format: '[< ncnnn >]', // define how the navigation should look like and in which order onFormat() get's called
                perpage: 40,
                lapping: 0, // don't overlap pages for the moment
                page: 1, // start at page, can also be "null" or negative
                onSelect: function (page) {
                    var data = this.slice;
                    $items.slice(prev[0], prev[1]).hide();
                    $items.slice(data[0], data[1]).show();
                    prev = data;
                },
                onFormat: function (type) {
                    switch (type) {
                        case 'block': // n and c
                            return ' <li><a href="#"' + (this.value == this.page ? ' class="current"' : '') + '>' + this.value + '</a></li>';
                        case 'next': // >
                            return '<li><a href="#">&rsaquo;</a></li>';
                        case 'prev': // <
                            return '<li><a href="#">&lsaquo;</a></li>';
                        case 'first': // [
                            return '<li><a href="#">&laquo;</a></li>';
                        case 'last': // ]
                            return '<li><a href="#">&raquo;</a></li>';
                    }
                }
            });
        }
    });


    });
})(jQuery);

