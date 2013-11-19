(function($){$(function(){


if ($('#themes li').length > 0) {
    $("#menu-themes").show();
}


$(".theme-begin").click(function(e) {
    e.preventDefault();
    if ($(this).css("overflow") == "hidden" || $(this).hasClass('showing')) {
        $(this).toggleClass("showing");
    }
});

})})(jQuery);
