import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import time


BASE_URL = "https://jo.opensooq.com/ar/real-estate-for-rent/apartments-for-rent"

DOMAIN = "https://jo.opensooq.com"

SAMPLE_SIZE = 1

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

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        return soup

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


        listings.append(
            {
                "listing_id": listing_id,
                "url": url,
                "title": title_tag.get_text(
                    strip=True
                )
            }
        )


    return listings


def get_listing_page(url):

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


        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        return soup


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


    description = section.find(
        "div",
        class_=lambda value:
            value and
            "overflow-hidden" in value
    )


    if not description:

        return None


    return description.get_text(
        "\n",
        strip=True
    )


def extract_price(soup):

    text = soup.get_text(
        " ",
        strip=True
    )


    match = re.search(
        r'(\d+(?:\.\d+)?)\s*(دينار|د\.ا)',
        text
    )


    if match:

        price = float(
            match.group(1)
        )

        currency = match.group(2)


        return price, currency


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

                latitude = float(
                    lat_match.group(1)
                )

                longitude = float(
                    lon_match.group(1)
                )


                return (
                    latitude,
                    longitude
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


    data = {

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


    return data


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


    search_soup = get_page(
        BASE_URL
    )


    if search_soup is None:

        print(
            "\nCould not load search page."
        )

        exit()


    listings = extract_listings(
        search_soup
    )


    print(
        "\nListings Found:",
        len(listings)
    )


    sample_listings = listings[
        :SAMPLE_SIZE
    ]


    print(
        "Sample Size:",
        len(sample_listings)
    )


    results = []


    for index, listing in enumerate(
        sample_listings,
        start=1
    ):

        print(
            "\n=============================="
        )

        print(
            f"Processing {index}/{len(sample_listings)}"
        )

        print(
            "Listing ID:",
            listing["listing_id"]
        )

        print(
            "Title:",
            listing["title"]
        )


        try:

            listing_soup = get_listing_page(
                listing["url"]
            )


            if listing_soup is None:

                print(
                    "Skipping this listing."
                )

                continue


            data = build_listing(
                listing,
                listing_soup
            )


            results.append(
                data
            )


            print(
                "Extraction successful."
            )


        except Exception as e:

            print(
                "Extraction error:",
                e
            )


        time.sleep(
            DELAY_BETWEEN_REQUESTS
        )


    print(
        "\n\n=============================="
    )

    print(
        "FINAL RESULTS"
    )

    print(
        "=============================="
    )


    print(
        "Successfully extracted:",
        len(results)
    )


    for index, item in enumerate(
        results,
        start=1
    ):

        print(
            f"\nLISTING {index}"
        )

        print(
            "------------------------------"
        )


        for key, value in item.items():

            print(
                f"{key}: {value}"
            )