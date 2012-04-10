(function($) {
    $(function() {

        // create containers for all ajaxable form links
        $('.ajaxable').each(function() {
            var $window = $("#ajaxable-window").clone();
            $window.attr("id", this.id + "-window");
            $('body').append($window);

            var $trigger = $(this)
            var trigger = '#' + this.id;

            $window.jqm({
                ajax: '@href',
                ajaxText: '<p><img src="' + STATIC_URL + 'img/indicator.gif" alt="*"/> ' + gettext("Loading") + '</p>',
                target: $('.target', $window)[0],
                overlay: 60,
                trigger: trigger,
                onShow: function(hash) {
                    var offset = $(hash.t).offset();
                    var oleft = offset.left - hash.w.width() + $(hash.t).width();
                    if (oleft < 0) oleft = 0;
                    hash.w.css({position: 'absolute', left: oleft, top: offset.top});
                    var width = $(hash.t).width();
                    width = width > 50 ? width : 50;
                    $('.header', hash.w).css({width: width});
                    hash.w.show();
                },
                onLoad: function(hash) {
                    $('form', hash.w).ajaxForm({
                        dataType: 'json',
                        target: $('.target', $window),
                        success: function(response) {
                            if (response.success) {
                                $('.target', $window).text(response.message);
                                setTimeout(function() { $window.jqmHide() }, 1000);
                                callback = ajaxable_callbacks[$trigger.attr('data-callback')];
                                callback && callback($trigger, response);
                                if (response.redirect)
                                    window.location = response.redirect;
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


        var login_and_retry = function($form) {
            var $window = $("#ajaxable-window").clone();
            $window.attr("id", "context-login-window");
            $('body').append($window);

            $window.jqm({
                ajax: '/uzytkownik/zaloguj-utworz/?next=' + escape(window.location),
                ajaxText: '<p><img src="' + STATIC_URL + 'img/indicator.gif" alt="*"/> ' + gettext("Loading") + '</p>',
                target: $('.target', $window)[0],
                overlay: 60,
                onShow: function(hash) {
                    var offset = $form.offset();
                    hash.w.css({position: 'absolute', left: offset.left - hash.w.width() + $form.width(), top: offset.top});
                    var width = $form.width();
                    width = width > 50 ? width : 50;
                    $('.header', hash.w).css({width: width});
                    hash.w.show();
                },
                onLoad: function(hash) {
                    $('form', hash.w).ajaxForm({
                        dataType: 'json',
                        target: $('.target', $window),
                        success: function(response) {
                            if (response.success) {
                                $('.target', $window).text(response.message);
                                setTimeout(function() { $window.jqmHide() }, 1000);
                                $form.submit();
                                location.reload();
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
            }).jqmShow();
            
        };


        $('.ajax-form').each(function() {
            var $form = $(this);
            $form.ajaxForm({
                dataType: 'json',
                beforeSubmit: function() {
                    $('input[type=submit]', $form)
                        .attr('disabled', 'disabled')
                        .after('<img src="/static/img/indicator.gif" style="margin-left: 0.5em"/>');
                },
                error: function(response) {
                        if (response.status == 403)
                            login_and_retry($form);
                    },
                success: function(response) {
                    if (response.success) {
                        callback = ajax_form_callbacks[$form.attr('data-callback')];
                        callback && callback($form, response);

                    } else {
                        $('span.error', $form).remove();
                        $.each(response.errors, function(id, errors) {
                            $('#id_' + id, $form).before('<span class="error">' + errors[0] + '</span>');
                        });
                        $('input[type=submit]', $form).removeAttr('disabled');
                        $('img', $form).remove();
                    }
                }
            });
        });


        var update_star = function($elem, response) {
            /* updates the star after successful ajax */
            var $star = $elem.closest('.star');
            if (response.like) {
                $star.addClass('like');
                $star.removeClass('unlike');
            }
            else {
                $star.addClass('unlike');
                $star.removeClass('like');
            }
        };

        var ajax_form_callbacks = {
            'social-like-book': update_star
        };

        var ajaxable_callbacks = {
            'social-book-sets': location.reload
        };



    // check placeholder browser support
    if (!Modernizr.input.placeholder)
    {
        // set placeholder values
        $(this).find('[placeholder]').each(function()
        {
            $(this).val( $(this).attr('placeholder') ).addClass('placeholder');
        });
 
        // focus and blur of placeholders
        $('[placeholder]').focus(function()
        {
            if ($(this).val() == $(this).attr('placeholder'))
            {
                $(this).val('');
                $(this).removeClass('placeholder');
            }
        }).blur(function()
        {
            if ($(this).val() == '' || $(this).val() == $(this).attr('placeholder'))
            {
                $(this).val($(this).attr('placeholder'));
                $(this).addClass('placeholder');
            }
        });

        // remove placeholders on submit
        $('[placeholder]').closest('form').submit(function()
        {
            $(this).find('[placeholder]').each(function()
            {
                if ($(this).val() == $(this).attr('placeholder'))
                {
                    $(this).val('');
                }
            })
        });
    }



    });
})(jQuery);

