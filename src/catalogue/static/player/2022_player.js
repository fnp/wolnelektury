(function($) {
    $(function() {

        $(".jp-jplayer").each(function() {
            console.log('starting player')
      	var $self = $(this);
        var $root = $self.parent();

            //  //  var $number = $('.number', $root);
        $self.jPlayer({
            swfPath: "/static/jplayer/",
            solution: "html,flash",
            supplied: 'oga,mp3',
            cssSelectorAncestor: "#" + $self.attr("data-player"),

            ready: function() {
                var player = $(this);
                console.log(1);

                var setMedia = function(elem, time=0) {
                    console.log('setMedia', elem, time);
                    var media = {}

                    media['mp3'] = elem.attr('data-mp3');
                    media['oga'] = elem.attr('data-ogg');
                    media['id'] = elem.attr('data-media-id');

                    $(".c-player__title", $root).html($(".title", elem).html());
                    $(".c-player__info", $root).html($(".attribution", elem).html());
                    $(".c-media__caption .content", $root).html($(".project-description", elem).html());
                    $(".c-media__caption .license", $root).html($(".license", elem).html());
                    $(".c-media__caption .project-logo", $root).html($(".project-icon", elem).html());
                    
                    player.jPlayer("setMedia", media);
                    player.jPlayer("pause", time);
                    return player;
                };

                $('.play-next', $root).click(function() {
                    var next = parseInt($number.text()) + 1;
                    var p = $('.jp-playlist .play:eq(' + (next - 1) + ')', $root);
                    if (p.length) {
                        setMedia(p).jPlayer("play");
                        $number.text(next)
                    }
                });
                $('.play-prev', $root).click(function() {
                    var next = parseInt($number.text()) - 1;
                    if (next < 1)
                        return;
                    var p = $('.jp-playlist .play:eq(' + (next - 1) + ')', $root);
                    setMedia(p).jPlayer("play");
                    $number.text(next)
                });

                console.log(1);

                var initialElem = $('.jp-playlist li', $root).first();
                var initialTime = 0;
                if (true || Modernizr.localstorage) {
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
                        $number.text($(".jp-playlist .play", $root).index(initialElem) + 1);
                    }
                }
                setMedia(initialElem, initialTime);
            },

            timeupdate: function(event) {
                //event.jPlayer.status.currentTime
                
                
                if (true || (event.jPlayer.status.currentTime && Modernizr.localstorage)) {
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
