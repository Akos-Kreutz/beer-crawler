import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
import argparse

LANG = None
SCRIPT_FOLDER = os.path.dirname(os.path.abspath(sys.argv[0]))
DAY_TIMESTAMP = datetime.now().strftime("%d-%m-%Y")
VERSION="2.4"
ARGS = None
class NotAvailable:
    text = "N/A"

class Beer:
    name = None
    brewery = None 
    package = None
    style = None
    country = None
    price = None
    currency = None
    abv = None
    link = None

def rotate_files(number_of_files_to_keep, folder):
    files = sorted(Path(folder).iterdir(), key=os.path.getmtime, reverse=True)

    for i in range(number_of_files_to_keep, len(files)):
        file = files[i]
        log_and_print("{}: {}".format(get_lang_text("DELETE_FILE"), file))
        os.remove(file)

def log_and_print(message):
    log_file = open("{}/log/{}.log".format(SCRIPT_FOLDER, DAY_TIMESTAMP), "a")

    for line in message.splitlines():
        line_with_timestamp = "[{}] {}".format(datetime.now().strftime("%H:%M:%S"), line)
        log_file.write("{}\n".format(line_with_timestamp))
        print(line_with_timestamp)

    log_file.close()

def is_path_exists(name):
    return os.path.exists("{}/{}".format(SCRIPT_FOLDER, name))

def create_folder(name):
    if not is_path_exists(name):
        os.makedirs("{}/{}".format(SCRIPT_FOLDER, name))

def write_json(list, module):
    new_json = json.dumps(list, ensure_ascii=False, indent=2).encode('utf8')

    with open("{}/{}.json".format(SCRIPT_FOLDER, module), "w", encoding='utf8') as outfile:
        outfile.write(new_json.decode())

def read_json(module):
     file =  open("{}/{}.json".format(SCRIPT_FOLDER, module), "r", encoding='utf8')

     return json.load(file)

def is_json_exists(module):
    return os.path.exists("{}/{}.json".format(SCRIPT_FOLDER, module))

def get_new_entries(old_json, new_json):
    old_beers = []
    new_beers = []

    for i in range(len(old_json)):
        old_beers.append(old_json[i]["name"])
        old_beers.append(old_json[i]["link"])

    for i in range(len(new_json)):
        if new_json[i]["name"] not in old_beers and new_json[i]["link"] not in old_beers:
            new_beers.append(new_json[i])

    return new_beers

def get_element(root_object, element_name, attributes={}, **kwargs):
    if root_object is not None and root_object is not NotAvailable:
        return root_object.find(element_name, attributes, **kwargs)
    else:
        return NotAvailable
    
def get_elements(root_object, element_name, attributes={}, **kwargs):
    if root_object is not None and root_object is not NotAvailable:
        return root_object.findAll(element_name, attributes, **kwargs)
    else:
        return NotAvailable
    
def get_element_attribute(element, attribute):
    if element is None:
        return NotAvailable.text

    attr = getattr(element, attribute, NotAvailable.text)

    try:
        return attr.strip()
    except:
        return attr
    
def get_tag_attribute(tag, attribute):
    if tag is None or tag is NotAvailable or attribute not in tag.attrs.keys():
        return NotAvailable.text
        
    try:
        return tag[attribute].strip()
    except:
        return tag[attribute]

def get_formatted_name(name, brewery):
    name = name.split("|")[0]
    name = re.sub(r'[0-9]+,[0-9]+[l,L]{1}', '', name)
    name = re.sub(r'[0-9]+[m,M]{1}[l,L]{1}', '', name)
    name = re.sub(r'[0-9]*\,*\.*[0-9]+[%]{1}', '', name)
    name = re.sub(r'\,*\s+\(.+\)', '', name)

    if ("&" in name or brewery == NotAvailable.text or name.count(brewery) > 1):
        return name.strip()

    return name.replace(brewery, "").strip()

def set_lang_file(lang):
    if not is_json_exists("lang/{}".format(lang)):
        print("Language file not found, loading english language file.")
        global LANG
        LANG = read_json("lang/en")
        return
    
    LANG = read_json("lang/{}".format(lang))

def get_lang_text(text):
    if text in LANG.keys():
        return LANG.get(text)
    
    return LANG.get("NO_TEXT")

def get_lang_code(code):
    values = list(LANG.values())

    if code in values:
        keys = list(LANG.keys())
        return keys[values.index(code)]
    
    print("Language code not found, returning english language code.")
    return "en"

def get_shops(shop_string):
    shops = []

    for shop in shop_string.split(","):
        shops.append(shop)

    return shops

def get_name_with_version():
    return "Beer Crawler v{}".format(VERSION)

def get_translated_list(list):
    translated_list = []

    for element in list:
        translated_list.append(get_lang_text(element))

    return translated_list

def get_languages():
    files = sorted(Path("{}/lang".format(SCRIPT_FOLDER)).iterdir())
    langs = []

    for file in files:
        langs.append(Path(file).stem)

    return langs

def get_args():
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
    parser.add_argument(
                "--gui",
                "-g",
                action="store_true",
                help="Starts the application in the GUI mode.",
            )
    parser.add_argument(
                "--daily",
                "-d",
                action="store_true",
                help="Only let's the script run one time per day.",
            )
    parser.add_argument(
                "--beercount",
                "-b",
                nargs=1,
                type=int,
                default="20",
                help="The amount of beer to check in each shop. By default the script will check up to 20 beers.",
            )

    args = parser.parse_args()

    if args.version:
        log_and_print(get_name_with_version())
        exit()

    if type(args.beercount) is list:
        args.beercount = int(args.beercount[0])

    if type(args.rotate) is list:
        args.rotate = int(args.rotate[0])

    if type(args.language) is list:
        args.language = args.language[0]

    if type(args.shops) is list:
        args.shops = args.shops[0]

    return args

ARGS = get_args()