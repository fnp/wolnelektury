(function($) {
    $(function() {


        var fold = $(window).scrollTop() + $(window).height();

        var inserts = [];
        $("#annoy-stubs .dynamic-insert").each(function() {inserts.push($(this));});

        var $intermissions = $("#annoy-stubs .annoy-banner_book-text-intermission");
        if ($intermissions.length) {
            var which = 0;
            $("#book-text a + h2").each(function(i, e) {
                console.log(i);
                if (i) {
                    $($intermissions[which]).clone().insertBefore($(this)).show();
                    which = (which + 1) % $intermissions.length;
                }
            });

            if ($("#footnotes").length) {
                $($intermissions[which]).clone().insertBefore($("#footnotes")).show();
            } else {
                $($intermissions[which]).clone().appendTo($("#book-text")).show();
            }
        };

        if (inserts) {
            var underFold = false;
            var counter = 0;
            $(".paragraph, .stanza").each(function() {
                var p = $(this);
                if (p.prev().hasClass('anchor')) p = p.prev();
                if (!underFold) {
                    if (p.offset().top > fold) {
                        underFold = true;
                    }
                }
                if (underFold) {
                    if (inserts[0].attr('data-paragraphs') == counter) {
                        insert = inserts.shift();
                        insert.insertBefore(p);
                    }
                    counter += 1;
                }
                return inserts.length > 0;
            });
        };

        
    });
})(jQuery);
