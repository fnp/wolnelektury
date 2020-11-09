(function($){$(function(){

    var interestingReferences = $("#interesting-references").text();
    if (interestingReferences) {
        interestingReferences = $.parseJSON(interestingReferences);
    }
    if (Object.keys(interestingReferences).length) {
        $("#settings-references").css('display', 'block');
    }

    
    
    var map_enabled = false;
    var marker = L.marker([0,0]);
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

            marker.setLatLng(ref.location);
            //marker.setContent(ref.label);
            marker.bindTooltip(ref.label).openTooltip();
            map.addLayer(marker);
            map.panTo(ref.location, {
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
                $('img', $i).attr('src', e.url);
                $("#reference-images").append($i);
            })
        }

        $("#reference-link").text(ref.label);
        $("#reference-link").attr('href', ref.wikipedia_link);
    });
})})(jQuery);
