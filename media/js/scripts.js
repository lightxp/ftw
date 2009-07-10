/*
 * inicjalizacja mapy
 */
function initialize() {
  if (GBrowserIsCompatible()) {
    map = new GMap2(document.getElementById("map"));
    map.setCenter(new GLatLng(52.406374, 16.9251681), appKontekst.zoomLvl);
    map.setUIToDefault();
	geocoder = new GClientGeocoder();
	geocoder.setBaseCountryCode('pl');

	cluster = new ClusterMarker(map, {
   			clusterMarkerTitle: 'Kliknij aby przyblić i zobaczyć %count przystanki'
   	});
	
	GEvent.addListener(map,"tilesloaded", function() {
		$('#msg').hide();
	}); 
	GEvent.addListener(map,"dragstart", function() {
		$('#msg').show();
	}); 
	GEvent.addListener(map,"dragend", function() {
		$('#msg').hide();
	}); 
	GEvent.addListener(map,"zoomend", function() {
		$('#msg').show();
	}); 
  }
}

/*
 * resize diva + start inicjalizacji mapy
 */
function start(){
	var newh = $(window).height();
	$('#map').height(newh-75);
	initialize();
}

/*
 * pokazanie przystanków autobusowych
 */
function showBusStops(){
	downloadMarkers(markersArray.bus,markersArray.bus.url);	
}

/*
 * pokazanie przystankow tramwajowych
 */
function showTramStops(){
	downloadMarkers(markersArray.tram,markersArray.tram.url);	
}

/*
 * pokazanie przystankow nocnych
 */
function showNightStops(){
	downloadMarkers(markersArray.night,markersArray.night.url);		
}

/*
 * pokazanie najblizszych punktow
 */
function showNearest(lat, lng){
	downloadMarkers(markersArray.nearest,markersArray.nearest.url + lat + '/' + lng + '/');		
	doDrawCircle(lat,lng);
	map.setCenter(new GLatLng(lat, lng),appKontekst.zoomLvlDetail);
	$('.nearest_hide').show();
}

/*
 * Pobiera markery z serwera i umieszcza je na mapie
 */
function downloadMarkers(markerType,url){
	$('#msg').show();
	
    GDownloadUrl(url, function(data, responseCode) {
		if (responseCode == 200) {
			var xml = GXml.parse(data);
			markerType.markers = [];
			var markers = xml.documentElement.getElementsByTagName("marker");
			if (markers.length > 0) {
				for (var i = 0; i < markers.length; i++) {
					var name = markers[i].getAttribute("name");
					var linie = markers[i].getAttribute("linie");
					var id = markers[i].getAttribute("id");
					var point = new GLatLng(parseFloat(markers[i].getAttribute("lat")), parseFloat(markers[i].getAttribute("lng")));
					
					markerType.markers.push(newMarker(point, name, id, linie));
				}
				showPointers(markerType.markers);
				$('#' + markerType.name + '_show').hide();
				$('#' + markerType.name + '_hide').show();
				markerType.visible = 1;
			}	
		}
     });		
}

/*
 * dodanie markera z przystankiem
 */
function newMarker(point, name, id, linie) {
	var marker = new GMarker(point);
	GEvent.addListener(marker, 'click', function() {
		map.setCenter(point,appKontekst.zoomLvlDetail);
		var html = 'Przystanek: ' + name + '<br>Linie: ';
		var linie_temp = linie.split('|');
		for(indeks in linie_temp){
			html = html + '<a href="/mapa/rozklad/'+id+'/'+linie_temp[indeks]+'/" target="_blank" title="Rozkład linii '+linie_temp[indeks]+'">' + linie_temp[indeks] + '</a>' + ' ';
		}
		if (appKontekst.fromMarker) {
			html = html + "<br><a href=\"javascript:showWay('From'," + point.lat() + "," + point.lng() + ");\">pokaż drogę na ten przystanek</a>";
		}	
		if (appKontekst.toMarker) {
			html = html + "<br><a href=\"javascript:showWay('To'," + point.lat() + "," + point.lng() + ");\">pokaż drogę z tego przystanku</a>";
		}	
		marker.openInfoWindowHtml(html);
	});
	return marker;
}

