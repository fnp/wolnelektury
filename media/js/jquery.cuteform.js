(function($) {
    $.fn.cuteform = function() {
        $('form.cuteform', this).each(function(index) {
            var formLabels = $('label', this)
            var maxWidth = 0;
            
            formLabels.each(function() {
                maxWidth = max(maxWidth, this);
            });
            formLabels.width(maxWidth);
        });
    };
})(jQuery)