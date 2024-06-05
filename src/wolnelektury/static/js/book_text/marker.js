(function($){$(function(){

    class PMarker {
        putBox(box) {

            let $z = $(this).closest('.zakladka');
            let $box = $("#zakladka-box");
            $z.append($box);
            $box.data('z', $z);

            anchor = $z.data('anchor');
            let note = anchor in zakladki ? zakladki[anchor].note : ''; 
            $('textarea', $box).val(note);
            
            // TODO update note content here.
            // And/or delete buttons.
            $box.toggle();


        }



        showForAnchor(anchor) {
        }

        showForP(p) {
        }
    }

    $.PMarker = PMarker;
    
    // There can be more than one marker.
    // Some markers

})})(jQuery);
