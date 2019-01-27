from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from datetime import datetime
import getpass

def parseOnePage(driver):
    #check to see if orders for a time period exist
    ordersExistBoolean = True
    try:
        orderDetailsLinks = driver.find_elements_by_xpath('//ul[contains(@class,"a-unordered-list a-nostyle a-vertical")]/a')[0::2]
    except NoSuchElementException:
        ordersExistBoolean = False
    if not orderDetailsLinks:
        ordersExistBoolean = False

    perTimePeriodItemsCostList = []
    perTimePeriodShippingCostList = []
    perTimePeriodDateList = []
    perTimePeriodOrderNumList = []
    # if orders exist
    if ordersExistBoolean == True:
        orderDetailsOuterBound = len(orderDetailsLinks)
        orderDetailsRange = range(0, orderDetailsOuterBound)
        # get specific order details
        for q in orderDetailsRange:
            orderDetailsLinks2 = driver.find_elements_by_xpath('//ul[contains(@class,"a-unordered-list a-nostyle a-vertical")]/a')[0::2]
            orderDetailsLinks2[q].click()
            dateOrdered = driver.find_elements_by_xpath('//span[contains(@class, "order-date-invoice-item")]')[0].text
            orderNumber = driver.find_elements_by_xpath('//span[contains(@class, "order-date-invoice-item")]')[1].text
            perTimePeriodDateList.append(dateOrdered)
            perTimePeriodOrderNumList.append(orderNumber)

            #check if shipping element exists
            shippingExists = driver.find_elements_by_xpath('//div[contains(@id, "od-subtotals")]/div/div[contains(@class,"a-column a-span5 a-text-right a-span-last")]')
            if len(shippingExists) != 0:
                shippingSubtotal = driver.find_elements_by_xpath('//div[contains(@id, "od-subtotals")]/div/div[contains(@class,"a-column a-span5 a-text-right a-span-last")]')[1].text
                itemsSubtotal = driver.find_elements_by_xpath('//div[contains(@id, "od-subtotals")]/div/div[contains(@class,"a-column a-span5 a-text-right a-span-last")]')[0].text
                perTimePeriodItemsCostList.append(itemsSubtotal)
                perTimePeriodShippingCostList.append(shippingSubtotal)
            elif len(shippingExists) == 0:
                itemsSubtotal = driver.find_element_by_xpath('//div[contains(@class,"a-fixed-right-grid-col a-col-right")]/div/div[contains(@class,"a-column a-span5 a-text-right a-span-last")]').text
                perTimePeriodItemsCostList.append(itemsSubtotal)
                perTimePeriodShippingCostList.append("$0.00")
            else:
                raise ValueError('How did you get here?')
            driver.back()
    # no orders for time frame
    else:
        perTimePeriodDateList.append("N/A")
        perTimePeriodOrderNumList.append("N/A")
        perTimePeriodItemsCostList.append("$0.00")
        perTimePeriodShippingCostList.append("$0.00")

    # compile per-time frame dataframe
    onePageDf = pd.DataFrame(
        {'Date_Ordered': perTimePeriodDateList,
         'Order_Number': perTimePeriodOrderNumList,
         'Order_Cost': perTimePeriodItemsCostList,
         'Shipping_Cost': perTimePeriodShippingCostList
         })
    return onePageDf

