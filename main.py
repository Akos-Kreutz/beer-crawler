from modules.beerselection import run as beerselection_run
from modules.csakajosor import run as csak_a_run
from modules.onebeer import run as onebeer_run
from modules.drinkstation import run as drinkstation_run
from modules.beerside import run as beerside_run
from modules.beerbox import run as beerbox_run
from modules.common import *
import xlsxwriter
from datetime import datetime
import argparse

def main():
    args = check_usage()

    beers = {}

    set_lang_file(args.language)

    for shop in args.shops.split(","):
        run_crawl(shop, beers)

    should_crete_worksheet = False

    for value in beers.values():
        if len(value) > 0:
            should_crete_worksheet = True
            break

    if should_crete_worksheet:
        create_worksheet(beers)
    else:
        print(get_lang_text("NO_NEW_BEER"))

def run_crawl(shop, beers):
    if not os.path.exists("{}/json".format(SCRIPT_FOLDER)):
        os.makedirs("{}/json".format(SCRIPT_FOLDER))

    match shop:
        case "beerselection":
            beers["Beerselection"] = beerselection_run()
        case "csakajosor":
            beers["Csak a jó sör"] = csak_a_run()
        case "onebeer":
            beers["One Beer"] = onebeer_run()
        case "drinkstation":
            beers["Drink Station"] = drinkstation_run()
        case "beerside":
            beers["Beerside"] = beerside_run()
        case "beerbox":
            beers["Beerbox"] = beerbox_run()

def create_worksheet(beers):
    print(get_lang_text("CREATE_REPORT"))

    if not os.path.exists("{}/report".format(SCRIPT_FOLDER)):
        os.makedirs("{}/report".format(SCRIPT_FOLDER))

    workbook = xlsxwriter.Workbook("{}/report/{}.xlsx".format(SCRIPT_FOLDER, datetime.now().strftime("%d-%m-%Y_%H-%M-%S")))
    worksheet = workbook.add_worksheet("Beer Crawler")

    worksheet.write('A1', get_lang_text("NAME"))
    worksheet.write('B1', get_lang_text("BREWERY"))
    worksheet.write('C1', get_lang_text("COUNTRY"))
    worksheet.write('D1', get_lang_text("STYLE"))
    worksheet.write('E1', get_lang_text("ABV"))
    worksheet.write('F1', get_lang_text("PACKAGE"))
    worksheet.write('G1', get_lang_text("PRICE"))
    worksheet.write('H1', get_lang_text("CURRENCY"))
    worksheet.write('I1', get_lang_text("SHOP"))
    worksheet.write('J1', get_lang_text("LINK"))

    counter = 2
    for key in beers.keys():
        for beer in beers[key]:
            worksheet.write('A' + str(counter), beer['name'])
            worksheet.write('B' + str(counter), beer['brewery'])
            worksheet.write('C' + str(counter), beer['country'])
            worksheet.write('D' + str(counter), beer['style'])
            worksheet.write('E' + str(counter), beer['abv'])
            worksheet.write('F' + str(counter), beer['package'])
            worksheet.write('G' + str(counter), beer['price'])
            worksheet.write('H' + str(counter), beer['currency'])
            worksheet.write('I' + str(counter), key)
            worksheet.write('J' + str(counter), beer['link'])
            counter += 1
            print(".", end='', flush=True)

    workbook.close()

def check_usage():
    parser = argparse.ArgumentParser(
                description="A Crawler in search of new craft beers.",
                add_help=True,
            )
    parser.add_argument(
                "--language",
                "-l",
                nargs=1,
                type=str,
                default="en",
                help="Sets the language of the crawler. Available values: en, hu",
            )
    parser.add_argument(
                "--shops",
                "-s",
                nargs=1,
                type=str,
                default="beerselection,csakajosor,onebeer,drinkstation,beerside,beerbox",
                help="Determines which shops are searched. The value needs to be comma separated, like: beerselection,csakajosor. Available values: beerselection,csakajosor,onebeer,drinkstation,beerside,beerbox.",
            )
    parser.add_argument(
                "--version",
                "-v",
                action="store_true",
                help="Prints the version of the script and exits.",
            )

    args = parser.parse_args()

    if args.version:
        print("BeerCrawler 1.0")
        exit()

    if type(args.language) is list:
        args.language = args.language[0]

    if type(args.shops) is list:
        args.shops = args.shops[0]

    return args

main()