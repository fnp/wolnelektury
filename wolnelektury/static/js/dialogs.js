(function($) {
    $(function() {

        // create containers for all ajaxable form links
        $('.ajaxable').each(function() {
            var $window = $("#ajaxable-window").clone();
            $window.attr("id", this.id + "-window");
            $('body').append($window);

            var trigger = '#' + this.id;

            var href = $(this).attr('href');
            if (href.search('\\?') != -1)
                href += '&ajax=1';
            else href += '?ajax=1';

            $window.jqm({
                ajax: href,
                ajaxText: '<p><img src="' + STATIC_URL + 'img/indicator.gif" alt="*"/> ' + gettext("Loading") + '</p>',
                target: $('.target', $window)[0],
                overlay: 60,
                trigger: trigger,
                onShow: function(hash) {
                    var offset = $(hash.t).offset();
                    hash.w.css({position: 'absolute', left: offset.left - hash.w.width() + $(hash.t).width(), top: offset.top});
                    $('.header', hash.w).css({width: $(hash.t).width()});
                    hash.w.show();
                },
                onLoad: function(hash) {
                    $('form', hash.w).each(function() {this.action += '?ajax=1';});
                    $('form', hash.w).ajaxForm({
                        dataType: 'json',
                        target: $('.target', $window),
                        success: function(response) {
                            if (response.success) {
                                $('.target', $window).text(response.message);
                                setTimeout(function() { $window.jqmHide() }, 1000)
                            }
                            else {
                                $('.error', $window).remove();
                                $.each(response.errors, function(id, errors) {
                                    $('#id_' + id, $window).before('<span class="error">' + errors[0] + '</span>');
                                });
                                $('input[type=submit]', $window).removeAttr('disabled');
                                return false;
                            }
                        }
                    });
                }
            });
        });


    });
})(jQuery)

