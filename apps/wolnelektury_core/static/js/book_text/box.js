$(function() {
    /* Toggle hidden box on click. */
    $("nav a[data-box]").each(function() {
        $("#" + $(this).attr("data-box")).hide();

        $(this).click(function(e) {
            e.preventDefault();
            var showing = $(this).hasClass("active");
            $("nav .active").each(function() {
                $(this).removeClass("active");
                $("#" + $(this).attr("data-box")).hide();
            });
            if (!showing) {
                $(this).addClass("active");
                $("#" + $(this).attr("data-box")).show();
            }
        });
    });
});
