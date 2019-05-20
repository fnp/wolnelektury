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
    
});
