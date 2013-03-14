(function($) {
    $(function() {


$("#annoy-on").click(function(e) {
    e.preventDefault();
    $("#annoy").slideDown('fast');
    $(this).hide();
    if (Modernizr.localstorage) localStorage.removeItem("annoyed2013");
});

$("#annoy-off").click(function() {
    $("#annoy").slideUp('fast');
    $("#annoy-on").show();
    if (Modernizr.localstorage) localStorage["annoyed2013"] = true;
});


if (Modernizr.localstorage) {
    if (!localStorage["annoyed2013"]) {
        $("#annoy-on").hide();
        $("#annoy").show();
    }
}



    });
})(jQuery);
