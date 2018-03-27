function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(updatePosition)
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}
function updatePosition(position) {
  map.setView([position.coords.latitude, position.coords.longitude], 13);
}

var map = L.map('map').setView([52.087306, 4.288373], 13);

L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
	maxZoom: 18,
	id: 'mapbox.light'
}).addTo(map);

$(document).ready(getLocation())

// Initialise the FeatureGroup to store editable layers
var editableLayers = new L.FeatureGroup();
map.addLayer(editableLayers);

var drawPluginOptions = {
  position: 'topright',
  draw: {
    polygon: {
      allowIntersection: false, // Restricts shapes to simple polygons
      drawError: {
        color: '#e1e100', // Color the shape will turn when intersects
        message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
      },
      shapeOptions: {
        color: '#97009c'
      }
    },
    // disable toolbar item by setting it to false
    polyline: false,
    circle: false, // Turns off this drawing tool
    rectangle: false,
    marker: false,
		circlemarker: false
    },
  edit: {
    featureGroup: editableLayers, //REQUIRED!!
    remove: true
  }
};

// Initialise the draw control and pass it the FeatureGroup of editable layers
var drawControl = new L.Control.Draw(drawPluginOptions);
map.addControl(drawControl);

map.on('draw:drawstart', function(e) {
	editableLayers.eachLayer(function (layer) {
    editableLayers.removeLayer(layer);
	});
	$("#download-panel").html("")
});

map.on('draw:deleted', function(e) {
	editableLayers.eachLayer(function (layer) {
    editableLayers.removeLayer(layer);
	});
	$("#download-panel").html("")
});

map.on('draw:created', function(e) {
  var type = e.layerType,
  layer = e.layer;
  editableLayers.addLayer(layer);
	$("#download-panel").html('<form id=fmeform><div class="form-group"><div class="form-group"><label for="usr">Username:</label><input type="text" class="form-control" id="usr"></div><div class="form-group"><label for="pwd">Password:</label><input type="password" class="form-control" id="pwd"></div></div><button id="fmesubmit" type="button" class="btn btn-default">Submit</button></form>')

	$("#fmesubmit").click(function(){
		editableLayers.eachLayer(function (layer) {
			for (var f in layer._renderer._layers){
				var feature = layer._renderer._layers[f];
			}
			var userPolygon = feature.toGeoJSON();
			console.log(userPolygon)
			callFME($('#usr').val(),$('#pwd').val())
		});
	});

});
