def get_map_scale_params(toponym):
    """Функция подбора параметров для масштаба карты по заданному объекту в отдельном файле."""
    bounding_box = toponym['boundedBy']['Envelope']

    lower_corner = bounding_box['lowerCorner'].split()
    upper_corner = bounding_box['upperCorner'].split()

    lon_span = abs(float(upper_corner[0]) - float(lower_corner[0]))
    lat_span = abs(float(upper_corner[1]) - float(lower_corner[1]))

    lon_span *= 1.2
    lat_span *= 1.2

    return (str(lon_span), str(lat_span))
