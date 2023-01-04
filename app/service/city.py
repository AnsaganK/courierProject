from app.models import City, OFC


def add_city_for_ofc(ofc: OFC = None, many: bool = True):
    city_short_names = City.objects.exclude(short_name=None).values_list('short_name', flat=True)
    if many:
        ofcs = OFC.objects.filter(city=None)
        for city_short_name in city_short_names:
            for ofc in ofcs:
                if city_short_name in ofc.address or f'({city_short_name.lower()}' in ofc.address.lower():
                    ofc.city = City.objects.get(short_name=city_short_name)
                    ofc.save()
    else:
        for city_short_name in city_short_names:
            if city_short_name in ofc.address or f'({city_short_name.lower()}' in ofc.address.lower():
                ofc.city = City.objects.get(short_name=city_short_name)
                ofc.save()