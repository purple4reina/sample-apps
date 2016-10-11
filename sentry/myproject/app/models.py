from django.db import models

class Wiggle(models.Model):
    OSM_TYPE_CHOICES = (
        ('r', 'relation'),
        ('w', 'way'),
        ('n', 'node'),
    )

    osm_id = models.BigIntegerField(null=True)
    osm_type = models.CharField(max_length=1, choices=OSM_TYPE_CHOICES,
            null=True)
    name = models.CharField(max_length=150, db_index=True)
    location_type = models.IntegerField(default=123)

    @classmethod
    def search_by_point(cls, lng, lat):
        """
        Search for all areas enclosing the given long/lat point.
        :rtype: LocationArea queryset
        """
        wkt_point = create_point_str(lng, lat)
        return cls.objects.filter(polygon__contains=wkt_point)

    @classmethod
    #@cache(cache_key=get_point_cache_key, expires_in=CacheExpiryTime.ONE_YEAR)
    def get_airport_by_point(cls, lng, lat):
        """
        Get the airport enclosing the given point, or None if the point is not withing an airport.
        :rtype: LocationArea
        """
        return cls.search_by_point(lng, lat).filter(location_type=LocationType.AIRPORT).first()
