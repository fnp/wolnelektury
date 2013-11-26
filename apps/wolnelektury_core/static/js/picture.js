
(function($) {
  $.widget('wl.pictureviewer', {

    options: {
      steps: 6, // steps of zoom
      max: 300, // max zoom in percent
      plus_button: undefined,
      minus_button: undefined
    },

    _create: function() {
      var self = this;
      self._zoom = 0;
      self.initial_size = [ 
	self.element.width(),
	self.element.height()
      ];
      self.initial_position = self.element.offset();

      self.element.css({
	'margin': 0,
	'position': 'absolute',
      });
      self.element.offset(self.initial_position);

      if (self.options.plus_button)
	self.options.plus_button.click(
	  function(ev) { self.zoom(1); });
      if (self.options.minus_button)
	self.options.minus_button.click(
	  function(ev) { self.zoom(-1); });

      function contain(event, ui) {
	var fix = self.allowedPosition(ui.position);
	console.log("fix: ", fix);
	if (fix !== undefined) {
	  return false;
	};
      };
      self.element.draggable({drag: contain});

      return self;
    },

    zoom: function(steps) {
      var t = this._zoom + steps;
      return this.zoomTo(t);
    },

    zoomForStep: function(step) {
      // 0 => initial
      // max_step-1 => max %
      return 100 + (this.options.max - 100) / this.options.steps * step
    },

    zoomTo: function(level) {
      if (level < 0 || level > this.options.steps)
	return;
      var ratio = this.zoomForStep(level) / 100;
      var new_width  = ratio * this.initial_size[0];
      var new_height = ratio * this.initial_size[1];
      var target = {
	'width': new_width,
	'left': this.initial_position.left - (new_width - this.initial_size[0])/2,
	'top': this.initial_position.top - (new_height - this.initial_size[1])/2,
      };
      this._zoom = level;
      this.element.animate(target, 200); // default duration=400
    },

    allowedPosition: function(off) {
      var x = undefined, fix_x = undefined;
      var y = undefined, fix_y = undefined;
      var w = this.element.width();
      var h = this.element.height();
      var cw = $(window).width();
      var ch = $(window).height();
      var off = off || this.element.offset();

      if (w <= cw) {
	var x = off.left;
	if (x < 0) 
	  fix_x = 0;
	if (x + w > cw)
	  fix_x = cw - w;
      } else {
	if (x > 0)
	  fix_x = 0;
	if (x + w < cw)
	  fix_x = cw - w;
      }

      if (h <= ch) {
	var y = off.top;
	if (y < 0)
	  fix_y = 0;
	if (y + h > ch)
	  fix_y = ch - h;
      } else {
	if (y > 0)
	  fix_y = 0;
	if (y + h < ch)
	  fix_y = ch - h;
      }
      if (fix_x !== undefined || fix_y !== undefined)
	return { top: fix_y, left: fix_x };
      return undefined;

    },
  });
}(jQuery));


$(document).ready(function(){
  $("img.canvas").pictureviewer({
    plus_button: $(".toolbar .button.plus"),
    minus_button: $(".toolbar .button.minus")
  });
});

