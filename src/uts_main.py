#kevin fink
#kevin@shorecode.org
#uts_main.py
#October 16 2023

#UW presentation

from dataclasses import dataclass
import time
import random
import yaml
import csv
import os
from typing import Generator
import requests
import webbrowser
import tkinter as tk
from tkinter import ttk
from valdec.decorators import validate
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import uts_logging

logger = uts_logging.set_logging('uts', 'uts_main.log')

@dataclass
class TalentScraper:
    url = str()
    query = str()
    page = 1
    final_result = []
    @validate
    def set_url(self, url: str):
        self.url = url
        self.original_url = url
    def get_url(self) -> str:
        return self.url
    @validate
    def set_query(self, query: str):
        logger.info(f'Setting query to {query}')
        self.query = query
        self.url = self.url + f'?q={query}'
        self.original_url = self.original_url + f'?q={query}'
    def get_query(self) -> str:
        return self.query
    def get_proxies(self) -> list:
        with open('uts_proxies.yaml', 'r') as fn:            
            return yaml.safe_load(fn)
    def get_page_content(self) -> webdriver.Firefox():
        if 'driver' not in vars(self):
            logger.info('Starting Selenium web driver in headless mode')
            proxies = self.get_proxies()
            random_proxy = random.choice(proxies)
            random_ua = UserAgent().random
            logger.info(f'Using proxy: {random_proxy}')
            logger.info(f'Using UA: {random_ua}')
            options = webdriver.FirefoxOptions()
            options.add_argument('--proxy-server=%s' % random_proxy)
            options.add_argument('--headless')
            options.add_argument(f'--user-agent={random_ua}')
            self.driver = webdriver.Firefox(options=options)
        try:
            logger.info(f'Scraping webpage: {self.url}')
            self.driver.get(self.url)
        except selenium.common.exceptions.WebDriverException:
            time.sleep(20)
            self.driver.get(self.url)
        return self.driver    
    def find_all_query(self) -> list:        
        tag_list = [".identity-name", "[data-qa-freelancer-ciphertext]",
                    'strong', '.up-job-success-text'
                    ]
        logger.info(f'Retrieving information from {self.url}. CSS selectors: {tag_list}')
        self.result = []
        self.hourly_list = []
        self.earnings_list = []
        for t in tag_list:
            selector_list = self.driver.find_elements(By.CSS_SELECTOR, t)
            if t == 'strong':
                for s in selector_list:
                    s_text = s.text
                    if '$' in s_text and '.' in s_text:
                        self.hourly_list.append(s)
                self.result.append(self.hourly_list)
            else:
                self.result.append(selector_list)
        if len(self.result) == 0:
            logger.info('Search returned no results, or there is another error')
            return self.result, False
        else:
            logger.info('Page parsing finished, succeeded to obtain results')
            self.object_list = list(zip(*self.result))
            self.result_list = self.extract_results(self.object_list)
            logger.info(self.result_list)
            return self.result_list, True

    def extract_results(self, results: list):
        clean_list = []
        for r in results:
            clean_list.append((r[0].text, r[1].get_attribute('data-qa-freelancer-ciphertext'), float(r[2].text[1:]), float(r[3].text[:3].replace('%', ''))))
        else:
            return clean_list
    def next_page(self) -> str:
        self.page += 1
        self.url = self.original_url + '&page=' + str(self.page)
        logger.info(f'Next webpage added to url: {self.url}')
        return self.url
    def add_page_result(self):
        self.final_result += self.result_list
    def get_final_result(self) -> list:
        return self.final_result
    @validate
    def scrape(self, query: str, sort_column: str) -> list:
        logger.info('Beginning main scrape logic')
        self.set_url('https://www.upwork.com/search/profiles/')
        self.set_query(query)
        while self.page < 35:
            logger.info(f'Loading page# {self.page}')
            self.get_page_content()
            results, loop_flag = self.find_all_query()            
            if loop_flag == True:
                self.add_page_result()
                self.next_page()
                time.sleep(0.7)
            else:
                return self.get_final_result(), True if len(self.get_final_result()) > 0 else self.result,False
        return self.get_final_result(), True if len(self.get_final_result()) > 0 else self.result,False

