
import sqlite3


conn = sqlite3.connect("opensooq.db")
cursor = conn.cursor()

cursor.execute("""

    CREATE TABLE IF NOT EXISTS listings(
  listing_id       TEXT PRIMARY KEY NOT NULL,
reference_number TEXT,
title            TEXT,
price            REAL,
currency         TEXT,
rent_period      TEXT,
city             TEXT,
neighborhood     TEXT,
area_m2          REAL,
bedrooms         INTEGER,
bathrooms        INTEGER,
furnished        TEXT,
floor            TEXT,
building_age     TEXT,
latitude         REAL,
longitude        REAL,
published_at     TEXT,
first_seen       TEXT,
last_seen        TEXT,
status            TEXT

    )


""")


def listing_exists(listing_id):
    cursor.execute("""
    SELECT listing_id
    FROM listings
    WHERE listing_id = ?
    """, (listing_id,))

    row = cursor.fetchone()

    return row is not None

print(listing_exists("284980474"))
print(listing_exists("999999999"))
conn.commit()

conn.close()
