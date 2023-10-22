from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

import threading
import traceback
import xlsxwriter

from modules.beerselection import run as beerselection_run
from modules.csakajosor import run as csak_a_run
from modules.onebeer import run as onebeer_run
from modules.drinkstation import run as drinkstation_run
from modules.beerside import run as beerside_run
from modules.beerbox import run as beerbox_run
from modules.common import *

def main():
    try:
        create_folder("log")

        args = get_args()

        set_lang_file(args.language)

        global top
        top = None

        if args.gui:
            top = Tk()
            top.geometry("230x265")
            top.resizable(False, False)
            top.title(get_name_with_version())
            top.protocol("WM_DELETE_WINDOW", gui_window_closed)
            configure_gui(args)
            top.mainloop()

        else:
            run(args)

    except KeyboardInterrupt:
        log_and_print(get_lang_text("EXIT"))
        os._exit(0)
    except Exception:
        log_and_print(traceback.format_exc())

def gui_window_closed():
    log_and_print(get_lang_text("EXIT"))
    top.quit()
    top.destroy()
    os._exit(0)

def run(args):
    beers = {}

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

    crawl_threads = []

    for shop in args.shops.split(","):
        crawl_thread = threading.Thread(target = run_crawl, args = (shop, beers))
        crawl_threads.append(crawl_thread)
        crawl_thread.start()

    if is_gui_active():
        gui_run(crawl_threads, beers)
    else:
        cli_run(crawl_threads, beers)

def cli_run(crawl_threads, beers):
    for crawl_thread in crawl_threads:
        crawl_thread.join(1)

    create_template(beers)

def gui_run(crawl_threads, beers):
    for crawl_thread in crawl_threads:
        monitor_crawl_thread(crawl_thread)

    monitor_crawl_progress(beers)

def create_template(beers):
    should_create_worksheet = False

    for value in beers.values():
        if len(value) > 0:
            should_create_worksheet = True
            break

    if should_create_worksheet:
        create_worksheet(beers)
    else:
        increase_progress()
        create_message_box(get_lang_text("NO_NEW_BEER"))
        log_and_print(get_lang_text("NO_NEW_BEER"))

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
    
    increase_progress()
    log_and_print(get_lang_text("REPORT_CREATED"))
    create_message_box(get_lang_text("REPORT_CREATED"))

def monitor_crawl_thread(crawl_thread):
    if crawl_thread.is_alive():
        top.after(100, lambda: monitor_crawl_thread(crawl_thread))
    else:
        increase_progress()

def monitor_crawl_progress(beers):
    if progress_bar['value'] < (100 - (STEP + 1)):
        top.after(100, lambda: monitor_crawl_progress(beers))
    else:
        create_template(beers)

def create_message_box(message):
    if not is_gui_active():
        return

    if progress_bar['value'] >= 100:
        messagebox.showinfo(title="Finished", message=message,)
        progress_bar['value'] = 0
        progress_bar.update()

    run_button['state'] = NORMAL

def increase_progress():
    if not is_gui_active():
        return
    
    if progress_bar['value'] < 100:
        progress_bar['value'] += STEP

    progress_bar.update()

def gui_set_args(args, rotate_entry, clean_var, shop_list):
    args.rotate = get_rotation_value(rotate_entry.get())

    if clean_var.get() == 0:
        args.clean = False
    else:
        args.clean = True

    list = []
    for shop in shop_list.curselection():
        list.append(shop_list.get(shop))

    args.shops = ",".join(list)

    global STEP
    STEP = round(100 / (len(list) + 1)) + 1

    run_button['state'] = DISABLED
    run(args)

def change_language(event):
    set_lang_file(get_lang_code(event.widget.get()))

    lang_combo.config(values=get_translated_list(get_languages()))

    lang_label.config(text=get_lang_text("LANG"))
    rotate_label.config(text=get_lang_text("ROTATE"))
    clean_label.config(text=get_lang_text("CLEAN"))
    shop_label.config(text=get_lang_text("SHOPS"))
    run_button.config(text=get_lang_text("RUN"))

def is_gui_active():
    return top is not None

def configure_gui(args):
    shops = get_shops(args.shops)

    lang_frame = Frame(top)
    lang_frame.place(x=10, y=10)

    global lang_label
    lang_label = Label(lang_frame, text=get_lang_text("LANG"))
    lang_label.pack(side = LEFT, fill = BOTH)

    global lang_combo
    lang_combo = ttk.Combobox(lang_frame, values=get_translated_list(get_languages()))
    lang_combo.set(get_lang_text(args.language))
    lang_combo.pack(side = RIGHT, fill = BOTH)
    lang_combo.bind("<<ComboboxSelected>>", change_language)

    rotate_frame = Frame(top)
    rotate_frame.place(x=10, y=40)

    global rotate_label
    rotate_label = Label(rotate_frame, text=get_lang_text("ROTATE"))
    rotate_label.pack(side = LEFT, fill = BOTH)

    rotate_entry = Entry(rotate_frame, bd=1)
    rotate_entry.insert(0, args.rotate)
    rotate_entry.pack(side = RIGHT, fill = BOTH)

    clean_frame = Frame(top)
    clean_frame.place(x=10, y=70)

    global clean_label
    clean_label = Label(clean_frame, text=get_lang_text("CLEAN"))
    clean_label.pack(side = LEFT, fill = BOTH)

    if args.clean:
        clean_var = IntVar(value=1)
    else:
        clean_var = IntVar(value=0)

    clean = Checkbutton(clean_frame, variable=clean_var)
    clean.pack(side = RIGHT, fill = BOTH)

    shop_frame = Frame(top)
    shop_frame.place(x=10, y=100)

    global shop_label
    shop_label = Label(shop_frame, text=get_lang_text("SHOPS"))
    shop_label.pack(side = LEFT, anchor=NW)

    shop_frame = Frame(shop_frame)
    shop_frame.pack(side = RIGHT)

    shop_list = Listbox(shop_frame, selectmode = "multiple", height=5) 
    shop_list.pack(side = LEFT, fill = BOTH)

    shop_scrollbar = Scrollbar(shop_frame)
    shop_scrollbar.pack(side = RIGHT, fill = BOTH)

    shop_list.config(yscrollcommand = shop_scrollbar.set) 
    shop_scrollbar.config(command = shop_list.yview) 

    for shop in range(len(shops)): 
        shop_list.insert(END, shops[shop]) 
        shop_list.select_set(shop)

    progress_frame = Frame(top)
    progress_frame.place(x=10, y=200)
    
    global progress_bar
    progress_bar = ttk.Progressbar(progress_frame, orient=HORIZONTAL, length=210, mode="determinate")
    progress_bar.pack(side = RIGHT, fill = BOTH)

    button_frame = Frame(top)
    button_frame.place(x=10, y=230)

    global run_button
    run_button = Button(button_frame, text=get_lang_text("RUN"), command=lambda: gui_set_args(args, rotate_entry, clean_var, shop_list), width=29)
    run_button.pack(side = LEFT, fill = BOTH)

main()