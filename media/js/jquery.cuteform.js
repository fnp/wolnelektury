(function($) {
    $(document).ready(function() {
        $('form.cuteform').each(function(index) {
            var formLabels = $('label', this)
            var maxWidth = 0;
    
            formLabels.each(function() {
                maxWidth = Math.max(maxWidth, $(this).width());
            }).css({display: 'inline-block'}).width(maxWidth);
        });
    });
})(jQuery);