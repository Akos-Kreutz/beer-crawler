from datetime import datetime

import threading
import traceback
import xlsxwriter

from modules.common import *
from modules.beerselection import run as beerselection_run
from modules.csakajosor import run as csak_a_run
from modules.onebeer import run as onebeer_run
from modules.drinkstation import run as drinkstation_run
from modules.beerbox import run as beerbox_run

# Loading up the language file is the most important step.
set_lang_file(ARGS.language)

# Creating folders
try:
    create_folder("log")
    create_folder("report")
    create_folder("json")
except Exception:
    log_and_print(traceback.format_exc())

# Docker does not support the GUI feature.
# If the import is not inside a try - except statement, then the script will fail to start due to not available packages.
try:
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
except:
    if(ARGS.gui):
        log_and_print(traceback.format_exc())
        os._exit(0)

def main():
    """Main function of the script."""
    try:
        global top
        top = None

        # Checking if the script should start in GUI or CLI mode.
        if ARGS.gui:
            top = Tk()
            top.geometry("230x295")
            top.resizable(False, False)
            top.title(get_name_with_version())
            top.protocol("WM_DELETE_WINDOW", gui_window_closed)
            configure_gui()
            top.mainloop()
        else:
            run()

    # Handling Keyboard Interrupts separately to avoid printing and logging a traceback.
    except KeyboardInterrupt:
        log_and_print(get_lang_text("EXIT"))
        os._exit(0)
    # Incase of any other exception the traceback will be printed and logged.
    except Exception:
        log_and_print(traceback.format_exc())

def gui_window_closed():
    """Ensurers that the script is exited properly when in GUI mode."""
    log_and_print(get_lang_text("EXIT"))
    top.quit()
    top.destroy()
    os._exit(0)

def run():
    """Handles argument related calls that can be configures by argument or in the GUI.
    Starts multiple crawl threads for the defined shops."""
    # In cleaning mode the script empties the log, report and json folder, then exists.
    if ARGS.clean:
        rotate_files(0, "{}/log".format(SCRIPT_FOLDER))
        rotate_files(0, "{}/report".format(SCRIPT_FOLDER))
        rotate_files(0, "{}/json".format(SCRIPT_FOLDER))
        exit()

    # If the rotate value is lower than 0 the script considers it disabled.
    # Otherwise it will rotate the give amount of files.
    if ARGS.rotate < 0:
        log_and_print(get_lang_text("DISABLE_ROTATE"))
    else:
        rotate_files(ARGS.rotate, "{}/log".format(SCRIPT_FOLDER))
        rotate_files(ARGS.rotate, "{}/report".format(SCRIPT_FOLDER))
        # Determining if the script already ran today by checking if the log file exists.
        if ARGS.daily and is_file_contains_string("log/{}.log".format(DAY_TIMESTAMP), "#"):
            log_and_print(get_lang_text("DAILY_EXIT"))
            os._exit(0)

    beers = {}
    crawl_threads = []

    # For each shop the script creates its own thread.
    for shop in ARGS.shops.split(","):
        crawl_thread = threading.Thread(target = run_crawl, args = (shop, beers))
        crawl_threads.append(crawl_thread)
        crawl_thread.start()

    if is_gui_active():
        gui_run(crawl_threads, beers)
    else:
        cli_run(crawl_threads, beers)

def cli_run(crawl_threads, beers):
    """[CLI method] waits until all the crawl threads are finished, then calls the create_template method.
    CLI mode can use the threading module to wait until every thread is finished."""
    for crawl_thread in crawl_threads:
        while crawl_thread.is_alive():
            # With join(1) the user can still use Keyboard Interrupts
            crawl_thread.join(1)

    print()
    create_template(beers)

def gui_run(crawl_threads, beers):
    """[GUI method] calls the monitor_crawl_thread method for each thread, then calls the monitor_crawl_progress method.
    GUI mode needs to use tkinter to wait up for every thread as the GUI needs to be constantly updated by the main thread."""
    for crawl_thread in crawl_threads:
        monitor_crawl_thread(crawl_thread)

    monitor_crawl_progress(beers)

def create_template(beers):
    """If there is new beer found calls the create_worksheet method, otherwise calls the increase_progress method and prints out the NO_NEW_BEER message."""
    should_create_worksheet = False

    # As beers are in a dictionary with the shop name as the key, the script checks the length of the the lists stored in the value.
    # If at least one of the list is not empty the worksheet will be generated.
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

    log_and_print("#")

def run_crawl(shop, beers):
    """Initiates the crawl for every shops set by the user.
    The returned beer list is added to a dictionary<String, List<Beer>>."""
    match shop:
        case "beerselection":
            beers["Beerselection"] = beerselection_run()
        case "csakajosor":
            beers["Csak a jó sör"] = csak_a_run()
        case "onebeer":
            beers["One Beer"] = onebeer_run()
        case "drinkstation":
            beers["Drink Station"] = drinkstation_run()
        case "beerbox":
            beers["Beerbox"] = beerbox_run()

def create_worksheet(beers):
    """Creates an xlsx file containing every new beer."""
    log_and_print(get_lang_text("CREATE_REPORT"))

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

    workbook.close()
    
    increase_progress()
    log_and_print(get_lang_text("REPORT_CREATED"))
    create_message_box(get_lang_text("REPORT_CREATED"))

def monitor_crawl_thread(crawl_thread):
    """[GUI method] used to monitor a single thread. If the thread is still active after 100 milliseconds calls itself, thus creating a loop.
    If the thread is finished updates the progress bar by calling the increase_progress method."""
    if crawl_thread.is_alive():
        top.after(100, lambda: monitor_crawl_thread(crawl_thread))
    else:
        increase_progress()

