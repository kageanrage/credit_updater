import os, time, pprint, logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from config import Config   # this imports the config file where the private data sits
import pandas as pd
import se_general, se_admin, se_zoho

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')  # turns on logging
# logging.disable(logging.CRITICAL)     # switches off logging when desired

logging.debug('Imported modules')
logging.debug('Start of program')
logging.debug(f'Current cwd = {os.getcwd()}')

cfg = Config()  # create an instance of the Config class, essentially brings private config data into play
os.chdir(cfg.cwd)  # change the current working directory to the one stipulated in config file


# outdated as of 17-12-20
def login(driv):
    driv.get(cfg.assign_URL)  # use selenium webdriver to open web browser and desired URL from config file
    email_elem = driv.find_element_by_id('UserName')  # find the 'Username' text box on web page using its element ID
    email_elem.send_keys(cfg.uname)  # enter username from config file
    pass_elem = driv.find_element_by_id('Password')  # find the 'Password' text box using its element ID
    pass_elem.send_keys(cfg.pwd)  # enter password from config file
    pass_elem.submit()
    time.sleep(2)   # wait 2 seconds for the login process to take place (unsure if this is necessary)


def enter_data(driv, guid, reas, quan):
    try:  # structured as try / except statement in case something's gone wrong with reading in the excel file
        guid_elem = driv.find_element_by_id('MemberId')  # find the 'Member Id' text box on web page using its element ID
        guid_elem.clear()  # delete any text present in that field
        guid_elem.send_keys(guid)  # enter guid string
        reas_elem = driv.find_element_by_id('Reason')  # find the 'Reason' text box on web page using its element ID
        reas_elem.clear()  # delete any text present in that field
        reas_elem.send_keys(reas)  # enter Reason string
        quan_elem = driv.find_element_by_id('Quantity')  # find the 'Quantity' text box on web page using its element ID
        quan_elem.clear()  # delete any text present in that field
        quan_elem.send_keys(quan)  # enter Quantity string
        quan_elem.send_keys(Keys.ENTER)  # Press Enter key
    except:
        print(f"(in enter data function) - issue arose. GUID = {guid}")


def check_for_error(driv, memberid):  # checks the screen for the word 'error' and adds guid to appropriate list
    logging.debug("Running 'check_for_error'")
    try:
        err = driv.find_element_by_xpath("//*[contains(text(),'errors')]")  # check on screen for the word 'error'
        print(f"check_for_error: error detected with {memberid}")
        errors_list.append(memberid)  # if 'error' was found on screen, add the guid from the current loop to the errors list
    except:
        print(f'check_for_error: No error detected on page with {memberid}')
        success_list.append(memberid)  # if 'error' was not found on screen, add the guid from the current loop to the success list


driver = se_general.init_selenium()
driver.implicitly_wait(30)
se_admin.login_sa_2fa(driver, cfg.assign_URL)  # now using fn from module

excel_file = cfg.excel_file  # xlsx filename pulled from config file
df = pd.read_excel(excel_file, index_col=0, engine="openpyxl")  # read excel file into pandas DataFrame

errors_list = []  # create empty list of guids which had errors, to be populated later
success_list = []  # create empty list of guids which reported no errors, to be populated later

for row in df.itertuples():  # iterate through each row in the DataFrame
    guid = row.Index  # assign whatever is in the 'Index' column, to the variable 'guid'
    reason = row.Reason  # assign whatever is in the 'Reason' column, to the variable 'Reason'
    num_of_credits = row.Credits  # assign whatever is in the 'Credits' column, to the variable 'num_of_credits'
    driver.get(cfg.assign_URL)  # load desired URL
    logging.debug(f"Start of loop - guid = {guid}, reason = {reason}, credits = {num_of_credits}")  # logging
    enter_data(driver, guid, reason, num_of_credits)
    time.sleep(2)  # possibly not necessary, but don't want the next bit to happen if browser not ready
    check_for_error(driver, guid)
    time.sleep(2)  # possibly not necessary, but don't want to restart loop if browser not ready

print('Errors detected with the following member IDs:')
pprint.pprint(errors_list)
print('Success with the following member IDs:')
pprint.pprint(success_list)
