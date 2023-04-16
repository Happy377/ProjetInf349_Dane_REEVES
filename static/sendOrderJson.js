function sendOrderJson() {

  var jsonData = document.getElementById("json-data").value;

  fetch("http://localhost:5000/order", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: jsonData
  })
  .then(response => {
    return response.json();
  })
  .then(data => {
    console.log(data);
  })
}