/*
 * dodanie pointerow do clustera
 */
function showPointers(markersIn){
	cluster.addMarkers(markersIn);
	cluster.refresh(true);
	$('#msg').hide();
}

/*
 * ukrycie punktow z mapy
 */
function hideStops(type){
	$('#msg').show();
	cluster.removeMarkers();
	if(markersArray.bus.visible == 1 && type != 'A'){
		cluster.addMarkers(markersArray.bus.markers);
	}
	if(markersArray.tram.visible == 1 && type != 'T'){
		cluster.addMarkers(markersArray.tram.markers);
	}
	if(markersArray.night.visible == 1 && type != 'N'){
		cluster.addMarkers(markersArray.night.markers);
	}
	if(markersArray.nearest.visible == 1 && type == 'Nearest'){
		cluster.addMarkers(markersArray.nearest.markers);
	}	
	switch(type){
		case 'A':
				$('#' + markersArray.bus.name + '_show').show();
				$('#' + markersArray.bus.name + '_hide').hide();
				markersArray.bus.visible = 0;
				break;					
		case 'T':
				$('#' + markersArray.tram.name + '_show').show();
				$('#' + markersArray.tram.name + '_hide').hide();
				markersArray.tram.visible = 0;
				break;					
		case 'N':
				$('#' + markersArray.night.name + '_show').show();
				$('#' + markersArray.night.name + '_hide').hide();
				markersArray.night.visible = 0;
				break;					
		case 'Nearest':
				$("#showNearest").show();
				$('#' + markersArray.nearest.name + '_hide').hide();
				markersArray.nearest.visible = 0;
		default:
				break;					
	}
	cluster.refresh(true);
	$('#msg').hide();
}

/*
 * posadowienie pinezki Z/Do
 */
function putMarker(direction,lat,lng,name, bus_id){
	if (lat == undefined || lng == undefined || lat == '' || lng == '') {
		if (geocoder) {
			geocoder.getLatLng('Polska, Poznań, ' + name, function(point){
				putMarker(direction, point.lat(), point.lng(), name);
			});
		return;	
		}
	}
	
	if (direction == 'To')
		var new_marker = appKontekst.toMarker;
	if (direction == 'From')
		var new_marker = appKontekst.fromMarker;

	var m_icon = new GIcon(G_DEFAULT_ICON);
	m_icon.image = new_marker.ico;

	if (new_marker.storage != '') {
			map.removeOverlay(new_marker.storage);
	}

	new_marker.storage = new GMarker(new GLatLng(lat, lng), {
		icon: m_icon,
		draggable: true
	});
	generateHTMLmarker(new_marker,name);
	
	GEvent.addListener(new_marker.storage, "click", function(){
		new_marker.storage.openInfoWindowHtml(new_marker.desc);
	});
	GEvent.addListener(new_marker.storage, "dragend", function() {
		geocoder.getLocations(new_marker.storage.getLatLng(), function(wyniki){
			reverseCoder(new_marker,wyniki);
		});
	});
	map.addOverlay(new_marker.storage);
	map.setCenter(new GLatLng(lat, lng), appKontekst.zoomLvl);
}

/*
 * generuje opis markera z pozycja
 */
function generateHTMLmarker(new_marker,name){
	var lat = new_marker.storage.getLatLng().lat();
	var lng = new_marker.storage.getLatLng().lng();
	var	nearest = "<br><a href=\"javascript:showNearest("+lat+","+lng+");\" id='showNearest'>pokaż przystanki w okolicy</a><a href=\"javascript:hideNearest();\" class='hideNearest' style='display:none;'>ukryj przystanki w okolicy</a>";
	new_marker.desc = new_marker.prefix + ': ' + name + nearest;
}

/*
 * wyrysowanie kola o zadanej srednicy
 */
