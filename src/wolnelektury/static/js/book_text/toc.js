(function($){$(function(){

    if ($("#toc a").length > 0) {
        $("#toc > ol").appendTo($("#heretoc"));
    }

    if ($('#wltoc li').length > 0) {
        $('a[href="#wltoc"]').show();
    }

    if ($('#wltoc li a').length == 0) {
        $('a[href="#wltoc"]').remove();
    }

    $("#toc").remove();

})})(jQuery);
