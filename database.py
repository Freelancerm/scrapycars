import sqlite3

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

test_data = {
    "Model": "BMW",
    "Name": "X5",
    "mileage": 120000,
    "registered": "2020",
    "engine": "3.0 Diesel",
    "range": "700",
    "exterior": "Black",
    "fuel": "Diesel",
    "transmission": "Automatic",
    "registration": "AA1234BB",
    "upholstery": "Leather"
}

con = sqlite3.connect('bmw_cars.db')
cur = con.cursor()
cur.execute(CREATE_TABLE)
con.commit()
cur.execute(LISTING_INSERT, test_data)
con.commit()
