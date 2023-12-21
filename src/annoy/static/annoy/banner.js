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
                _paq.push(['trackEvent', 'banner', 'banner-unhide', $target.attr('id')]);
            });

            $off.click(function() {
                $target.slideUp('fast');
                $on.show();
                if (Modernizr.localstorage) localStorage[tag] = true;
                _paq.push(['trackEvent', 'banner', 'banner-hide', $target.attr('id')]);
            });

            if (!localStorage[tag]) {
                $on.hide();
                $target.show();
                _paq.push(['trackEvent', 'banner', 'banner-show', $target.attr('id')]);
            }
        });

        $(document).on('click', ".annoy-banner a", function() {
            banner = $(this).closest('.annoy-banner');
            _paq.push(['trackEvent', 'banner', 'banner-click', banner.attr('id')]);
        });
        $(document).on('click', ".dynamic-insert a", function() {
            banner = $(this).closest('.dynamic-insert');
            _paq.push(['trackEvent', 'dynamic-insert', 'dynamic-insert-click', 'insert-' + banner.attr('data-paragraphs') + '-pars-text-' + banner.attr('data-textid')]);
        });

    });
})(jQuery);