def monitor_crawl_progress(beers):
    """[GUI method] used to mintor the progress of the crawl process by checking the value of the progressbar.
    If the value is not high enough, after 100 milliseconds calls itself, thus creating a loop.
    If all threads are finished calls the create_template method."""
    if progress_bar['value'] < (100 - (STEP + 1)):
        top.after(100, lambda: monitor_crawl_progress(beers))
    else:
        create_template(beers)

def create_message_box(message):
    """[GUI method] creates a popup messagebox signaling the end of the crawl to the user."""
    if not is_gui_active():
        return

    if progress_bar['value'] >= 100:
        messagebox.showinfo(title="Finished", message=message,)
        progress_bar['value'] = 0
        progress_bar.update()

    run_button['state'] = NORMAL

def increase_progress():
    """[GUI method] if GUI is active increases the value of the progressbar by one step."""
    if not is_gui_active():
        return
    
    if progress_bar['value'] < 100:
        progress_bar['value'] += STEP

    progress_bar.update()

def gui_set_args(rotate_entry, clean_var, shop_list, beer_count_entry):
    """[GUI method] sets the values of the argument variables based on the GUI.
    Also sets the value for the STEP variable based on the number of shops.
    After the argument values set calls the run method."""
    ARGS.rotate = int(rotate_entry.get())
    ARGS.beercount = int(beer_count_entry.get())

    if clean_var.get() == 0:
        ARGS.clean = False
    else:
        ARGS.clean = True

    list = []
    for shop in shop_list.curselection():
        list.append(shop_list.get(shop))

    ARGS.shops = ",".join(list)

    # Global variable represents the value of one shop in the progressbar.
    global STEP
    STEP = round(100 / (len(list) + 1)) + 1

    # Disabling the run button to avoid multiple runs.
    run_button['state'] = DISABLED
    run()

def change_language(event):
    """[GUI method] when new language is selected in the language combobox, loads up the new lang file and changes the text on every UI element."""
    set_lang_file(get_lang_code(event.widget.get()))

    lang_combo.config(values=get_translated_list(get_languages()))

    lang_label.config(text=get_lang_text("LANG"))
    rotate_label.config(text=get_lang_text("ROTATE"))
    clean_label.config(text=get_lang_text("CLEAN"))
    shop_label.config(text=get_lang_text("SHOPS"))
    run_button.config(text=get_lang_text("RUN"))
    beer_count_label.config(text=get_lang_text("BEER_COUNT"))

def is_gui_active():
    """Returns if the script is running in UI mode or not."""
    return top is not None

def configure_gui():
    """[GUI method] creates all the GUI elements and sets their value based on the argument values."""

    # Language combobox
    lang_frame = Frame(top)
    lang_frame.place(x=10, y=10)

    global lang_label
    lang_label = Label(lang_frame, text=get_lang_text("LANG"))
    lang_label.pack(side = LEFT, fill = BOTH)

    global lang_combo
    lang_combo = ttk.Combobox(lang_frame, values=get_translated_list(get_languages()))
    lang_combo.set(get_lang_text(ARGS.language))
    lang_combo.pack(side = RIGHT, fill = BOTH)
    lang_combo.bind("<<ComboboxSelected>>", change_language)

    # Rotate entry
    rotate_frame = Frame(top)
    rotate_frame.place(x=10, y=40)

    global rotate_label
    rotate_label = Label(rotate_frame, text=get_lang_text("ROTATE"))
    rotate_label.pack(side = LEFT, fill = BOTH)

    rotate_entry = Entry(rotate_frame, bd=1)
    rotate_entry.insert(0, ARGS.rotate)
    rotate_entry.pack(side = RIGHT, fill = BOTH)

    # Beer Count entry
    beer_count_frame = Frame(top)
    beer_count_frame.place(x=10, y=70)

    global beer_count_label
    beer_count_label = Label(beer_count_frame, text=get_lang_text("BEER_COUNT"))
    beer_count_label.pack(side = LEFT, fill = BOTH)

    beer_count_entry = Entry(beer_count_frame, bd=1)
    beer_count_entry.insert(0, ARGS.beercount)
    beer_count_entry.pack(side = RIGHT, fill = BOTH)

    # Cleaning checkbutton
    clean_frame = Frame(top)
    clean_frame.place(x=10, y=100)

    global clean_label
    clean_label = Label(clean_frame, text=get_lang_text("CLEAN"))
    clean_label.pack(side = LEFT, fill = BOTH)

    if ARGS.clean:
        clean_var = IntVar(value=1)
    else:
        clean_var = IntVar(value=0)

    clean = Checkbutton(clean_frame, variable=clean_var)
    clean.pack(side = RIGHT, fill = BOTH)

    # Shops listbox
    shop_frame = Frame(top)
    shop_frame.place(x=10, y=130)

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

    shops = get_shops_as_list(ARGS.shops)

    for shop in range(len(shops)): 
        shop_list.insert(END, shops[shop]) 
        shop_list.select_set(shop)

    # Progressbar
    progress_frame = Frame(top)
    progress_frame.place(x=10, y=230)
    
    global progress_bar
    progress_bar = ttk.Progressbar(progress_frame, orient=HORIZONTAL, length=210, mode="determinate")
    progress_bar.pack(side = RIGHT, fill = BOTH)

    # Run button
    button_frame = Frame(top)
    button_frame.place(x=10, y=260)

    global run_button
    run_button = Button(button_frame, text=get_lang_text("RUN"), command=lambda: gui_set_args(rotate_entry, clean_var, shop_list, beer_count_entry), width=29)
    run_button.pack(side = LEFT, fill = BOTH)

main()