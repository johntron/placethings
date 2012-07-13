var inspectorWrapper = function( obj ) {
	for(var o in obj){
		this[o] = obj[o];
	}
}
inspectorWrapper.prototype = new google.maps.OverlayView()

var inspectorProxy = new inspectorWrapper({
	inspector_: false,
	map_: false,
	id_: false,
	window_: false,
	init: function( inspector, map, id ) {
		this.inspector_ = inspector
		this.id_ = id
		this.map_ = map
		this.setMap( map )
		return this
	},
	onAdd: function() {
		var panes = this.getPanes()
		var floatPane = panes.floatPane
		floatPane.appendChild( document.getElementById( this.id_ ) )
		this.window_ = $( '#' + this.id_ )
	},
	draw: function() { },
	toggle: function() {
		this.window_.hasClass( 'hidden' ) ? inspector.show() : inspector.hide()
	},
	show: function() {
		this.window_.removeClass( 'hidden' )
		
		var centerToBottom = Math.floor( map_canvas.height() / 2 )
		var markerLatLng = Placethings.marker_cache.getMarker( this.inspector_.thing_.id ).getPosition()
		var markerPixels = this.getProjection().fromLatLngToDivPixel( markerLatLng )
		markerPixels.y -= centerToBottom - 64
		markerLatLng = this.getProjection().fromDivPixelToLatLng( markerPixels )
		this.map_.panTo( markerLatLng )
		this.window_.width( $(map_canvas).width() )
		this.window_.height( $(map_canvas).height() )
		map.setOptions( { 'scrollwheel': false } )
	},
	hide: function() {
		this.window_.addClass( 'hidden' )
		map.setOptions( { 'scrollwheel': true } )
	}
})


var inspector = {
	visible_: false,
	id_: '',
	window_: null,
	bundleView_: null,
	thingView_: null,
	repliesView_: null,
	proxy_: null,
	thing_: null,
	init: function( map, id ) {
		this.id_ = id
		$(document.body).append( '<div id="proxy"></div>' ) 
		this.proxy_ = inspectorProxy.init( this, map, 'proxy' )
		this.window_ = $( '#' + this.id_ )
		this.thingView_ = InspectorThingView.init( $( '#thing', this.window_ ) )
		this.window_.click( this.toggle )
		return this
	},
	toggle: function() {
		inspector.isVisible() ? inspector.hide() : inspector.show()
	},
	show: function() {
		this.window_.removeClass( 'hidden' )
		this.proxy_.show()
		this.thingView_.show()
		this.visible_ = true
	},
	hide: function() {
		this.window_.addClass( 'hidden' )
		
		this.proxy_.hide()
		this.thingView_.hide()
		//this.bundleView_.hide()
		//this.repliesView_.hide()
		
		this.visible_ = false
	},
	isVisible: function() { return this.visible_ },
	resize: function() {
		this.proxy_.show()
		this.thingView_.resize()
	},
	populate: function( thing ) {
		this.thingView_.populate( thing )
		/*
		var bundle_list = $( '#bundle' )
		if ( thing.bundles.length ) {
			bundle_list.show()
			bundle_list.html( '' )
		    jQuery.ajax({
		    	'type': 'GET',
		    	'url': '/api/list-bundle/',
		    	'data': 'format=json&id=' + thing.bundles[ 0 ],
		    	'dataType': 'json',
		    	'success': function( data, textStatus ) {
		    		if ( data.status != 'success' ) {
		    			alert( 'fail' )
		    			return
		    		}
		    		$( data.things ).each( function( i, thing ) {
		    			bundle_list.append( '<li><img src="' + Placethings.get_thumbnail_url( thing.media, 100, 100 ) + '" /></li>' )
		    		})
		    	}
		    })
		} else {
			bundle_list.hide()
		}
	
		if ( thing.replies > 0 ) {
			this.repliesView_.populate( thing, thing_cache )
			this.repliesView_.show()
		} else {
			this.repliesView_.hide()
		}
		*/
		this.thing_ = thing
	},
	setMarker: function( marker ) {
		this.populate( marker.thing )
	}
}

