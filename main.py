from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
import random
import nba

teams = {'MINNESOTA TIMBERWOLVES LIVE': 'MIN', 'ORLANDO MAGIC LIVE': 'ORL',
         'LOS ANGELES CLIPPERS LIVE': 'LAC', 'INDIANA PACERS LIVE': 'IND', 'TORONTO RAPTORS LIVE': 'TOR',
         'ATLANTA HAWKS LIVE': 'ATL', 'MEMPHIS GRIZZLIES LIVE': 'MEM', 'OKLAHOMA CITY THUNDER LIVE': 'OKC',
         'LOS ANGELES LAKERS LIVE': 'LAL', 'BOSTON CELTICS LIVE': 'BOS', 'DENVER NUGGETS LIVE': 'DEN',
         'CLEVELAND CAVALIERS LIVE': 'CLE', 'NEW YORK KNICKS LIVE': 'NYK', 'MILWAUKEE BUCKS LIVE': 'MIL',
         'CHICAGO BULLS LIVE': 'CHI', 'GOLDEN STATE WARRIORS LIVE': 'GSW', 'MIAMI HEAT LIVE': 'MIA',
         'CHARLOTTE HORNETS LIVE': 'CHA', 'NEW ORLEANS PELICANS LIVE': 'NOP', 'WASHINGTON WIZARDS LIVE': 'WAS',
         'PHOENIX SUNS LIVE': 'PHX', 'BROOKLYN NETS LIVE': 'BKN', 'PORTLAND TRAIL BLAZERS LIVE': 'POR',
         'DALLAS MAVERICKS LIVE': 'DAL', 'SAN ANTONIO SPURS LIVE': 'SAS', 'UTAH JAZZ LIVE': 'UTA',
         'DETROIT PISTONS LIVE': 'DET', 'PHILADELPHIA 76ERS LIVE': 'PHI', 'HOUSTON ROCKETS LIVE': 'HOU',
         'SACRAMENTO KINGS LIVE': 'SAC'}

teamnum = {'ATL': 0, 'BOS': 1, 'BKN': 2, 'CHA': 3, 'CHI': 4, 'CLE': 5, 'DAL': 6, 'DEN': 7, 'DET': 8, 'GSW': 9,
           'HOU': 10, 'IND': 11, 'LAC': 12, 'LAL': 13, 'MEM': 14, 'MIA': 15, 'MIL': 16, 'MIN': 17, 'NOP': 18,
           'NYK': 19, 'OKC': 20, 'ORL': 21, 'PHI': 22, 'PHX': 23, 'POR': 24, 'SAC': 25, 'SAS': 26, 'TOR': 27,
           'UTA': 28, 'WAS': 29}

cbox = "lg_41"
games = nba.populate()
driver = webdriver.Firefox(executable_path=r'geckodriver.exe')


def connect():
    driver.get("")
    assert "" in driver.title
    elem = driver.find_element_by_id("Account")
    elem.clear()
    elem.send_keys("")
    elem = driver.find_element_by_id("Password")
    elem.clear()
    elem.send_keys("")
    elem.send_keys(Keys.RETURN)
    elem = WebDriverWait(driver, 3).until(ec.presence_of_element_located((By.LINK_TEXT, "Straight")))
    elem.click()
    try:
        driver.find_element_by_name(cbox).click()
    except NoSuchElementException:
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
        ou = cont.div.div.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.div.string
        if 'EV' in ou:
            ou = ou.split('EV')[0][1:].replace('½', '.5')
        elif '+' in ou:
            ou = ou.split('+')[0][1:].replace('½', '.5')
        else:
            ou = ou.split('-')[0][1:].replace('½', '.5')
    except AttributeError:
        cont = cont.next_sibling.next_sibling
        continue

    team = teams[cont.div.div.next_sibling.next_sibling.img['team']]
    team2 = teams[cont.div.next_sibling.next_sibling.div.next_sibling.next_sibling.img['team']]
    timeleft = nba.time(games[team])

    if games[team] in open("bets.log", "r").read() or timeleft >= 36:
        cont = cont.next_sibling.next_sibling
        continue

    score = nba.score(games[team])
    poss = nba.poss(games[team])
    means = nba.ortg(teamnum[team], teamnum[team2])
    team1_rating = score[1]/poss
    team2_rating = score[2]/poss
    team1_mean = means[0]
    team2_mean = means[1]
    pace = 48 * poss / (48 - timeleft)
    remaining_poss = timeleft * pace / 48
    prediction1 = team1_rating * remaining_poss + team2_rating * remaining_poss + score[0]
    predictionmean = team1_mean * remaining_poss + team2_mean * remaining_poss + score[0]
    predictionmean2 = team1_mean * pace + team2_mean * pace
    prediction = ((2*predictionmean2) + (3*predictionmean) + (3*prediction1)) / 8

    print(team + ' ou' + ou)
    print('Prediction: ' + '%.1f' % prediction + ' (' + '%.1f' % predictionmean2 + ','
          + '%.1f' % predictionmean + ',' + '%.1f' % prediction1 + ')' + ', Time: ' + '%.2f' % timeleft)
    print('Pace: ' + '%.1f' % pace + ', Rating1: ' + '%.2f' % team1_rating + ', Rating2: ' + '%.2f' % team2_rating)

    if prediction >= float(ou) + 7 and timeleft <= 22.5 and abs(predictionmean2 - prediction1) < 40\
            and abs(predictionmean2 - float(ou)) < 20:
        open("bets.log", "a").write('[' + games[team] + ']' + ' ' + team + ' o' + ou + ', Time: '
                                    + '%.2f' % timeleft + ', Prediction: ' + '%.1f' % prediction
                                    + ' (' + '%.1f' % predictionmean2 + ','
                                    + '%.1f' % predictionmean + ',' + '%.1f' % prediction1 + ')\n')
    elif prediction <= float(ou) - 7 and timeleft <= 22.5 and abs(predictionmean2 - prediction1) < 40\
            and abs(predictionmean2 - float(ou)) < 20:
        open("bets.log", "a").write('[' + games[team] + ']' + ' ' + team + ' u' + ou + ', Time: '
                                    + '%.2f' % timeleft + ', Prediction: ' + '%.1f' % prediction
                                    + ' (' + '%.1f' % predictionmean2 + ','
                                    + '%.1f' % predictionmean + ',' + '%.1f' % prediction1 + ')\n')
    else:
        print('')

    cont = cont.next_sibling.next_sibling
