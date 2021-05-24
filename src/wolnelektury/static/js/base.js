(function($) {
    $(function() {
        $.fn.toggle_slide = function(p) {
            var cont = $(this);
            var short_el = p['short_el'] || $(':first-child', this);
            var long_el = p['long_el'] || short_el.next();
            var button = p['button'];
            var short_text = p['short_text'];
            var long_text = p['long_text'];

            var toggle_fun = function(cont, short_el, long_el, button, short_text, long_text) {
                return function () {
                    if (cont.hasClass('short')) {
                        cont.animate({"height": long_el.attr("cont_h") + 'px'}, {duration: "fast"})
                            .removeClass('short');
                        short_el.hide();
                        long_el.show();
                        if (button && long_text) button.html(long_text);
                    } else {
                        cont.animate({"height": short_el.attr("cont_h") + 'px'}, {duration: "fast"}).addClass('short');
                        long_el.hide();
                        short_el.show();
                        if (button && short_text) button.html(short_text);
                    }
                    return false;
                };
            };
            if (long_el.html().length <= short_el.html().length)
                return;

            // ensure long element shown first
            long_el.show();short_el.hide();
            long_el.attr("cont_h", $(this).height()).hide();
            short_el.show().attr("cont_h", $(this).height());
            $(this).addClass('short');

            if (button && short_text)
                button.html(short_text);
            if (button)
                button.click(toggle_fun(cont, short_el, long_el, button, short_text, long_text));
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

        $('.more-expand').each(function () {
            $(this).shorten({
                showChars: 150,
                moreText: "więcej",
                lessText: "mniej"
            });
        });


        $('.carousel').on('cycle-before', function(event, optionHash, outgoingSlideEl, incomingSlideEl, forwardFlag) {
            $("iframe", outgoingSlideEl).attr("src", '');
            $("iframe", incomingSlideEl).attr("src", $("iframe", incomingSlideEl).attr('data-src'));
        });
        $('.carousel section').first().each(function() {
            $("iframe", this).attr("src", $("iframe", this).attr('data-src'));
        });

        $(".media-eink .carousel").cycle({fx: "none"});


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
                                dataType: "json"
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
                                                else
                                                    $(this).hide();
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
            //$('#menu').toggle('fast');
            $('body').toggleClass('menu-on');
        });


        $('#book-list-nav').find('h2').click(function(event) {
            event.preventDefault();
            $('#book-list-nav-index').toggle();
        });


        $('#themes-list-toggle').click(function(event) {
            event.preventDefault();
            $('#themes-list').toggle('fast');
        });


        $('.book-list-index').click(function(){
            $('.book-list-show-index').hide('fast');
            var books_ul = $(this).parent().next().children().first();
            if(books_ul.first().is(':hidden')){
                books_ul.toggle('fast');
            }
            return false;
        });

        $('.hoverclick').click(function() {$(this).closest('.hoverget').toggleClass('hover');});

        $(function(){
            $("#search").search();
        });

        $('body').on('click', '.simple-toggler' , function(ev) {
            ev.preventDefault();
            var scope = $(this).closest('.simple-toggler-scope');
            scope.find('.simple-hidden-box').each(function() {
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
                                return ' <li><a href="#"' + (this.value == this.page ? ' class="current"' : '') + '>' +
                                    this.value + '</a></li>';
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

        /* global tlite */
        tlite(function (el) {
            return $(el).hasClass('tlite-tooltip');
        });

        /* more/less switch from https://codepen.io/JoshBlackwood/pen/pEwHe */
        // Hide the extra content initially, using JS so that if JS is disabled, no problemo:
        $('.read-more-content').addClass('hide');
        $('.read-more-show, .read-more-hide').removeClass('hide');

        // Set up the toggle effect:
        $('.read-more-show').on('click', function(e) {
          $(this).next('.read-more-content').removeClass('hide');
          $(this).addClass('hide');
          e.preventDefault();
        });

        // Changes contributed by @diego-rzg
        $('.read-more-hide').on('click', function(e) {
          var p = $(this).parent('.read-more-content');
          p.addClass('hide');
          p.prev('.read-more-show').removeClass('hide'); // Hide only the preceding "Read More"
          e.preventDefault();
        });


        function update_info() {
            var amount = parseInt($("#id_amount").val());
            var monthly =  $("#id_monthly").val() == 'True';
            if (monthly) slug = "monthly";
            else if (amount >= parseInt($("#plan-single").attr('data-min-for-year'))) slug = 'single-year';
            else slug = 'single';

            var chunk = $('.club-form-info .chunk-' + slug);
            if (chunk.css('display') == 'none') {
                $('.chunk-alt').css('height', $('.chunk-alt').height());
                $('.chunk-alt .chunk').css('position', 'absolute');

                $('.club-form-info .chunk').fadeOut();
                $('.club-form-info .chunk.chunk-' + slug).fadeIn(function() {
                    $('.chunk-alt .chunk').css('position', 'static');
                    $('.chunk-alt').css('height', 'auto');
                });
                $('.chunk-alt').animate({height: chunk.height()}, 100);
            }
        }
        
        $("#id_amount").val($("#plan-monthly").attr('data-amount'));
        
        $(".button.kwota").click(function() {
            var plan = $(this).closest('.plan');
            $('.kwota', plan).removeClass('active')
            $('.inna', plan).removeClass('active')
            $(this).addClass('active');

            var amount = $(this).text();
            plan.attr("data-amount", amount);
            $("#id_amount").val(amount);

            update_info();
            return false;
        });

        $(".plan-toggle").click(function() {
            $(".plan-toggle").removeClass('active');
            $(this).addClass('active')
            $(".plan").hide();
            var plan = $("#" + $(this).attr('data-plan'));
            plan.show();
            $("#id_amount").val(plan.attr('data-amount'));
            $("#id_monthly").val(plan.attr('data-monthly'));

            update_info();
            return false;
        });

        $(".inna .button").click(function() {
            var plan = $(this).closest('.plan');
            $('.kwota', plan).removeClass('active');
            $(this).parent().addClass('active');
            $('input', plan).focus();

            var amount = $('input', $(this).parent()).val();
            plan.attr("data-amount", amount);
            $("#id_amount").val(amount);

            update_info();
            return false;
        });
        
        $(".inna input").on('input', function() {
            var plan = $(this).closest('.plan');
            $('.kwota', plan).removeClass('active');
            var amount = $(this).val();
            plan.attr("data-amount", amount);
            $("#id_amount").val(amount);

            update_info();
            return false;
        });

    });
})(jQuery);

