(function($) {
    $(function() {

        $("#search").search();
        $("#search").on('focus', function() {
            $(".l-navigation__logo").addClass('search-active');
        });
        $("#search").on('blur', function() {
            $(".l-navigation__logo").removeClass('search-active');
        });

    });
})(jQuery);
