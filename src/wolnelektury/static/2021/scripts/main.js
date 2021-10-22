// JS Menu
(function () {
  let button = $('.js-menu');
  let menu = $('.l-navigation__menu');
  let menuLinks = menu.find('a');

  button.on('click', function() {
    if(!$(this).hasClass('is-active')) {
      $(this).addClass('is-active');
      menu.addClass('is-open');
      button.find('.bar').addClass('animate');
      menuLinks.attr('tabindex', 0);
    } else {
      $(this).removeClass('is-active');
      menu.removeClass('is-open');
      button.find('.bar').removeClass('animate');
      menuLinks.attr('tabindex', -1);
    }
  });

  $(document).keyup(function(e) {
    if (e.keyCode === 27) {
      button.removeClass('is-active');
      menu.removeClass('is-open');
      button.find('.bar').removeClass('animate');
      menuLinks.attr('tabindex', -1);
    }
  });
})();
