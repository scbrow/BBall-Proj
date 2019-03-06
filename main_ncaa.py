from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
import random
import ncaa

cbox = "lg_4"
driver = webdriver.Firefox(executable_path=r'C:\Users\scott\Downloads\geckodriver-v0.24.0-win64\geckodriver.exe')


def connect():
    driver.get("")
    assert "SportsBook Login" in driver.title
    driver.find_element_by_id("Account").send_keys("")
    driver.find_element_by_id("Password").send_keys("" + Keys.RETURN)
    elem = WebDriverWait(driver, 3).until(ec.presence_of_element_located((By.LINK_TEXT, "Straight")))
    elem.click()
    try:
        driver.find_element_by_name(cbox).click()
    except NoSuchElementException:
        driver.find_element(By.LINK_TEXT, "Straight").click()
        driver.find_element_by_name(cbox).click()
    driver.find_element_by_id("magic_continue").click()


def refresh():
    driver.find_element(By.LINK_TEXT, "Straight").click()
    driver.find_element_by_name(cbox).click()
    driver.find_element_by_id("magic_continue").click()


connect()
soup = BeautifulSoup(driver.page_source, 'lxml')
cont = soup.find(attrs={"class": "Competition container-fluid AltRow"})

while True:
    if cont is None or cont.div.div.next_sibling.string == '90001':
        time.sleep(random.randint(5, 10))
        try:
            driver.find_element_by_xpath("//input[@value='Refresh']").click()
        except NoSuchElementException:
            connect()
        soup = BeautifulSoup(driver.page_source, 'lxml')
        cont = soup.find(attrs={"class": "Competition container-fluid AltRow"})
        continue

    try:
        ou_box = cont.div.div.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.div
        if 'EV' in ou_box.string:
            ou = ou_box.string.split('EV')[0][1:].replace('½', '.5')
        elif '+' in ou_box.string:
            ou = ou_box.string.split('+')[0][1:].replace('½', '.5')
        else:
            ou = ou_box.string.split('-')[0][1:].replace('½', '.5')
    except AttributeError:
        cont = cont.next_sibling.next_sibling
        continue

    ou_value = ou_box['data-target'].split('_')
    team1 = cont.div.div.next_sibling.next_sibling.img['team'].split(" BK LIVE")[0].replace('CENTRAL FLORIDA', 'UCF')
    team2 = cont.div.next_sibling.next_sibling.div.next_sibling.next_sibling.img['team'].split(" BK LIVE")[0] \
        .replace('CENTRAL FLORIDA', 'UCF')
    timeleft = ncaa.time(team1, team2)

    if team1 in open("bets.log", "r").read() or timeleft >= 30:
        cont = cont.next_sibling.next_sibling
        continue

    score = ncaa.score(team1, team2)
    poss = ncaa.poss(team1, team2)
    means = ncaa.ortg(team1, team2)
    team1_rating = score[1] / poss
    team2_rating = score[2] / poss
    team1_mean = means[0]
    team2_mean = means[1]
    pace = 40 * poss / (40 - timeleft)
    remaining_poss = timeleft * pace / 40
    prediction1 = team1_rating * remaining_poss + team2_rating * remaining_poss + score[0]
    predictionmean = team1_mean * remaining_poss + team2_mean * remaining_poss + score[0]
    predictionmean2 = team1_mean * pace + team2_mean * pace
    prediction = (predictionmean + predictionmean2 + prediction1) / 3

    print(team1 + ' ou' + ou)
    print('Prediction: ' + '%.1f' % prediction + ' (' + '%.1f' % predictionmean2 + ','
          + '%.1f' % predictionmean + ',' + '%.1f' % prediction1 + ')' + ', Time: ' + '%.2f' % timeleft)
    print('Pace: ' + '%.1f' % pace + ', Rating1: ' + '%.2f' % team1_rating + ', Rating2: ' + '%.2f' % team2_rating)

    if prediction >= float(ou) + 5 and timeleft < 20 and abs(predictionmean2 - prediction1) < 38:
        open("bets.log", "a").write('[' + team1 + ']' + ' ' + team2 + ' o' + ou + ', Time: '
                                    + '%.2f' % timeleft + ', Prediction: ' + '%.1f' % prediction
                                    + ' (' + '%.1f' % predictionmean2 + ','
                                    + '%.1f' % predictionmean + ',' + '%.1f' % prediction1 + ')\n')
        # driver.find_element_by_xpath("//div[@data-target='2_" + ou_value[1] + "_-" + ou.replace('.', '_')
        #                             + "_" + ou_value[-1] + "']").click()
        # driver.find_element_by_id("magic_continue").click()
        # driver.find_element_by_id("WAMT_").send_keys("10" + Keys.RETURN)
        # WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "password")))\
        #    .send_keys("" + Keys.RETURN)
        # refresh()
        # soup = BeautifulSoup(driver.page_source, 'lxml')
        # cont = soup.find(attrs={"class": "Competition container-fluid AltRow"})
        # continue
    elif prediction <= float(ou) - 5 and timeleft < 20 and abs(predictionmean2 - prediction1) < 38:
        open("bets.log", "a").write('[' + team1 + ']' + ' ' + team2 + ' u' + ou + ', Time: '
                                    + '%.2f' % timeleft + ', Prediction: ' + '%.1f' % prediction
                                    + ' (' + '%.1f' % predictionmean2 + ','
                                    + '%.1f' % predictionmean + ',' + '%.1f' % prediction1 + ')\n')

        # driver.find_element_by_xpath("//div[@data-target='3_" + ou_value[1] + "_" + ou.replace('.', '_')
        #                             + "_" + ou_value[-1] + "']").click()
        # driver.find_element_by_id("magic_continue").click()
        # driver.find_element_by_id("WAMT_").send_keys("10" + Keys.RETURN)
        # WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "password"))) \
        #    .send_keys("" + Keys.RETURN)

        # refresh()
        # soup = BeautifulSoup(driver.page_source, 'lxml')
        # cont = soup.find(attrs={"class": "Competition container-fluid AltRow"})
        # continue
    else:
        print('')

    cont = cont.next_sibling.next_sibling
