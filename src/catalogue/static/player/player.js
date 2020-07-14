(function($) {
    $(function() {

      $(".jp-jplayer").each(function() {
      	var $self = $(this);
        var $root = $self.parent();
        var $number = $('.number', $root);
        $self.jPlayer({
            swfPath: "/static/jplayer/",
            solution: "html,flash",
            supplied: $self.attr('data-supplied'),
            cssSelectorAncestor: "#" + $self.attr("data-player"),

            ready: function() {
                var player = $(this);
                var setMedia = function(elem, time=0) {
                    var li = $(elem).parent();
                    var media = {}

                    media['mp3'] = li.attr('data-mp3');
                    media['oga'] = li.attr('data-ogg');
                    media['id'] = li.attr('data-media-id');

                    $(".title", $root).html(li.html());
                    player.jPlayer("setMedia", media);
                    player.jPlayer("pause", time);
                    return player;
                };

                $('.play-next', $root).click(function() {
                    var next = parseInt($number.text()) + 1;
                    var p = $('.play:eq(' + next + ')', $root);
                    if (p.length) {
                        setMedia(p).jPlayer("play");
                        $number.text(next)
                    }
                });
                $('.play-prev', $root).click(function() {
                    var next = parseInt($number.text()) - 1;
                    if (next < 1)
                        return;
                    var p = $('.play:eq(' + next + ')', $root);
                    setMedia(p).jPlayer("play");
                    $number.text(next)
                });

                var initialElem = $('.play', $root).first();
                var initialTime = 0;
                if (Modernizr.localstorage) {
                    try {
                        audiobooks = JSON.parse(localStorage["audiobook-history"]);
                    } catch {
                        audiobooks = {};
                    }
                    last = audiobooks[$root.attr("data-book-slug")]
                    // Fallback for book id;
                    if (!last) {
                        last = audiobooks[$root.attr("data-book-id")]
                    }

                    if (last) {
                        initialElem = $('[data-media-id="' + last[1] + '"] .play', $root).first();
                        initialTime = last[2];
                    }
                }
                setMedia(initialElem, initialTime);
            },

            timeupdate: function(event) {
                if (event.jPlayer.status.currentTime && Modernizr.localstorage) {
                    try {
                        audiobooks = JSON.parse(localStorage["audiobook-history"]);
                    } catch {
                        audiobooks = {};
                    }
                    t = event.jPlayer.status.currentTime;
                    if (t && event.jPlayer.status.duration - t > 10) {
                        audiobooks[$root.attr("data-book-slug")] = [
                            Date.now(),
                            event.jPlayer.status.media.id,
                            event.jPlayer.status.currentTime
                        ];
                    } else {
                        delete audiobooks[$root.attr("data-book-slug")];
                    }
                    // Remove old book id, if present.
                    delete audiobooks[$root.attr("data-book-id")];
                    localStorage["audiobook-history"] = JSON.stringify(audiobooks);
                }
            }
        });
      });



    });
})(jQuery)
