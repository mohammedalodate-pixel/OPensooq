import sqlite3


conn = sqlite3.connect("opensooq.db")
cursor = conn.cursor()


cursor.execute("""
    SELECT COUNT(*)
    FROM listings
""")

total_listings = cursor.fetchone()[0]


cursor.execute("""
    SELECT COUNT(DISTINCT city)
    FROM listings
    WHERE city IS NOT NULL
""")

total_cities = cursor.fetchone()[0]


cursor.execute("""
    SELECT COUNT(DISTINCT neighborhood)
    FROM listings
    WHERE neighborhood IS NOT NULL
""")

total_neighborhoods = cursor.fetchone()[0]


cursor.execute("""
    SELECT COUNT(*)
    FROM listings
    WHERE furnished IS NOT NULL
""")

furnished_info = cursor.fetchone()[0]


cursor.execute("""
    SELECT COUNT(*)
    FROM listings
    WHERE description IS NOT NULL
    AND description != ''
""")

descriptions = cursor.fetchone()[0]


cursor.execute("""
    SELECT MIN(price), MAX(price), AVG(price)
    FROM listings
    WHERE price IS NOT NULL
""")

min_price, max_price, avg_price = cursor.fetchone()


cursor.execute("""
    SELECT MIN(area_m2), MAX(area_m2), AVG(area_m2)
    FROM listings
    WHERE area_m2 IS NOT NULL
""")

min_area, max_area, avg_area = cursor.fetchone()


print("==============================")
print("DATABASE STATISTICS")
print("==============================")

print("Total listings:", total_listings)

print("Cities:", total_cities)

print("Neighborhoods:", total_neighborhoods)

print("Listings with furnished info:", furnished_info)

print("Listings with description:", descriptions)

print()

print("PRICE")
print("Minimum:", min_price)
print("Maximum:", max_price)
print("Average:", avg_price)

print()

print("AREA")
print("Minimum:", min_area)
print("Maximum:", max_area)
print("Average:", avg_area)


conn.close()


