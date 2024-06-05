(function($){$(function(){

    class PBox {
        items = [];

        constructor(element) {
            this.$element = element;
        }

        addItem(item) {
            this.items.unshift(item);
        }

        clear() {
            $("div", this.$element).remove();
        }

        showButton(item, text, cls) {
            let btn = $("<div>");
            btn.addClass('zakladka-tool');
            btn.addClass('cls');
            btn.text(text);
            btn.on('click', item.action);
            this.$element.append(btn);
        }

        // What's a p?
        // We should open at a *marker*.
        // And it's the marker that should know its context.
        openAt(marker) {
            this.marker = marker;
            this.clear();
            $.each(this.items, (i, item) => {
                item.update(this);
            });
        }

        close() {
        }
    }

    $.pbox = new PBox($('#zakladka-box'));  // TODO: rename id


    
})})(jQuery);
