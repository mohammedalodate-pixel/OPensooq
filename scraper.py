import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time

from SQL_Code import (
    connect_db,
    listing_exists,
    save_listing
)


BASE_URL = "https://jo.opensooq.com/ar/real-estate-for-rent/apartments-for-rent"

PAGINATION_URL = "https://jo.opensooq.com/ar/عقارات/شقق-للايجار"

DOMAIN = "https://jo.opensooq.com"

NUMBER_OF_PAGES = 100

REQUEST_TIMEOUT = (10, 15)

DELAY_BETWEEN_REQUESTS = 1


headers = {
    "User-Agent": "Mozilla/5.0"
}


def get_page(url):

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        print(
            "Search Status:",
            response.status_code
        )

        response.raise_for_status()

        return BeautifulSoup(
            response.text,
            "html.parser"
        )

    except requests.exceptions.Timeout:

        print(
            "Search request timed out."
        )

        return None

    except requests.exceptions.RequestException as e:

        print(
            "Search request error:",
            e
        )

        return None


def extract_listings(soup):

    ads = soup.find_all(
        "a",
        class_="postListItemData"
    )

    listings = []

    seen_ids = set()


    for ad in ads:

        url = ad.get("href")

        title_tag = ad.find("h2")


        if not url or not title_tag:

            continue


        listing_id = url.rstrip(
            "/"
        ).split("/")[-1]


        if not listing_id:

            continue


        if listing_id in seen_ids:

            continue


        seen_ids.add(
            listing_id
        )


        listings.append({
            "listing_id": listing_id,
            "url": url,
            "title": title_tag.get_text(
                strip=True
            )
        })


    return listings


