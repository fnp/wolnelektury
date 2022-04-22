(function($) {
    $(function() {

        $.jPlayer.timeFormat.showHour = true;

        $(".jp-jplayer").each(function() {
            console.log('starting player')
            var $self = $(this);
            var $root = $self.parent();
            var $currentMedia = null
            var currentDuration = 0;
            var speed = 1;
            var totalDurationLeft = 0;
            var lastUpdate = 0;

        $self.jPlayer({
            swfPath: "/static/js/contrib/jplayer/",
            solution: "html,flash",
            supplied: 'oga,mp3',
            cssSelectorAncestor: "#" + $self.attr("data-player"),
            useStateClassSkin: true,

            ready: function() {
                var player = $(this);
                console.log(1);

                var setMedia = function(elem, time=0) {
                    console.log('setMedia', elem, time);
                    var media = {}

                    media['mp3'] = elem.attr('data-mp3');
                    media['oga'] = elem.attr('data-ogg');
                    media['id'] = elem.attr('data-media-id');

                    $(".c-player__head", $root).html(
                        $(".attribution", elem).html())
                    ;
                    $(".c-player__info", $root).html(
                        $(".title", elem).html()
                    );
                    $(".c-media__caption .content", $root).html($(".project-description", elem).html());
                    $(".c-media__caption .license", $root).html($(".license", elem).html());
                    $(".c-media__caption .project-logo", $root).html($(".project-icon", elem).html());
                    
                    player.jPlayer("setMedia", media);
                    $("audio")[0].playbackRate = speed;
                    player.jPlayer("pause", time);

                    $currentMedia = elem;
                    $(".play-prev", $root).prop("disabled", !elem.prev().length);
                    $(".play-next", $root).prop("disabled", !elem.next().length);

                    let du = elem.data('duration');
                    currentDuration = du;
                    elem.nextAll().each(function() {
                        du += $(this).data('duration');
                    });
                    totalDurationLeft = du;

                    return player;
                };

                let selectItem = $('.c-select li');
                selectItem.on('click', function() {
                    let speedStr = $(this).data('speed');
                    speed = parseFloat(speedStr);
                    $("audio")[0].playbackRate = speed;
                    localStorage['audiobook-speed'] = speedStr;
                });
                
                $('.play-next', $root).click(function() {
                    let p = $currentMedia.next();
                    if (p.length) {
                        setMedia(p).jPlayer("play");
                    }
                });
                $('.play-prev', $root).click(function() {
                    let p = $currentMedia.prev();
                    if (p.length) {
                        setMedia(p).jPlayer("play");
                    }
                });

                $('.jp-playlist li', $root).click(function() {
                    setMedia($(this)).jPlayer("play");
                    $('.c-player__chapters').removeClass('is-active');
                });

                var initialElem = $('.jp-playlist li', $root).first();
                var initialTime = 0;
                if (true || Modernizr.localstorage) {
                    try {
                        let speedStr = localStorage['audiobook-speed'];
                        if (speedStr) {
                            speed = parseFloat(speedStr);
                            $(".speed .is-active").removeClass("is-active");
                            $(".speed [data-speed='" + speedStr + "']").addClass("is-active");
                        }
                    } catch {}

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
                        initialElem = $('[data-media-id="' + last[1] + '"]', $root).first();
                        initialTime = last[2];
                    }
                }
                setMedia(initialElem, initialTime);
            },

            timeupdate: function(event) {
                t = event.jPlayer.status.currentTime;
                ttl = (totalDurationLeft - t) / speed;
                ttl = $.jPlayer.convertTime(ttl);
                $(".total-time-left").text('Czas do końca: ' + ttl);

                $(".time-left").text('– ' + $.jPlayer.convertTime(
                    currentDuration - t,
                ));
                
                
                if (Math.abs(t - lastUpdate) > 3) {
                    try {
                        audiobooks = JSON.parse(localStorage["audiobook-history"]);
                    } catch {
                        audiobooks = {};
                    }
                    if (t && event.jPlayer.status.duration - t > 10) {
                        console.log('writer');
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
                    lastUpdate = t;
                }
            }
        });
      });



    });
})(jQuery)
