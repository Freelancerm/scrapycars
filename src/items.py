import scrapy


class CarItem(scrapy.Item):
    Model = scrapy.Field()
    Name = scrapy.Field()

    mileage = scrapy.Field()
    registered = scrapy.Field()

    engine = scrapy.Field()
    range = scrapy.Field()

    exterior = scrapy.Field()
    fuel = scrapy.Field()
    transmission = scrapy.Field()

    registration = scrapy.Field()
    upholstery = scrapy.Field()