import sqlite3

from src.handlers import (
    clean_mileage,
    normalize_fuel,
    validate_required_fields
)

CREATE_TABLE = """
         CREATE TABLE IF NOT EXISTS car_listings(
         Model TEXT NOT NULL,
         Name TEXT NOT NULL,
         mileage INTEGER NOT NULL,
         registered TEXT NOT NULL,
         engine TEXT,
         range TEXT,
         exterior TEXT NOT NULL,
         fuel TEXT,
         transmission TEXT,
         registration TEXT UNIQUE NOT NULL,
         upholstery TEXT
         );
        """

LISTING_INSERT = """
          INSERT INTO car_listings
            (Model, Name, mileage, registered, engine, range,
             exterior, fuel, transmission, registration, upholstery)
          VALUES
            (:Model, :Name, :mileage, :registered, :engine, :range,
            :exterior, :fuel, :transmission, :registration, :upholstery)
          ON CONFLICT (registration) DO NOTHING;
          """


class CleaningPipeline:

    @staticmethod
    def process_item(item, spider):
        validate_required_fields(item)

        item["mileage"] = clean_mileage(
            item.get("mileage")
        )

        item["fuel"] = normalize_fuel(
            item.get("fuel")
        )

        return item


class SQLitePipeline:

    def __init__(self):
        self.con = None
        self.cur = None

    def open_spider(self, spider):
        self.con = sqlite3.connect("bmw_cars.db")
        self.cur = self.con.cursor()
        self.cur.execute(CREATE_TABLE)
        self.con.commit()

    def close_spider(self, spider):
        self.con.close()

    def process_item(self, item, spider):
        self.cur.execute(
            LISTING_INSERT,
            dict(item)
        )

        self.con.commit()

        return item