def get_listing_page(url):

    if url.startswith("http"):

        full_url = url

    else:

        full_url = DOMAIN + url


    try:

        response = requests.get(
            full_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        print(
            "Listing Status:",
            response.status_code
        )

        response.raise_for_status()

        return BeautifulSoup(
            response.text,
            "html.parser"
        )

    except requests.exceptions.Timeout:

        print(
            "Listing request timed out:",
            full_url
        )

        return None

    except requests.exceptions.RequestException as e:

        print(
            "Listing request error:",
            e
        )

        return None


def extract_basic_info(soup):

    data = {}


    section = soup.find(
        "section",
        id="listingViewBasicInfo"
    )


    if not section:

        return data


    items = section.find_all(
        "li"
    )


    for item in items:

        spans = item.find_all(
            "span"
        )

        links = item.find_all(
            "a"
        )


        if len(spans) >= 2:

            key = spans[0].get_text(
                strip=True
            )

            value = spans[1].get_text(
                strip=True
            )


            if key:

                data[key] = value


        elif (
            len(spans) > 0
            and
            len(links) > 0
        ):

            key = spans[0].get_text(
                strip=True
            )

            value = links[0].get_text(
                strip=True
            )


            if key:

                data[key] = value


    return data


def extract_description(soup):

    section = soup.find(
        "section",
        id="listingViewDescription"
    )


    if not section:

        return None


    return section.get_text(
        "\n",
        strip=True
    )


def extract_price(soup):

    price_element = soup.find(
        class_="redColor"
    )


    if price_element:

        text = price_element.get_text(
            " ",
            strip=True
        )


        match = re.search(
            r'(\d+(?:\.\d+)?)\s*(دينار|د\.ا)',
            text
        )


        if match:

            return (
                float(match.group(1)),
                match.group(2)
            )


    return None, None


def extract_coordinates(soup):

    scripts = soup.find_all(
        "script"
    )


    for script in scripts:

        text = script.get_text()


        if (
            "latitude" in text
            and
            "longitude" in text
        ):

            lat_match = re.search(
                r'"latitude":\s*(-?\d+(?:\.\d+)?)',
                text
            )


            lon_match = re.search(
                r'"longitude":\s*(-?\d+(?:\.\d+)?)',
                text
            )


            if lat_match and lon_match:

                return (
                    float(lat_match.group(1)),
                    float(lon_match.group(1))
                )


    return None, None


def clean_number(value):

    if not value:

        return None


    numbers = re.findall(
        r'\d+',
        value
    )


    if numbers:

        return int(
            numbers[0]
        )


    return None


def clean_area(value):

    if not value:

        return None


    numbers = re.findall(
        r'\d+(?:\.\d+)?',
        value
    )


    if numbers:

        return float(
            numbers[0]
        )


    return None


def build_listing(
    listing,
    soup
):

    info = extract_basic_info(
        soup
    )


    description = extract_description(
        soup
    )


    price, currency = extract_price(
        soup
    )


    latitude, longitude = extract_coordinates(
        soup
    )


    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    return {

        "listing_id":
            listing["listing_id"],

        "reference_number":
            info.get(
                "الرقم المرجعي"
            ),

        "title":
            listing["title"],

        "description":
            description,

        "price":
            price,

        "currency":
            currency,

        "rent_period":
            info.get(
                "مدة الإيجار"
            ),

        "city":
            info.get(
                "المدينة"
            ),

        "neighborhood":
            info.get(
                "الحي"
            ),

        "area_m2":
            clean_area(
                info.get(
                    "المساحة"
                )
            ),

        "bedrooms":
            clean_number(
                info.get(
                    "عدد الغرف"
                )
            ),

        "bathrooms":
            clean_number(
                info.get(
                    "عدد الحمامات"
                )
            ),

        "furnished":
            info.get(
                "مفروشة؟"
            ),

        "floor":
            info.get(
                "الطابق"
            ),

        "building_age":
            info.get(
                "عمر البناء"
            ),

        "latitude":
            latitude,

        "longitude":
            longitude,

        "published_at":
            info.get(
                "تاريخ النشر"
            ),

        "first_seen":
            now,

        "last_seen":
            now,

        "status":
            "active"
    }


if __name__ == "__main__":

    print(
        "=============================="
    )

    print(
        "OpenSooq Scraper"
    )

    print(
        "=============================="
    )


    conn = connect_db()

    cursor = conn.cursor()


    all_listings = []

    seen_ids = set()


    for page_number in range(
        1,
        NUMBER_OF_PAGES + 1
    ):

        if page_number == 1:

            page_url = BASE_URL

        else:

            page_url = (
                PAGINATION_URL
                + "?page="
                + str(page_number)
            )


        print(
            "\n=============================="
        )

        print(
            "SEARCH PAGE:",
            page_number
        )

        print(
            "URL:",
            page_url
        )


        search_soup = get_page(
            page_url
        )


        if search_soup is None:

            continue


        page_listings = extract_listings(
            search_soup
        )


        print(
            "Listings on this page:",
            len(page_listings)
        )


        new_ids = 0


        for listing in page_listings:

            listing_id = listing[
                "listing_id"
            ]


            if listing_id in seen_ids:

                continue


            seen_ids.add(
                listing_id
            )


            if listing_exists(
                cursor,
                listing_id
            ):

                print(
                    "Already in database:",
                    listing_id
                )

                continue


            all_listings.append(
                listing
            )

            new_ids += 1


        print(
            "New listings to process:",
            new_ids
        )


        time.sleep(
            DELAY_BETWEEN_REQUESTS
        )


    print(
        "\n=============================="
    )

    print(
        "NEW LISTINGS TO PROCESS:",
        len(all_listings)
    )

    print(
        "=============================="
    )


    inserted = 0

    failed = 0


    for index, listing in enumerate(
        all_listings,
        start=1
    ):

        print(
            "\n=============================="
        )

        print(
            f"Processing {index}/{len(all_listings)}"
        )

        print(
            "Listing ID:",
            listing["listing_id"]
        )


        try:

            listing_soup = get_listing_page(
                listing["url"]
            )


            if listing_soup is None:

                failed += 1

                continue


            data = build_listing(
                listing,
                listing_soup
            )


            action = save_listing(
                cursor,
                data
            )


            if action == "INSERTED":

                inserted += 1


            print(
                "Database:",
                action
            )


        except Exception as e:

            failed += 1

            print(
                "Extraction error:",
                e
            )


        time.sleep(
            DELAY_BETWEEN_REQUESTS
        )


    conn.commit()

    conn.close()


    print(
        "\n=============================="
    )

    print(
        "SCRAPING FINISHED"
    )

    print(
        "=============================="
    )

    print(
        "New listings inserted:",
        inserted
    )

    print(
        "Failed:",
        failed
    )