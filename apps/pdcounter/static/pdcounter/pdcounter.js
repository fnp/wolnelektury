(function($) {
    $(function() {

        $('.countdown').each(function() {
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

            var options = {
                until: new Date($this.attr('data-until')),
                format: 'ydHMS',
                serverSync: serverTime,
                onExpiry: function(){location.reload()}, // TODO: no reload
            };
            if ($this.hasClass('inline')) {
                options.layout = '{dn} {dl} {hnn}{sep}{mnn}{sep}{snn}';
            }
            
            $this.countdown(options);
        });


    });
})(jQuery);
