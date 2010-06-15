/*
 * jQuery Event Delegation Plugin - jquery.eventdelegation.js
 * Fast flexible event handling
 *
 * January 2008 - Randy Morey (http://dev.distilldesign.com/)
 */

(function ($) {
	/* setup list of allowed events for event delegation
	 * only events that bubble are appropriate
	 */
	var allowed = {};
	$.each([
		'click',
		'dblclick',
		'mousedown',
		'mouseup',
		'mousemove',
		'mouseover',
		'mouseout',
		'keydown',
		'keypress',
		'keyup'
		], function(i, eventName) {
			allowed[eventName] = true;
	});

	$.fn.extend({
		delegate: function (event, selector, f) {
			return $(this).each(function () {
				if (allowed[event])
					$(this).bind(event, function (e) {
						var el = $(e.target),
							result = false;

						while (!$(el).is('body')) {
							if ($(el).is(selector)) {
								result = f.apply($(el)[0], [e]);
								if (result === false)
									e.preventDefault();
								return;
							}

							el = $(el).parent();
						}
					});
			});
		},
		undelegate: function (event) {
			return $(this).each(function () {
				$(this).unbind(event);
			});
		}
	});
})(jQuery);