from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.expections import ElementNotInteractableExpection, NoSuchElementExpection,  StableElementReferenceExpection
from random import randict, randrange 
import time
import random



url = 'https://www.amazon.com'
wait_time = 5


class Amazon:
    def __init__(self, username, password):
        '''Intitalizes bot with class_wide variables'''
        self.username = username
        self.password = password
        
        self.driver = webdriver.Chrome()

    def signIn(self):
        driver = self.driver

        username_elem = driver.find_element_by_xpath("//input[@name'email']")
        username_elem.clear()
        username_elem.send_keys(self.username, )

Amazon.driver.get(url)

Amazon.driver.maximize_window()



