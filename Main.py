from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdrivermanager import ChromeDriverManager
from Product import Product
import json, time

driver = ChromeDriverManager()
driver.download_and_install()

# User Input
search_term = input("Enter the name of the product:")

# Global Variables
biggest_discount = 0.0
lowest_price = 0.0
cheapest_product = Product("", "", "", "")
best_deal_product = Product("", "", "", "")
search_terms = search_term.split(" ")
products = []

# Initialize ChromeDriver
options = Options()
webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
chrome_path = r"/Users/franktran/Library/Application Support/WebDriverManager/bin/chromedriver"
driver = webdriver.Chrome(executable_path=chrome_path, options=options)

# Launch the Website
print('Navigating to Amazon...')
driver.get("http://amazon.ca/")
assert "Amazon" in driver.title, driver.title

# Search for Item
print(f'Searching for {search_term}...')
driver.find_element_by_id("twotabsearchtextbox").send_keys(search_term, Keys.RETURN)

# Get Item Details
counter = 0
itemPath = '//*[@id="search"]/div[1]/div[2]/div/span[3]/div[2]'
print('Retrieving Product Details...')

# Iterates through 5 Pages
pagesToSearch = 5
while pagesToSearch > 0:
    driver.get(driver.current_url + "&page=" + str(pagesToSearch))
    print('Current Page: ', driver.current_url)

    for item in driver.find_elements_by_xpath(itemPath):
        print('Gathering Products...')
        name = ""
        link = ""
        price = 0.0
        prev_price = 0.0
        counter = 0

        # Search for 70 products on that page
        while counter <= 70:
            # print('Counter', counter)
            try:
                name = item.find_element_by_xpath(f'//div[{counter}]/div/span/div/div/div[2]/h2/a/span').text
                print('Product Name: ', name)
                link = item.find_element_by_xpath(f'//div[{counter}]/div/span/div/div/div[2]/h2/a').get_attribute('href')
                print('Product Link: ', link)
                price = item.find_element_by_xpath(f'//div[{counter}]').find_element_by_class_name('a-price').text
                price = float(price.replace('\n', '.').replace("CDN$", ''))
                print('Current Price: ', price)
                try:
                    prev_price = item.find_element_by_xpath(f'//div[{counter}]').find_element_by_class_name('a-text-price').text
                    prev_price = float(prev_price.replace('\n', '.').replace("CDN$", ''))
                    print('Previous Price: ', prev_price)
                except:
                    prev_price = price

                product = Product(name, price, prev_price, link)
                products.append(product)
            except:
                "I'm retarded try me again"

            counter += 1

    pagesToSearch -= 1
    print('Searching Page: ', pagesToSearch)
    counter = 0
    if pagesToSearch == 0:
        break

driver.quit()

print('Identifying Best Deal and Lowest Price...')

firstRun = True

# Check if Search Terms are in the Product Name
for product in products:
    containSearchWord = True
    for word in search_terms:
        if word.lower() not in product.name.lower():
            containSearchWord = False
    if containSearchWord:
        if firstRun:
            lowest_price = product.price
            cheapest_product = product
            firstRun = False
        # Compare the prices of each product to identify cheapest item
        elif product.price < lowest_price:
            lowest_price = product.price
            cheapest_product = product
        # Identify product with the biggest discount
        discount = product.prev_price - product.price
        if discount > biggest_discount:
            biggest_discount = discount
            best_deal_product = product

# Compile and store matching results into a JSON file
with open('products.json', 'w') as json_file:
    data = {}
    data["Products"] = []
    for prod in products:
        data["Products"].append(prod.serialize())
    json.dump(data, json_file, sort_keys=True, indent=4)

# Print out the Lowest Price, and the Best Deal
print('Cheapest Product')
print(json.dumps(cheapest_product.serialize(), indent=4, sort_keys=True))
print('Biggest Deal on Product')
print(json.dumps(best_deal_product.serialize(), indent=4, sort_keys=True))

# Opens the webpage to the best discounted product
options = Options()
webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(executable_path=chrome_path, options=options)
driver.get(best_deal_product.link)
