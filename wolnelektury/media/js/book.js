$(function() {
    $('#toc').hide();
    
    if ($('#toc li').length == 0) {
        $('#menu li a[href="#toc"]').remove();
    }
    
    $('#toc a').click(function(event) {
        event.preventDefault();
        $('#menu li a.selected[href="#toc"]').click();
        $.scrollTo('a[name="' + $(this).attr('href').slice(1) + '"]', {offset: {top: -50, left: 0}});
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
