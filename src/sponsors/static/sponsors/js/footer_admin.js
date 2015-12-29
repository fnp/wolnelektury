(function($) {
  $.fn.sponsorsFooter = function(options) {
    var settings = {
      sponsors: []
    };
    $.extend(settings, options);

    var input = $(this).hide();

    var container = $('<div class="sponsors"></div>').appendTo(input.parent());
    var groups = $.evalJSON(input.val());

    var unusedDiv = $('<div class="sponsors-sponsor-group sponsors-unused-sponsor-group"></div>')
      .appendTo(container)
      .append('<p class="sponsors-sponsor-group-name sponsors-unused-sponsor-group-name">dostępni sponsorzy</p>');
    var unusedList = $('<ol class="sponsors-sponsor-group-list sponsors-unused-group-list"></ol>')
        .appendTo(unusedDiv)
        .sortable({
          connectWith: '.sponsors-sponsor-group-list'
    		});

    // Edit group name inline
    function editNameInline(name) {
      name.unbind('click.sponsorsFooter');
      var inlineInput = $('<input></input>').val(name.html());
      name.html('');

      function endEditing() {
        name.html(inlineInput.val());
        inlineInput.remove();
        name.bind('click.sponsorsFooter', function() {
          editNameInline($(this));
        });
        input.parents('form').unbind('submit.sponsorsFooter', endEditing);
        return false;
      }

      inlineInput.appendTo(name).focus().blur(endEditing);
      input.parents('form').bind('submit.sponsorsFooter', endEditing);
    }

    // Remove sponsor with passed id from sponsors array and return it
    function popSponsor(id) {
      for (var i=0; i < settings.sponsors.length; i++) {
        if (settings.sponsors[i].id == id) {
          var s = settings.sponsors[i];
          settings.sponsors.splice(i, 1);
          return s;
        }
      }
      return null;
    }

    // Create sponsor group and bind events
    function createGroup(name, sponsors) {
      if (!sponsors) {
        sponsors = [];
      }

      var groupDiv = $('<div class="sponsors-sponsor-group"></div>');

      $('<a class="sponsors-remove-sponsor-group">X</a>')
        .click(function() {
          groupDiv.fadeOut('slow', function() {
            $('.sponsors-sponsor', groupDiv).hide().appendTo(unusedList).fadeIn();
            groupDiv.remove();
          });
        }).appendTo(groupDiv);

      $('<p class="sponsors-sponsor-group-name">' + name + '</p>')
        .bind('click.sponsorsFooter', function() {
          editNameInline($(this));
        }).appendTo(groupDiv);

      var groupList = $('<ol class="sponsors-sponsor-group-list"></ol>')
        .appendTo(groupDiv)
        .sortable({
          connectWith: '.sponsors-sponsor-group-list'
    		});


      for (var i = 0; i < sponsors.length; i++) {
        $('<li class="sponsors-sponsor"><img src="' + sponsors[i].image + '" alt="' + sponsors[i].name + '"/></li>')
          .data('obj_id', sponsors[i].id)
          .appendTo(groupList);
      }
      return groupDiv;
    }

    // Create groups from data in input value
    for (var i = 0; i < groups.length; i++) {
      var group = groups[i];
      var sponsors = [];

      for (var j = 0; j < group.sponsors.length; j++) {
        var s = popSponsor(group.sponsors[j]);
        if (s) {
          sponsors.push(s);
        }
      }
      createGroup(group.name, sponsors).appendTo(container);
    }

    // Serialize input value before submiting form
    input.parents('form').submit(function(event) {
      var groups = [];
      $('.sponsors-sponsor-group', container).not('.sponsors-unused-sponsor-group').each(function() {
        var group = {name: $('.sponsors-sponsor-group-name', this).html(), sponsors: []};
        $('.sponsors-sponsor', this).each(function() {
          group.sponsors.push($(this).data('obj_id'));
        });
        groups.push(group);
      });
      input.val($.toJSON(groups));
    });

    for (i = 0; i < settings.sponsors.length; i++) {
      $('<li class="sponsors-sponsor"><img src="' + settings.sponsors[i].image + '" alt="' + settings.sponsors[i].name + '"/></li>')
        .data('obj_id', settings.sponsors[i].id)
        .appendTo(unusedList);
    }

    $('<button type="button">Dodaj nową grupę</button>')
      .click(function() {
        var newGroup = createGroup('').appendTo(container);
        editNameInline($('.sponsors-sponsor-group-name', newGroup));
      }).prependTo(input.parent());

    input.parent().append('<div style="clear: both"></div>');
  };
})(jQuery);
