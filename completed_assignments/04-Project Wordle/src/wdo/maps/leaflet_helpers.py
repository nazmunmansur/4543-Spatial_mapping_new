"""
wdo.maps.leaflet_helpers

Reusable mapping helpers built on ipyleaflet.
"""

from ipyleaflet import (
    Map, GeoJSON, basemaps,
    ScaleControl, Rectangle, Polyline
)


# -----------------------------
# Map
# -----------------------------
def make_map(center=(20, 0), zoom=2, **kwargs):
    """Create and return a map object."""
    return Map(center=center, zoom=zoom, **kwargs)


# -----------------------------
# Basemap
# -----------------------------
def add_basemap(map_obj, name="OpenStreetMap"):
    """Set the basemap (replaces existing one)."""

    basemap_dict = {
        "OpenStreetMap": basemaps.OpenStreetMap.Mapnik,
        "Satellite": basemaps.Esri.WorldImagery,
        "Terrain": basemaps.Stamen.Terrain,
    }

    map_obj.basemap = basemap_dict.get(name, basemaps.OpenStreetMap.Mapnik)


# -----------------------------
# GeoJSON
# -----------------------------
def add_geojson(map_obj, data, name=None, style=None):
    """Add GeoJSON data to a map."""

    style = style or {
        "color": "black",
        "weight": 2,
        "fillOpacity": 0.4
    }

    layer = GeoJSON(data=data, name=name, style=style)
    map_obj.add_layer(layer)
    return layer


# -----------------------------
# Fit bounds
# -----------------------------
def fit_map_to_geojson(map_obj, data):
    """Fit map view to GeoJSON bounds."""

    def extract_points(geo):
        pts = []

        # Normalize input
        if geo.get("type") == "Feature":
            features = [geo]
        else:
            features = geo.get("features", [])

        for f in features:
            geom = f.get("geometry", {})
            coords = geom.get("coordinates", [])
            gtype = geom.get("type")

            if gtype == "Polygon":
                for ring in coords:
                    pts.extend(ring)

            elif gtype == "MultiPolygon":
                for poly in coords:
                    for ring in poly:
                        pts.extend(ring)

        return pts

    pts = extract_points(data)

    if not pts:
        raise ValueError("No coordinates found in GeoJSON")

    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]

    bounds = [
        [min(lats), min(lons)],
        [max(lats), max(lons)]
    ]

    map_obj.fit_bounds(bounds)


# -----------------------------
# Controls
# -----------------------------
def add_scale_control(map_obj, position="bottomleft"):
    """Add scale control widget."""
    control = ScaleControl(position=position)
    map_obj.add_control(control)
    return control


# -----------------------------
# Bounding box
# -----------------------------
def add_bbox(map_obj, bbox, **style):
    """Draw a bounding box.

    bbox = (min_lon, min_lat, max_lon, max_lat)
    """

    if len(bbox) != 4:
        raise ValueError("bbox must be (min_lon, min_lat, max_lon, max_lat)")

    min_lon, min_lat, max_lon, max_lat = bbox

    rect = Rectangle(
        bounds=[(min_lat, min_lon), (max_lat, max_lon)],
        color=style.get("color", "red"),
        weight=style.get("weight", 2),
        fill_opacity=style.get("fill_opacity", 0.1)
    )

    map_obj.add_layer(rect)
    return rect


# -----------------------------
# Path / polyline
# -----------------------------
def add_path(map_obj, coords, **style):
    """Add a path/polyline.

    coords = [(lat, lon), ...]
    """

    if not coords or len(coords) < 2:
        raise ValueError("coords must contain at least two (lat, lon) points")

    line = Polyline(
        locations=coords,
        color=style.get("color", "blue"),
        weight=style.get("weight", 3),
        opacity=style.get("opacity", 1.0)
    )

    map_obj.add_layer(line)
    return line