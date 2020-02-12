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
                var setMedia = function(elem) {
                    var li = $(elem).parent();
                    var media = {}

                    media['mp3'] = li.attr('data-mp3');
                    media['oga'] = li.attr('data-ogg');

                    $(".title", $root).html(li.html());
                    return player.jPlayer("setMedia", media);
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

                setMedia($('.play', $root).first());

            }
        });
      });



    });
})(jQuery)
