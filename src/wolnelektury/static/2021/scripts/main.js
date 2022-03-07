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

// Ebook/Audiobook Btns
(function() {
  let button = $('.c-media__btn button');
  let closeButton = $('.c-media__popup__close');

  button.on('click', function () {
    let target = $(this).attr('id');
    $('[data-popup=' + target).addClass('is-open');
  });

  closeButton.on('click', function() {
    $(this).closest('.c-media__popup').removeClass('is-open');
  });

  $(document).keyup(function(e) {
    if (e.keyCode === 27) {
      $('.c-media__popup').removeClass('is-open');
    }
  });
})();

// Text overlay toggler
(function () {
  let overlays = $('.l-article__overlay');
  let button = $('.l-article__read-more');

  overlays.each(function () {
    let maxHeight = $(this).attr('data-max-height');
    if($(this).outerHeight() > maxHeight) {
      $(this).css({'maxHeight': maxHeight+'px'}).addClass('is-active');
    } else {
      $(this).next('.l-article__read-more').hide();
    }
  });

  button.on('click', function() {
    let dataLabel = $(this).attr('data-label');
    let dataAction = $(this).attr('data-action');
    $(this).parent().find('.l-article__overlay').toggleClass('is-clicked');
    if($(this).text() === dataLabel) {
      $(this).text(dataAction);
    } else {
      $(this).text(dataLabel);
    }
  });
})();

//Zmieniamy się popup
(function() {
  let $change = $('.l-change-pop');
  function change() {
    if(localStorage.getItem('change') === null) {
      $change.addClass('show');
    } else {
      $change.remove();
      return false;
    }

    $change.on('click', '.l-change-pop__close', function () {
      $change.slideUp();
      localStorage.setItem('change', 'showed');
    });
  }

  if($change.length) { change(); }
})();