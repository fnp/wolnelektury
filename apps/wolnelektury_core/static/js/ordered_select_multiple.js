(function($) {
  $.fn.orderedSelectMultiple = function(options) {
    var settings = {
      choices: []
    };
    $.extend(settings, options);

    var input = $(this).hide();
    var values = input.val().split(',');

    var container = $('<div></div>').insertAfter($(this));
    var choicesList = $('<ol class="choices connectedSortable"></ol>').appendTo(container).css({
      width: 200, float: 'left', minHeight: 200, backgroundColor: '#eee', margin: 0, padding: 0
    });
    var valuesList = $('<ol class="values connectedSortable"></ol>').appendTo(container).css({
      width: 200, float: 'left', minHeight: 200, backgroundColor: '#eee', margin: 0, padding: 0
    });
    var choiceIds = [];
    $.each(settings.choices, function() {
      choiceIds.push('' + this.id);
    });

    function createItem(hash) {
      return $('<li>' + hash.name + '</li>').css({
        backgroundColor: '#cff',
        display: 'block',
        border: '1px solid #cdd',
        padding: 2,
        margin: 0
      }).data('obj-id', hash.id);
    }

    $.each(settings.choices, function() {
      if ($.inArray('' + this.id, values) == -1) {
        choicesList.append(createItem(this));
      }
    });

    $.each(values, function() {
      var index = $.inArray('' + this, choiceIds); // Why this[0]?
      if (index != -1) {
        valuesList.append(createItem(settings.choices[index]));
      }
    });

    choicesList.sortable({
  		connectWith: '.connectedSortable'
  	}).disableSelection();

  	valuesList.sortable({
  		connectWith: '.connectedSortable',
  		update: function() {
  		  values = [];
  		  $('li', valuesList).each(function(index) {
          values.push($(this).data('obj-id'));
          console.log($(this).data('obj-id'));
  		  });
  		  console.log('update', values.join(','), input);
  		  input.val(values.join(','));
  		}
  	}).disableSelection();
  };
})(jQuery);
