import scrapy
import re
import json
from src.items import CarItem


class BmwApiSpider(scrapy.Spider):
    """Scrapy spider for BMW UK used-car listings via page HTML + internal JSON API.

    Flow:
    1. Visit search result pages to obtain CSRF token.
    2. Call listing API for each page using CSRF header.
    3. Visit each vehicle detail page.
    4. Extract embedded `UVL.AD` JSON object and yield normalized car fields.
    """

    name = "bmw_api"

    # Using start_urls since start_requests was behaving unexpectedly in this environment
    start_urls = [
        f"https://usedcars.bmw.co.uk/result/?page={page}&size=23"
        for page in range(1, 6)
    ]

    def parse(self, response):
        """Parse listing HTML page, extract CSRF token, then request list API.

        Token extraction strategy:
        - `<meta name="csrf-token" ...>`
        - `csrfToken` value embedded in page scripts
        - `csrftoken` cookie from `Set-Cookie` headers

        Args:
            response: Scrapy HTML response for a listing result page.

        Yields:
            scrapy.Request: API request to `/vehicle/api/list/` for same page number.
        """
        # Extract page number from URL
        page_match = re.search(r"page=(\d+)", response.url)
        page = page_match.group(1) if page_match else "1"

        self.logger.info(f"HTML loaded for page {page}. Extracting CSRF...")

        csrf_token = response.xpath('//meta[@name="csrf-token"]/@content').get()
        if not csrf_token:
            match = re.search(r'csrfToken":\s*"([^"]+)"', response.text)
            if match:
                csrf_token = match.group(1)

        if not csrf_token:
            cookies = response.headers.getlist("Set-Cookie")
            for cookie in cookies:
                cookie_str = cookie.decode("utf-8")
                if "csrftoken" in cookie_str:
                    csrf_token = cookie_str.split("csrftoken=")[1].split(";")[0]
                    break

        if not csrf_token:
            self.logger.error("CSRF token NOT found!")
            csrf_token = ""

        api_url = f"https://usedcars.bmw.co.uk/vehicle/api/list/?page={page}&size=23"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": response.url,
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrf_token,
        }

        yield scrapy.Request(
            url=api_url,
            headers=headers,
            callback=self.parse_api,
            meta={"csrf_token": csrf_token, "page": page},
            dont_filter=True,
        )

    def parse_api(self, response):
        """Parse vehicle-list API response and enqueue detail-page requests.

        Expects JSON payload with `results` list. Each result should contain
        `advert_id`, used to build vehicle detail URL.

        Args:
            response: Scrapy JSON response from `/vehicle/api/list/`.

        Yields:
            scrapy.Request: Vehicle detail-page request for each valid advert.
        """
        page = response.meta.get("page")

        if response.status == 200:
            data = response.json()
            cars = data.get("results", [])
            self.logger.info(
                f"Found {len(cars)} cars on page {page}. Requesting HTML pages..."
            )

            for car in cars:
                advert_id = car.get("advert_id")
                if not advert_id:
                    continue

                vehicle_url = f"https://usedcars.bmw.co.uk/vehicle/{advert_id}"

                yield scrapy.Request(
                    url=vehicle_url,
                    callback=self.parse_vehicle_page,
                    meta={"advert_id": advert_id},
                    dont_filter=True,
                )
        else:
            self.logger.error(f"List API Error {response.status} on page {page}")

    def parse_vehicle_page(self, response):
        """Parse vehicle detail HTML, extract embedded `UVL.AD` JSON, yield item.

        Uses regex to capture JS assignment of `UVL.AD` and handles multiline
        JSON with semicolons inside string values via fallback pattern.

        Extracted fields include model, derivative, mileage, registration data,
        engine size, range, exterior, fuel type, transmission, and upholstery
        (with fallback to interior feature list when missing).

        Args:
            response: Scrapy HTML response for a vehicle detail page.

        Yields:
            dict: Normalized vehicle record for downstream pipeline/export.
        """
        advert_id = response.meta.get("advert_id")

        # Improved Regex: match everything between UVL.AD = and the next UVL. assignment or script end
        # This handles semicolons inside car descriptions
        json_match = re.search(
            r"UVL\.AD\s*=\s*(\{.*?)\s*;\s*\n\s*(?:UVL\.|</script>)",
            response.text,
            re.DOTALL,
        )

        if not json_match:
            # Fallback regex if the structure is slightly different
            json_match = re.search(
                r"UVL\.AD\s*=\s*(\{.*?)\s*;\s*$",
                response.text,
                re.MULTILINE | re.DOTALL,
            )

        if json_match:
            try:
                json_str = json_match.group(1).strip()
                car = json.loads(json_str)

                # Extract registration data
                reg_iso = car.get("dates", {}).get("registration_iso")
                reg_number = car.get("identification", {}).get("registration")

                # Extract upholstery from specification
                spec = car.get("specification", {})
                upholstery = spec.get("interior")

                # Fallback: if specification.interior is empty, check features.interior.standard
                if not upholstery or upholstery == "N/A":
                    features = car.get("features", {})
                    interior_features = features.get("interior", {}).get("standard", [])
                    if isinstance(interior_features, list) and interior_features:
                        upholstery = ", ".join(interior_features)

                # Extract engine info
                engine_data = car.get("engine", {})
                engine_str = f"{engine_data.get('size', {}).get('litres')}"

                # Extract exterior (standard feature)
                features = car.get("features", {})
                exterior_list = features.get("exterior", {}).get("standard")
                exterior = exterior_list[0]

                item = CarItem()
                item["Model"] = str(car.get("title"))
                item["Name"] = str(spec.get("derivative"))
                item["mileage"] = car.get("condition_and_state", {}).get("mileage", 0)
                item["registered"] = str(reg_iso)
                item["engine"] = engine_str
                item["range"] = str(
                    car.get("consumption", {})
                    .get("range", {})
                    .get("values", {})
                    .get("total")
                )
                item["exterior"] = str(exterior)
                item["fuel"] = str(spec.get("raw_fuel_type"))
                item["transmission"] = str(spec.get("transmission"))
                item["registration"] = reg_number
                item["upholstery"] = upholstery
                yield item

            except Exception as e:
                self.logger.error(f"Failed to parse JSON for {advert_id}: {str(e)}")
        else:
            self.logger.error(f"Could not find UVL.AD data in HTML for {advert_id}")
