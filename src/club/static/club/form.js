$(function() {

    function update_methods() {
        $("#payment-form .payment-method").addClass("disabled");
        $("#payment-form .payment-method input").prop("disabled", true);
        var plan = $("#payment-form .plan:checked");
        if (plan.length) {
            $.each(
                $("#payment-form .plan:checked").attr('data-methods').trim().split(" "),
                function(i, slug) {
                    $("#payment-method-" + slug).removeClass("disabled");
                    $("#payment-method-" + slug + " input").prop("disabled", false);
                }
            );
        }
    }
    update_methods();
    $("#payment-form .plan").change(update_methods);


    function qs(key) {
        key = key.replace(/[*+?^$.\[\]{}()|\\\/]/g, "\\$&"); // escape RegEx meta chars
        var match = location.search.match(new RegExp("[?&]"+key+"=([^&]+)(&|$)"));
        return match && decodeURIComponent(match[1].replace(/\+/g, " "));
    }

    $("#payment-form").submit(function() {
        let camp = qs('pk_campaign');
        if (!camp && window.location.pathname !== "/towarzystwo/") {
            camp = window.location.pathname;
        }
        let dims = camp ? {dimension2: camp} : {};
        _paq.push(['trackGoal', 12, parseFloat($("#id_amount").val()), dims]);
    });
});
