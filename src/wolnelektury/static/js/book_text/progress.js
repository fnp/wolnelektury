(function($){$(function(){

    t = $('#global-progress').data('t');
    function upd_t() {
        $text = $('#main-text #book-text');
        texttop = $text.offset().top;

        $footnotes = $('#footnotes', $text);
        if ($footnotes.length) {
            textbottom = $footnotes.offset().top;
        } else {
            textbottom = texttop + $text.height();
        }

        textlen = textbottom - texttop;
        progress = (window.scrollY - texttop) / textlen;
        progress = Math.max(0, Math.min(progress, 1))
        console.log('SCROLL BODY', progress);

        $('#global-progress .filled').css('right', (1 - progress) * 100 + '%');
        tleft = Math.round((1 - progress) * t / 60);
        tt = '';
        if (tleft > 60) {
            h = Math.floor(tleft / 60);
            tt = h + ' h ';
            tleft -= h * 60;
        }
        tt += tleft + ' min';
        $('#global-progress .progress-text-value').text(tt);
    }
    upd_t();
    $(window).scroll(upd_t);
})})(jQuery);
