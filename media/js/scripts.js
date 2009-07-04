function initialize() {
  if (GBrowserIsCompatible()) {
    map = new GMap2(document.getElementById("map"));
    map.setCenter(new GLatLng(52.406374, 16.9251681), 13);
    map.setUIToDefault();
  }
}

function start(){
	var newh = $(window).height();
	$('#map').height(newh-50);
	initialize();
}

function showBusStops(){
	var searchUrl = '/exporter/przystanki/';

    GDownloadUrl(searchUrl, function(data, responseCode) {
		if (responseCode == 200) {
			var xml = GXml.parse(data);
			BusmarkersArray = [];
			var markers = xml.documentElement.getElementsByTagName("marker");
			if (markers.length > 0) {
				for (var i = 0; i < markers.length; i++) {
					var name = markers[i].getAttribute("name");
					var id = markers[i].getAttribute("id");
					var point = new GLatLng(parseFloat(markers[i].getAttribute("lat")), parseFloat(markers[i].getAttribute("lng")));
					
					BusmarkersArray.push(newMarker(point, name, id));
				}
				showPointers();
			}	
		}
     });	
}

function newMarker(point, name, id) {
	var marker = new GMarker(point);
	GEvent.addListener(marker, 'click', function() {
		map.setCenter(point,17);
		marker.openInfoWindowHtml(name + ' ' + id);
	});
	return marker;
}


function showPointers(){
	alert(BusmarkersArray);
	cluster = new ClusterMarker(map, {
   			clusterMarkerTitle: 'Kliknij aby przyblić i zobaczyć %count przystanki'
   	});
	cluster.addMarkers(BusmarkersArray);
	cluster.refresh(true);
}

function showTramStops(){
	
}

function showNightStops(){
	
}
