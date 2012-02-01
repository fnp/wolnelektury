(function($) {
    $(function() {

      $("#jplayer").each(function() {
      	var $self = $(this);
        $self.jPlayer({
            swfPath: "/static/jplayer/",
            solution: "html,flash",
            supplied: $self.attr('data-supplied'),
    
            ready: function() {
                var player = $(this);
                var setMedia = function(elem) {
                    var li = $(elem).parent();
                    $('.jp-playlist-current').removeClass('jp-playlist-current');
                    $(li).addClass('jp-playlist-current');
                    var media = {}
    
                    $('.mp3', li).each(function() {media['mp3'] = $(this).attr('href')});
                    $('.ogg', li).each(function() {media['oga'] = $(this).attr('href')});
    
                    return player.jPlayer("setMedia", media);
                };
                setMedia($('.play').first()).jPlayer("play");
    
                $('.play').click(function() {
                    setMedia(this).jPlayer("play");
                });
            }
        });
      });

    });
})(jQuery)