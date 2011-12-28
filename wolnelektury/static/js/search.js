
var __bind = function (self, fn) {
    return function() { fn.apply(self, arguments); };
};

(function($){
    $.widget("wl.search", {
	options: {
          minLength: 0,
        },

	_create: function() {
	    var opts = { 
		minLength: this.options.minLength,
		select: __bind(this, this.enter),
		focus: function() { return false; },
		source: this.element.data('source'),
	    };
	    this.element.autocomplete(opts).data("autocomplete")._renderItem = __bind(this, this.render_item);
	},

	enter: function(event, ui) {
	    if (ui.item.url != undefined) {
		location.href = ui.item.url;
	    } else {
		this.element.closest('form').submit();
	    }
	},
   
	render_item: function (ul, item) {
	    return $("<li></li>").data('item.autocomplete', item)
		.append('<a href="'+item.url+'">'+item.label+ ' ('+item.category+')</a>')
		.appendTo(ul);
	},

	destroy: function() {

	},
	


	});

    $(function() {
	$("#search-area input[name=q]").search();
	
    });

})(jQuery);
