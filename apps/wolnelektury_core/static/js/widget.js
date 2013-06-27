/* create basic elements */
var id          = "wl";
var widget      = document.getElementById(id);
var linkLogo    = document.createElement('a');
var logo        = document.createElement('img');
var form        = document.createElement('form');
var inputText   = document.createElement('input');
var inputSubmit = document.createElement('input');
var body        = document.getElementsByTagName('body')
var stylesheet = document.createElement('link');
var stylesheetJQUI = document.createElement('linl');

var host = 'wolnelektury.pl';

/* set attributes of created elements */
stylesheet.setAttribute('type', 'text/css');
stylesheet.setAttribute('rel', 'stylesheet');
stylesheet.setAttribute('href', '//'+host+'/static/css/widget.css');
stylesheetJQUI.setAttribute('type', 'text/css');
stylesheetJQUI.setAttribute('rel', 'stylesheet');
stylesheetJQUI.setAttribute('href', '//'+host+'/static/css/ui-lightness/jquery-ui-1.8.16.custom.css');
linkLogo.setAttribute('href', '//'+host);
logo.setAttribute('src', '//'+host+'/static/img/logo-bez.png');
form.setAttribute('action', '//'+host+'/szukaj/');
form.setAttribute('method', 'get');
form.setAttribute('accept-charset', 'utf-8');
form.setAttribute('id', 'wl-form');
inputText.setAttribute('type', 'text');
inputText.setAttribute('title', 'tytul, autor, motyw/temat, epoka, rodzaj, gatunek');
inputText.setAttribute('value', '');
inputText.setAttribute('name', 'q');
inputText.setAttribute('id', 'id_qq');
inputText.setAttribute('data-source', '//'+host+'/szukaj/hint/');
/*inputText.setAttribute('size', '13');*/
inputSubmit.setAttribute('type', 'image');
inputSubmit.setAttribute('src', '//'+host+'/static/img/search.png');
/* inputSubmit.setAttribute('style', 'position:relative; top:5px; margin-left:5px');*/

/* import jquery and autocomplete */
var scriptJ = document.createElement('script');
scriptJ.setAttribute('type', 'text/javascript');
scriptJ.setAttribute('src', '//'+host+'/static/js/jquery.js');

var scriptUI = document.createElement('script');
scriptUI.setAttribute('type', 'text/javascript');
scriptUI.setAttribute('src', '//'+host+'/static/js/jquery-ui-1.8.2.custom.min.js');
scriptUI.setAttribute('id', 'wl-jquery-ui-script')

var scriptSearch = document.createElement('script');
scriptSearch.setAttribute('type', 'text/javascript');
scriptSearch.setAttribute('src', '//'+host+'/static/js/search.js');
scriptSearch.setAttribute('id', 'wl-search-script')

body[0].appendChild(scriptJ);
scriptJ.onload = function() { body[0].appendChild(scriptUI); };
scriptJ.onreadystatechange = function() { if (scriptJ.readyState == 'complete') { scriptJ.onload(); } };

scriptUI.onload = function() { body[0].appendChild(scriptSearch); };
scriptUI.onreadystatechange = function() { if (scriptUI.readyState == 'complete') { scriptUI.onload(); } };

scriptSearch.onload = function() {
    	var s = $('#id_qq');
        var url = s.attr('data-source');
        s.search({source: 
                        function(req, cb) {
                        $.ajax({url: url,
                                dataType: "jsonp",
                                data: { term: req.term },
                                type: "GET",
                                success: function(data) { cb(data); },
                                error: function() { cb([]); }
                    });
                        },
            dataType: "jsonp",
            host: "//"+host});
}
scriptSearch.onreadystatechange = function() { if (scriptSearch.readyState == 'complete') { scriptSearch.onload(); } };

/* append elements to widget */
widget.appendChild(stylesheet);
//widget.appendChild(stylesheetJQUI);
widget.appendChild(linkLogo);
linkLogo.appendChild(logo);
widget.appendChild(form);
form.appendChild(inputText);
form.appendChild(inputSubmit);

/* ...and a little make-up */
/*
widget.style.borderColor = "#84BF2A";
widget.style.borderWidth = "2px";
widget.style.borderStyle = "solid";
widget.style.width = "160px";
widget.style.padding = "10px";
widget.style.fontSize = "12px";
form.style.paddingTop = "10px";
*/

/* resize - if needed */
if(widget.getAttribute('width') == '140'){
    logo.setAttribute('width', '140');
    inputText.setAttribute('size', '10');
    widget.style.width = "140px";
}



