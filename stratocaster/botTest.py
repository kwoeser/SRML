from selenium import webdriver

driver = webdriver.Chrome()

url = 'https://www.youtube.com/watch?v=1pzoiIRdVas'

driver.get(url)

driver.maximize_window()

