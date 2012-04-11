
var wl_scripts_loaded = {};

function wl_load_search_if_ready(id) {
    wl_scripts_loaded[id] = true;
    if (wl_scripts_loaded['wl-search-script'] &&
	wl_scripts_loaded['wl-jquery-ui-script']) 
    {
	var s = $('#id_qq');
	s.search({source: s.attr('data-source')});
    }
}

$('#wl-search-script').ready(function(){wl_load_search_if_ready('wl-search-script');});
$('#wl-jquery-ui-script').ready(function(){wl_load_search_if_ready('wl-jquery-ui-script');});

/*autocomplete({
			source: function(request, response) {
				$.ajax({
					url: "http://www.wolnelektury.pl/katalog/jtags/",
					dataType: "jsonp",
					data: {
						featureClass: "P",
						style: "full",
						maxRows: 10,
						q: request.term
					},
					success: function(data) {
						response($.map(data.matches, function(item) {
							return {
								label: item,
								value: item
							}
						}))
					}					
				})
			},
			minLength: 2,
            select: function(event, ui) {
                $("#id_qq").val(ui.item.value);
                $("#wl-form").submit();
            }			
		});
	});
*/
