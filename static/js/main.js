var map;
var uLat;
var uLong;
var infowindow;


function initMap() {

  var toronto = {lat: 43.6532, lng: -79.3832}; //43.6532 N, 79.3832 W
  // The map, centered at Toronto
  map = new google.maps.Map(
      document.getElementById('map'), {zoom: 11, center: toronto});

  $.get("http://localhost:5000/getChildCareData", function(data){
    var parsed = JSON.parse(data);
    var rec_centers = JSON.parse(parsed[0]);
    var child_care_centers = JSON.parse(parsed[1]);

    //Create markers through all filtered results
    for(var i=0; i<Object.keys(child_care_centers).length; i++){
      new_marker(child_care_centers[i]);
    }

    //Create recommendations from results
    for(var i=0; i<Object.keys(rec_centers).length; i++){
      if(i>=5){
        break;
      }
      new_recommendation(rec_centers[i]);
    }
  });

  $.get("http://localhost:5000/getAddreses", function(data){
     var parsed = JSON.parse(data);
     var home = parsed[0];
     var work = parsed[1];
    //marker for home address
     var marker = new google.maps.Marker({
        position: {lat: home.lat, lng: home.lng},
        map: map,
        title: "Home",
        icon: {
            path: fontawesome.markers.HOME,
            fillColor: '#36454f',
            fillOpacity: 0.8,
            strokeColor: '#000000',
            strokeOpacity: 1,
            strokeWeight: 1,
            scale: 0.5
        }
      });    
     //marker for work address
     var marker = new google.maps.Marker({
        position: {lat: work.lat, lng: work.lng},
        map: map,
        title: "Work",
        icon: {
            path: fontawesome.markers.BRIEFCASE,
            fillColor: '#36454f',
            fillOpacity: 0.8,
            strokeColor: '#000000',
            strokeOpacity: 1,
            strokeWeight: 1,
            scale: 0.5
        }
      });   
   

  });
}

//infowindow = new google.maps.InfoWindow();


function loc_infowindow(info) {
  return `<table class='table'>
      <tbody>
        <tr> 
          <th scope="row">` + info.LOC_NAME + `</th>
        <tr>
          <th scope="row">Phone</th>
          <td>` + info.PHONE + `</td>
        </tr>
        </tbody>
        </table>`;
}
      
function new_marker(info) {
  var marker = new google.maps.Marker({
    position: {lat: info.LATITUDE, lng: info.LONGITUDE},
    map: map,
    title: info.LOC_NAME,
    icon: {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: '#00F',
        fillOpacity: 0.6,
        strokeColor: '#00A',
        strokeOpacity: 0.9,
        strokeWeight: 1,
        scale: 4
    }
  });

  infowindow = new google.maps.InfoWindow({
    content: loc_infowindow(info)
  });
  
  marker.addListener('click', function() {
    //infowindow.setContent(loc_infowindow(info))
    infowindow.setContent(
    `<table class='table'>
    <tbody>
      <tr> 
        <th scope="row">` + info.LOC_NAME + `</th>
      </tr>
      <tr>
        <th scope="row">Address</th>
        <td>` + info.STR_NO + ' ' + info.STREET + `</td>
      </tr>
      <tr>
        <th scope="row">Rating</th>
        <td>` + into.RATING + `</td>
      </tr>
      <tr>
        <th scope="row">Phone</th>
        <td>` + info.PHONE + `</td>
      </tr>
      </tbody>
    </table>`)
    infowindow.open(map, marker);
  });
}

function new_recommendation(info){
  var marker = new google.maps.Marker({
    position: {lat: info.LATITUDE, lng: info.LONGITUDE},
    map: map,
    title: info.LOC_NAME,
    icon: {
        path: fontawesome.markers.STAR,
        fillColor: '#FFDF00',
        fillOpacity: 0.8,
        strokeColor: '#D4AF37',
        strokeOpacity: 1,
        strokeWeight: 2,
        scale: 0.5
    }
  });

  infowindow = new google.maps.InfoWindow({
    content: loc_infowindow(info)
  });
  
  marker.addListener('click', function() {
    //infowindow.setContent(loc_infowindow(info))
    infowindow.setContent(
    `<table class='table'>
    <tbody>
      <tr> 
        <th scope="row">` + info.LOC_NAME + `</th>
      </tr>
      <tr>
        <th scope="row">Address</th>
        <td>` + info.STR_NO + ' ' + info.STREET + `</td>
      </tr>
      <tr>
        <th scope="row">Rating</th>
        <td>` + into.RATING + `</td>
      </tr>
      <tr>
        <th scope="row">Phone</th>
        <td>` + info.PHONE + `</td>
      </tr>
      </tbody>
    </table>`)
    infowindow.open(map, marker);
  });

  $('.list-group').append(`<a href='#'' class='list-group-item list-group-item-action flex-column align-items-start'>
    <div class='d-flex w-100 justify-content-between'>
      <h5 class='mb-1'>`+ info.LOC_NAME + `</h5>
    </div>
    <p class='mb-1'>`+"Rating: "+ info.RATING.toFixed(1) +"/5.0" + `</p>
    <small>`+"Distance From Home: "+ info.DIST_FROM_HOME.toFixed(2)+" km"+`</small></a>`);

}


function sidebar_click(button) {
  button.classList.toggle("btn-light");
  button.classList.toggle("btn-dark");
  button.classList.toggle("active");
}

$(document).ready(function() {
  uLat = "43.599911"
  uLong = "-79.504631"
  initMap();
});
