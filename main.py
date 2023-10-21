from modules.beerselection import run as beerselection_run
from modules.csakajosor import run as csak_a_run
from modules.onebeer import run as onebeer_run
from modules.drinkstation import run as drinkstation_run
from modules.beerside import run as beerside_run
from modules.beerbox import run as beerbox_run
from modules.common import *
import traceback
import xlsxwriter
from datetime import datetime
import argparse

def main():
    try:
        create_folder("log")

        args = check_usage()

        beers = {}

        set_lang_file(args.language)

        if args.clean:
            rotate_files(0, "{}/log".format(SCRIPT_FOLDER))
            rotate_files(0, "{}/report".format(SCRIPT_FOLDER))
            rotate_files(0, "{}/json".format(SCRIPT_FOLDER))
            exit()

        if args.rotate < 0:
            log_and_print(get_lang_text("DISABLE_ROTATE"))
        else:
            rotate_files(args.rotate, "{}/log".format(SCRIPT_FOLDER))
            rotate_files(args.rotate, "{}/report".format(SCRIPT_FOLDER))

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
            log_and_print(get_lang_text("NO_NEW_BEER"))
    except KeyboardInterrupt:
        log_and_print(get_lang_text("EXIT"))
    except Exception:
        log_and_print(traceback.format_exc())

def run_crawl(shop, beers):
    create_folder("json")

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
    log_and_print(get_lang_text("CREATE_REPORT"))

    create_folder("report")

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
    parser.add_argument(
                "--rotate",
                "-r",
                nargs=1,
                type=int,
                default="5",
                help="The script will keep the set number of newest files in the log & report folder and delete the others. To disable this feature set the value lower than zero. By default the script will keep 5 of the newest files.",
            )
    parser.add_argument(
                "--clean",
                "-c",
                action="store_true",
                help="Deletes all files from the log, report and json folders then exits.",
            )

    args = parser.parse_args()

    if args.version:
        log_and_print("BeerCrawler 1.0")
        exit()

    if type(args.rotate) is list:
        args.rotate = args.rotate[0]

    if type(args.language) is list:
        args.language = args.language[0]

    if type(args.shops) is list:
        args.shops = args.shops[0]

    return args

main()