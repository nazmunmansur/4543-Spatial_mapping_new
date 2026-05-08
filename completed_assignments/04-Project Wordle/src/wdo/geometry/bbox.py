def bbox_from_points(points):
    """Return bbox as (min_lon, min_lat, max_lon, max_lat)."""
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    return (min(lons), min(lats), max(lons), max(lats))


def bbox_from_feature(feature):
    """Extract all coordinates from a feature and compute bbox."""
    raise NotImplementedError


def bbox_from_features(features):
    """Compute bbox across multiple features."""
    raise NotImplementedError


def bbox_to_polygon(bbox):
    """Convert bbox tuple into a closed polygon coordinate list."""
    min_lon, min_lat, max_lon, max_lat = bbox
    return [
        (min_lat, min_lon),
        (min_lat, max_lon),
        (max_lat, max_lon),
        (max_lat, min_lon),
        (min_lat, min_lon),
    ]


"""
Mean center (average of vertices) for GeoJSON features.
"""

def _extract_points(feature):
    """Internal helper: flatten Polygon/MultiPolygon into (lon, lat) list."""
    geom = feature.get("geometry", {})
    coords = geom.get("coordinates")
    gtype = geom.get("type")

    if not coords:
        return []

    pts = []

    if gtype == "Polygon":
        for ring in coords:
            pts.extend(ring)

    elif gtype == "MultiPolygon":
        for poly in coords:
            for ring in poly:
                pts.extend(ring)

    else:
        return []

    return pts


def feature_center_mean(feature):
    """
    Return (lat, lon) using mean of all vertices.

    Notes
    -----
    - More balanced than bbox center for irregular shapes
    - Still not perfect for MultiPolygon (use largest_polygon_only if needed)
    """

    pts = _extract_points(feature)

    if not pts:
        return None

    avg_lon = sum(p[0] for p in pts) / len(pts)
    avg_lat = sum(p[1] for p in pts) / len(pts)

    return avg_lat, avg_lon


def largest_polygon_only(feature):
    """Return feature with only largest polygon (for MultiPolygon)."""

    geom = feature.get("geometry", {})

    if geom.get("type") != "MultiPolygon":
        return feature

    polys = geom.get("coordinates", [])

    if not polys:
        return feature

    largest = max(polys, key=lambda p: sum(len(ring) for ring in p))

    return {
        "type": "Feature",
        "properties": feature.get("properties", {}),
        "geometry": {
            "type": "Polygon",
            "coordinates": largest
        }
    }

# for Center box
# Center (bbox)
# -----------------------------
def feature_center(feature):
    pts = _extract_points(feature)
    if not pts:
        return None

    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]

    return (
        (min(lats) + max(lats)) / 2,
        (min(lons) + max(lons)) / 2
    )


# Bounding box (for fit)
# -----------------------------
def bbox_from_feature(feature):
    pts = _extract_points(feature)

    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]

    return min(lons), min(lats), max(lons), max(lats)

def fix_antimeridian(lon1, lon2):
    """Adjust longitudes so the line takes the shortest path."""
    if abs(lon2 - lon1) > 180:
        if lon2 > lon1:
            lon2 -= 360
        else:
            lon2 += 360
    return lon1, lon2
