from bs4 import BeautifulSoup
from modules.common import *
import requests
import os

MODULE_NAME = os.path.basename(__file__).replace(".py", "")
MANDATORY_COOKIE_NAME = "adult_only_accepted"
MANDATORY_COOKIE_VALUE = None

def run():
    log_and_print(get_lang_text("BROWSE_BEERBOX"))
    global MANDATORY_COOKIE_VALUE
    MANDATORY_COOKIE_VALUE = get_mandatory_cookie_value()
    list = crawl("https://beerbox.hu/product-category/sorok-8?page=1")
    new_entries = list

    if is_json_exists("json/" + MODULE_NAME):
        old_json = read_json("json/" + MODULE_NAME)
        new_entries = get_new_entries(old_json, list)
        
    write_json(list, "json/" + MODULE_NAME)
    return new_entries

def crawl(url):
    req = requests.get(url, cookies={MANDATORY_COOKIE_NAME:MANDATORY_COOKIE_VALUE})
    soup = BeautifulSoup(req.text, "html.parser")
    list = []
    print(end='', flush=True)

    for element in soup.find_all("div", "single-product product-item text-center white-bg"):

        product_images = element.find("div", "product-images")

        if product_images is None:
            continue

        sub_element = product_images.find('a')

        if sub_element is None or 'href' not in sub_element.attrs:
            continue

        sub_soup = BeautifulSoup(requests.get(sub_element['href'], cookies={MANDATORY_COOKIE_NAME:MANDATORY_COOKIE_VALUE}).text, "html.parser")
        beer = Beer()

        beer.link = sub_element['href']
        style_and_abv = get_element_attribute(get_element(sub_soup, "div", "product-content"), "text")
        abv = re.search(r'[0-9]*\,*\.*[0-9]+[%]{1}', style_and_abv)
        if abv is None:
            beer.abv = NotAvailable.text
        else:
            beer.abv = abv.group(0)

        beer.style = style_and_abv.replace(beer.abv, "").strip()
        set_attributes(sub_soup, beer)
        beer.name = get_formatted_name(get_element_attribute(get_element(sub_soup, "h3", "breadcum-page-title text-center"), "text"), beer.brewery)
        beer.price = get_element_attribute(get_element(get_element(sub_soup, "ul", "d-sm-flex align-items-sm-center"), "span"), "text").replace("Ft", "").replace(" ", "")
        beer.currency = "HUF"

        list.append(beer.__dict__)
        print(".", end='', flush=True)

    print()
    return list

def get_mandatory_cookie_value():
    session = requests.session()
    session.get("https://beerbox.hu/accept-adult-only")
    return requests.utils.dict_from_cookiejar(session.cookies).get(MANDATORY_COOKIE_NAME)

def set_attributes(sub_soup, beer):
    table_striped = get_element(sub_soup, "table", "table table-striped")

    if table_striped is NotAvailable:
        beer.package = NotAvailable.text
        beer.brewery = NotAvailable.text
        beer.country = NotAvailable.text
        return

    elements = get_elements(table_striped, "td")

    if elements is NotAvailable:
        beer.package = NotAvailable.text
        beer.brewery = NotAvailable.text
        beer.country = NotAvailable.text
    else:
        beer.package = get_element_attribute(elements[0], "text")
        beer.brewery = get_element_attribute(elements[1], "text")
        beer.country = get_element_attribute(elements[2], "text")