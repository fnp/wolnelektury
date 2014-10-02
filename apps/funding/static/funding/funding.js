$(function() {
    $('.funding .close').click(function(e) {
        e.preventDefault();
        var fundNode = $(e.target).parent();
        fundNode.slideUp(function(){fundingHandle.show()});
        if(Modernizr.localstorage)
            localStorage['hide-offer-id'] = fundNode.attr('data-offer-id');
    });

    var fundingTopHeader = $('#funding-closeable');
    var fundingHandle = $('#funding-handle');
    fundingHandle.click(function(e) {
        fundingTopHeader.slideDown();
        $(e.target).hide();
        if(Modernizr.localstorage)
            localStorage.removeItem('hide-offer-id');
    });
});