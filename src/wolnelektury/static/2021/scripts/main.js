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
  let button = $('.c-media__btn button:not(.l-button--media--full)');
  let popupLayer = $('.c-media__popup');
  let closeButton = $('.c-media__popup__close');
  let playButton = $('.c-player__btn--md');
  let chaptersButton = $('.c-player__chapters span');
  let select = $('.c-select');
  let selectItem = $('.c-select li');
  let volumeButton = $('.icon-volume');

  playButton.on('click', function() {
    if($(this).find('.icon').hasClass('icon-play')) {
      $(this).find('.icon-play').removeClass('icon-play').addClass('icon-pause');
    } else if($(this).find('.icon').hasClass('icon-pause')) {
      $(this).find('.icon-pause').removeClass('icon-pause').addClass('icon-play');
    }
  });

  button.on('click', function () {
    let target = $(this).attr('id');
    $('[data-popup=' + target).addClass('is-open');
    $('body').addClass('popup-open');
  });

  closeButton.on('click', function() {
    $(this).closest('.c-media__popup').removeClass('is-open');
    $('body').removeClass('popup-open');
  });

  popupLayer.on('click', function(e) {
    let _this = $(this);
    if($(e.target).is(popupLayer)) {
      _this.removeClass('is-open');
      $('body').removeClass('popup-open');
    }
  });

  chaptersButton.on('click', function() {
    $(this).parent().toggleClass('is-active');
  });

  select.on('click', function() {
    $(this).toggleClass('is-active');
  });

  selectItem.on('click', function() {
    selectItem.removeClass('is-active');
    $(this).addClass('is-active');
  });

  volumeButton.on('click', function() {
    if($(this).hasClass('icon-volume')) {
      $(this).removeClass('icon-volume').addClass('icon-mute');
      $(this).next().val(0);
      $(this).next().css('background-size', '0% 100%');
    } else if($(this).hasClass('icon-mute')) {
      $(this).removeClass('icon-mute').addClass('icon-volume');
      $(this).next().val(50);
      $(this).next().css('background-size', '50% 100%');
    }
  });

  $(document).keyup(function(e) {
    if (e.keyCode === 27) {
      $('.c-media__popup').removeClass('is-open');
    }
  });
})();

// Range
const rangeInputs = document.querySelectorAll('input[type="range"]')

function handleInputChange(e) {
  let target = e.target
  if (e.target.type !== 'range') {
    target = document.getElementById('range')
  }
  const min = target.min
  const max = target.max
  const val = target.value

  target.style.backgroundSize = (val - min) * 100 / (max - min) + '% 100%'
}

rangeInputs.forEach(input => {
  input.addEventListener('input', handleInputChange)
});

// Quotes slider
(function () {
  let slider = $('.l-author__quotes__slider');

  slider.slick({
    slidesToScroll: 1,
    slidesToShow: 1,
    infinite: true,
    dots: true,
    arrows: false,
    autoplay: true,
    autoplaySpeed: 2500
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

//Switch
(function() {
  let $switchOnce = $('#switch-once');
  let $switchMonthly = $('#switch-monthly');

  $switchMonthly.on('click', function() {
    $('.l-checkout__payments__box').removeClass('once');
  });

  $switchOnce.on('click', function() {
    $('.l-checkout__payments__box').addClass('once');
  });
})();

//Copy function
(function() {
  let $copy = $('.js-copy');

  $copy.on('click', function() {
    let $copyText = $(this).closest('.l-checkout__info__item').find('input');
    $copyText.select();
    document.execCommand('copy');
  });
})();
