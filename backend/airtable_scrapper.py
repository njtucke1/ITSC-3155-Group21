import time
import math
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date
import csv

def remove_duplicates_tuple(lst):
    return [t for t in (set(tuple(i) for i in lst))]


def wheel_element(element, deltaY = 120, offsetX = 0, offsetY = 0):
  error = element.parent.execute_script("""
    var element = arguments[0];
    var deltaY = arguments[1];
    var box = element.getBoundingClientRect();
    var clientX = box.left + (arguments[2] || box.width / 2);
    var clientY = box.top + (arguments[3] || box.height / 2);
    var target = element.ownerDocument.elementFromPoint(clientX, clientY);

    for (var e = target; e; e = e.parentElement) {
      if (e === element) {
        target.dispatchEvent(new MouseEvent('mouseover', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new MouseEvent('mousemove', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new WheelEvent('wheel',     {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY, deltaY: deltaY}));
        return;
      }
    }    
    return "Element is not interactable";
    """, element, deltaY, offsetX, offsetY)
  if error:
    raise WebDriverException(error)

url = "https://airtable.com/shrpj2r4Kjc4YoMu4/tbl8m95GiuWehnIiT?blocks=hide"

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--headless")   #don't show Chrome.
#chrome_options.add_argument("window-size=1920,1080") #standardize height and width.
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
driver.maximize_window()
height = driver.execute_script("return document.body.scrollHeight") #get height of maximized chrome window.
companies_unclean = []
for i in range(9999999999999999999999):     #We'll break from this loop once the bottom of the Airtable is reached.
    time.sleep(0.1)     #smallest amout time to wait. Any lower & the automated down scrolling will freeze up.
    page = driver.page_source   #get HTML at this 'scrolled to' location in the table.
    table_element = driver.find_element_by_css_selector('#table')
    wheel_element(table_element, math.floor(height/3))  #scrolls down the list each iteration by the amount of 1/3 your browser's height.
    soup = BeautifulSoup(page, 'html.parser')
    left_pane = soup.find_all('div', attrs = {'class':'dataRow leftPane'})  #column 1.
    right_pane = soup.find_all('div', attrs = {'class':'dataRow rightPane'}) #column 2-999999.

    if len(left_pane) == len(right_pane):   #if column 1 should be the same size as column 2-9999999.
        for column_1, column_2 in zip(left_pane, right_pane):
            company = dict.fromkeys(['name', 'status', 'description', 'date', 'time'])  #initialize empty dictionary. Will later be converted to tuple.
            name = column_1.find('div', attrs={'class': 'line-height-4 overflow-hidden truncate'})
            status = column_2.find_all('div', attrs={'class': 'flex-auto truncate'}) #can have multiple status stored in different divs.
            status_str = '' # will have become the string version of the list of status.
            first_flag = True
            if status is not None:
                for val in status:
                    if first_flag:              #don't add preceding comma if it's the first element
                        first_flag = False
                        status_str += val.text
                    else:
                        status_str += ',' + val.text
            date_val = column_2.find('div', attrs={'class': 'truncate col-6 pl1'})
            time_val = column_2.find('div', attrs={'class': 'timeDblClickEdit col-6 truncate pl1 pr1'})
            description = column_2.find('p', attrs={'class': 'truncate'})
            if name is None:    #if the cell is empty in Airtable it will return as NoneType so you have to check for it and put an empty string in it's place
                name = ''
                company['name'] = name
            else:
                company['name'] = name.text
            if status is None:
                status = ''
                company['status'] = status
            else:
                company['status'] = status_str
            if date_val is None:
                date_val = ''
                company['date'] = date_val
            else:
                company['date'] = date_val.text
            if time_val is None:
                time_val = ''
                company['time'] = time_val
            else:
                company['time'] = time_val.text
            if description is None:
                description = ''
                company['description'] = description
            else:
                company['description'] = description.getText()      #text was in a <span></span> tag so .text won't work here
            tuple_data = (company['name'], company['status'], company['description'], company['date'], company['time'])     #each row in the spreadsheet is stored as a tuple(makes it easier to remove duplicates and sort alphabetically)
            companies_unclean.append(tuple_data)

        val_1 = len(left_pane) * -1
        val_2 = (len(left_pane) * 2) * -1
        if companies_unclean[val_1:] == companies_unclean[val_2:val_1]:     #If scrapped data is the same as the last iteration you have reached the end of the Airtable so stop scrapping
            break
driver.quit()   #Close Chrome
companies_clean = remove_duplicates_tuple(companies_unclean)    #Will mess up the alphabetical ordering
companies_clean_sorted = sorted(companies_clean, key=lambda x: x[0].lower())    #Puts list back in order



cred = credentials.Certificate('./ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()
today = str(date.today().strftime('%m-%d-%y'))
batch = db.batch()

counter = 0
total_counter = 0
for company in companies_clean_sorted:
    firebase_upload = {}
    if (counter <  500) or (total_counter == len(companies_clean_sorted) - 1):
        firebase_upload['name'] = company[0]
        firebase_upload['status'] = company[1]
        firebase_upload['description'] = company[2]
        firebase_upload['date'] = company[3]
        firebase_upload['time'] = company[4]
        doc_ref = db.collection(today).document(str(total_counter))
        batch.set(doc_ref,firebase_upload)
        counter += 1
    else:
        batch.commit()
        counter = 0
    total_counter += 1
'''
try:
    doc = doc_ref.get()
    print('Document data: {}'.format(doc.to_dict()))
except:
    print('No such document!')
'''
'''with open('airtable_data.csv', 'w', newline='\n', encoding='utf-8') as out:     #Write list of tuples to csv
    csv_out=csv.writer(out)
    csv_out.writerow(['name','status','description', 'date', 'time'])
    for row in companies_clean_sorted:
        csv_out.writerow(row)'''