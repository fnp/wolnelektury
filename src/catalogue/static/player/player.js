(function($) {
    $(function() {

        $(".book-right-column").remove();

        if ($("#player-bar").length) {
            $("#book-text-buttons").append(
                $("<a class='enable-player-bar'><i class='icon icon-play'></i> zacznij słuchać</a>")
            ).show();
        }
        
        $(".enable-player-bar").click(function() {
            
            $('body').addClass('with-player-bar');
            $('.jp-play').click();
            return false;
        })

                                      
        var smil = $("#smil").text();
        if (smil) {
            smil = $.parseJSON(smil);

            $.each(smil, function(i, e) {
                $('#' + e).addClass('syncable');
            })
        }


        scrolling = false;
        /*$(window).on('scroll', function() {
            if (!scrolling) {
                $("#locator").removeClass('snap');
            }
        });*/

        lastscroll = null;
        
        scrollTo = function() {
            if (!scrolling && $('.playing-highlight').length && $('.playing-highlight')[0] != lastscroll) {
                lastscroll = $('.playing-highlight')[0];
                scrolling = true;
                $("html").animate({
                    scrollTop: $('.playing-highlight').offset().top,
                }, {
                    duration: 2000,
                    done: function() {
                        scrolling = false;
                        
                    },
                });
            }
        }

        
        $.jPlayer.timeFormat.showHour = true;

        $(".jp-jplayer").each(function() {
            var $self = $(this);
            
            var $root = $self.parent();
            var $currentMedia = null
            var currentDuration = 0;
            var speed = 1;
            var totalDurationLeft = 0;
            var totalDurationBefore = 0;
            var lastUpdate = 0;
            var player = null;
            var doesUpdateSynchro = true;

            // TODO: will need class for attach
            // may be added from sync data


            $(".zakladka-tool_sluchaj").click(function() {
                $('body').addClass('with-player-bar');
                let id = $(this).data('sync');
                if (!id) return;
                for (let i=0; i<smil.length; ++i) {
                    if (smil[i][0] == id) {
                        setMediaFromTime(smil[i][1], 'play');
                        //player.jPlayer('play');
                        return;
                    }
                }
            });

            var setMediaFromTime = function(time, cmd='pause') {
                $('.jp-playlist li', $root).each((i, e) => {
                    d = parseFloat($(e).data('duration'));
                    if (time < d) {
                        setMedia($(e), time, cmd);
                        return false
                    } else {
                        time -= d;
                    }
                })
            }
            
            var setMedia = function(elem, time=0, cmd='pause') {
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

                console.log('sm 1');
                doesUpdateSynchro = false;
                if (!$currentMedia || $currentMedia[0] != elem[0]) {
                    console.log('set', player.jPlayer("setMedia", media))
                    player.jPlayer("option", "playbackRate", speed);
                }
                doesUpdateSynchro = true;
                player.jPlayer(cmd, time);

                $currentMedia = elem;
                $(".play-next", $root).prop("disabled", !elem.next().length);

                let du = parseFloat(elem.data('duration'));
                currentDuration = du;
                elem.nextAll().each(function() {
                    du += parseFloat($(this).data('duration'));
                });
                totalDurationLeft = du;

                let pdu = 0;
                elem.prevAll().each(function() {
                    pdu += parseFloat($(this).data('duration'));
                });
                totalDurationBefore = pdu;
                console.log('sm 3', du, pdu);

                return player;
            };


            var updateSynchrotext = function(position) {
                if (!doesUpdateSynchro) return;
                
                let curElemId = null;
                for (let i=0; i<smil.length; ++i) {
                    // can faster
                    if (smil[i][1] <= position) curElemId = smil[i][0];
                    else break;
                }
                $(".playing-highlight").removeClass("playing-highlight");
                if (curElemId !== null) {
                    let curElem = $("#" + curElemId);
                    curElem.addClass("playing-highlight");

                    let miny = window.scrollY;
                    let maxy = miny + window.innerHeight;
                    let y = curElem.offset().top;

                    let locator = $("#locator");
                    // TODO: if snap then roll
                    locator.removeClass('up').removeClass('down');
                    if (locator.hasClass('snap')) {
                        console.log('SCROLL!');
                        scrollTo();
                    } else {
                        if (y < miny) {
                            locator.addClass('up');
                        }
                        if (y > maxy) {
                            locator.addClass('down');
                        }
                    }
                }
            }
            
        $self.jPlayer({
            swfPath: "/static/js/contrib/jplayer/",
            solution: "html,flash",
            supplied: 'oga,mp3',
            cssSelectorAncestor: "#" + $self.attr("data-player"),
            useStateClassSkin: true,

            ready: function() {
                player = $(this);

                let selectItem = $('.c-select li');
                selectItem.on('click', function() {
                    let speedStr = $(this).data('speed');
                    speed = parseFloat(speedStr);
                    player.jPlayer("option", "playbackRate", speed);
                    localStorage['audiobook-speed'] = speedStr;
                    _paq.push(['trackEvent', 'audiobook', 'speed', speedStr]);
                });
                
                $('.jp-play', $root).click(function() {
                    _paq.push(['trackEvent', 'audiobook', 'play']);
                });
                $('.jp-seek-bar', $root).click(function() {
                    _paq.push(['trackEvent', 'audiobook', 'seek']);
                });
                $('.jp-mute', $root).click(function() {
                    _paq.push(['trackEvent', 'audiobook', 'mute']);
                });
                $('.jp-volume-bar', $root).click(function() {
                    _paq.push(['trackEvent', 'audiobook', 'volume']);
                });

                $('.play-next', $root).click(function() {
                    let p = $currentMedia.next();
                    if (p.length) {
                        setMedia(p).jPlayer("play");
                        _paq.push(['trackEvent', 'audiobook', 'next']);
                    }
                });
                $('.play-prev', $root).click(function() {
                    let p = $currentMedia.prev();
                    if (p.length) {
                        setMedia(p).jPlayer("play");
                        _paq.push(['trackEvent', 'audiobook', 'prev']);
                    } else {
                        // If in first part, restart it.
                        setMedia($currentMedia).jPlayer("play");
                        _paq.push(['trackEvent', 'audiobook', 'rewind']);
                    }
                });

                $('.jp-playlist li', $root).click(function() {
                    setMedia($(this)).jPlayer("play");
                    $('.c-player__chapters').removeClass('is-active');
                    _paq.push(['trackEvent', 'audiobook', 'chapter']);
                });

                console.log('READY 3!');
                var initialElem = $('.jp-playlist li', $root).first();
                var initialTime = 0;
                console.log('READY 4!');
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
                console.log('READY 5!', initialElem, initialTime);
                setMedia($(initialElem), initialTime);
                console.log('READY 6!');
            },

            timeupdate: function(event) {
                t = event.jPlayer.status.currentTime;

                updateSynchrotext(totalDurationBefore + t);
                
                
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
            },


            ended: function(event) {
                let p = $currentMedia.next();
                if (p.length) {
                    setMedia(p).jPlayer("play");
                }
            }
        });
      });


   $('#locator').on('click', function() {
       $(this).toggleClass('snap');
       lastscroll = null;
   });

        

    });
})(jQuery)
