
(function($) {
  $.widget('wl.pictureviewer', {
    
    options: {
      step: 20, // step in % of initial image
      plus_button: undefined,
      minus_button: undefined,
    },
    ORIGINAL_LOADING: 0, 
    ORIGINAL_AVAILABLE: 1, 
    ORIGINAL_SHOWN: 2,

    _create: function() {
      var self = this;
      self.initial_size = [ 
	self.element.data('width'),
	self.element.data('height') 
      ];
      self.original_size = [
	self.element.data('original-width'),
	self.element.data('original-height')
      ];
      self._zoom = 0;
      self._ratio = 1.0;

      self.original = self.element.find('img.original').eq(0);
      
      self._original_avaialble = self.ORIGINAL_LOADING;
      function original_loaded() {
	self._original_avaialble = self.ORIGINAL_AVAILABLE;
	self.options.plus_button.removeClass('inactive');
	self.options.minus_button.removeClass('inactive');
	console.log("Original image available, sizes initial: " + self.initial_size + ", original: " + self.original_size);
      };
      self.original.load(original_loaded);

      self.element.width(self.initial_size[0]);
      self.element.height(self.initial_size[1]);

      if (self.options.plus_button)
	self.options.plus_button.click(
	  function(ev) { self.zoom(1); });
      if (self.options.minus_button)
	self.options.minus_button.click(
	  function(ev) { self.zoom(-1); });

      self._initial_mark = null;
      function clean_initial_mark() {
	if (self._initial_mark) {
	  self._initial_mark.remove();
	  self._initial_mark = null;
	}
      }
      var initial_hash = window.location.hash;
      if (initial_hash) {
	var mk = null;
	if (initial_hash.startsWith('#object-')) {
	  $("[href=#picture-objects]").trigger('click');
	} else if (initial_hash.startsWith('#theme-')) {
	  $("[href=#picutre-themes]").trigger('click');
	}
	mk = $("[href=" + initial_hash + "]").eq(0);
	self._initial_mark = self.createMark({
	  label: mk.text(),
	  coords: mk.data('coords')
	});
      }      


      self.options.areas_links.hover(function() {
	clean_initial_mark();
	$this = $(this);
	var coords = $this.data("coords");
	this._picture_mark = self.createMark({
//	  label: $this.text(),
	  coords: coords,
	});
      }, function() {
	$(this._picture_mark).remove();
	this._picture_mark = undefined;
      }).click(function(ev) {
	ev.preventDefault();
	var $mark = self.element.find('.mark').eq(0);
	var markPos = $mark.offset();
	markPos = [markPos.left, markPos.top];
	var markSize = [ $mark.width(), $mark.height() ]
	var wSize = [ window.innerWidth, window.innerHeight ];
	window.scrollTo(
	  markPos[0] + markSize[0]/2 - wSize[0]/2,
	  markPos[1] + markSize[1]/2 - wSize[1]/2	
	);
	
      });

      

      return self;
    },

    currentSize: function() {
      return [this.element.width(), this.element.height() ];
    },

    currentZoom: function() { return this._zoom; },

    initOriginal: function() {
      if (this._original_avaialble > this.ORIGINAL_LOADING && 
	  this._original_avaialble < this.ORIGINAL_SHOWN) {
	this.element.css({'background-image': 'url('+ this.original.attr('src')+')', 'background-size':  this.initial_size[0]+'px'});
	this._original_avaialble = this.ORIGINAL_SHOWN;
      };
    },

    zoom: function(steps) {
      this.initOriginal();
      var t = this._zoom + steps;
      return this.zoomTo(t);
    },

    zoomForStep: function(step) {
      // 0 => initial
      // max_step-1 => max %
      if (step < 0) step = 0;
      var zoomperc = 100 + step * this.options.step;
      if (zoomperc * this.initial_size[0] > this.original_size[0] * 100) {
	zoomperc = this.original_size[0] * 100 / this.initial_size[0];
      };
      return zoomperc;
    },

    zoomTo: function(level) {
      var ratio = this.zoomForStep(level) / 100;
      var new_width  = ratio * this.initial_size[0];
      var new_height = ratio * this.initial_size[1];
      var cs = this.currentSize();
      if (new_width == cs[0]) 
	return;

      var target = {
	'width': new_width + 'px',
	'height': new_height + 'px',
	'background-size': new_width + 'px',
      };

      this._zoom = level;
      this._ratio = ratio;

      this.element.css(target);
      if (this._initial_mark) {
	this._initial_mark = this.redrawMark(this._initial_mark);
      }

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
    redrawMark: function(mark) {
      var $mark = $(mark);
      var $newmark = this.createMark($mark.data('mark'));
      $mark.remove();
      return $newmark;
    },
    // mark
    // {
    //  label: "...",
    //  coords: [x, y, w, h]
    // }
    createMark: function(mark) {
      if (mark.label === undefined)
	mark.label = '';
      var $mark = $('<div class="mark"><div class="label">' + 
		    mark.label + '</div></div>');
      var cs = this.currentSize()
      var ratio = cs[0] / this.original_size[0];
      var scale = function (v) { 
	return v * ratio; 
      }
      if (mark.coords[1][0] < 0 || mark.coords[1][1] < 0) { // whole
	var s = this.original_size;
	if (mark.coords[1][0] < 0) mark.coords[1][0] = s[0];
	if (mark.coords[1][1] < 0) mark.coords[1][1] = s[1];
      }

      var coords = [[scale(mark.coords[0][0]), scale(mark.coords[0][1])],
		    [scale(mark.coords[1][0]), scale(mark.coords[1][1])]];
      this.element.append($mark);
      $mark.width(coords[1][0] - coords[0][0]);
      $mark.height(coords[1][1] - coords[0][1]);
      $mark.css({left: coords[0][0], top: coords[0][1]});

      $mark.data('mark', mark);
      return $mark.get(0);
    },
  });
}(jQuery));


$(document).ready(function() {
  $.highlightFade.defaults.speed = 3000;

  $('.toolbar a.dropdown').each(function() {
    $t = $(this);
    $($t.attr('href')).hide().insertAfter(this);
  });

  function closeDD() {
    $(this).removeClass('selected');
    $($(this).attr('href')).slideUp('fast');
    
  }
  $('.toolbar a.dropdown').click(function(ev) {
    $("#sponsors:not(:hidden)").fadeOut();
    ev.preventDefault();
    if ($(this).hasClass('selected')) {
      closeDD.call(this);
    } else {
      $(this).addClass('selected');
      $($(this).attr('href')).slideDown('fast');
      $(this).parent().siblings(".button:has(.dropdown)").children(".dropdown").each(closeDD);
    }
  });

  $(".picture-wrap").pictureviewer({
    plus_button: $(".toolbar .button.plus"),
    minus_button: $(".toolbar .button.minus"),
    areas_links: $("#picture-objects a, #picture-themes a"),
  });

});