@dataclass
class TalentScraperGui:
    def search_box(self) -> list[ttk.Entry, ttk.Label]:
        self.entry = ttk.Entry(self.root, width=50)
        self.query_label = ttk.Label(self.root, text="Enter your search query:")
        return self.entry, self.query_label
    def on_radio_select(self):
        selected_value = self.radio_var.get()
        self.sort_column = selected_value
    def create_radio_buttons(self) -> list[ttk.Radiobutton, ttk.Label]:
        self.radio_var = tk.StringVar()
        radio_buttons = []
        options = [["Name", 1], ["Hourly Rate", 3], ["Success Score", 4], ["Don't sort", 5]]
        for option in options:
            radio_buttons.append(ttk.Radiobutton(self.root2, text=option[0],
                       variable=self.radio_var, value=option[1], command=self.on_radio_select))
        radio_label = ttk.Label(self.root, text="Choose Sorting:")
        return radio_buttons, radio_label
    def create_checkbox(self) -> ttk.Checkbutton:
        self.check_var = tk.IntVar()
        check_box = ttk.Checkbutton(self.root3, variable = self.check_var, text = 'Reverse')
        return check_box
    def create_main_window(self) -> ttk.Frame:
        logger.info('Creating main tkinter window')
        self.main_win = tk.Tk()
        logger.info('Setting ttk style')
        self.main_win.call('source', 'awthemes/awdark.tcl')
        self.style = ttk.Style(self.main_win)
        self.style.theme_use('awdark')
        self.root = ttk.Frame(self.main_win, padding='10')
        self.root2 = ttk.Frame(self.main_win, padding='10')
        self.root3 = ttk.Frame(self.main_win, padding='10')
        self.main_win.bind('<Return>', self.key_press)
        self.img = tk.PhotoImage(file='gfg.png')
        self.main_win.wm_iconphoto(True, self.img)
        self.main_win.wm_title('Upwork Talent Search And Sort Tool')
        self.root.pack(fill=tk.BOTH)
        self.root2.pack(fill=tk.BOTH)
        self.root3.pack(fill=tk.BOTH)
        return self.root
    def create_search_button(self) -> ttk.Button:
        self.button = ttk.Button(self.root, text="Search", command=self.result_window)
        return self.button
    def start_gui(self):
        self.create_main_window()
        search_box, search_box_label = self.search_box()
        search_button = self.create_search_button()
        radio_buttons, radio_label = self.create_radio_buttons()
        check_box = self.create_checkbox()
        logger.info('Adding all widgets to the main window')
        search_box_label.grid(row=1, column=1, pady=5)
        search_box.grid(row=2, column=1)
        search_button.grid(row=3, column=1, pady=5)
        radio_label.grid(row=4, column=1)
        # Unpacking radio buttons and setting the last one as default (no sorting) using .invoke()
        count = 0
        for r in radio_buttons:
            r.grid(row=1, column=count, padx=5)
            count += 1
            r.invoke()
        check_box.pack()
        self.main_win.mainloop()
    def result_window(self):
        logger.info('Initializing scraping class and creating results window')
        try:
            self.res_box.destroy()            
        except AttributeError:
            pass
        scraper = TalentScraper()
        self.query = self.entry.get()
        results = scraper.scrape(query=self.query, sort_column=self.sort_column)
        self.res_box = tk.Toplevel()
        self.res_box.wm_title(f'Upwork search results for {self.query}')
        # If statement to determine if the search yielded results. results[0] is a Boolean flag, True
        # indicates results were obtained. False indicates the opposite.
        if results[1] is True:
            self.create_buttons(results[0])
            logger.info('Sending results to CSV file')
            self.to_csv(results[0], self.query)
        else:
            self.error_display(results[0])
    @validate
    def create_buttons(self, results_list: list):
        try:
            self.res_win.destroy()            
        except AttributeError:
            pass        
        self.res_win = ttk.Frame(self.res_box, padding='10')
        self.res_win.pack()        
        page_count = 0
        buttons = dict()
        sorted_list = self.sort_list(results_list)
        # Splits the list into chunks of 30. Each column in the results window will contain 30 entries.
        split_list = list(self.divide_chunks(sorted_list, 10))
        self.button_dict = dict()
        # For loop to create a button for each profile obtained in the search.
        logger.info('Creating link buttons')
        for lst in split_list:
            count = 1
            for l in lst:
                # Unpacking the data from the search results list
                name, profile_id, *details = l
                # Dictionary to store the profile_id of each profile. Used to create the URL for the
                # website accessed when the user presses a button
                self.button_dict[name] = profile_id
                button_text = name + ', $' + str(details[0]) + ', ' + str(details[1]) + '% Job Success'
                buttons[count] = ttk.Button(self.res_win, text=button_text,
                        command=lambda x=name: self.launch_browser(x), width=63)
                buttons[count].grid(row=count, column=page_count)
                count += 1
            if page_count == 2:                
                show_more_button = ttk.Button(self.res_win, text='Show More',
                    command=lambda x=sorted_list: self.create_buttons(x[(count-1)*3:]), width=190)
                show_more_button.grid(row=count, column=0, columnspan=3)
                break
            page_count += 1

    @validate
    def divide_chunks(self, l, n) -> Generator[list, None, None]:
        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]
    @validate
    def prep_button_text(self, lst: list) -> list:
        # Retrieves data from the Selenium Web Objects
        return lst[0].text, lst[1].get_attribute('data-qa-freelancer-ciphertext'), lst[2].text, lst[3].text
    @validate
    def launch_browser(self, name: str):
        logger.info(f'Launching firefox to view {name}\'s profile. Profile ID: {self.button_dict[name]}')
        profile_url = f'https://www.upwork.com/freelancers/{self.button_dict[name]}'
        firefox = webbrowser.Mozilla('/bin/firefox')
        firefox.open(profile_url)
    @validate
    def error_display(self, error_msg):
        self.error_label = ttk.Label(self.res_win, text=f"Your search returned no results, perhaps there\
 was an error.")
        self.error_label.pack()
    @validate
    def key_press(self, enter):
        logger.info('Enter key pressed, initializing search')
        self.result_window()
    @validate
    def to_csv(self, results_list: list, query: str):
        # Create the data directory if it doesn't exist
        if os.path.isdir('data') == False:
            os.mkdir('data')
        csv_file = f'data/{query}_search_results.csv'
        # Writes the data to a csv file
        if os.path.isfile(csv_file):
            os.remove(csv_file)
        with open(csv_file, 'w', encoding='utf-8') as fn:
            writer = csv.writer(fn)
            headers = ['name', 'profile_id', 'hourly_rate', 'job_success']
            writer.writerow(headers)
            writer.writerows(results_list)
    def sort_list(self, result_list: list) -> list:
        if self.check_var.get() == 1:
            sorted_list = sorted(result_list, key=lambda x:(x[int(self.sort_column)-1]), reverse=True)
        else:
            sorted_list = sorted(result_list, key=lambda x:(x[int(self.sort_column)-1]))
        if self.sort_column != 5:
            return sorted_list
        else:
            return result_list

if __name__=='__main__':
    gui = TalentScraperGui()
    gui.start_gui()
