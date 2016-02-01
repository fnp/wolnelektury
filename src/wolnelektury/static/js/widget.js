var WOLNELEKTURY_LOADED;
if (WOLNELEKTURY_LOADED == undefined) {
    var iframe = document.createElement('iframe');
    iframe.setAttribute('style', 'width: 100%; height: 140px; border: none; box-shadow: 0 0 .5rem #191919;');
    iframe.setAttribute('src', '//wolnelektury.pl/widget.html');
    document.getElementById('wl').appendChild(iframe);
    WOLNELEKTURY_LOADED = true;
}