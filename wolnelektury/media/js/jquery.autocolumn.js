// version 1.1.0
// http://welcome.totheinter.net/columnizer-jquery-plugin/
// created by: Adam Wulf adam.wulf@gmail.com

(function($){
 $.fn.columnize = function(options) {


	var defaults = {
		width: 400,
		columns : false,
		buildOnce : false
	};
	var options = $.extend(defaults, options);

    return this.each(function() {
	    var $inBox = $(this);
		var maxHeight = $inBox.height();
		var $cache = $('<div></div>'); // this is where we'll put the real content
		var lastWidth = 0;
		var columnizing = false;
		$cache.append($inBox.children().clone());
		
		columnizeIt();
		
		$(window).resize(function() {
			if(!options.buildOnce && $.browser.msie){
				if($inBox.data("timeout")){
					clearTimeout($inBox.data("timeout"));
				}
				$inBox.data("timeout", setTimeout(columnizeIt, 200));
			}else if(!options.buildOnce){
				columnizeIt();
			}else{
				// don't rebuild
			}
		});
		
		/**
		 * return a node that has a height
		 * less than or equal to height
		 *
		 * @param putInHere, a dom element
		 * @$pullOutHere, a jQuery element
		 */
		function columnize($putInHere, $pullOutHere, $parentColumn, height){
			while($parentColumn.height() < height &&
				  $pullOutHere[0].childNodes.length){
				$putInHere.append($pullOutHere[0].childNodes[0]);
			}
			if($putInHere[0].childNodes.length == 0) return;
			
			// now we're too tall, undo the last one
			var kids = $putInHere[0].childNodes;
			var lastKid = kids[kids.length-1];
			$putInHere[0].removeChild(lastKid);
			var $item = $(lastKid);
			if($item[0].nodeType == 3){
				// it's a text node, split it up
				var oText = $item[0].nodeValue;
				var counter2 = options.width / 8;
				var columnText;
				while($parentColumn.height() < height && oText.length){
					if (oText.indexOf(' ', counter2) != '-1') {
						columnText = oText.substring(0, oText.indexOf(' ', counter2));
					} else {
						columnText = oText;
					}
					$putInHere.append(document.createTextNode(columnText));
					if(oText.length > counter2){
						oText = oText.substring(oText.indexOf(' ', counter2));
					}else{
						oText = "";
					}
				}
				if(oText.length){
					$item[0].nodeValue = oText;
				}else{
					return;
				}
			}
			
			if($pullOutHere.children().length){
				$pullOutHere.prepend($item);
			}else{
				$pullOutHere.append($item);
			}
		}
		
		function split($putInHere, $pullOutHere, $parentColumn, height){
			if($pullOutHere.children().length){
				$cloneMe = $pullOutHere.children(":first");
				$clone = $cloneMe.clone();
				if($clone.attr("nodeType") == 1){ 
					$putInHere.append($clone);
					if($clone.is("img") && $parentColumn.height() < height + 20){
						$cloneMe.remove();
					}else if(!$cloneMe.hasClass("dontsplit") && $parentColumn.height() < height + 20){
						$cloneMe.remove();
					}else if($clone.is("img") || $cloneMe.hasClass("dontsplit")){
						$clone.remove();
					}else{
						$clone.empty();
						columnize($clone, $cloneMe, $parentColumn, height);
						if($cloneMe.children().length){
							split($clone, $cloneMe, $parentColumn, height);
						}
					}
				}
			}
		}
		
		
		function singleColumnizeIt() {
			if ($inBox.data("columnized") && $inBox.children().length == 1) {
				return;
			}
			$inBox.data("columnized", true);
			$inBox.data("columnizing", true);
			
			$inBox.empty();
			$inBox.append($("<div class='first last column'></div>")); //"
			$col = $inBox.children().eq($inBox.children().length-1);
			$col.append($cache.clone());
			
			$inBox.data("columnizing", false);
		}
		
		
		function columnizeIt() {
			if(lastWidth == $inBox.width()) return;
			lastWidth = $inBox.width();
			
			var numCols = Math.round($inBox.width() / options.width);
			if(options.columns) numCols = options.columns;
//			if ($inBox.data("columnized") && numCols == $inBox.children().length) {
//				return;
//			}
			if(numCols <= 1){
				return singleColumnizeIt();
			}
			if($inBox.data("columnizing")) return;
			$inBox.data("columnized", true);
			$inBox.data("columnizing", true);
			
			$inBox.empty();
			$inBox.append($("<div style='width:" + (Math.round(100 / numCols) - 2)+ "%; padding: 3px; float: left;'></div>")); //"
			$col = $inBox.children(":last");
			$col.append($cache.clone());
			maxHeight = $col.height();
			$inBox.empty();
			
			var targetHeight = maxHeight / numCols;
			var firstTime = true;
			var maxLoops = 3;
			for(var loopCount=0;loopCount<maxLoops;loopCount++){
				$inBox.empty();
				var $destroyable = $cache.clone();
				$destroyable.css("visibility", "hidden");
				// create the columns
				for (var i = 0; i < numCols; i++) {
					/* create column */
					var className = (i == 0) ? "first column" : "column";
					var className = (i == numCols - 1) ? ("last " + className) : className;
					$inBox.append($("<div class='" + className + "' style='width:" + (Math.round(100 / numCols) - 2)+ "%; float: left;'></div>")); //"
				}
				
				// fill all but the last column
				for (var i = 0; i < numCols-1; i++) {
					var $col = $inBox.children().eq(i);
					columnize($col, $destroyable, $col, targetHeight);
					split($col, $destroyable, $col, targetHeight);
				}
				// the last column in the series
				$col = $inBox.children().eq($inBox.children().length-1);
				while($destroyable.children().length) $col.append($destroyable.children(":first"));
				var afterH = $col.height();
				var diff = afterH - targetHeight;
				var totalH = 0;
				var min = 10000000;
				var max = 0;
				$inBox.children().each(function($inBox){ return function($item){
					var h = $inBox.children().eq($item).height();
					totalH += h;
					if(h > max) max = h;
					if(h < min) min = h;
				}}($inBox));
				var avgH = totalH / numCols;
				if(max - min > 30){
					targetHeight = avgH + 30;
				}else if(Math.abs(avgH-targetHeight) > 20){
					targetHeight = avgH;
				}else{
					loopCount = maxLoops;
				}
				$inBox.append($("<br style='clear:both;'>"));
			}
			$inBox.data("columnizing", false);
		}
    });
 };
})(jQuery);
