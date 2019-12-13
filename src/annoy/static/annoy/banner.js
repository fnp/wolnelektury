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
            });

            $off.click(function() {
                $target.slideUp('fast');
                $on.show();
                if (Modernizr.localstorage) localStorage[tag] = true;
            });

            if (Modernizr.localstorage) {
                if (!localStorage[tag]) {
                    $on.hide();
                    $target.show();
                }
            }
        });

    });
})(jQuery);
