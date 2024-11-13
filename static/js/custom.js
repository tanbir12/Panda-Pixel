	$(".js-height-full").height($(window).height());
	$(".js-height-parent").each(function() {
	    $(this).height($(this).parent().first().height());
	});



	$('.header').affix({
	    offset: {
	        top: 100,
	        bottom: function() {
	            //
	        }
	    }
	})

	$(window).on('load', function() {
		setTimeout(function() {
			$("#preloader").fadeOut(500);
			$(".preloader").fadeOut(600);
		}, 500); // This will wait for 500 milliseconds before executing the fadeOut
	});