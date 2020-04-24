(function($){$(function(){

    if ($("#toc a").length > 0) {
        $("#toc > ol").appendTo($("#heretoc"));
    }

    if ($('#wltoc li').length > 0) {
        $('#menu-toc').show();
    }

    if ($('#wltoc li a').length == 0) {
        $('#menu li a[href="#wltoc"]').remove();
    }

    $("#toc").remove();

})})(jQuery);
