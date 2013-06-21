$(function() {
    function scrollToAnchor(anchor) {
        if (anchor) {
            var anchor_name = anchor.slice(1);
            var element = $('a[name="' + anchor_name + '"]');
            if (element.length > 0) {
                $.scrollTo(element, 500, {offset: {top: -50, left: 0}});
                foot_elem = $('#footnotes a[name="' + anchor_name + '"]');
                if (foot_elem.length > 0) {
                    $(element).parent().highlightFade('yellow');
                }
                window.location.hash = anchor;
            }
        }
    }

    $.highlightFade.defaults.speed = 3000;
    $('#toc').hide();
    if ($('#toc li').length == 0) {
        $('#menu li a[href="#toc"]').remove();
    }
    if ($('#themes li').length == 0) {
        $('#menu li a[href="#themes"]').remove();
    }
    if ($('#nota_red').length == 0) {
        $('#menu li a[href="#nota_red"]').remove();
    }

    // On page load, scroll to anchor
    scrollToAnchor(window.location.hash)

    $('#toc, #themes, #book-text').delegate('click', 'a', function(event) {
        event.preventDefault();
        $('#menu li a.selected').click();
        scrollToAnchor($(this).attr('href'));
    });

    $('#menu li a.menu').toggle(function() {
        $('#menu li a.selected').click();
        $(this).addClass('selected');
        $($(this).attr('href')).slideDown('fast');
    }, function() {
        $(this).removeClass('selected');
        $($(this).attr('href')).slideUp('fast');
    });
    

    if (window.getSelection) {
        $('.theme-begin').click(function() {
            var selection = window.getSelection();
            selection.removeAllRanges();
            var range = document.createRange();

            var e = $(".theme-end[fid='" + $(this).attr('fid') + "']")[0];

            if (e) {
                range.setStartAfter(this);
                range.setEndBefore(e);
                selection.addRange(range);
            }
        });
    }

});
