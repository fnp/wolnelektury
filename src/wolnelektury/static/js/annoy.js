(function($) {
    $(function() {

var tag = "annoyed2019wspieraj";

$("#annoy-on").click(function(e) {
    e.preventDefault();
    $("#annoy").slideDown('fast');
    $(this).hide();
    if (Modernizr.localstorage) localStorage.removeItem(tag);
});

$("#annoy-off").click(function() {
    $("#annoy").slideUp('fast');
    $("#annoy-on").show();
    if (Modernizr.localstorage) localStorage[tag] = true;
});


if (Modernizr.localstorage) {
    if (!localStorage[tag]) {
        $("#annoy-on").hide();
        $("#annoy").show();
    }
}



    });
})(jQuery);
