(function($){$(function(){


$('#menu-toggle-on').click(function(e) {
    e.preventDefault();
    var body = $("body");
    body.removeClass("menu-hidden");
    if (!$("#menu").is(":visible")) {
        body.addClass("menu-showed");
    }
});

$('#menu-toggle-off').click(function(e) {
    e.preventDefault();
    var body = $("body");
    body.removeClass("menu-showed");
    if ($("#menu").is(":visible")) {
        body.addClass("menu-hidden");
    }
});



})})(jQuery);
