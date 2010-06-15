$(function() {
    function scrollToAnchor(anchor) {
        if (anchor) {
            var element = $('a[name="' + anchor.slice(1) + '"]');
            if (element.length > 0) {
                $.scrollTo(element, 500, {offset: {top: -50, left: 0}});
                $(element).highlightFade('yellow');
                window.location.hash = anchor;
            }
        }
    }

    $.highlightFade.defaults.speed = 3000;
    $('#toc').hide();
    if ($('#toc li').length == 0) {
        $('#menu li a[href="#toc"]').remove();
    }

    // On page load, scroll to anchor
    scrollToAnchor(window.location.hash)

    $('#toc, #themes, #book-text').delegate('click', 'a', function(event) {
        event.preventDefault();
        $('#menu li a.selected').click();
        scrollToAnchor($(this).attr('href'));
    });

    $('#menu li a').toggle(function() {
        $('#menu li a.selected').click();
        $(this).addClass('selected');
        $($(this).attr('href')).slideDown('fast');
    }, function() {
        $(this).removeClass('selected');
        $($(this).attr('href')).slideUp('fast');
    });
});
