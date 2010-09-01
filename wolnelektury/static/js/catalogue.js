var LOCALE_TEXTS = {
    "pl": {
        "DELETE_SHELF": "Czy na pewno usunąć półkę",
        "HIDE_DESCRIPTION": "Zwiń opis",
        "EXPAND_DESCRIPTION": "Rozwiń opis",
        "LOADING": "Ładowanie"
    },
    "de": {
        "DELETE_SHELF": "﻿Möchtest du wirklich dieses Bücherregal entfernen?",
        "HIDE_DESCRIPTION": "Beschreibung zuklappen",
        "EXPAND_DESCRIPTION": "Beschreibung aufklappen",
        "LOADING": "Herunterladen"
    },
    "fr": {
        "DELETE_SHELF": "Voulez-vous supprimer l'étagère  définitivement?",
        "HIDE_DESCRIPTION": "Montrer la description",
        "EXPAND_DESCRIPTION": "Cacher la description",
        "LOADING": "Chargement"
    },
    "en": {
        "DELETE_SHELF": "Are you sure you want to delete this shelf?",
        "HIDE_DESCRIPTION": "Hide",
        "EXPAND_DESCRIPTION": "Expand",
        "LOADING": "Loading"
    },
    "ru": {
        "DELETE_SHELF": "Уверены ли вы том, чтобы удалить полку?",
        "HIDE_DESCRIPTION": "Свернуть описание",
        "EXPAND_DESCRIPTION": "Раскрыть описание",
        "LOADING": "Загрузка"
    },
    "es": {
        "DELETE_SHELF": "¿Estás seguro que quieres borrar este estante?",
        "HIDE_DESCRIPTION": "Esconder la descripción",
        "EXPAND_DESCRIPTION": "Ampliar la descripción",
        "LOADING": "Cargando"
    },
    "lt":{
        "DELETE_SHELF": "Ar tikrai nori pašalinti lentną?",
        "HIDE_DESCRIPTION": "Suvyniok aprašymą ",
        "EXPAND_DESCRIPTION": "Išplėsk aprašymą",
        "LOADING": "Krovimas"
    },
    "uk":{
        "DELETE_SHELF": "Ви впевнені, що хочете видалити полицю?",
        "HIDE_DESCRIPTION": "Сховати опис",
        "EXPAND_DESCRIPTION": "Показати опис",
        "LOADING": "Завантажується"
    }
}
var BANNER_TEXTS = [
    'Przekaż 1% żeby ukryć ten baner.',
    'Jak dobrze wydać 1% swojego podatku? <strong>Poradnik dla opornych</strong>.',
    'Wiadomość systemowa: wystąpił błąd brak funduszy. Wykonaj procedurę 1%.',
    '<strong>FREE!</strong> Wygraj darmowe lektury!',
    'Confidential business offer. Not scam! 1% for you.',
    'Biblioteka Wolne Lektury wymaga aktualizacji. Kliknij dalej.',
    '1000 lektur. <strong>1 procent</strong>.',
    '1% dla biblioteki lektur szkolnych. 1% dla Twojej biblioteki.',
    '1% na lektury szkolne.',
    '1% dla wolności lektur szkolnych.',
    'Podaruj Jeden Procent na rzecz szkolnej biblioteki internetowej.',
    '1% podatku dla biblioteki szkolnej Wolne Lektury.',
    '1% na rzecz darmowego dostępu do szkolnych lektur.',
    'Żeby czytać teksty a nie skany. Przekaż 1%.',
    'Czytaj teksty a nie skany. Przekaż 1%',
    'Motyw artysty w literaturze - 47 cytatów. Pomóż znaleźć następne.',
    'Twój 1% uwolni więcej lektur.',
    'Ponad 400 motywów, blisko 10 000 000 cytatów. Pomóż znaleźć następne. Przekaż swój 1%.',
    'Twój 1% uwolni lektury.',
    'Rozlicz swój PIT z Wolnymi Lekturami. Skorzystaj z darmowego programu do rozliczania podatków.',
    'Lektury 2010: Pan Tadeusz, Trylogia.',
    'Pan Tadeusz też chce być w Internecie! Przekaż 1% swojego podatku.',
    'Pomóż uwolnić 286 utworów z listy lektur szkolnych. Przekaż swój 1% na Wolne Lektury.'
]


