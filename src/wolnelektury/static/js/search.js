
var __bind = function (self, fn) {
    return function() { return fn.apply(self, arguments); };
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

            this.element.autocomplete($.extend(opts, this.options));
            if (this.element.autocomplete('instance') !== undefined) this.element.autocomplete('instance')._renderItem = __bind(this, this.render_item_2022);
            if (this.element.data('autocomplete') !== undefined) this.element.data('autocomplete')._renderItem = __bind(this, this.render_item);;
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

        render_item_2022: function (ul, item) {
            var label;
            var $label = $("<li><a><div></div><span></span></a></li>");
            if (item.img) {
                $('div', $label).append($('<img>').attr('src', item.img));
            }
            if (item.author) {
                label = '<cite>' + item.label + '</cite>, ' + item['author'];
            } else {
                label = item.label;
            }
            $('span', $label).html(label);
            $label.addClass('type-' + item.type);
            $label.appendTo(ul);
            return $label;
        },

        destroy: function() {
        }
    });

})(jQuery);
