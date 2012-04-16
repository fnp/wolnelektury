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

var host = 'localhost:8000'; //'www.wolnelektury.pl';

/* set attributes of created elements */
stylesheet.setAttribute('type', 'text/css');
stylesheet.setAttribute('rel', 'stylesheet');
stylesheet.setAttribute('href', 'http://'+host+'/static/css/widget.css');
stylesheetJQUI.setAttribute('type', 'text/css');
stylesheetJQUI.setAttribute('rel', 'stylesheet');
stylesheetJQUI.setAttribute('href', 'http://'+host+'/static/css/ui-lightness/jquery-ui-1.8.16.custom.css');
linkLogo.setAttribute('href', 'http://'+host);
logo.setAttribute('src', 'http://'+host+'/static/img/logo-bez.png');
form.setAttribute('action', 'http://'+host+'/szukaj/');
form.setAttribute('method', 'get');
form.setAttribute('accept-charset', 'utf-8');
form.setAttribute('id', 'wl-form');
inputText.setAttribute('type', 'text');
inputText.setAttribute('title', 'tytul, autor, motyw/temat, epoka, rodzaj, gatunek');
inputText.setAttribute('value', '');
inputText.setAttribute('name', 'q');
inputText.setAttribute('id', 'id_qq');
inputText.setAttribute('data-source', 'http://'+host+'/szukaj/hint');
/*inputText.setAttribute('size', '13');*/
inputSubmit.setAttribute('type', 'image');
inputSubmit.setAttribute('src', 'http://'+host+'/static/img/search.png');
/* inputSubmit.setAttribute('style', 'position:relative; top:5px; margin-left:5px');*/

/* import jquery and autocomplete */
var scriptJ = document.createElement('script');
scriptJ.setAttribute('type', 'text/javascript');
scriptJ.setAttribute('src', 'http://'+host+'/static/js/jquery.js');

var scriptUI = document.createElement('script');
scriptUI.setAttribute('type', 'text/javascript');
scriptUI.setAttribute('src', 'http://'+host+'/static/js/jquery-ui-1.8.2.custom.min.js');
scriptUI.setAttribute('id', 'wl-jquery-ui-script')

var scriptSearch = document.createElement('script');
scriptSearch.setAttribute('type', 'text/javascript');
scriptSearch.setAttribute('src', 'http://'+host+'/static/js/search.js');
scriptSearch.setAttribute('id', 'wl-search-script')


body[0].appendChild(scriptJ);
body[0].appendChild(scriptUI);
body[0].appendChild(scriptSearch);

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

var wl_loaded_scripts = {};

function wl_initialize_after_load(just_loaded) {
    wl_loaded_scripts[just_loaded] = true;
    if (wl_loaded_scripts.jquery 
	&& wl_loaded_scripts.ui 
	&& wl_loaded_scripts.search) {
	var s = $('#id_qq');
	s.search({source: s.attr('data-source')});
    }
}

scriptJ.onload = function() { wl_initialize_after_load('jquery'); };
scriptJ.onreadystatechange = function() { if (scriptJ.readyState == 'complete') { wl_initialize_after_load('jquery'); } };

scriptUI.onload = function() { wl_initialize_after_load('ui'); };
scriptUI.onreadystatechange = function() { if (scriptUI.readyState == 'complete') { wl_initialize_after_load('jquery'); } };

scriptSearch.onload = function() { wl_initialize_after_load('search'); };
scriptSearch.onreadystatechange = function() { if (scriptSearch.readyState == 'complete') { wl_initialize_after_load('jquery'); } };

