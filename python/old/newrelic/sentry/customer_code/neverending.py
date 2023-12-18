@python_2_unicode_compatible
class LocationArea(models.Model):
    """
    Model that represents an area on map.
    """

    OSM_TYPE_CHOICES = (
        ('r', 'relation'),
        ('w', 'way'),
        ('n', 'node'),
    )

    osm_id = models.BigIntegerField(null=True, help_text=_("OpenStreetMaps ID"))
    osm_type = models.CharField(max_length=1, choices=OSM_TYPE_CHOICES, null=True, help_text=_("OpenStreetMaps type"))
    name = models.CharField(max_length=150, db_index=True, help_text=_("LocationArea name"))
    polygon = models.PolygonField(help_text=_("Use GeoJSON to create"))
    location_type = models.IntegerField(default=LocationType.UNKNOWN, help_text=_("Type of location"))

    @classmethod
    def search_by_point(cls, lng, lat):
        """
        Search for all areas enclosing the given long/lat point.
        :rtype: LocationArea queryset
        """
        wkt_point = create_point_str(lng, lat)
        return cls.objects.filter(polygon__contains=wkt_point)

    @classmethod
    @cache(cache_key=get_point_cache_key, expires_in=CacheExpiryTime.ONE_YEAR)
    def get_airport_by_point(cls, lng, lat):
        """
        Get the airport enclosing the given point, or None if the point is not withing an airport.
        :rtype: LocationArea
        """
        return cls.search_by_point(lng, lat).filter(location_type=LocationType.AIRPORT).first()

    # this is from the view and is not part of the model...
    @list_route(methods=['get'])
    def airport_checking(self, request, format=None):
        """
        Return airport location enclosing the given point (lng,lat in query params).
        """
        #get the latitude and longitude parameters and check their values are sane
        serializer = PointSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        lat = serializer.validated_data['lat']
        lng = serializer.validated_data['lng']
        # call the class method to get the first airport which area contains the coordinates
        airport = LocationArea.get_airport_by_point(lng, lat)

        if airport:
            return Response(AirportSerializer(airport).data)

        return Response({})
