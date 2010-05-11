/* http://keith-wood.name/countdown.html
 * Polish initialisation for the jQuery countdown extension
 * Written by Pawel Lewtak lewtak@gmail.com (2008) 
 * and Radek Czajka radoslaw.czajka@nowoczesnapolska.org.pl (2010) */
(function($) {
	$.countdown.regional['pl'] = {
		labels: ['lat', 'miesięcy', 'tygodni', 'dni', 'godzin', 'minut', 'sekund'],
		labels1: ['rok', 'miesiąc', 'tydzień', 'dzień', 'godzina', 'minuta', 'sekunda'],
        labels2: ['lata', 'miesiące', 'tygodnie', 'dni', 'godziny', 'minuty', 'sekundy'],
		compactLabels: ['l', 'm', 't', 'd'],
		compactLabels1: ['r', 'm', 't', 'd'],
        compactLabels2: ['l', 'm', 't', 'd'],
		timeSeparator: ':', isRTL: false,
		which: function(n){
			return n==1 ? 1 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 2 : 0;

			
			n == 1 ? 1 : 0;
		}
	};
	$.countdown.setDefaults($.countdown.regional['pl']);
})(jQuery);