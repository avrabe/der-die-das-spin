// Define a function that loads and displays the JSON data
function loadJSON() {
    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();
  
    // Define the URL of the JSON file
    var url = "entry.json";
  
    // Open a new connection to the server
    xhr.open("GET", url, true);
  
    // Set the response type to JSON
    xhr.responseType = "json";
  
    // Define what to do when the request is successful
    xhr.onload = function() {
      // Get the JSON data from the response
      var data = xhr.response;
  
      // Check if the data is valid
      if (data) {
        // Display the data in the website
        // For example, you can use document.getElementById() to get an element by its ID
        // and use innerHTML to change its content
        document.getElementById("genus").hidden = true;
        if (data[0].genus === "m") {
            document.getElementById("genus").innerHTML = "Der"
        } else if (data[0].genus === "f") {
            document.getElementById("genus").innerHTML = "Die"
        } else if (data[0].genus === "n") {
            document.getElementById("genus").innerHTML = "Das"
        }
            document.getElementById("nominativ_singular").innerHTML = data[0].nominativ_singular;
      } else {
        // Display an error message
        document.getElementById("error").innerHTML = "Invalid JSON data";
      }
    };
  
    // Define what to do when the request fails
    xhr.onerror = function() {
      // Display an error message
      document.getElementById("error").innerHTML = "Request failed";
    };
  
    // Send the request to the server
    xhr.send();
  }

  function reveal(artikel) {
    if ( artikel === document.getElementById("genus").innerHTML ) {
        document.getElementById("genus").className = "richtig"
    } else {
        document.getElementById("genus").className = "falsch"
    }
    document.getElementById("genus").hidden = false;
  }
  