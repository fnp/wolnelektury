(function($) {
    $(function() {

        $(".annoy-banner-on").each(function() {
            var $on = $(this);
            var tag = 'annoyed' + $on.attr('data-target');
            var $target = $($on.attr('data-target'));
            var $off = $('.annoy-banner-off', $target);

            $on.click(function(e) {
                e.preventDefault();
                $target.slideDown('fast');
                $on.hide();
                if (Modernizr.localstorage) localStorage.removeItem(tag);
                _paq.push(['trackEvent', 'banner', 'unhide', $on.attr('data-target')]);
            });

            $off.click(function() {
                $target.slideUp('fast');
                $on.show();
                if (Modernizr.localstorage) localStorage[tag] = true;
                _paq.push(['trackEvent', 'banner', 'hide', $on.attr('data-target')]);
            });

            if (Modernizr.localstorage) {
                if (!localStorage[tag]) {
                    $on.hide();
                    $target.show();
                    _paq.push(['trackEvent', 'banner', 'show', $on.attr('data-target')]);
                }
            }
        });

        $(document).on('click', ".annoy-banner a", function() {
            banner = $(this).closest('.annoy-banner');
            _paq.push(['trackEvent', 'banner', 'click', banner.attr('id')]);
        });
        $(document).on('click', ".dynamic-insert a", function() {
            banner = $(this).closest('.dynamic-insert');
            _paq.push(['trackEvent', 'dynamic-insert', 'click', banner.attr('data-paragraphs'), banner.attr('data-textid')]);
        });

    });
})(jQuery);
