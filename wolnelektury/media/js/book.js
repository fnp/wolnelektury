$(function() {
    $.highlightFade.defaults.speed = 3000;
    
    $('#toc').hide();
    $.scrollTo('-=50px');
    
    if ($('#toc li').length == 0) {
        $('#menu li a[href="#toc"]').remove();
    }
    
    $('body').delegate('click', '#toc a, #themes a, .anchor, .annotation', function(event) {
        event.preventDefault();
        $('#menu li a.selected').click();
        if ($(this).attr('href')) {
            var name = $(this).attr('href').slice(1);
            $.scrollTo('a[name="' + name + '"]', 500, {offset: {top: -50, left: 0}});
            $('a[name="' + name + '"]').highlightFade('yellow');
        }
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
