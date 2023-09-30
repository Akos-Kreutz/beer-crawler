import json
import os
import re

LANG = None

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

def write_json(list, module):
    new_json = json.dumps(list, ensure_ascii=False, indent=2).encode('utf8')

    with open("json/{}.json".format(module), "w", encoding='utf8') as outfile:
        outfile.write(new_json.decode())

def read_json(module):
     file =  open("{}.json".format(module), "r", encoding='utf8')

     return json.load(file)

def is_json_exists(module):
    return os.path.exists("{}.json".format(module))

def get_new_entries(old_json, new_json):
    old_names = []
    new_beers = []

    for i in range(len(old_json)):
        old_names.append(old_json[i]["name"])

    for i in range(len(new_json)):
        if new_json[i]["name"] not in old_names:
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
    if tag is None or attribute not in tag.attrs.keys():
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