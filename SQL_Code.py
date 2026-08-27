import sqlite3


DATABASE_NAME = "opensooq.db"


def connect_db():

    return sqlite3.connect(
        DATABASE_NAME
    )


def listing_exists(
    cursor,
    listing_id
):

    cursor.execute("""
        SELECT listing_id
        FROM listings
        WHERE listing_id = ?
    """, (listing_id,))

    row = cursor.fetchone()

    return row is not None


def insert_listing(
    cursor,
    data
):

    cursor.execute("""
        INSERT INTO listings (
            listing_id,
            reference_number,
            title,
            description,
            price,
            currency,
            rent_period,
            city,
            neighborhood,
            area_m2,
            bedrooms,
            bathrooms,
            furnished,
            floor,
            building_age,
            latitude,
            longitude,
            published_at,
            first_seen,
            last_seen,
            status
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        data["listing_id"],
        data["reference_number"],
        data["title"],
        data["description"],
        data["price"],
        data["currency"],
        data["rent_period"],
        data["city"],
        data["neighborhood"],
        data["area_m2"],
        data["bedrooms"],
        data["bathrooms"],
        data["furnished"],
        data["floor"],
        data["building_age"],
        data["latitude"],
        data["longitude"],
        data["published_at"],
        data["first_seen"],
        data["last_seen"],
        data["status"]
    ))


def update_last_seen(
    cursor,
    listing_id,
    last_seen,
    status
):

    cursor.execute("""
        UPDATE listings
        SET last_seen = ?,
            status = ?
        WHERE listing_id = ?
    """, (
        last_seen,
        status,
        listing_id
    ))


def save_listing(
    cursor,
    data
):

    if listing_exists(
        cursor,
        data["listing_id"]
    ):

        update_last_seen(
            cursor,
            data["listing_id"],
            data["last_seen"],
            data["status"]
        )

        return "UPDATED"

    else:

        insert_listing(
            cursor,
            data
        )

        return "INSERTED"