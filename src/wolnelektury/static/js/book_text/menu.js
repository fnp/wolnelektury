(function($){$(function(){


function hide_menu_boxes() {
    /* Closes any open menu boxes. */
    $("#menu .active").each(function() {
        $(this).removeClass("active");
        $("#" + $(this).attr("data-box")).hide();
        if ($(this).hasClass('dropdown')) {
            $($(this).attr('href')).slideUp('fast');
        }
    });
    $("#box-underlay").hide();
}

function release_menu() {
    /* Exits the menu. It only really disappears on small screens. */
    hide_menu_boxes();
    $("body").removeClass("menu-showed");
}

/* Show menu */
$('#menu-toggle-on').click(function(e) {
    e.preventDefault();
    var body = $("body");
    /* Just stop hiding the menu. This way, after narrowing the browser,
     * menu will still disappear normally. */
    body.removeClass("menu-hidden");
    /* Menu still not visible? Really open it then. */
    if (!$("#menu").is(":visible")) {
        body.addClass("menu-showed");
    }
    _paq.push(['trackEvent', 'html', 'menu-on']);
});

/* Hide menu */
$('#menu-toggle-off').click(function(e) {
    e.preventDefault();
    /* Just release the menu. This way, after widening the browser,
     * menu will still appear normally. */
    release_menu();
    /* Menu still visible after releasing it? Really hide it then. */
    if ($("#menu").is(":visible")) {
        $("body").addClass("menu-hidden");
    }
    _paq.push(['trackEvent', 'html', 'menu-off']);
});


/* Exit menu by clicking anywhere else. */
$("#box-underlay").click(release_menu);


/* Toggle hidden box on click. */
$("#menu a").each(function() {
    var boxid = $(this).attr("data-box");
    if (boxid) {
        $("#" + boxid).hide();

        $(this).click(function(e) {
            e.preventDefault();
            var showing = $(this).hasClass("active");
            hide_menu_boxes();
            if (!showing) {
                $("body").addClass("menu-showed");
                $(this).addClass("active");
                $("#box-underlay").show();
                $("#" + boxid).show();
            }
        });
        _paq.push(['trackEvent', 'html', boxid]);
    }
    else if ($(this).hasClass('dropdown')) {
        $(this).click(function(e) {
            e.preventDefault();
            var showing = $(this).hasClass("active");
            hide_menu_boxes();
            if (!showing) {
                $("body").addClass("menu-showed");
                $("#sponsors:not(:hidden)").fadeOut();
                $(this).addClass("active");
                $($(this).attr('href')).slideDown('fast');
            }
        });
    }
    else if (!$(this).hasClass('button')) {
        $(this).click(release_menu);
    }
});


/* Show menu item for other versions of text. 
 * It's only present if there are any. */
$("#menu-other").show();


    function insertOtherText(text) {
	let tree = $(text);
	let lang = tree.attr('lang') || 'pl';
	
	// toc?
	// themes?

	let cursor = $(".main-text-body #book-text").children().first();
	// wstawiamy przed kursorem
	lastTarget = '';
	tree.children().each((i, e) => {
	    let $e = $(e);

	    if ($e.hasClass('anchor')) return;
	    if ($e.hasClass('numeracja')) return;
	    if ($e.attr('id') == 'toc') return;
	    if ($e.attr('id') == 'nota_red') return;
	    if ($e.attr('id') == 'themes') return;
	    if ($e.attr('name') && $e.attr('name').startsWith('sec')) return;
	    
	    if ($e.hasClass('target')) {
		let target = $e.attr('name');

		while (lastTarget != target) {
		    let nc = cursor.next();
		    if (!nc.length) {
			break;
		    }
		    cursor = nc;
		    lastTarget = cursor.attr('name');
		}

		while (true) {
		    let nc = cursor.next();
		    if (!nc.length) {
			break;
		    }
		    cursor = nc;
		    lastTarget = cursor.attr('name');
		    if (lastTarget) break;
		}
		
	    } else {
		let d = $('<div class="other">');
		d.attr('lang', lang);
		d.append(e);
		d.insertBefore(cursor);
	    }
	});
    }
    
/* Load other version of text. */
$(".display-other").click(function(e) {
    e.preventDefault();
    release_menu();

    $(".other").remove();
    $("body").addClass('with-other-text');

    $.ajax($(this).attr('data-other'), {
        success: function(text) {
	    insertOtherText(text);
            $("#other-text-waiter").hide();
            loaded_text($(".other"));
        }
    });
    _paq.push(['trackEvent', 'html', 'other-text']);
});



    

/* Remove other version of text. */
$(".other-text-close").click(function(e) {
    release_menu();
    e.preventDefault();
    $(".other").remove();
    $("body").removeClass('with-other-text');
    _paq.push(['trackEvent', 'html', 'other-text-close']);
});


/* Release menu after clicking inside TOC. */
    $("#toc a").click(function(){
        release_menu();
        _paq.push(['trackEvent', 'html', 'toc-item']);
    });


if ($('#nota_red').length > 0) {
    $("#menu-nota_red").show();
}

/* Show themes menu item, if there are any. */
if ($('#themes li').length > 0) {
    $("#menu-themes").show();
}

function loaded_text(text) {
    /* Attach events to elements inside book texts here.
     * This way they'll work for the other text when it's loaded. */

    $(".theme-begin", text).click(function(e) {
        e.preventDefault();
        if ($(this).css("overflow") == "hidden" || $(this).hasClass('showing')) {
            $(this).toggleClass("showing");
        }
    });

}
loaded_text("#book-text");


})})(jQuery);
