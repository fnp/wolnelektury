/*
 * jQuery Shorten plugin 1.1.0
 *
 * Copyright (c) 2014 Viral Patel
 * http://viralpatel.net
 *
 * Licensed under the MIT license:
 *   http://www.opensource.org/licenses/mit-license.php
 */

/*
** updated by Jeff Richardson
** Updated to use strict,
** IE 7 has a "bug" It is returning undefined when trying to reference string characters in this format
** content[i]. IE 7 allows content.charAt(i) This works fine in all modern browsers.
** I've also added brackets where they weren't added just for readability (mostly for me).
*/

/*
** largely modified by Jan Szejko
** Now it doesn't shorten the text, just changes adds a class and lets CSS do the rest
 */

(function($) {
    $.fn.shorten = function(settings) {
        "use strict";

        var config = {
            showChars: 100,
            minHideChars: 10,
            moreText: "more",
            lessText: "less",
            onLess: function() {},
            onMore: function() {},
            errMsg: null,
            force: false
        };

        if (settings) {
            $.extend(config, settings);
        }

        if ($(this).data('jquery.shorten') && !config.force) {
            return false;
        }
        $(this).data('jquery.shorten', true);

        $(document).off("click", '.morelink');

        $(document).on({
            click: function() {

                var $this = $(this), $main = $this.prev();
                if ($main.hasClass('short')) {
                    $main.removeClass('short');
                    $this.html(config.lessText);
                    config.onMore();
                } else {
                    $main.addClass('short');
                    $this.html(config.moreText);
                    config.onLess();
                }
                return false;
            }
        }, '.morelink');

        return this.each(function() {
            var $this = $(this);
            var button = '<a href="javascript:void(0)" class="morelink">' + config.moreText + '</a></span>';
            $this.addClass('short');
            $this.after(button);
        });

    };

})(jQuery);
