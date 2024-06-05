(function($){$(function(){
    let csrf = $("[name='csrfmiddlewaretoken']").val();

    var interestingReferences = $("#interesting-references").text();
    if (interestingReferences) {
        interestingReferences = $.parseJSON(interestingReferences);
    }
    if (Object.keys(interestingReferences).length) {
        $("#settings-references").css('display', 'block');
    }

    var map_enabled = false;
    var marker = L.circleMarker([0,0]);
    var map = null;

    function enable_map() {
        $("#reference-map").show('slow');

        if (map_enabled) return;

        map = L.map('reference-map').setView([0, 0], 11);
        L.tileLayer('https://tile.thunderforest.com/cycle/{z}/{x}/{y}.png?apikey=a8a97f0ae5134403ac38c1a075b03e15', {
            attribution: 'Maps © <a href="http://www.thunderforest.com">Thunderforest</a>, Data © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
        }).addTo(map);

        map_enabled = true;
    }
    function disable_map() {
        $("#reference-map").hide('slow');
    }
    

    $("#reference-close").on("click", function(event) {
        event.preventDefault();
        $("#reference-box").hide();
    });
    
    $('a.reference').each(function() {
        $this = $(this);
        uri = $this.attr('data-uri');
        if (uri == '') {
            $this.remove();
            return;
        }
        if (interestingReferences.hasOwnProperty(uri)) {
            $this.addClass('interesting');
            ref = interestingReferences[uri];

            $this.attr('href', ref.wikipedia_link);
            $this.attr('target', '_blank');
        }
    });


    $('a.reference.interesting').on('click', function(event) {
        event.preventDefault();

        $("#reference-box").show();

        $this = $(this);
        uri = $this.attr('data-uri');
        ref = interestingReferences[uri];

        if (ref.location) {
            enable_map();

            let newLoc = [
                ref.location[0],
                ref.location[1] + Math.round(
                    (map.getCenter().lng - ref.location[1]) / 360
                ) * 360
            ];

            marker.setLatLng(newLoc);
            marker.bindTooltip(ref.label).openTooltip();
            map.addLayer(marker);

            map.panTo(newLoc, {
                animate: true,
                duration: 1,
            });
        } else {
            disable_map();
            if (map) {
                map.removeLayer(marker);
            }
        }

        $("#reference-images a").remove();
        if (ref.images) {
            $.each(ref.images, function(i, e) {
                $i = $("<a target='_blank'><img></a>");
                $i.attr('href', e.page);
                $('img', $i).attr('src', e.thumburl || e.url);
                if (e.thumbresolution) {
                    $('img', $i).attr('width', e.thumbresolution[0]).attr('height', e.thumbresolution[1]);
                }

                $("#reference-images").append($i);
            })
        }

        $("#reference-link").text(ref.label);
        $("#reference-link").attr('href', ref.wikipedia_link);

        _paq.push(['trackEvent', 'html', 'reference']);
    });


    function putNoteAt($elem, anchor, side) {
        $elem.data('anchoredTo', anchor);
        updateNote($elem, side);
    }

    function updateNote($elem, side) {
        anchor = $elem.data('anchoredTo')
        if (!anchor) return;
        let anchorRect = anchor.getBoundingClientRect();

        let x = anchorRect.x + anchorRect.width / 2;
        let y = anchorRect.y;
        if ($elem.data('attach-bottom')) {
            y += anchorRect.height;
        }
        minx = $("#book-text").position().left;
        maxx = minx + $("#book-text").width();

        margin = 20;
        minx += margin;
        maxx -= margin;
        maxx += 10000;

        //boxwidth = 470;
        boxwidth = $elem.width();
        
        if (maxx - minx <= boxwidth) {
            nx = margin;
            right = margin;
            leftoffset = x - margin;
        } else {
            right = '';
        
            // default position.
            leftoffset = 40;
            leftoffset = $elem.data('default-leftoffset');
            
            nx = x - leftoffset;

            $elem.css({right: ''});

            // Do we need to move away from the left?
            if (nx < minx) {
                let d = minx - nx;
                nx += d;
                leftoffset -= d;
            }

            // Do we need to move away from the right?
            if (nx + boxwidth > maxx) {
                // ACTUALLY CALCULATE STUFF
                // if maxx - minx < 470 px -- daj z lewej do prawej i już!
                
                right = '';
                let d = nx + boxwidth - maxx;
                //if (leftoffset + d > $elem.width() - 10) d = $elem.width() - leftoffset - 10;
                nx -= d;
                leftoffset += d;
            }
        }
        $elem.css({
            left: nx,
            right: right
        });
        if (!$elem.data('attach-bottom')) {
            ny = y - $elem.height() - 10;
        } else {
            ny = y + 10;
        }
        $elem.css({
            top: ny
        });
        $('.pointer', $elem).css({
            left: leftoffset - 6
        });

        $elem.css({
            display: "block"
        });
    }

    function closeNoteBox() {
        $('#annotation-box').data('anchoredTo', null).fadeOut();
    }
    $(document).on('click', function(event) {
        let t = $(event.target);
        if (t.parents('#annotation-box').length && !t.is('#footnote-link')) {
            return;
        }
        closeNoteBox();
    });
    $(window).on('resize', closeNoteBox);

    function getPositionInBookText($e) {
        let x = 0, y = 0;

        // Ok dla Y, nie ok dla X
        
        while ($e.attr('id') != 'book-text') {
            let p = $e.position();
            x += p.left;
            y += p.top;
            $e = $e.offsetParent();
            break;
        }
        return {"x": x, "y": y}
    }
    
    $('#book-text .annotation').on('click', function(event) {
        if ($(this).parents('#footnotes').length) return;
        event.preventDefault();



        let x = $(this).width() / 2, y = 0;
        let elem = $(this);
        while (elem.attr('id') != 'book-text') {
            let p = $(elem).position();
            x += p.left;
            y += p.top;
            elem = elem.parent();
        }
        href = $(this).attr('href').substr(1);
        content = $("[name='" + href + "']").next().next().html();
        if (!content) return;
        $("#annotation-content").html(content);
        $("#footnote-link").attr('href', '#' + href)

        
        putNoteAt($('#annotation-box'), this);
        event.stopPropagation();
    });


    
    let zakladki = {};
    $.get({
        url: '/zakladki/',
        success: function(data) {
            zakladki = data;
            $.each(zakladki, (i, e) => {
                zakladkaUpdateFor(
                    // TODO: not just paragraphs.
                    $('[href="#' + e.anchor + '"]').nextAll('.paragraph').first()
                );
            });
        }
    });

    // TODO: create bookmarks on init
    // We need to do that from anchors.
    
    function zakladkaUpdateFor($item) {

        let anchor = $item.prevAll('.target').first().attr('name');
        
        if (anchor in zakladki) {
            let $booktag = $item.data('booktag');
            if (!$booktag) {

                // TODO: only copy without the dialog.
                $booktag = $("<div class='zakladka'>");
                $booktag.append($('.icon', $zakladka).clone());
                
                $item.data('booktag', $booktag);
                $booktag.data('p', $item);
                $booktag.data('anchor', anchor);
                $zakladka.after($booktag);

                zakladkaSetPosition($booktag);
                $booktag.show();
            }

            $z = $booktag;
            if (zakladki[anchor].note) {
                $z.removeClass('zakladka-exists');
                $z.addClass('zakladka-note');
            } else {
                $z.removeClass('zakladka-note');
                $z.addClass('zakladka-exists');
            }
        } else {
            let $booktag = $item.data('booktag');
            if ($booktag) {
                $item.data('booktag', null);
                $zakladka.append($("#zakladka-box"));
                $booktag.remove();
            }
        }
    }

    function zakladkaSetPosition($z) {
        $item = $z.data('p');
        pos = getPositionInBookText($item);
        $z.css({
            display: 'block',
            top: pos.y,
            right: ($('#main-text').width() - $('#book-text').width()) / 2,
        });
    }

    let $zakladka = $('#zakladka');
    $('#book-text .paragraph').on('mouseover', function() {showMarker($(this));});
    $('#book-text .verse').on('mouseover', function() {showMarker($(this));});
        //$.PMarker.showForP(this);


    function showMarker(p) {
        
        // Close the currently tag box when moving to another one.
        // TBD: Do we want to keep the box open and prevent moving?
        $("#zakladka-box").hide();

        let anchor = p.prevAll('.target').first().attr('name');
        // Don't bother if there's no anchor to use.
        if (!anchor) return;

        // Only show tag if there is not already a tag for this p.
        if (p.data('booktag')) {
            $zakladka.hide();
        } else {
            $zakladka.data('p', p);
            $zakladka.data('anchor', anchor);

            // (not needed) zakladkaUpdateClass();
            // TODO: UPDATE THIS ON OPEN?
            //let note = anchor in zakladki ? zakladki[anchor].note : ''; 
            //$('textarea', $zakladka).val(note);

            zakladkaSetPosition($zakladka);
            $zakladka.show();
        }
    }

    $(".zakladka-tool_zakladka").on('click', function() {
        let $z = $("#zakladka-box").data('z');
        let anchor = $z.data('anchor');
        let $p = $z.data('p');
        $.post({
            url: '/zakladki/',
            data: {
                csrfmiddlewaretoken: csrf,
                anchor: anchor
            },
            success: function(data) {
                zakladki[data.anchor] = data;
                $("#zakladka-box").hide();

                // Just hide, and create new .zakladka if not already exists?
                // In general no hiding 'classed' .zakladka.
                // So the 'cursor' .zakladka doesn't ever need class update.
                //zakladkaUpdateClass();
                zakladkaUpdateFor($p);

            }
        });
    });

    $(".zakladka-tool_notka_text textarea").on('input', function() {
        // FIXME: no use const $zakladka here, check which .zakladka are we attached to.
        let $z = $(this).closest('.zakladka');
        let anchor = $z.data('anchor');

        $("#notka-saved").hide();
        //$("#notka-save").show();
        $.post({
            url: '/zakladki/' + zakladki[anchor].uuid + '/',
            data: {
                csrfmiddlewaretoken: csrf,
                note: $(this).val()
            },
            success: function(data) {
                zakladki[anchor] = data;
                zakladkaUpdateFor($z.data('p'));
                $("#notka-save").hide();
                $("#notka-saved").fadeIn();
            }
        });
    });

    $(".zakladka-tool_zakladka_delete").on('click', function() {
        let $z = $(this).closest('.zakladka');
        let anchor = $z.data('anchor');
        $.post({
            url: '/zakladki/' + zakladki[anchor].uuid + '/delete/',
            data: {
                csrfmiddlewaretoken: csrf,
            },
            success: function(data) {
                delete zakladki[anchor];
                $("#zakladka-box").hide();
                zakladkaUpdateFor($z.data('p'));
            }
        });
    });

    $("#main-text").on("click", ".zakladka .icon", function() {
        let $z = $(this).closest('.zakladka');
        let $box = $("#zakladka-box");
        $z.append($box);
        $box.data('z', $z);

        let $p = $z.data('p');
        let anchor = $z.data('anchor');
        let note = anchor in zakladki ? zakladki[anchor].note : ''; 

        $('.zakladka-tool_zakladka', $box).toggle(!(anchor in zakladki));
        $('.zakladka-tool_sluchaj', $box).toggle($p.hasClass('syncable')).data('sync', $p.attr('id'));
        $('textarea', $box).val(note);

        $box.toggle();
    });


    class QBox {
        constructor(qbox) {
            this.qbox = qbox;
        }
        showForSelection(sel) {
            // TODO: only consider ranges inside text.?
            this.selection = sel;

            // TODO: multiple ranges.
            let range = sel.getRangeAt(0);
            let rect = range.getBoundingClientRect();

            putNoteAt(this.qbox, range)
        }
        showForBlock(b) {
            let rect = b.getBoundingClientRect();

            putNoteAt(this.qbox, b, 'left')
        }
        hide() {
            this.qbox.data('anchoredTo', null);
            this.qbox.fadeOut();
        }
        hideCopied() {
            this.qbox.data('anchoredTo', null);
            this.qbox.addClass('copied').fadeOut(1500, () => {
                this.qbox.removeClass('copied');
            });
        }

        copyText() {
            // TODO: only consider ranges inside text.?
            let range = this.selection.getRangeAt(0);
            let e = range.startContainer;
            let anchor = getIdForElem(e);
            let text = window.location.protocol + '//' +
                window.location.host +
                window.location.pathname;

            navigator.clipboard.writeText(
                this.selection.toString() +
                    '\n\nCałość czytaj na: ' + text
            );
            this.hideCopied();
        }
        copyLink() {
            // TODO: only consider ranges inside text.?
            let range = this.selection.getRangeAt(0);
            let e = range.startContainer;
            let anchor = getIdForElem(e);
            let text = window.location.protocol + '//' +
                window.location.host +
                window.location.pathname;
            if (anchor) text += '#' + anchor;
            navigator.clipboard.writeText(text);
            
            this.hideCopied();
        }
        quote() {
            // What aboot non-contiguous selections?
            let sel = this.selection;
            let textContent = sel.toString();
            let anchor = getIdForElem(sel.getRangeAt(0).startContainer);
            let paths = getSelectionPaths(sel);
            $.post({
                url: '/cytaty/',
                data: {
                    csrfmiddlewaretoken: csrf,
                    text: textContent,
                    startElem: anchor,
                    //endElem: endElem,
                    //startOffset: 0,
                    //endOffset: 0,
                    paths: paths,
                },
                success: function (data) {
                    var win = window.open('/cytaty/' + data.uuid + '/', '_blank');
                }
            });
            
        }
        
    }
    let qbox = new QBox($("#qbox"));


    function getPathToNode(elem) {
        // Need normalize?
        let path = [];
        while (elem.id != 'book-text') {
            let p = elem.parentElement;
            path.unshift([...p.childNodes].indexOf(elem))
            elem = p;
        }
        return path;
    }
    function getSelectionPaths(selection) {
        // does it work?
        let range1 = selection.getRangeAt(0);
        let range2 = selection.getRangeAt(selection.rangeCount - 1);
        let paths = [
            getPathToNode(range1.startContainer) + [range1.startOffset],
            getPathToNode(range2.endContainer) + [range2.endOffset]
        ]
        return paths;
    }
    

    function getIdForElem(elem) {
        // is it used?
        let $elem = $(elem);
        // check if inside book-text?

        while (true) {
            if ($elem.hasClass('target')) {
                return $elem.attr('name');
            }
            $p = $elem.prev();
            if ($p.length) {
                $elem = $p;
            } else {
                // Gdy wychodzimy w górę -- to jest ten moment, w którym znajdujemy element od którego wychodzimy i zliczamy znaki.

                
                $p = $elem.parent()
                if ($p.length) {
                    // is there text?
                    $elem = $p;
                } else {
                    return undefined;
                }
            }
        }
    }

    function getIdForElem(elem) {
        // is it used?
        // check if inside book-text?
        $elem = $(elem);
        while (true) {
            if ($elem.hasClass('target')) {
                return $elem.attr('name');
            }
            $p = $elem.prev();
            if ($p.length) {
                $elem = $p;
            } else {
                $p = $elem.parent()
                if ($p.length) {
                    // is there text?
                    $elem = $p;
                } else {
                    return undefined;
                }
            }
        }
    }


    function positionToIIDOffset(container, offset) {
        // Container and offset follow Range rules.
        // If container is a text node, offset is text offset.
        // If container is an element node, offset is number of child nodes from container start.
        // (containers of type Comment, CDATASection - ignore)z
    }


    function updateQBox() {
        sel = document.getSelection();
        let goodS = true;
        if (sel.isCollapsed || sel.rangeCount < 1) {
            goodS = false;
        }
        
        if (!goodS) {
            qbox.hide();
        } else {
            qbox.showForSelection(sel);
        }
    };
    $(document).on('selectionchange', updateQBox);

    function updateBoxes() {
        updateNote(qbox.qbox);
        updateNote($('#annotation-box'));
        
    }
    $(window).on('scroll', updateBoxes);
    $(window).on('resize', updateBoxes);


    $(window).on('resize', function() {
        $('.zakladka').each(function() {
            zakladkaSetPosition($(this));
        });
    });

    $('a.anchor').on('click', function(e) {
        e.preventDefault();

        let sel = window.getSelection();
        sel.removeAllRanges();
        let range = document.createRange();

        let $p = $(this).nextAll('.paragraph').first()
        range.selectNode($p[0]);
        sel.addRange(range);
        
        qbox.showForSelection(sel);

        showMarker($p);
    });
    
   
    
    $('.qbox-t-copy').on('click', function(e) {
        e.preventDefault();
        qbox.copyText();
    });
    $('.qbox-t-link').on('click', function(e) {
        e.preventDefault();
        qbox.copyLink();
    });
    $('.qbox-t-quote').on('click', function(e) {
        e.preventDefault();
        qbox.quote();
    });


    /*
    $(".paragraph").on('click', function(e) {
        qbox.showForBlock(this);
    });
    */

    
    function scrollToAnchor(anchor) {
        if (anchor) {
            var anchor_name = anchor.slice(1);
            var element = $('a[name="' + anchor_name + '"]');
            if (element.length > 0) {
                $("html").animate({
                    scrollTop: element.offset().top - 55
                }, {
                    duration: 500,
                    done: function() {
                        history.pushState({}, '', anchor);
                    },
                });
            }
        }
    }
    scrollToAnchor(window.location.hash)
    $('#toc, #themes, #book-text, #annotation').on('click', 'a', function(event) {
        event.preventDefault();
        scrollToAnchor($(this).attr('href'));
    });

    
})})(jQuery);
