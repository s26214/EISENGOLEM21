const viewer = new Cesium.Viewer("cesiumContainer", {
  shouldAnimate: true,
  animation: false, // Hides the timeline
  timeline: false, // Hides the timeline controls
  fullscreenButton: false, // Hides the fullscreen button
  homeButton: false, // Hides the home button
  geocoder: false, // Hides the geocoder (search bar)
  navigationHelpButton: false, // Hides the help button
  sceneModePicker: false, // Hides the scene mode picker (2D/3D)
  baseLayerPicker: false, // Hides the map layer picker
  creditContainer: null, // Hides Cesium credits
});

viewer.cesiumWidget.creditContainer.style.display = "none"; //Hides the CESIUM info

document
  .getElementById("satellitesButton")
  .addEventListener("click", function () {
    viewer.dataSources.add(
      Cesium.CzmlDataSource.load("../czml_data/simple.czml")
    );
    viewer.camera.flyHome(0); // Move the camera to default view
  });
