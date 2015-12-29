var s = $('#id_qq');
var url = s.attr('data-source');
s.search({
    source: function(req, cb) {
        $.ajax({url: url,
            dataType: "jsonp",
            data: {term: req.term},
            type: "GET",
            success: function(data) {cb(data);},
            error: function() {cb([]);}
        });
    },
    dataType: "jsonp",
    select: function(event, ui) {
        if (ui.item.url != undefined) {
            window.top.location.href = '//wolnelektury.pl' + ui.item.url;
        } else {
            $('form').submit();
        }
    },
    position: {
        my: "center bottom",
        at: "center bottom",
        of: "#wl a"
    },
});
