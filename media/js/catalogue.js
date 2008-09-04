(function($) {
    $(function() {
        $('#id_q').labelify({labelledClass: 'blur'});
        
        target = $('#login-register-window div.target');
        
        $('#show-registration-form').click(function() {
            $('#login-form').hide();
            $('#registration-form').show();
        });
        
        $('#show-login-form').click(function() {
            $('#registration-form').hide();
            $('#login-form').show();
        });
        
        $('.fragment-text').toggle(
            function() { $(this).addClass('fragment-text-full').removeClass('fragment-text'); }, 
            function() { $(this).addClass('fragment-text').removeClass('fragment-text-full'); }
        ).hover(
            function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
            function() { $(this).css({background: '#FFF'}); }
        )
        
        $('#registration-form').ajaxForm({
            dataType: 'json',
            beforeSubmit: function() {
                $('#registration-form input[type=submit]')
                    .attr('disabled', 'disabled')
                    .after('<img src="/media/img/indicator.gif" style="margin-left: 0.5em"/>');
            },
            success: function(response) {
                if (response.success) {
                    location.reload(true);
                } else {
                    $('#registration-form span.error').remove();
                    $.each(response.errors, function(id, errors) {
                        $('#id_registration-' + id).before('<span class="error">' + errors[0] + '</span>');
                    });
                    $('#registration-form input[type=submit]').removeAttr('disabled');
                    $('#registration-form img').remove();
                }
            }
        });
        
        $('#login-form').ajaxForm({
            dataType: 'json',
            beforeSubmit: function() {
                $('#login-form input[type=submit]')
                    .attr('disabled', 'disabled')
                    .after('<img src="/media/img/indicator.gif" style="margin-left: 0.5em"/>');
            },
            success: function(response) {
                if (response.success) {
                    location.reload(true);
                } else {
                    $('#login-form span.error').remove();
                    $.each(response.errors, function(id, errors) {
                        $('#id_login-' + id).before('<span class="error">' + errors[0] + '</span>');
                    });
                    $('#login-form input[type=submit]').removeAttr('disabled');
                    $('#login-form img').remove();
                }
            }
        });
        
        $('#login-register-window').jqm({
            target: target[0],
            overlay: 60,
            trigger: '#login-register-link',
            onShow: function(hash) {
                var offset = $(hash.t).offset();
                hash.w.css({position: 'absolute', left: offset.left - hash.w.width() + $(hash.t).width(), top: offset.top});
                $('div.header', hash.w).css({width: $(hash.t).width()});
                hash.w.show();
            }
        });
        $('#login-register-window').labelify({labelledClass: 'blur'});
    });
})(jQuery)