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


    $('.js-collections').each(function() {
        //return;
        let collectionsSlider = $('.l-books', this);
        if (collectionsSlider.children().length < 2) return;

        // remove flexbox
        collectionsSlider.css('display', 'block');
        
        let collectionsNextSlide = $('.js-next-slide', this);
        let collectionsPrevSlide = $('.js-prev-slide', this);

  collectionsSlider.slick({
      //prevArrow, nextArrow,

      slidesToScroll: 1,
      slidesToShow: 1,
      infinite: false,
      dots: false,
      arrows: false,
      autoplay: false,

      swipeToSlide: true,
      centerMode: false,
      mobileFirst: true,
      responsive: [
          {
              breakpoint: 360 - .01,
              settings: {
                  slidesToShow: 2,
              }
          },
          {
              breakpoint: 520 - .01,
              settings: {
                  slidesToShow: 3
              }
          },
          {
              breakpoint: 680 - .01,
              settings: {
                  slidesToShow: 4
              }
          },
          {
              breakpoint: 840 - .01,
              settings: {
                  slidesToShow: 5
              }
          },
          {
              breakpoint: 1172 - .01,
              settings: {
                  slidesToShow: 5,
                  variableWidth: true,
              }
          },
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
    autoplaySpeed: 3000
  });


  let sliderHomepage = $('.l-quotes');
  sliderHomepage.slick({
    slidesToShow: 1,
    centerMode: false,
    infinite: true,
    dots: true,
    arrows: false,
    autoplay: true,
    autoplaySpeed: 4000,
  });

})();




// Carousel
(function () {
  let slider = $('.p-homepage__info__box--carousel');

  slider.slick({
    slidesToScroll: 1,
    slidesToShow: 1,
    infinite: true,
    dots: true,
    arrows: false,
    autoplay: true,
    autoplaySpeed: 5000
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



// Likes
(function() {

    ids = new Set(); 
    $(".icon-like").each(
        (i, e)=>{
            ids.add($(e).attr('data-book'));
        }
    );
    ids = [...ids].join(',');

    state = {
        liked: [],
    };
    
    $(document).on('click', '.icon-like', function(e) {
        e.preventDefault();
        let liked = $(this).hasClass('icon-liked');
        $btn = $(this);
        if (liked) {
            $.post({
                url: '/ludzie/lektura/' + $(this).attr('data-book-slug') + '/nie_lubie/',
                data: {'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()},
                success: function() {
                    delete state.liked[$btn.attr('data-book')];
                    updateLiked($btn);
                }
            })
        } else {
            $.post({
                url: '/ludzie/lektura/' + $(this).attr('data-book-slug') + '/lubie/',
                data: {'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()},
                success: function() {
                    state.liked[$btn.attr('data-book')] = [];
                    updateLiked($btn);
                },
                error: function(e) {
                    if (e.status == 403) {
                        $('#login-link').click();
                    }
                },
            });
        }
    })

    // TODO: DYNAMICALLY ADD
   $(".add-set-tag input[name=name]").autocomplete({
       source: '/ludzie/moje-tagi/',
   }).on('autocompleteopen', function() {
       $(this).closest('article').addClass('ac-hover');
   }).on('autocompleteclose', function() {
       $(this).closest('article').removeClass('ac-hover');
   });
    $(".add-set-tag").on("submit", function(e) {
        e.preventDefault();
        let $form = $(this);
        $.post({
            url: $form.attr("action"),
            data: $form.serialize(),
            success: (data) => {
                updateFromData(data);
                updateLikedAll();
                $('input[name=name]', $form).val('');
            }
        });
    })

    $(document).on("click", ".sets .close", function() {
        let bookId = $(this).closest("[data-book]").attr('data-book');
        $.post({
            url: '/ludzie/usun-tag/',
            data: {
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
                book: bookId,
                slug: $(this).parent().attr('data-set'),
            },
            success: (data) => {
                updateFromData(data);
                updateLikedAll();
            }
        });
    })

    
    function refreshAll(ids) {
        $.ajax('/ludzie/ulubione/?ids=' + ids, {
            success: function(result) {
                updateFromData(result);
                updateLikedAll();
            },
        });
    }
    refreshAll(ids);
    $.refreshLikes = refreshAll;

    function updateFromData(data) {
        for (pk in data) {
            if (data[pk] === null) {
                delete state.liked[pk];
            } else {
                state.liked[pk] = data[pk];
            }
        }
    }
    
    function updateLikedAll() {
        $(".icon-like").each(
            (i, e) => {
                updateLiked(e);
            }
        )
    }

    function updateLiked(e) {
        let bookId = $(e).attr('data-book');
        let liked = bookId in state.liked;
        $(e).toggleClass('icon-liked', liked);
        let $bookContainer = $('.book-container-' + bookId);
        $bookContainer.toggleClass('book-liked', liked);
        let $sets = $(".sets", $bookContainer);
        $sets.empty();
        $.each(state.liked[bookId], (i,e) => {
            let $set = $("<span>");
            $set.attr("data-set", e.slug);
            let $setA = $("<a>").appendTo($set);
            $setA.attr("href", e.url);
            $setA.text(e.name);
            let $setX = $("<a class='close'></a>").appendTo($set);
            $sets.append($set);
        });
    }
    
})();



// Toggle a class on long press.
(function() {
    const TIME = 250;
    let timer;

    $("[data-longpress]").on("touchstart", (e) => {
        $e = $(e.currentTarget);
        timer = setTimeout(() => {
            $e.toggleClass($e.attr('data-longpress'));
        }, TIME);
    });

    $("[data-longpress]").on("touchend", () => {
        clearTimeout(timer);
    });
})();



// Update search form filters.
(function() {
    $('.j-form-auto').each(function() {
        let $form = $(this);
        $('input', $form).change(function() {$form.submit()});
        $('select', $form).change(function() {$form.submit()});
        $('textarea', $form).change(function() {$form.submit()});
    });

    
    // experiments
    $(".experiment input").on('change', function() {
        let name = $(this).attr('name');
        let val = $(this).val();
        document.cookie = 'EXPERIMENT_' + name + '=' + val + '; path=/; max-age=31536000';
        window.location.reload(true);
    });

    $('.c-lang').on('click', function() {
        !$(this).toggleClass('is-open');
    });





    $(".c-media__settings > i").on('click', function() {
        $(".c-media__settings").toggleClass('active');
    });

})();