/*
	Inspector Thing view
	A single Thing
*/
var InspectorThingView = {
	window_: null,
	thing_: null,
	visible_: false,
	loading_els: 0,
	init: function ( window ) {
		this.window_ = window
		return this
	},
	populate: function( thing ) {
		this.thing_ = thing
		if ( thing.title && thing.title != '' ) {
			if ( $( 'h2', this.window_ ).hasClass( 'hidden' ) ) {
				$( 'h2', this.window_ ).removeClass( 'hidden' )
			}
			$( 'h2', this.window_ ).html( thing.title )
		} else if ( !$( 'h2', this.window_ ).hasClass( 'hidden' ) ) {
			$( 'h2', this.window_ ).addClass( 'hidden' )			
		}
		if ( thing.type == 'I' ) {
			var url = Placethings.get_thumbnail_url( thing.media, 350, 350 )
			var media = $( '.media', this.window_ )
			media.html( '<img src="" />' )
			this.loading_el()
			$( 'img', media ).load( this.handle_load ).error( this.handle_load ).attr( 'src', url)
		} else {
			var media = $( '.media', this.window_ )
			media.html( '<p></p>' )
			this.loading_el()
			media.load( thing.media, false, this.handle_load )
		}
		if ( thing.author ) {
			if ( thing.author ) {
				author = thing.author
				if ( author.avatar ) {
					var avatar = $( '.avatar', this.window_ )
					var url = Placethings.get_thumbnail_url( author.avatar, 64, 64 )
					avatar.html( '<img src="" />' ).removeClass( 'hidden' )
					this.loading_el()
					$( 'img', avatar ).load( this.handle_load ).error( this.handle_load ).attr( 'src', url )
				} else {
					$( '.avatar', this.window_ ).addClass( 'hidden' )
				}
				$( '.username', this.window_ ).attr( 'href', Placethings.get_url_for_user( author.username ) ).html( author.username ).removeClass( 'hidden' )
				$( '.follow', this.window_ ).attr( 'href', Placethings.get_url_for_user( author.username ) ).removeClass( 'hidden' )
			}
		} else {
			$( '.avatar', this.window_ ).addClass( 'hidden' )
			$( '.username', this.window_ ).addClass( 'hidden' )
		}
		$( 'span.age', this.window_ ).text( thing.timestamp )
		$( 'span.location', this.window_ ).html( '(' + thing.lattitude + ', ' + thing.longitude + ')' )
	},
	show: function() {
		this.clearMargins()
		// Wait for images to finish loading, then show and position window
		var timeout = false
		var to = setTimeout( function() { timeout = true }, 20000 )
		var view = this
		var int = setInterval( function() { if ( timeout || !view.images_loading() ) {
			clearInterval( int )
			clearTimeout( to )
			view.window_.removeClass( 'hidden' )
			view.resize()
			view.visible_ = true
		} }, 250 )
	},
	hide: function() {
		this.window_.addClass( 'hidden' )
		this.visible_ = false
	},
	resize: function() {
		var margin = String( Math.floor( (this.window_.parent().width() - this.window_.width() ) / 2 ) ) + 'px'
		this.setMargins( margin )
	},
	loading_el: function( ) {
		this.loading_els++
	},
	handle_load: function() {
		this.loading_els--
	},
	images_loading: function() {
		return 0 == this.loading_els
	},
	toggle: function() {
		this.visible_ ? this.hide() : this.show()
	},
	setMargins: function( margin ) {
		this.window_.css( 'margin-left', margin ) //.css( 'margin-right', margin )
	},
	clearMargins: function() {
		this.window_.css( 'margin-left', 'auto' ) //.css( 'margin-right', 'auto' )
	}
}


/*
	Inspector bundle view
	A list of Things
*/
var InspectorBundleView = {
	window_: null,
	things_: null,
	visible_: null,
	init: function ( window ) {
		this.window_ = $( window )
		this.things_
		this.visible_ = false
		return this
	},
	populate: function( parent, replies ) {
	},
	show: function() {
		this.window_.removeClass( 'hidden' )
		this.visible_ = true
	},
	hide: function() {
		this.window_.addClass( 'hidden' )
		this.visible_ = false
	},
	toggle: function() {
		this.visible_ ? this.hide() : this.show()
	}
}



/*
	Inspector replies view
	A list of replies
*/
var InspectorRepliesView = {
	window_: null,
	replies_: null,
	visible_: false,
	init: function ( window ) {
		this.window_ = window
		return this
	},
	populate: function( replies ) {
		if ( replies ) this.replies_ = $( replies )
		
		if ( this.replies_ ) {
			$( 'ul', this.window_ ).empty()
			this.replies_.each( function( i, reply ) {
				if ( i < 5 ) {
					InspectorReply.init( reply ).appendTo( $( 'ul', this.window_ ) )
				} else if ( i == 6 ) {
					InspectorReply.init( reply, true ).appendTo( $( 'ul', this.window_ ) )
				}
			})
		} else {
			
		}
	},
	show: function() {
		this.window_.removeClass( 'hidden' )
		this.visible_ = true
	},
	hide: function() {
		this.window_.addClass( 'hidden' )
		this.visible_ = false
	},
	toggle: function() {
		this.visible_ ? this.hide() : this.show()
	}
}



/*
	Inspector reply view
	A single reply
*/

var InspectorReply = {
	init: function ( thing, last ) {
		this.thing_ = thing
		this.last_ = last
	},
	appendTo: function( el ) {
		if( this.last_ ) {
			if( this.thing_.type == 'I' ) {
				$(el).append( '<li class="last"><img src="' + Placethings.get_thumbnail_url( this.thing_.media, 64, 64 ) + '" > By ' + this.thing_.username + '</li>' )
			} else if( this.thing_.type == 'T' ) {
				$(el).append( '<li class="last"><p></p></li>' )
				$( 'li p', $(el) ).load( this.thing_.media, false, function( responseText ) {
					this.innerHTML = responseText.substr( 0, 100 )
				})
			}
		} else {
			if( this.thing_.type == 'I' ) {
				$(el).append( '<li><img src="' + Placethings.get_thumbnail_url( this.thing_.media, 64, 64 ) + '" > By ' + this.thing_.username + '</li>' )
			} else if( this.thing_.type == 'T' ) {
				$(el).append( '<li><p></p></li>' )
				$( 'li p', $(el) ).load( this.thing_.media, false, function( responseText ) {
					this.innerHTML = responseText.substr( 0, 100 )
				})
			}
		}
	}
}