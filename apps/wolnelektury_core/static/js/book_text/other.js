(function($){$(function(){


$("#menu-other").show();


$(".display-other").click(function(e) {
    e.preventDefault();

    if ($('#big-pane').length == 0)
        $("#other-text").show();
    $("#other-versions").slideUp('fast');
    $(".menu").removeClass('selected');

    $("#other").hide();
    $("nav .active").removeClass('active');
    $("body").addClass('with-other-text');

    $.ajax($(this).attr('data-other'), {
        success: function(text) {
            $("#other-text-body").html(text);
            $("#other-text-waiter").hide();
            $("#other-text-body").show();
        }
    });
});


$("#other-text-close").click(function(e) {
    e.preventDefault();
    if ($('#big-pane').length == 0)
        $("#other-text").hide();
    $("body").removeClass('with-other-text');
});

})})(jQuery);
