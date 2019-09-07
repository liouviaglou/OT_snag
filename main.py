# /usr/local/bin/python3

from bs4 import BeautifulSoup
from urllib.request import urlopen
import smtplib
import sys
import os
import configparser
from datetime import *
import urllib.parse as urlparse
from urllib.parse import urlencode

from selenium import webdriver  

from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait

from webdriver_manager.chrome import ChromeDriverManager

import collections

# python3 main.py config.txt

BASE_URL = "http://www.opentable.com/"
# GMAIL_ACCOUNT = "" #gmail account of the sender
# GMAIL_PASSWORD = "" #password of the sender

chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.binary_location = '/Applications/Google Chrome   Canary.app/Contents/MacOS/Google Chrome Canary'  
# driver = webdriver.Chrome()#, chrome_options=chrome_options)

# driver = webdriver.Chrome(ChromeDriverManager().install())

def get_status(ConvertedURL):
	html = urlopen(ConvertedURL).read()
	soup = BeautifulSoup(html, "html.parser")
	avail=soup.select('div[data-auto="timeslot"]')
	availTimes = []
	if avail == None:
		return []
	for x in avail:
		aTime = x.find("span").text
		PaTime = datetime.strptime(aTime, '%I:%M %p')
		if ((ParsedTime-PaTime).total_seconds()<float(Window)*60):
		   availTimes.append(aTime)
	return availTimes

def snag_rez(availTimes): 
	driver.get(ConvertedURL)  
	aTime = availTimes[0] # for aTime in availTimes:
	print (aTime)
	wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='{}']".format(aTime)))).click()
	sign_up()
	paramS_list = ['rid', 'confnumber', 'token']
	urlparam_dict = capture_urlparam(paramS_list)
	cancel(urlparam_dict)

def sign_up():
	driver.find_element_by_id("firstName").send_keys(config['signup']['firstName'])
	driver.find_element_by_id("lastName").send_keys(config['signup']['lastName'])
	driver.find_element_by_name("phoneNumber").send_keys(config['signup']['phoneNumber'])
	driver.find_element_by_name("email").send_keys(config['signup']['email'])
	driver.find_element_by_css_selector('#btn-complete').click()


def sign_in():
	driver.find_element_by_partial_link_text('Sign in').click()
	driver.find_element_by_css_selector('#Email').send_keys(config['signin']['email'])
	driver.find_element_by_css_selector('#Password').send_keys(config['signin']['password'])
	driver.find_element_by_css_selector('#signInButton').click()

def capture_urlparam(paramS_list):
	wait(driver, 5).until(
		lambda driver: all(x in driver.current_url for x in paramS_list))
	urlString = driver.current_url
	urlParams = urlparse.urlparse(urlString).query
	urlPrDict = {k: urlparse.parse_qs(urlParams)[k] for k in paramS_list}
	print (urlPrDict)
	return urlPrDict

	
	

def cancel(urlparam_dict):
	# https://www.opentable.com/book/view?rid=52636&d=2019-09-23%2016%3A30&sd=2019-09-23%2016%3A30&p=2&pt=100&pofids=&hash=3073588394&st=Standard&avt=eyJ2IjoxLCJtIjowLCJwIjowLCJjIjo2fQ&corrid=79915f8a-6613-445c-96a8-0f035958a088&dateTime=&iid=1&rai=false&reso=1&resoC=0&rgt=0&anon=0&conv=0&ui=new&user=0&confnumber=2064023270&token=01ubQJSIyuqpZu2CzE9f--cVSq_buzB9Jii251X-JkXok1
	# https://www.opentable.com/book/cancel?rid=52636&confnumber=2064023270&token=01ubQJSIyuqpZu2CzE9f--cVSq_buzB9Jii251X-JkXok1

	# https://www.opentable.com/book/cancel?rid=%5B%2752636%27%5D&confnumber=%5B%27281444232%27%5D&token=%5B%2701hqs7v_NJcMTfSpIOcEU78puA3vEZVW3_fAwv9-ssN1k1%27%5D



	url = 'https://www.opentable.com/book/cancel?'+urlencode(urlparam_dict, True)
	print (url)
	driver.get(url)
	driver.find_element_by_css_selector('#btn-cancel').click()




def convert_time(Time):
	converted_time_results = []
	converted_time_results.append("20" + Time[0]+Time[1])
	converted_time_results.append("3A" + Time[3]+Time[4])
	return converted_time_results

def convert_rest_name(RestName):
	RestName = RestName.lower()
	RestName = RestName.replace(" ","-")    
	return RestName

def convert_URL(DateTime,Covers,ConvertedTime,RestName):
	return BASE_URL+ RestName+"?DateTime="+DateTime+"%"+ConvertedTime[0]+"%"+ConvertedTime[1]+"&Covers="+Covers


def send_email(availTimes, ConvertedURL, RestName):
			gmail_user = GMAIL_ACCOUNT
			gmail_pwd = GMAIL_PASSWORD
			FROM = 'The Open Table bot'
			TO = [''] #must be a list
			SUBJECT = "I Found a Table at %s" %RestName + "!"
			tempText =""
			for x in availTimes:
				tempText = tempText + "%s" %x + "\n"
			TEXT = "Hi, I managed to find a table at: \n"  + tempText + "Book it here: %s" %ConvertedURL

			# Prepare actual message
			message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
			""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
			try:
				#server = smtplib.SMTP(SERVER) 
				server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
				server.ehlo()
				server.starttls()
				server.login(gmail_user, gmail_pwd)
				server.sendmail(FROM, TO, message)
				#server.quit()
				server.close()
				print ('successfully sent the mail')
			except:
				print ("failed to send mail")

if __name__ == "__main__":
	driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())

	config = configparser.ConfigParser()
	config.read(sys.argv[1])

	ConvertedRestName = convert_rest_name(config['args']['restName'])
	ConvertedTime = convert_time(config['args']['time'])
	ParsedTime = datetime.strptime(config['args']['time'], '%H:%M')
	ConvertedURL = convert_URL(config['args']['date'],config['args']['partySize'],ConvertedTime,ConvertedRestName)
	Window = config['args']['windowSizeMin']

	print (ConvertedURL)
	
	availTimes = get_status(ConvertedURL)
	print (availTimes)
	snag_rez(availTimes)

	
	

	
	# if availTimes == []:
	#     print ("Sorry, no availablity")
	# else:
		# send_email(availTimes,ConvertedURL,RestName)
		# print (availTimes)

	

	
	sys.exit