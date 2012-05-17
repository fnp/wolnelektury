
var __bind = function (self, fn) {
    return function() { fn.apply(self, arguments); };
};

(function($){
    $.widget("wl.search", {
	options: {
          minLength: 0,
	  dataType: "json",
        },

	_create: function() {
            console.log("dataType: " + this.options.dataType);
            var url = this.element.data('source');
	    var opts = { 
		minLength: this.options.minLength,
		select: __bind(this, this.enter),
		focus: function() { return false; },
		source: function(req, cb) {
                    $.ajax({url: url,
                            dataType: "jsonp",
                            type: "GET",
                            success: function(data) {
                                cb(data);
                            },
                            error: function() { cb([]); }

                });
                },
	    };

	    this.element.autocomplete($.extend(opts, this.options))
		.data("autocomplete")._renderItem = __bind(this, this.render_item);
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
		.append('<a href="'+item.url+'"><span class="search-hint-label">'+item.label+'</span>'+
			'<span class="search-hint-category mono">'+item.category+'</span></a>')
		.appendTo(ul);
	}, 

	destroy: function() {

	},
	

    });


})(jQuery);
