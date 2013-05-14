$(function() {
    $('.funding .close').click(function(e) {
        e.preventDefault();
        var fundNode = $(e.target).parent();
        fundNode.slideUp(function(){fundingHandle.show()});
        if(Modernizr.localstorage)
            localStorage['hide-offer-id'] = fundNode.attr('data-offer-id');
    });
        

    var fundingTopHeader = $('.funding-top-header');
    var fundingHandle = $('.funding-handle');
    if(fundingTopHeader) {
        var currentOfferId = fundingTopHeader.attr('data-offer-id');
        var toggle = true;
        if(Modernizr.localstorage) {
            toggle = localStorage['hide-offer-id'] !== currentOfferId;
        }
        fundingTopHeader.toggle(toggle);
        fundingHandle.toggle(!toggle);
    }
    fundingHandle.click(function(e) {
        fundingTopHeader.slideDown();
        $(e.target).hide();
        localStorage.removeItem('hide-offer-id');
    });
});