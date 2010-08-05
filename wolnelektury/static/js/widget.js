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

/* set attributes of created elements */
stylesheet.setAttribute('type', 'text/css');
stylesheet.setAttribute('rel', 'stylesheet');
stylesheet.setAttribute('href', 'http://www.wolnelektury.pl/static/css/widget.css');
linkLogo.setAttribute('href', 'http://www.wolnelektury.pl');
logo.setAttribute('src', 'http://www.wolnelektury.pl/static/img/logo.png');
form.setAttribute('action', 'http://www.wolnelektury.pl/katalog/szukaj/');
form.setAttribute('method', 'get');
form.setAttribute('accept-charset', 'utf-8');
form.setAttribute('id', 'wl-form');
inputText.setAttribute('type', 'text');
inputText.setAttribute('title', 'tytul, autor, motyw/temat, epoka, rodzaj, gatunek');
inputText.setAttribute('value', '');
inputText.setAttribute('name', 'q');
inputText.setAttribute('id', 'id_q');
inputSubmit.setAttribute('type', 'submit');
inputSubmit.setAttribute('value', 'Szukaj');

/* import jquery and autocomplete */
var scriptJ = document.createElement('script');
scriptJ.setAttribute('type', 'text/javascript');
scriptJ.setAttribute('src', 'http://www.wolnelektury.pl/static/js/jquery.js');

var scriptAutoComplete = document.createElement('script');
scriptAutoComplete.setAttribute('type', 'text/javascript');
scriptAutoComplete.setAttribute('src', 'http://www.wolnelektury.pl/static/js/jquery-ui-1.8.2.custom.min.js');

var scriptInit = document.createElement('script');
scriptInit.setAttribute('type', 'text/javascript');
scriptInit.setAttribute('src', 'http://www.wolnelektury.pl/static/js/widgetInit.js');

body[0].appendChild(scriptJ);
body[0].appendChild(scriptAutoComplete);
body[0].appendChild(scriptInit);

/* append elements to widget */
widget.appendChild(stylesheet);
widget.appendChild(linkLogo);
linkLogo.appendChild(logo);
widget.appendChild(form);
form.appendChild(inputText);
form.appendChild(inputSubmit);

/* ...and a little make-up */
widget.style.borderColor = "#84BF2A";
widget.style.borderWidth = "2px";
widget.style.borderStyle = "solid";
widget.style.width = "260px";
widget.style.padding = "10px";
widget.style.fontSize = "12px";
form.style.paddingTop = "10px";
