from PyQt5.QtWebEngineWidgets import QWebEngineView # pyright: ignore[reportMissingImports]


class OSMMapWidget(QWebEngineView):

    def __init__(self, parent=None):

        super().__init__(parent)

        html = """

        <!DOCTYPE html>

        <html>

        <head>

            <meta charset="utf-8"/>

            <meta name="viewport"
                  content="width=device-width,
                           initial-scale=1.0">

            <link rel="stylesheet"
                  href="https://unpkg.com/leaflet/dist/leaflet.css"/>

            <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>

            <style>

                html, body {
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                    background: black;
                }

                #map {
                    width: 100%;
                    height: 100%;
                }

            </style>

        </head>

        <body>

            <div id="map"></div>

            <script>

                var map = L.map('map', {

                    zoomControl: false,
                    attributionControl: false

                }).setView([12.9716, 77.5946], 15);

                L.tileLayer(
                    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                    {
                        maxZoom: 19
                    }
                ).addTo(map);

                var marker = L.marker(
                    [12.9716, 77.5946]
                ).addTo(map);

            </script>

        </body>

        </html>

        """

        self.setHtml(html)