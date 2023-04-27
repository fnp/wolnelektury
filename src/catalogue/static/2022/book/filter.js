(function($) {

    $(".quick-filter").each(function() {
        let bookList = $('#' + $(this).data('for'));
        let filterList = $('.' + $(this).data('filters'));

        $(this).on('focus', function() {
            filterList.addClass('filters-enabled');
        });
        $(this).on('blur', function() {
            filterList.removeClass('filters-enabled');
        });

        $(this).on('input propertychange', function() {
            let search = $(this).val().toLowerCase();

            bookList.children().each(function() {
                found = !search ||
                    $(".s", this).text().toLowerCase().search(search) != -1
                    ;
                if (found) 
                    $(this).fadeIn();
                else
                    $(this).fadeOut();
            });



            $('.filter-container', filterList).children().each(function() {
                console.log($(this).text().toLowerCase());
                found = !search ||
                    $(this).text().toLowerCase().search(search) != -1
                    ;
                if (found) 
                    $(this).fadeIn();
                else
                    $(this).fadeOut();
            });
        });

    });

    $(".l-books__sorting button").on('click', function() {
        if ($(this).hasClass('is-active')) return;
        $(".is-active", $(this).parent()).removeClass("is-active");
        $(this).addClass("is-active");
        let prop = $(this).attr('data-order');
        $(".l-books__item").css('opacity', '0');
        setTimeout(function() {
            if (prop) {
                $(".l-books__item").each(function() {
                    $(this).css('order', $(this).attr(prop));
                });
            } else {
                $(".l-books__item").css('order', '');
            }
            setTimeout(function() {
                $(".l-books__item").css('opacity', '100%');
            }, 200);
        }, 200);
    });
    
})(jQuery);
