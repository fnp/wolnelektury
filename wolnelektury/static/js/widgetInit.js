	$(function() {		
		$("#id_qq").autocomplete({
			source: function(request, response) {
				$.ajax({
					url: "http://lektury.staging.nowoczesnapolska.org.pl/katalog/jtags/",
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
