(function($){
    $(function() {


        if (Modernizr.localstorage) {
            try {
                audiobooks = JSON.parse(localStorage["audiobook-history"]);
            } catch {
                audiobooks = {};
            }

            latest = [];
            Object.keys(audiobooks).forEach(function(slug) {
                [ts, media_id, time] = audiobooks[slug];
                latest.push([ts, slug]);
            });
            latest.sort().reverse().forEach(function(item) {
                [ts, slug] = item;
                $newitem = $('<div style="display:inline-block;"></div>');  // remove from history
                $("#last-audiobooks").append($newitem);
                (function($box) {
                    $.get(
                        "/katalog/lektura/" + slug + "/mini_box.html",
                        function(data) {
                            console.log(data);
                            $box.html(data);
                            $("#personal-history").slideDown("slow");
                        }).fail(function() {
                            $box.remove();
                        });
                })($newitem);
            });
        }
    });
})(jQuery);
