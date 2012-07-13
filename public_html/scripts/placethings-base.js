var Placethings = {
	get_thumbnail_url: function( url, maxwidth, maxheight ) {
		var i,j = 0
		while ( i != -1 ) {
			j = i
			i = url.indexOf( '.', i + 1 )
		}
		return url.substr( 0, j ) + '-' + maxwidth + 'x' + maxheight + url.substr( j )
	},
	
	get_url_for_user: function( username ) {
		return 'http://placethings/user/' + username + '/'
	},
	marker_cache: {
		markers: [],
		addMarker: function( marker ) {
			if( "undefined" == typeof marker.thing ) {
				console.info( "marker.thing is undefined" )
				return
			}
			this.markers[ marker.thing.id ] = marker
		},
		getMarker: function( thing_id ) {
			if( this.markers[ thing_id ] ) {
				return this.markers[ thing_id ]
			} else {
				console.info( "no marker for thing #" + thing_id )
				return
			}
		}
	}
}