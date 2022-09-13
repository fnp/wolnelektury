(function($){$(function(){


$("#menu-settings").show();

$(".settings-switch").click(function(e) {
    e.preventDefault();
    $("body").toggleClass($(this).attr("data-setting"));
    _paq.push(['trackEvent', 'html', $(this).attr("data-setting")]);
});


})})(jQuery);
