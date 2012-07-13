var map
var map_canvas
var thing_cache = []
var loaded_bundles
var MINIMIZED = 1
var MAXIMIZED = 2
var list_state = $.cookie( 'list_state' ) || MAXIMIZED
var browser_state = $.cookie( 'browser_state' ) || MINIMIZED
var map_type = $.cookie( 'map_type' ) || google.maps.MapTypeId.HYBRID

var toggleBrowser = function( e ) {
	if ( e ) {
		e.stopImmediatePropagation()
	}
	$( '#browser .wrapper' ).toggleClass( 'hidden' ).hasClass( 'hidden' ) ? $( '#browser .zoom_control img' ).attr( 'src', '/images/panel_control_down.png' ) : $( '#browser .zoom_control img' ).attr( 'src', '/images/panel_control_up.png' )
	browser_state = $( '#browser .wrapper' ).hasClass( 'hidden' ) ? MINIMIZED : MAXIMIZED
	$.cookie( 'browser_state', browser_state )
	return false
}

var sizeMap = function() {
	map_canvas.height( $(window).height() - $('#title').height() ) // This can be optimized
	google.maps.event.trigger( map, 'resize' )
	if( inspector.isVisible() ) inspector.resize()
}

var loadMarkersForUser = function ( uid ) {
    /* Load map markers */
    jQuery.ajax({
    	'type': 'GET',
    	'url': '/api/view/',
    	'data': 'format=json&uid=' + uid,
    	'dataType': 'json',
    	'complete': function( xhr, textStatus ) { console.info( textStatus ) },
    	'success': function( data, textStatus ) {
    		if ( data.status != 'success' ) {
    			alert( 'fail' )
    			return
    		}

    		thing_cache = $( data.things )

    		var bounds = new google.maps.LatLngBounds()

    		$( data.things ).each( function( i, thing ) {
//				    	if ( thing.parent ) {
//				    	} else {
			    	var latlng = new google.maps.LatLng( Number( thing.lattitude ), Number( thing.longitude ) )
			    	bounds.extend( latlng )
				    var marker = new google.maps.Marker({
						position: latlng,
						map: map
					})
					marker.thing = thing
					Placethings.marker_cache.addMarker( marker )
					google.maps.event.addListener( marker, 'click', function() {
						inspector.setMarker( marker )
						inspector.show()
					})
//						}
    		})

    		map.fitBounds( bounds )

		    /* Connect list elements to markers on mouseover and mouseclick */
		    /*
		    $( '#list li.thing a' ).each( function ( i, el ) {
		    	el = $(el)
		    	var id = el.attr( 'thing' )
		    	el.hover( function( e ) {
		    		Placethings.marker_cache.getMarker( id ).setVisible( false )
		    	}, function( e ) {
		    		Placethings.marker_cache.getMarker( id ).setVisible( true )
		    	})
		    	var marker = Placethings.marker_cache.getMarker( id )
		    	var thing = marker.thing
		    	var latlng = marker.getPosition()
		    	el.bind( "click", marker, function( e ) {
		    		e.preventDefault()
		    		toggleBrowser( e )
		    		showInspectorForMarker( marker )
		    	})
		    })
		    */

		    /* Connect browser elements to markers on mouseover and mouseclick */
		    $( '#browser li.thing a' ).each( function ( i, el ) {
		    	el = $(el)
		    	var id = el.attr( 'thing' )
		    	el.hover( function( e ) {
		    		Placethings.marker_cache.getMarker( id ).setVisible( false )
		    	}, function( e ) {
		    		Placethings.marker_cache.getMarker( id ).setVisible( true )
		    	})
		    	var marker = Placethings.marker_cache.getMarker( id )
		    	if ( marker && marker.thing ) {
			    	var thing = marker.thing
			    	var latlng = marker.getPosition()
			    	el.bind( "click", marker, function( e ) {
			    		e.preventDefault()
			    		toggleBrowser( e )
			    		inspector.setMarker( marker )
			    		inspector.toggle()
			    	})
			    }
		    })

    	}
    })
}

var getMapTypeHandler = function ( type ) {
	return function ( e ) {
		e.stopImmediatePropagation()
		map.setMapTypeId( type )
		$.cookie( 'map_type', type )
		return false
	}
}

$(document).ready( function() {
	/* Load text excerpts and build slider */
	var browserWidth = 0
	$( '#browser li' ).each( function ( i, el ) {
		var url = $( 'p', el ).attr( 'src' )
		if ( url ) {
			$( 'p', el ).load( url )
		}
		browserWidth += $(el).width() + 10
	})
	$( '#browser .wrapper #slider' ).slider( { max: browserWidth, slide: function ( event, ui ) {
		var newOffset = '-' + String( ui.value ) + 'px'
		$( '#browser ul' ).css( 'left', newOffset )
	}} )

	/* build map */
	map_canvas = document.getElementById( 'map_canvas' )
    map = new google.maps.Map( map_canvas, {
		zoom: 16,
		center: new google.maps.LatLng(32.82248, -96.762986),
		mapTypeId: map_type,
/*
		navigationControl: true,
		navigationControlOptions: {
			style: google.maps.NavigationControlStyle.SMALL
		},
		scaleControl: true,
*/
		disableDefaultUI: true
    });
	map_canvas = $( map_canvas )

	sizeMap()
	$(window).resize( sizeMap )

	inspector.init( map, 'inspector' )

	/* Create map type controls (roadmap, satellite, hybrid) */
	var selector_controls = $( '#map_type_selectors a' )
	$(selector_controls[0]).click( getMapTypeHandler( google.maps.MapTypeId.ROADMAP ) )
	$(selector_controls[1]).click( getMapTypeHandler( google.maps.MapTypeId.SATELLITE ) )
	$(selector_controls[2]).click( getMapTypeHandler( google.maps.MapTypeId.HYBRID ))


    /* Setup UI states */
    var browser = $( '#browser' )
    $( '.zoom_control', browser ).click( toggleBrowser )

	if ( browser_state == MAXIMIZED ) {
		$( '.wrapper', browser ).removeClass( 'hidden' )
		$( '.zoom_control img', browser ).attr( 'src', '/images/panel_control_up.png' )
	} else {
		$( '.wrapper', browser ).addClass( 'hidden' )
		$( '.zoom_control img', browser ).attr( 'src', '/images/panel_control_down.png' )
	}

    // Load text excerpts
    $( '.excerpt' ).each( function( i, el ) {
    	el = $(el)

    	el.load( el.attr( 'media' ), false, function( response ) {
    		el.html( response.substring( 0, 255 ) )
    	})
    })

    // Build user dropdown
    var user_el = $( '#user' )
	$( '#login_form' ).toggle()
    $( '.wrapper', user_el ).append( '<a id="user_dropdown" href="#"><img src="/images/dropdown.png" /></a>' )
    $( '#login_form' ).addClass( 'floating' )
    $( '#user_dropdown' ).click( function( e ) {
    	e.preventDefault()
    	$( '#login_form' ).css( 'right', Math.ceil( $(document).width() - $( '#user' ).offset().left - $('#user').width() ) )
    	$( '#login_form' ).toggle()
		if ( $('#login_form').css('display') == 'none' ) {
	    	$( '#user' ).css( '-moz-border-radius-bottomright', '5px' ).css( '-moz-border-radius-bottomleft', '5px' )
		} else {
	    	$( '#user' ).css( '-moz-border-radius-bottomright', '0' ).css( '-moz-border-radius-bottomleft', '0' )
		}
    })
})