function changeBannerText() {
    var index = Math.floor(Math.random() * BANNER_TEXTS.length);
    if (BANNER_TEXTS[index] == $('#onepercent-text').html()) {
        // try again
        changeBannerText();
    } else {
        $('#onepercent-text').fadeOut('slow', function() {
            $(this).html(BANNER_TEXTS[index]);
            $(this).fadeIn('slow');
        });

        setTimeout(changeBannerText, 30 * 1000);
    }
}

function autocomplete_result_handler(event, item) {
    $(event.target).closest('form').submit();
}
function serverTime() {
    var time = null;
    $.ajax({url: '/katalog/zegar/',
        async: false, dataType: 'text',
        success: function(text) {
            time = new Date(text);
        }, error: function(http, message, exc) {
            time = new Date();
    }});
    return time;
}

(function($) {
    $(function() {

        $.fn.toggle_slide = function(p) {
            cont = $(this);
            short_el = p['short_el'] || $(':first-child', this);
            long_el = p['long_el'] || short_el.next();
            button = p['button'];
            short_text = p['short_text'],
            long_text = p['long_text'];

            var toggle_fun = function(cont, short_el, long_el, button, short_text, long_text) {
                var toggle = function() {
                    if (cont.hasClass('short')) {
                        cont.animate({"height": long_el.attr("cont_h")+'px'}, {duration: "fast" }).removeClass('short');
                        short_el.hide();
                        long_el.show();
                        if (button && long_text) button.html(long_text);
                    } else {
                        cont.animate({"height": short_el.attr("cont_h")+'px'}, {duration: "fast" }).addClass('short');
                        long_el.hide();
                        short_el.show();
                        if (button && short_text) button.html(short_text);
                    }
                    return false;
                }
                return toggle;
            }
            if (long_el.html().length <= short_el.html().length)
                return;

            // ensure long element shown first
            long_el.show();short_el.hide();
            long_el.attr("cont_h", $(this).height()).hide();
            short_el.show().attr("cont_h", $(this).height());
            $(this).addClass('short');

            if (button && short_text) button.html(short_text);
            if (button) button.hover(
                function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
                function() { $(this).css({background: '#EEE'}); }
            ).click(toggle_fun(cont, short_el, long_el, button, short_text, long_text));
            short_el.hover(
                function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
                function() { $(this).css({background: '#FFF'}); }
            ).click(toggle_fun(cont, short_el, long_el, button, short_text, long_text));
            long_el.hover(
                function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
                function() { $(this).css({background: '#FFF'}); }
            ).click(toggle_fun(cont, short_el, long_el, button, short_text, long_text));
        };

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
        $('.fragment-short-text').each(function() {
            var fragment = $(this).closest('.fragment');
            fragment.toggle_slide({
                short_el: $(this),
                long_el: fragment.find('.fragment-text')
            })
        });

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
                    .after('<img src="/static/img/indicator.gif" style="margin-left: 0.5em"/>');
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
                    .after('<img src="/static/img/indicator.gif" style="margin-left: 0.5em"/>');
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
            if (confirm(LOCALE_TEXTS[LANGUAGE_CODE]['DELETE_SHELF']+ ' '+ shelf_name + '?')) {
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
                    if (confirm(LOCALE_TEXTS[LANGUAGE_CODE]['DELETE_SHELF'] + ' ' + shelf_name + '?')) {
                        $.post(link.attr('href'), function(data, textStatus) {
                            link.parent().remove();
                        });
                    }
                    return false;
                });
            }
        });

        $('#suggest-window').jqm({
            ajax: '@href',
            target: $('#suggest-window div.target')[0],
            overlay: 60,
            trigger: '#suggest-link',
            onShow: function(hash) {
                var offset = $(hash.t).offset();
                hash.w.css({position: 'absolute', left: offset.left - hash.w.width() + $(hash.t).width(), top: offset.top});
                $('div.header', hash.w).css({width: $(hash.t).width()});
                hash.w.show();
            },
            onLoad: function(hash) {
                $('form', hash.w).ajaxForm({
                    dataType: 'json',
                    target: $('#suggest-window div.target'),
                    success: function(response) {
                        if (response.success) {
                            $('#suggest-window div.target').text(response.message);
                            setTimeout(function() { $('#suggest-window').jqmHide() }, 1000)
                        }
                        else {
                            $('#suggest-form .error').remove();
                            $.each(response.errors, function(id, errors) {
                                $('#suggest-form #id_' + id).before('<span class="error">' + errors[0] + '</span>');
                            });
                            $('#suggest-form input[type=submit]').removeAttr('disabled');
                            return false;
                        }
                    }
                });
            }
        });

        $('#books-list .book').hover(
            function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
            function() { $(this).css({background: '#FFF'}); }
        ).click(function() {
            location.href = $('h2 a', this).attr('href');
        });

        $('#description').each(function(){$(this).toggle_slide({
            long_el: $('#description-long', this),
            short_el: $('#description-short', this),
            button: $(this).nextAll('#toggle-description').first().find('p'),
            long_text: LOCALE_TEXTS[LANGUAGE_CODE]['HIDE_DESCRIPTION'] + ' ▲',
            short_text: LOCALE_TEXTS[LANGUAGE_CODE]['EXPAND_DESCRIPTION'] + ' ▼'
        })});

        $('#toggle-share-shelf').hover(
            function() { $(this).css({background: '#F3F3F3', cursor: 'pointer'}); },
            function() { $(this).css({background: '#EEE'}); }
        ).click(function() {
            if ($('#share-shelf').hasClass('hidden')) {
                $('#share-shelf').slideDown('fast').removeClass('hidden');
            } else {
                $('#share-shelf').slideUp('fast').addClass('hidden');
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
                target.html('<p><img src="/static/img/indicator.gif" />'+LOCALE_TEXTS[LANGUAGE_CODE]['DELETE_SHELF']+'</p>');
                hash.w.css({position: 'absolute', left: offset.left, top: offset.top}).show() },
            onLoad: function(hash) {
        try {
            $('#createShelfTrigger').click(function(){
                $('#createNewShelf').show();
            });
        } catch (e){}

                $('form', hash.w).ajaxForm({
                    target: target,
                    success: function() {
            setTimeout(function() {
                    $('#set-window').jqmHide();
                       }, 1000)}
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

        $('#share-shelf').hide().addClass('hidden');
        $('#share-shelf input').focus(function(){this.select();});

        $('#user-info').show();
        changeBannerText();
        $('#onepercent-banner').show();

        var formatsDownloaded = false;
        $('#download-shelf').click(function() {
            $('#download-shelf-menu').slideDown('fast');

            if (!formatsDownloaded) {
                // Get info about the formats
                formatsDownloaded = true;
                $.ajax({
                    url: $('#download-formats-form').attr('data-formats-feed'),
                    type: 'GET',
                    dataType: 'json',
                    complete: function() {
                        $('#download-formats-form-submit').attr('disabled', null);
                        $('#download-formats-form-submit-li img').remove();
                        $('#updating-formats').fadeOut('fast', function() {
                            $('#formats-updated').fadeIn('fast');
                        });
                    },
                    success: function(data) {
                        $('#download-formats-form li').each(function() {
                            var item = $(this);
                            if (!!item.attr('data-format') && !data[item.attr('data-format')]) {
                                item.fadeOut('fast', function() {
                                    item.remove();
                                });
                            }
                        });
                    }
                });
            }
            return false;
        });

        $('#download-formats-form-cancel').click(function() {
            $('#download-shelf-menu').slideUp('fast');
            return false;
        });

        $('marquee').marquee().mouseover(function () {
            $(this).trigger('stop');
        }).mouseout(function () {
            $(this).trigger('start');
             $(this).data('drag', false);
        }).mousemove(function (event) {
            if ($(this).data('drag') == true) {
                this.scrollLeft = $(this).data('scrollX') + ($(this).data('x') - event.clientX);
            }
        }).mousedown(function (event) {
            $(this).data('drag', true).data('x', event.clientX).data('scrollX', this.scrollLeft);
        }).mouseup(function () {
            $(this).data('drag', false);
        });

        $('.widget-code').focus(
            function(){
                $(this).animate({rows: '11'}, 100)
            } 
        ).blur(
            function(){
                $(this).animate({rows: '1'}, 300)
            } 
        );

    });
})(jQuery)
