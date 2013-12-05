
(function($) {
  $.widget('wl.pictureviewer', {

    options: {
      steps: 6, // steps of zoom
      max: -1, // max zoom in percent
      plus_button: undefined,
      minus_button: undefined,
      height: 500, // height to scale to initially
    },


    _create: function() {
      var self = this;
      /* Calibrate */
      self._zoom = 0;

      // the initial thumbnailed picture


      var img = self.element.find('img.initial').get(0);

      self.initial_size = [ 
	img.naturalWidth,
	img.naturalHeight
      ];

      self.element.width(self.initial_size[0]);
      self.element.height(self.initial_size[1]);
      
      self.initial_position = self.element.offset();

      var original = self.element.find('img.original').get(0);
      self._original = false;
      self.original_loeaded = undefined; // callback
      self._original_loaded = false;

      self.spinner = $("#spinner").progressSpin();

      $(original).load(function() {
	self._original_loaded = true;
	self.spinner.stop();
	var cb = self.original_loaded;
	self.original_loaded = undefined;
	if (cb)
	  cb()
      });
      
      if (self.options.max <= 0) {
	self.options.max = original.naturalWidth
	  * 100 / self.initial_size[0];
      }

      self.element.css({
	'margin': 0,
      });

      self.element.offset(self.initial_position);
      self.element.draggable({containment:"parent"});

      if (self.options.plus_button)
	self.options.plus_button.click(
	  function(ev) { self.zoom(1); });
      if (self.options.minus_button)
	self.options.minus_button.click(
	  function(ev) { self.zoom(-1); });

      self.options.areas_links.hover(function() {
	$this = $(this);
	var coords = $this.data("coords");
	this._picture_mark = self.createMark({
	  label: $this.text(),
	  coords: coords,
	});
      }, function() {
	$(this._picture_mark).remove();
	this._picture_mark = undefined;
      });
      return self;
    },

    natural_size: function() { 
      var img = this.element.find('img').get(0);
      return [ img.naturalWidth, img.naturalHeight ] 
    },

    currentZoom: function() { return this._zoom; },

    initOriginal: function() {
      var self = this;
      function subst_original() {
	self.element.find("img.initial").remove();
	self.element.find("img.loading").removeClass("loading");
	self._original = true;
      }
      if (!this._original) {
	if (this._original_loaded) {
	  return subst_original();
	} else {
	  self.original_loaded = subst_original;
	  self.spinner.start();
	}
      }

    },

    zoom: function(steps) {
      this.initOriginal();
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
	'left': Math.max(0, 
			 this.initial_position.left 
			 - (new_width - this.initial_size[0])/2),
	'top': Math.max(0, 
			this.initial_position.top 
			- (new_height - this.initial_size[1])/2),
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

    // mark
    // {
    //  label: "...",
    //  coords: [x, y, w, h]
    // }
    createMark: function(mark) {
      var $mark = $('<div class="mark"><div class="label">' + 
		    mark.label + '</div></div>');
      var ratio = this.zoomForStep(this.currentZoom()) *
	this.initial_size[0] / (100 * this.natural_size()[0]);
      var scale = function (v) { 
	return v * ratio; 
      }
      if (mark.coords[1][0] < 0 || mark.coords[1][1] < 0) { // whole
	var s = self.natural_size();
	if (mark.coords[1][0] < 0) mark.coords[1][0] = s[0];
	if (mark.coords[1][1] < 0) mark.coords[1][1] = s[1];
      }

      var coords = [[scale(mark.coords[0][0]), scale(mark.coords[0][1])],
		    [scale(mark.coords[1][0]), scale(mark.coords[1][1])]];
      this.element.append($mark);
      $mark.width(coords[1][0] - coords[0][0]);
      $mark.height(coords[1][1] - coords[0][1]);
      $mark.css({left: coords[0][0], top: coords[0][1]});
      return $mark.get(0);
    },
  });
}(jQuery));


$(document).ready(function(){
  $(".picture-wrap").pictureviewer({
    plus_button: $(".toolbar .button.plus"),
    minus_button: $(".toolbar .button.minus"),
    areas_links: $("#picture-objects a, #picture-themes a"),
  });

  $.highlightFade.defaults.speed = 3000;

  $('.toolbar a.dropdown').each(function() {
    $t = $(this);
    $($t.attr('href')).hide().insertAfter(this);
  });

  $('.toolbar a.dropdown').toggle(function() {
    $(this).addClass('selected');
    $($(this).attr('href')).slideDown('fast');
  }, function() {
    $(this).removeClass('selected');
    $($(this).attr('href')).slideUp('fast');
  });


});