def processOneTimePeriod(driver, timePeriod):
    paginationExistBoolean = True
    timePeriodDf = pd.DataFrame()
    #check for multiple pages
    try:
        isPagination = driver.find_elements_by_xpath('//ul[contains(@class, "a-pagination")]/li')
        numPages = len(isPagination)-2
        pageRange = range(0,numPages)
    except NoSuchElementException:
        paginationExistBoolean = False
    if not isPagination:
        paginationExistBoolean = False

    if paginationExistBoolean == True:
        for e in pageRange:
            onePageDf = parseOnePage(driver)
            timePeriodDf = timePeriodDf.append(onePageDf)
            try:
                nextPageButton = driver.find_element_by_xpath('//li[contains(@class, "a-last")]').click()
            except NoSuchElementException:
                disabledPageButton = driver.find_element_by_xpath('//li[contains(@class, "a-disabled a-last")]')
    else:
        onePageDf = parseOnePage(driver)
        timePeriodDf = timePeriodDf.append(onePageDf)

    #clean time period dataframe
    timePeriodDf.reset_index(inplace=True)
    timePeriodDf.drop('index', axis = 1, inplace = True)
    timePeriodDf.insert(loc = 0, column = 'Time_Period', value = timePeriod)

    timePeriodDf['Order_Cost'] = timePeriodDf.Order_Cost.str.replace('$', '')
    timePeriodDf['Order_Cost'] = timePeriodDf.Order_Cost.str.replace(',', '')
    timePeriodDf['Shipping_Cost'] = timePeriodDf.Shipping_Cost.str.replace('$', '')
    timePeriodDf['Shipping_Cost'] = timePeriodDf.Shipping_Cost.str.replace(',', '')
    timePeriodDf["Order_Cost"] = pd.to_numeric(timePeriodDf["Order_Cost"])
    timePeriodDf["Shipping_Cost"] = pd.to_numeric(timePeriodDf["Shipping_Cost"])

    timePeriodDf['Order_Total_Cost'] = timePeriodDf['Order_Cost'] + timePeriodDf['Shipping_Cost']
    return timePeriodDf

def main(username, pw, chromePath):
    ##set up options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_driver_location = chromePath
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_driver_location, options=chrome_options)
    driver.implicitly_wait(5)

    #initialize variables
    today = datetime.today().strftime('%m-%d-%Y')

    ##begin navigation
    driver.get(r'https://www.amazon.com/')
    driver.find_element_by_xpath('//a[contains(@id, "nav-link-accountList")]').click()
    driver.find_element_by_xpath('//input[contains(@type, "email")]').send_keys(username)
    driver.find_element_by_xpath('//input[contains(@type, "password")]').send_keys(pw)
    driver.find_element_by_xpath('//input[contains(@id, "signInSubmit")]').click()
    ##navigate to orders
    driver.find_element_by_xpath('//a[contains(@id, "nav-orders")]').click()

    #try to find orders per time period, set order details list variables
    #click dropdown
    driver.find_element_by_xpath('//span[contains(@class, "a-button-text a-declarative")]').click()
    listOfTimePeriods = driver.find_elements_by_xpath('//ul[contains(@class, "a-nostyle a-list-link")]/li')
    timePeriodsRange = range(0,len(listOfTimePeriods))
    timePeriodsTextList = []
    for t in listOfTimePeriods:
        timePeriodsTextList.append(t.text)

    cumulativeFrame = pd.DataFrame()

    for r, y in zip(timePeriodsRange,timePeriodsTextList):
        if r == 0:
            listOfTimePeriods[r].click()

            #begin parsing
            tempDfToAppend = processOneTimePeriod(driver, y)
            cumulativeFrame = cumulativeFrame.append(tempDfToAppend)

        else:
            driver.find_element_by_xpath('//span[contains(@class, "a-button-text a-declarative")]').click()
            listOfTimePeriods = driver.find_elements_by_xpath('//ul[contains(@class, "a-nostyle a-list-link")]/li')
            listOfTimePeriods[r].click()

            #begin parsing
            tempDfToAppend = processOneTimePeriod(driver, y)
            cumulativeFrame = cumulativeFrame.append(tempDfToAppend)

    #create groupedby frames
    groupedByOrderTotals = cumulativeFrame.groupby(['Time_Period'])[["Order_Cost"]].sum()
    groupedByShippingTotals = cumulativeFrame.groupby(['Time_Period'])[["Shipping_Cost"]].sum()
    summaryFrame = pd.merge(groupedByOrderTotals, groupedByShippingTotals, on='Time_Period')

    cumulativeFrame.to_csv(str(today)+'_fullAmazonPurchaseHistory.csv')
    summaryFrame.to_csv(str(today) + '_summarizedAmazonPurchaseHistory.csv')

    driver.close()

if __name__ == "__main__":
    print("Let's see how much money you've given to Jeff Bezos!")
    userName = input('Amazon Username/Email Address: ')
    pw = getpass.getpass('Password: ')
    chromePath = input('Filepath to Chrome Exe: ')
    main(userName, pw, chromePath)