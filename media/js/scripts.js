function initialize() {
  if (GBrowserIsCompatible()) {
    map = new GMap2(document.getElementById("map"));
    map.setCenter(new GLatLng(52.406374, 16.9251681), appKontekst.zoomLvl);
    map.setUIToDefault();
	geocoder = new GClientGeocoder();

	cluster = new ClusterMarker(map, {
   			clusterMarkerTitle: 'Kliknij aby przyblić i zobaczyć %count przystanki'
   	});

  }
}

function start(){
	var newh = $(window).height();
	$('#map').height(newh-50);
	initialize();
}

function showBusStops(){
	var searchUrl = '/exporter/przystanki/autobusy/';

    GDownloadUrl(searchUrl, function(data, responseCode) {
		if (responseCode == 200) {
			var xml = GXml.parse(data);
			BusmarkersArray = [];
			var markers = xml.documentElement.getElementsByTagName("marker");
			if (markers.length > 0) {
				for (var i = 0; i < markers.length; i++) {
					var name = markers[i].getAttribute("name");
					var linie = markers[i].getAttribute("linie");
					var id = markers[i].getAttribute("id");
					var point = new GLatLng(parseFloat(markers[i].getAttribute("lat")), parseFloat(markers[i].getAttribute("lng")));
					
					BusmarkersArray.push(newMarker(point, name, id, linie));
				}
				showPointers(BusmarkersArray);
				$('#showBusStop').hide();
				$('#hideBusStop').show();
				appKontekst.visibleBus = 1;
			}	
		}
     });	
}

function showTramStops(){
	var searchUrl = '/exporter/przystanki/tramwaje/';

    GDownloadUrl(searchUrl, function(data, responseCode) {
		if (responseCode == 200) {
			var xml = GXml.parse(data);
			TrammarkersArray = [];
			var markers = xml.documentElement.getElementsByTagName("marker");
			if (markers.length > 0) {
				for (var i = 0; i < markers.length; i++) {
					var name = markers[i].getAttribute("name");
					var id = markers[i].getAttribute("id");
					var linie = markers[i].getAttribute("linie");
					var point = new GLatLng(parseFloat(markers[i].getAttribute("lat")), parseFloat(markers[i].getAttribute("lng")));
					
					TrammarkersArray.push(newMarker(point, name, id, linie));
				}
				showPointers(TrammarkersArray);
				$('#showTramStop').hide();
				$('#hideTramStop').show();
				appKontekst.visibleTram = 1;
			}	
		}
     });	
}

function showNightStops(){
	var searchUrl = '/exporter/przystanki/nocne/';

    GDownloadUrl(searchUrl, function(data, responseCode) {
		if (responseCode == 200) {
			var xml = GXml.parse(data);
			NightmarkersArray = [];
			var markers = xml.documentElement.getElementsByTagName("marker");
			if (markers.length > 0) {
				for (var i = 0; i < markers.length; i++) {
					var name = markers[i].getAttribute("name");
					var id = markers[i].getAttribute("id");
					var linie = markers[i].getAttribute("linie");
					var point = new GLatLng(parseFloat(markers[i].getAttribute("lat")), parseFloat(markers[i].getAttribute("lng")));
					
					NightmarkersArray.push(newMarker(point, name, id, linie));
				}
				showPointers(NightmarkersArray);
				$('#showNightStop').hide();
				$('#hideNightStop').show();
				appKontekst.visibleNight = 1;
			}	
		}
     });		
}

function newMarker(point, name, id, linie) {
	var marker = new GMarker(point);
	GEvent.addListener(marker, 'click', function() {
		map.setCenter(point,appKontekst.zoomLvlDetail);
		var html = 'Przystanek: ' + name + '<br>Linie: ';
		var linie_temp = linie.split('|');
		for(indeks in linie_temp){
			html = html + '<a href="/mapa/rozklad/'+id+'/'+linie_temp[indeks]+'/" target="_blank" title="Rozkład linii '+linie_temp[indeks]+'">' + linie_temp[indeks] + '</a>' + ' ';
		}
		marker.openInfoWindowHtml(html);
	});
	return marker;
}


function showPointers(markersIn){
	cluster.addMarkers(markersIn);
	cluster.refresh(true);
}

function hideStops(type){
	cluster.removeMarkers();
	if(appKontekst.visibleBus == 1 && type != 'A'){
		cluster.addMarkers(BusmarkersArray);
	}
	if(appKontekst.visibleTram == 1 && type != 'T'){
		cluster.addMarkers(TrammarkersArray);
	}
	if(appKontekst.visibleNight == 1 && type != 'N'){
		cluster.addMarkers(NightmarkersArray);
	}
	switch(type){
		case 'A':
				$('#showBusStop').show();
				$('#hideBusStop').hide();
				break;					
		case 'T':
				$('#showTramStop').show();
				$('#hideTramStop').hide();
				break;					
		case 'N':
				$('#showNightStop').show();
				$('#hideNightStop').hide();
				break;					
		default:
				break;					
	}
	cluster.refresh(true);
}

function putMarker(direction,lat,lng,name, bus_id){
	if (lat == undefined || lng == undefined || lat == '' || lng == '') {
		if (geocoder) {
			geocoder.getLatLng('Polska, Poznań, ' + name, function(point){
				putMarker(direction, point.lat(), point.lng(), name);
			});
		return;	
		}
	}

	var blueIcon = new GIcon(G_DEFAULT_ICON);
	blueIcon.image = "http://www.google.com/intl/en_us/mapfiles/ms/micons/blue-dot.png";
	var redIcon = new GIcon(G_DEFAULT_ICON);
	redIcon.image = "http://www.google.com/intl/en_us/mapfiles/ms/micons/red-dot.png";

	if(direction == 'To'){
		if (appKontekst.toMarker != '') {
			map.removeOverlay(appKontekst.toMarker);
		}			

		appKontekst.toMarker = new GMarker(new GLatLng(lat, lng), {
			icon: blueIcon
		});
		GEvent.addListener(appKontekst.toMarker, "click", function(){
			appKontekst.toMarker.openInfoWindowHtml("Do: " + name);
		});
		map.addOverlay(appKontekst.toMarker);
		map.setCenter(new GLatLng(lat, lng), appKontekst.zoomLvl);
	}
	
	if(direction == 'From'){
		if (appKontekst.toMarker != '') {
			map.removeOverlay(appKontekst.fromMarker);
		}			
		appKontekst.fromMarker = new GMarker(new GLatLng(lat, lng), {
			icon: redIcon
		});
		GEvent.addListener(appKontekst.fromMarker, "click", function(){
			appKontekst.fromMarker.openInfoWindowHtml("Z: " + name);
		});
		map.addOverlay(appKontekst.fromMarker);
		map.setCenter(new GLatLng(lat, lng), appKontekst.zoomLvl);
	}	
}
