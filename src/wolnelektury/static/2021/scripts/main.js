// JS Menu
(function () {
  let button = $('.js-menu');
  let menu = $('.l-navigation');
  let menuLinks = menu.find('a');

  button.on('click', function() {
    if(!$(this).hasClass('is-active')) {
      $(this).addClass('is-active');
      menu.addClass('is-open');
      $('body').addClass('is-open');
      button.find('.bar').addClass('animate');
      menuLinks.attr('tabindex', 0);
    } else {
      $(this).removeClass('is-active');
      menu.removeClass('is-open');
      $('body').removeClass('is-open');
      button.find('.bar').removeClass('animate');
      menuLinks.attr('tabindex', -1);
    }
  });

  $(document).keyup(function(e) {
    if (e.keyCode === 27) {
      button.removeClass('is-active');
      menu.removeClass('is-open');
      $('body').removeClass('is-open');
      button.find('.bar').removeClass('animate');
      menuLinks.attr('tabindex', -1);
    }
  });
})();

// User menu.
(function() {
    let button = $('.l-navigation__actions .user');
    let menu = $('#user-menu');
    let menuLinks = menu.find('a');

    button.on('click', function() {
        if (!menu.hasClass('is-open')) {
            menu.addClass('is-open');
            menuLinks.attr('tabindex', 0);
        } else {
            menu.removeClass('is-open');
            menuLinks.attr('tabindex', -1)
        }
        return false;
    });

    $(document).keyup(function(e) {
        if (e.keyCode === 27) {
            menu.removeClass('is-open');
            menuLinks.attr('tabindex', -1);
        }
    });

    $(document).click(function() {
      menu.removeClass('is-open');
      menuLinks.attr('tabindex', -1);
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

  $(document).keyup(function(e) {
    if (e.keyCode === 27) {
      $('.c-media__popup').removeClass('is-open');
    }
  });
})();

// Homepage books sliders
(function () {
  let shelfSlider = $('.l-your-books__shelf .l-books');
  let shelfNextSlide = $('.l-your-books__shelf .js-next-slide');
  let shelfPrevSlide = $('.l-your-books__shelf .js-prev-slide');
  let shelfCollapse = $('.l-your-books__shelf .js-collapse');

  shelfSlider.slick({
    slidesToScroll: 1,
    slidesToShow: 4,
    infinite: false,
    dots: false,
    arrows: false,
    autoplay: false,
    responsive: [
      {
        breakpoint: 768,
        settings: {
          centerMode: false,
          slidesToShow: 1
        }
      }
    ]
  });

  shelfNextSlide.on('click', function (event) {
    event.preventDefault();
    shelfSlider.slick('slickNext');
  });

  shelfPrevSlide.on('click', function (event) {
    event.preventDefault();
    shelfSlider.slick('slickPrev');
  });

  shelfCollapse.on('click', function (event) {
    event.preventDefault();
    shelfSlider.slick('slickPrev');
  });

  let collectionsSlider = $('.js-collections .l-books');
  let collectionsNextSlide = $('.js-collections .js-next-slide');
  let collectionsPrevSlide = $('.js-collections .js-prev-slide');

  collectionsSlider.slick({
    slidesToScroll: 1,
    slidesToShow: 5,
    infinite: false,
    dots: false,
    arrows: false,
    autoplay: false,
    responsive: [
      {
        breakpoint: 768,
        settings: {
          centerMode: false,
          slidesToShow: 2
        }
      }
    ]
  });

  collectionsNextSlide.on('click', function (event) {
    event.preventDefault();
    collectionsSlider.slick('slickNext');
  });

  collectionsPrevSlide.on('click', function (event) {
    event.preventDefault();
    collectionsSlider.slick('slickPrev');
  });

  let newBooksSlider = $('.js-new-books-slider .l-books');
  let newBooksNextSlide = $('.js-new-books-slider .js-next-slide');
  let newBooksPrevSlide = $('.js-new-books-slider .js-prev-slide');

  newBooksSlider.slick({
    slidesToScroll: 1,
    slidesToShow: 5,
    infinite: false,
    dots: false,
    arrows: false,
    autoplay: false,
    responsive: [
      {
        breakpoint: 768,
        settings: {
          centerMode: false,
          slidesToShow: 2
        }
      }
    ]
  });

  newBooksNextSlide.on('click', function (event) {
    event.preventDefault();
    newBooksSlider.slick('slickNext');
  });

  newBooksPrevSlide.on('click', function (event) {
    event.preventDefault();
    newBooksSlider.slick('slickPrev');
  });
})();

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


  let sliderHomepage = $('.l-quotes');
  sliderHomepage.slick({
    slidesToShow: 1,
    centerMode: true,
    centerPadding: '250px',
    infinite: true,
    dots: true,
    arrows: false,
    autoplay: true,
    autoplaySpeed: 2500,
    responsive: [
      {
        breakpoint: 768,
        settings: {
          centerMode: false,
          slidesToShow: 1
        }
      }
    ]
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


    function quit_experiment() {
        document.cookie = 'EXPERIMENT_layout=off; path=/; max-age=31536000';
        window.location.reload(true);
    }
    $(".quit-experiment").click(quit_experiment);

})();

(function() {
    $('.l-checkout__payments__box button').on('click', function() {
        let container = $(this).closest('.l-checkout__payments');
        $('input', container).val($(this).val());
        $('.is-active', container).removeClass('is-active');
        $(this).closest('.l-checkout__payments__box').addClass('is-active');
        $('#kwota').val('');
        return false;
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
