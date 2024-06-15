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

	$(window).load(function() {
	    $("#preloader").on(500).fadeOut();
	    $(".preloader").on(600).fadeOut("slow");
	});