function doDrawCircle(lat,lng){
	if (circle) {
		map.removeOverlay(circle);
	}
	
	var bounds = new GLatLngBounds();	
	var circlePoints = Array();

	with (Math) {
		var d = appKontekst.circleRadius/6378.8;	// radians

		var lat1 = (PI/180)* lat; // radians
		var lng1 = (PI/180)* lng; // radians

		for (var a = 0 ; a < 361 ; a++ ) {
			var tc = (PI/180)*a;
			var y = asin(sin(lat1)*cos(d)+cos(lat1)*sin(d)*cos(tc));
			var dlng = atan2(sin(tc)*sin(d)*cos(lat1),cos(d)-sin(lat1)*sin(y));
			var x = ((lng1-dlng+PI) % (2*PI)) - PI ; // MOD function
			var point = new GLatLng(parseFloat(y*(180/PI)),parseFloat(x*(180/PI)));
			circlePoints.push(point);
			bounds.extend(point);
		}

		if (d < 1.5678565720686044) {
			circle = new GPolygon(circlePoints, '#000000', 2, 1, '#000000', 0.25);	
		}
		else {
			circle = new GPolygon(circlePoints, '#000000', 2, 1);	
		}
		map.addOverlay(circle); 
	}
}

/*
 * ukrycie najblizszych punktow
 */
function hideNearest(){
	if (circle) {
		map.removeOverlay(circle);
	}
	hideStops('Nearest');	
}

/*
 * pokazanie drogi na/z przystanku
 */
function showWay(direction,lat,lng){
	$('#msg').show();
	var startPoint = [];
	var endPoint = [];
	
	if(direction == 'To'){
		endPoint['lat'] = appKontekst.toMarker.storage.getLatLng().lat();
		endPoint['lng'] = appKontekst.toMarker.storage.getLatLng().lng();
		startPoint['lat'] = lat;
		startPoint['lng'] = lng;
	}

	if(direction == 'From'){
		startPoint['lat'] = appKontekst.fromMarker.storage.getLatLng().lat();
		startPoint['lng'] = appKontekst.fromMarker.storage.getLatLng().lng();
		endPoint['lat'] = lat;
		endPoint['lng'] = lng;
	}
	if(directions){
		directions.clear();
	}
	directions = new GDirections(map, document.getElementById("route_msg"));
	directions.load("from: "+startPoint['lat']+","+startPoint['lng']+" to: "+endPoint['lat']+","+endPoint['lng'], {travelMode:G_TRAVEL_MODE_WALKING, locale: 'pl_PL'});
	
	GEvent.addListener(directions,"load", function() {
		appKontekst.tripDistance = directions.getDistance().meters;
		appKontekst.tripDuration = directions.getDuration().seconds;
    	$('#status .distance').html(directions.getDistance().html);
    	$('#status .duration').html(directions.getDuration().html);
		$('#hideDirection').show();
		$('#msg').hide();
	}); 
}

/*
 * usuwa trase piesza
 */
function hideDirection(){
	$('#hideDirection').hide();
	appKontekst.tripDistance -= directions.getDistance().meters;
	appKontekst.tripDuration -= directions.getDuration().seconds;
	$('#status .distance').empty();
	$('#status .duration').empty();	
	directions.clear();
}

/*
 * po przesunieciu pinezki pobierz nazwe ulicy
 */
function reverseCoder(marker, wyniki) {
	var address = new Array();
	if (!wyniki || wyniki.Status.code != 200) {
		//brak lokalizacji
	} else {
		if(wyniki.Placemark[0].AddressDetails && wyniki.Placemark[0].AddressDetails.Country && wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea){
			if (wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.AdministrativeAreaName && wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.AdministrativeAreaName) {
				address['area'] = wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.AdministrativeAreaName;
			}
			if (wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality && wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.SubAdministrativeArea) {
				address['city'] = wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.LocalityName;
			} 
			if (wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality 
				&& wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.SubAdministrativeArea 
				&& wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.Thoroughfare) {
				address['street'] = wyniki.Placemark[0].AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.Thoroughfare.ThoroughfareName ;
			}			
		}
		address['full_address'] = wyniki.Placemark[0].address;
	}
	$('#'+marker.input_id).val(address['street']);
	generateHTMLmarker(marker,address['street']);
}
