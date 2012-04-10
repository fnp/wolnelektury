(function($) {
    $(function() {


        $('#countdown').each(function() {
            var $this = $(this);

            var serverTime = function() {
                var time = null;
                $.ajax({url: '/zegar/',
                    async: false, dataType: 'text',
                    success: function(text) {
                        time = new Date(text);
                    }, error: function(http, message, exc) {
                        time = new Date();
                }});
                return time;
            }

            if (LANGUAGE_CODE != 'en') {
                $.countdown.setDefaults($.countdown.regional[LANGUAGE_CODE]);
            }
            else {
                $.countdown.setDefaults($.countdown.regional['']);
            }

            var d = new Date($this.attr('data-year'), 0, 1);
            function re() {location.reload()};
            $this.countdown({until: d, format: 'ydHMS', serverSync: serverTime,
                onExpiry: re, alwaysExpire: true});

        });


    });
})(jQuery);