(function($) {
    $(function() {
        $('form input').labelify({labelledClass: 'blur'});
        
        target = $('#login-register-window div.target');
        
        $('#show-registration-form').click(function() {
            $('#login-form').hide();
            $('#registration-form').show();
        });
        
        $('#show-login-form').click(function() {
            $('#registration-form').hide();
            $('#login-form').show();
        });
        
        // Fragments
        $('.fragment-text').each(function() {
            if ($(this).prev().filter('.fragment-short-text').length) {
                $(this).hover(
                    function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
                    function() { $(this).css({background: '#FFF'}); }
                ).click(function() {
                    $(this).fadeOut(function() {
                        $(this).prev().fadeIn()
                    });
                })
            }
        });
        
        $('.fragment-short-text').click(function() {
            $(this).fadeOut(function() { $(this).next().fadeIn() });
        }).hover(
            function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
            function() { $(this).css({background: '#FFF'}); }
        );
        
        $('.show-all-tags').click(function() {
            $(this).parent().parent().fadeOut(function() { 
                $(this).next().fadeIn();
            });
            return false;
        });
        
        $('.hide-all-tags').click(function() {
           $(this).parent().parent().fadeOut(function() {
               $(this).prev().fadeIn();
           });
           return false; 
        });
        
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
            trigger: '.login-register-link',
            onShow: function(hash) {
                var offset = $(hash.t).offset();
                hash.w.css({position: 'absolute', left: offset.left - hash.w.width() + $(hash.t).width(), top: offset.top});
                $('div.header', hash.w).css({width: $(hash.t).width()});
                hash.w.show();
            }
        });
        
        $('ul.shelf-list li').hover(function() {
            $(this).css({background: '#EEE', cursor: 'pointer'});
        }, function() {
            $(this).css({background: 'transparent'});
        }).click(function() {
            location.href = $('a.visit-shelf', this).attr('href');
        });
        
        $('.delete-shelf').click(function() { 
            var link = $(this);
            var shelf_name = $('.visit-shelf', link.parent()).text();
            if (confirm('Czy na pewno usunąć półkę ' + shelf_name + '?')) {
                $.post(link.attr('href'), function(data, textStatus) {
                    link.parent().remove();
                });
            }
            return false;
        });
        
        $('#user-shelves-window').jqm({
            ajax: '@href',
            target: $('#user-shelves-window div.target')[0],
            overlay: 60,
            trigger: '#user-shelves-link',
            onShow: function(hash) {
                var offset = $(hash.t).offset();
                hash.w.css({position: 'absolute', left: offset.left - hash.w.width() + $(hash.t).width(), top: offset.top});
                $('div.header', hash.w).css({width: $(hash.t).width()});
                hash.w.show();
            },
            onLoad: function(hash) { 
                $('form', hash.w).ajaxForm({
                    target: $('#user-shelves-window div.target'),
                    success: function() { setTimeout(function() { $('#user-shelves-window').jqmHide() }, 1000) }
                });
                
                $('input', hash.w).labelify({labelledClass: 'blur'});
                
                $('ul.shelf-list li', hash.w).hover(function() {
                    $(this).css({background: '#EEE', cursor: 'pointer'});
                }, function() {
                    $(this).css({background: 'transparent'});
                }).click(function() {
                    location.href = $('a.visit-shelf', this).attr('href');
                });
                
                $('.delete-shelf').click(function() {
                    var link = $(this);
                    var shelf_name = $('.visit-shelf', link.parent()).text();
                    if (confirm('Czy na pewno usunąć półkę ' + shelf_name + '?')) {
                        $.post(link.attr('href'), function(data, textStatus) {
                            link.parent().remove();
                        });
                    }
                    return false;
                });
            }
        });
    
        $('#books-list .book').hover(
            function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
            function() { $(this).css({background: '#FFF'}); }
        ).click(function() {
            location.href = $('h2 a', this).attr('href');
        });
    
        $('#toggle-description').hover(
            function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
            function() { $(this).css({background: '#EEE'}); }
        ).click(function() {
            if ($('#description').hasClass('hidden')) {
                $('#description').slideDown('fast').removeClass('hidden');
                $('p', this).html('Zwiń opis ▲');
            } else {
                $('#description').slideUp('fast').addClass('hidden');
                $('p', this).html('Rozwiń opis ▼');
            }
        });
    
        var target = $('#set-window div.target');
    
        $('#set-window').jqm({
            ajax: '@href', 
            target: target[0],
            overlay: 60,
            trigger: 'a.jqm-trigger', 
            onShow: function(hash) { 
                var offset = $(hash.t).offset();
                target.html('<p><img src="/media/img/indicator.gif" /> Ładowanie</p>');
                hash.w.css({position: 'absolute', left: offset.left, top: offset.top}).show() },
            onLoad: function(hash) { 
                $('form', hash.w).ajaxForm({
                    target: target,
                    success: function() { setTimeout(function() { $('#set-window').jqmHide() }, 1000) }
                });
            }
        });
        
        $('a.remove-from-shelf').click(function(event) {
            event.preventDefault();
            link = $(this);
            $.post(link.attr('href'), function(data, textStatus) {
                link.parent().remove();
            });
        });
        
        $('#user-info').show();
    });
})(jQuery)