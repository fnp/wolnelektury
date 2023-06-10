(function($) {

    let unpagedSearch = null;
    if (!$(".quick-filter").val() && !$('.l-pagination li').length) {
        unpagedSearch = '';
    }
    
    function get_page(page, search, ordering, callback) {
        get_page_by_url('.?page=' + page + '&order=' + ordering + '&search=' + search, callback);
    }

    let lastFulfilledPage = 0;

    function get_page_by_url(url, callback) {
        let requestTime = + new Date();
        $.get(
            url,
            function(data) {
                if (lastFulfilledPage > requestTime) return;
                lastFulfilledPage = requestTime;

                html = $(data);
                objectList = $('#object-list', html);
                paginate = $('#paginate', html);

                ids = new Set(); 
                $(".icon-like", objectList).each(
                    (i, e)=>{
                        ids.add($(e).attr('data-book'));
                    }
                );
                ids = [...ids].join(',');
                $.refreshLikes(ids);

                $('#book-list').html(objectList.children());
                $('#paginator').html(paginate.children());
                history.replaceState({}, '', url);
                callback && callback();
            }
        )
    }

    $("#paginator").on('click', 'a', function() {
        get_page_by_url(url=$(this).attr('href'));
        return false;
    });

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

            if (!search.startsWith(unpagedSearch)) {
                get_page(1, search, 'title', function() {
                    if ($('.l-pagination li').length) {
                        unpagedSearch = null;
                    }
                })
            } else {
                bookList.children().each(function() {
                    found = !search ||
                        $(".s", this).text().toLowerCase().search(search) != -1
                    ;
                    if (found) 
                        $(this).fadeIn();
                    else
                        $(this).fadeOut();
                });
            }

            $('.filter-container', filterList).children().each(function() {
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
        $(".l-books__sorting select").val(prop);
        if (prop == '-') prop = '';
        resort(prop);
    });
    $(".l-books__sorting select").on('change', function() {
        let prop = $(this).val();
        $(".is-active", $(this).parent()).removeClass("is-active");
        $("[data-order='" + prop +"']", $(this).parent()).addClass("is-active");
        if (prop == '-') prop = '';
        resort(prop);
    });

    function resort(prop) {
        // do we NOW have pages (possibly after filtering)?
        // if we don't have pages, we can just sort here.
        let havePages = $('.l-pagination li').length > 0;

        $(".l-books__item").css('opacity', '0');
        setTimeout(function() {
            if (havePages) {
                get_page(1, '', prop);
            } else {
                if (prop) {
                    $(".l-books__item").each(function() {
                        $(this).css('order', $(this).attr('data-' + prop));
                    });
                } else {
                    $(".l-books__item").css('order', '');
                }
                setTimeout(function() {
                    $(".l-books__item").css('opacity', '100%');
                }, 200);
            }
        }, 200);
    }
    
})(jQuery);
