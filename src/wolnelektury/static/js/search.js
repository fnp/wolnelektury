
var __bind = function (self, fn) {
    return function() { fn.apply(self, arguments); };
};

(function($){
    $.widget("wl.search", {
        options: {
              minLength: 0,
          dataType: "json",
              host: ''
            },

        _create: function() {
            var opts = {
            minLength: this.options.minLength,
            select: __bind(this, this.enter),
            focus: function() { return false; },
                    source: this.element.data('source')
            };

            this.element.autocomplete($.extend(opts, this.options))
            .data("autocomplete")._renderItem = __bind(this, this.render_item);
        },

        enter: function(event, ui) {
            if (ui.item.url !== undefined) {
            location.href = this.options.host+ui.item.url;
            } else {
            this.element.closest('form').submit();
            }
        },

        render_item: function (ul, item) {
            var label;
            if (item['author']) {
                label = '<cite>' + item.label + '</cite>, ' + item['author'];
            } else {
                label = item.label;
            }
            return $("<li></li>").data('item.autocomplete', item)
            .append('<a href="'+this.options.host+item.url+'"><span class="search-hint-label">'+label+'</span>')
            .appendTo(ul);
        },

        destroy: function() {
        }
    });

})(jQuery);
