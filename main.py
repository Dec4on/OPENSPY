import threading
import time
import json
from libs.printer import TextPrinter, TextStyle 
from libs.utilities import Utilities
from libs.pirate import Pirate
from libs.newday import Newday
from libs.ruins import Ruins
from libs.victims import Victims
from libs.generateExe import Generate
from libs.overclaim import getOverclaim, getOverclaimTowns
from libs.fallingin import getTownsFallingIn
from libs.noperm import getNoPerm
from libs.forsale import getForSaleTowns
from libs.trades import getTrades
from libs.protect import protectPlayerCheck 
from libs.trustedin import getTrustedTowns
from libs.joinnation import getJoinNations
import math
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Global variables
VERSION = 1.3

BOLD = '\033[1m'
GRAY = '\033[90m'
ENDC = '\033[0m'

protection_list = []


def findPlayer():
    conn = Utilities.DBstart()

    if Utilities.getSetting(conn, 'collect_locations') == False:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Find Player', TextStyle.HEADER)
        TextPrinter.print('Location tracking is turned off in settings.', TextStyle.WARNING)
        input = TextPrinter.input()
        return
    
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Find Player', TextStyle.HEADER)

        input = TextPrinter.input().strip()
        if input == '/b':
            return
        
        player_data = Utilities.fetchPlayerData(conn, input)
        if player_data == None:
            TextPrinter.print('Player not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Find Player', TextStyle.HEADER)
        
        print(BOLD + 'Name: ' + ENDC + player_data['name'])
        print(BOLD + 'X: ' + ENDC + str(player_data['x']))
        print(BOLD + 'Z: ' + ENDC + str(player_data['z']))

        record_date = Utilities.epochToDatetime(player_data['timestamp'] * 1000)
        print(BOLD + 'At Location: ' + ENDC + record_date)

        input = TextPrinter.input()
        if input.strip() == '/b':
            continue


def getTown():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.guide('Divide towns with commas.')
        TextPrinter.print('Town Lookup', TextStyle.HEADER)

        input = TextPrinter.input()
        if input.strip() == '/b':
            return

        result = ','.join(Utilities.queryToList(input))
        response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/towns?query={result}')
        if response == None:
            TextPrinter.print('Town not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.print('Town Lookup', TextStyle.HEADER)

            if len(response) > 1:
                TextPrinter.print('Type item index to select.')

                index = 1
                for item in response:
                    town_name = item['name']
                    TextPrinter.print(f'- {town_name} ({index})', TextStyle.ARGUMENT)
                    index += 1

                input = TextPrinter.input()
                if input.strip() == '/b':
                    return
                
                try:
                    selected_index = int(input.strip()) - 1
                except Exception:
                    continue
                
                TextPrinter.clear()
                TextPrinter.guide("'/b' to go back.")
                TextPrinter.print('Town Lookup', TextStyle.HEADER)
            else:
                selected_index = 0

            try:
                town = response[selected_index]
            except Exception:
                TextPrinter.print('Wrong index.', TextStyle.WARNING)
                time.sleep(.4)
                continue

            print(BOLD + 'Name: ' + ENDC + town['name'])

            if town['board'] and town['board'] != '/town set board [msg]':
                print(BOLD + 'Board: ' + ENDC + town['board'])

            if town['wiki']:
                print(BOLD + 'Wiki: ' + ENDC + town['wiki'])
            
            print(BOLD + 'Capital: ' + ENDC + str(town['status']['isCapital']))

            print(BOLD + 'Mayor: ' + ENDC + town['mayor']['name'])

            if town['nation']['name']:
                print(BOLD + 'Nation: ' + ENDC + town['nation']['name'])

            balance = int(town['stats']['balance'])
            print(BOLD + 'Bank: ' + ENDC + str(balance) + 'g')

            is_public = str(town['status']['isPublic'])
            is_open = str(town['status']['isOpen'])
            overclaimshield = str(town['status']['hasOverclaimShield'])
            print(BOLD + 'Status: ' + ENDC + 'isPublic=' + is_public + ' isOpen=' + is_open + ' hasOverclaimShield=' + overclaimshield)

            print(BOLD + 'Total Town Blocks: ' + ENDC + str(town['stats']['numTownBlocks']))

            print(BOLD + 'Residents: ' + ENDC + str(town['stats']['numResidents']))

            print(BOLD + 'Registered: ' + ENDC + Utilities.epochToDatetime(town['timestamps']['registered']))

            def getRanked(list):
                new_list = []
                for user in list:
                    new_list.append(user['name'])
                return new_list
            
            if town['ranks']['Councillor'] != []:
                print(BOLD + 'Councillor: ' + ENDC + Utilities.listToString(town['ranks']['Councillor']))

            if town['ranks']['Builder'] != []:
                print(BOLD + 'Colonist: ' + ENDC + Utilities.listToString(town['ranks']['Councillor']))

            if town['outlaws'] != []:
                formatted_list = getRanked(town['outlaws'])
                print(BOLD + 'Outlaws: ' + ENDC + Utilities.listToString(formatted_list))

            if town['trusted'] != []:
                formatted_list = getRanked(town['trusted'])
                print(BOLD + 'Trusted: ' + ENDC + Utilities.listToString(formatted_list))

            input = TextPrinter.input()
            if input == '/b' and len(response) == 1:
                break


def getNation():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.guide('Divide nations with commas.')
        TextPrinter.print('Nation Lookup', TextStyle.HEADER)

        input = TextPrinter.input()
        if input.strip() == '/b':
            return

        result = ','.join(Utilities.queryToList(input))
        response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/nations?query={result}')
        if response == None:
            TextPrinter.print('Nation not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.print('Nation Lookup', TextStyle.HEADER)

            if len(response) > 1:
                TextPrinter.print('Type item index to select.')

                index = 1
                for item in response:
                    nation_name = item['name']
                    TextPrinter.print(f'- {nation_name} ({index})', TextStyle.ARGUMENT)
                    index += 1

                input = TextPrinter.input()
                if input.strip() == '/b':
                    return
                
                try:
                    selected_index = int(input.strip()) - 1
                except Exception:
                    continue
                
                TextPrinter.clear()
                TextPrinter.guide("'/b' to go back.")
                TextPrinter.print('Nation Lookup', TextStyle.HEADER)
            else:
                selected_index = 0

            try:
                nation = response[selected_index]
            except Exception:
                TextPrinter.print('Wrong index.', TextStyle.WARNING)
                time.sleep(.4)
                continue

            print(BOLD + 'Name: ' + ENDC + nation['name'])
            if nation['board']:
                print(BOLD + 'Board: ' + ENDC + nation['board'])

            if nation['wiki']:
                print(BOLD + 'Wiki: ' + ENDC + nation['wiki'])
            
            print(BOLD + 'Capital: ' + ENDC + nation['capital']['name'])

            print(BOLD + 'King: ' + ENDC + nation['king']['name'])

            balance = int(nation['stats']['balance'])
            print(BOLD + 'Bank: ' + ENDC + str(balance) + 'g')

            is_public = str(nation['status']['isPublic'])
            is_open = str(nation['status']['isOpen'])
            is_neutral = str(nation['status']['isNeutral'])
            print(BOLD + 'Status: ' + ENDC + 'isPublic=' + is_public + ' isOpen=' + is_open + ' isNeutral=' + is_neutral)

            print(BOLD + 'Total Town Blocks: ' + ENDC + str(nation['stats']['numTownBlocks']))

            print(BOLD + 'Residents: ' + ENDC + str(nation['stats']['numResidents']))

            print(BOLD + 'Towns: ' + ENDC + str(nation['stats']['numTowns']))
            
            def getRanked(list):
                new_list = []
                for user in list:
                    new_list.append(user['name'])
                return new_list

            if nation['allies'] != []:
                formatted_list = getRanked(nation['allies'])
                print(BOLD + 'Allies: ' + ENDC + Utilities.listToString(formatted_list))
            else:
                print(BOLD + 'Allies: ' + ENDC + "None")

            if nation['enemies'] != []:
                formatted_list = getRanked(nation['enemies'])
                print(BOLD + 'Enemies: ' + ENDC + Utilities.listToString(formatted_list))
            else:
                print(BOLD + 'Enemies: ' + ENDC + "None")

            print(BOLD + 'Registered: ' + ENDC + Utilities.epochToDatetime(nation['timestamps']['registered']))
            
            if nation['ranks']['Chancellor'] != []:
                print(BOLD + 'Chancellors: ' + ENDC + Utilities.listToString(nation['ranks']['Chancellor']))

            if nation['ranks']['Colonist'] != []:
                print(BOLD + 'Colonist: ' + ENDC + Utilities.listToString(nation['ranks']['Colonist']))

            if nation['ranks']['Diplomat'] != []:
                print(BOLD + 'Diplomat: ' + ENDC + Utilities.listToString(nation['ranks']['Diplomat']))

            if nation['sanctioned'] != []:
                formatted_list = getRanked(nation['sanctioned'])
                print(BOLD + 'Sanctioned: ' + ENDC + Utilities.listToString(formatted_list))

            input = TextPrinter.input()
            if input == '/b' and len(response) == 1:
                break


def fallingIn():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Falling in Nation', TextStyle.HEADER)
        TextPrinter.print('What nation do you want to check?', TextStyle.ARGUMENT)

        input = TextPrinter.input().strip()
        if input == '/b':
            return

        response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/nations?query={input}')
        if response == None:
            TextPrinter.print('Nation not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Falling in Nation', TextStyle.HEADER)
        TextPrinter.print('This can take a while...', TextStyle.ARGUMENT)

        ruined_towns, fallen_towns = getTownsFallingIn(response[0])
        
        if ruined_towns == None or fallen_towns == None:
            TextPrinter.print('Rate limited, try again in a minute.', TextStyle.WARNING)
            input = TextPrinter.input().strip()
            if input == '/b':
                return
            continue

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Falling in Nation', TextStyle.HEADER)
        TextPrinter.print('Within 3 newdays.', TextStyle.ARGUMENT)

        TextPrinter.print('\nFalling Towns', TextStyle.BLUE)
        for town in fallen_towns:
            TextPrinter.print('--------', TextStyle.GRAY)
            print(BOLD + 'Town: ' + ENDC + town['name'])
            print(BOLD + 'Balance: ' + ENDC + str(town['stats']['balance']))
            print(BOLD + 'Chunks: ' + ENDC + str(town['stats']['numTownBlocks']))
        if fallen_towns == []:
            TextPrinter.print('No falling towns.', TextStyle.ARGUMENT)

        TextPrinter.print('--------', TextStyle.GRAY)
        TextPrinter.print('Ruined Towns', TextStyle.BLUE)
        for town in ruined_towns:
            TextPrinter.print('--------', TextStyle.GRAY)
            print(BOLD + 'Town: ' + ENDC + town['name'])
            print(BOLD + 'Balance: ' + ENDC + str(town['stats']['balance']))
            print(BOLD + 'Chunks: ' + ENDC + str(town['stats']['numTownBlocks']))
        if ruined_towns == []:
            TextPrinter.print('No ruined towns.', TextStyle.ARGUMENT)
        input = TextPrinter.input().strip()
        if input == '/b':
            return


def voteparty():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")

        response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/')
        if response != None:
            TextPrinter.print('Voteparty', TextStyle.HEADER)
            target = response['voteParty']['target']
            numRemaining = target - response['voteParty']['numRemaining']
            TextPrinter.print(f'{numRemaining} / {target}', TextStyle.BOLD)
        else:
            TextPrinter.print('Error, press ENTER to refresh.', TextStyle.ERROR)
        
        input = TextPrinter.input()
        if input == '/b':
            break


def online():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Online in Nation or Town', TextStyle.HEADER)
        TextPrinter.print('Type the town or nation.', TextStyle.ARGUMENT)

        input = TextPrinter.input()
        if input.strip() == '/b':
            return
        response = Utilities.fetchAPI(f"https://api.earthmc.net/v3/aurora/towns?query={input}")

        if response != None:
            response = response[0]
            x = int(response['coordinates']['spawn']['x'])
            z = int(response['coordinates']['spawn']['z'])
        else:
            response = Utilities.fetchAPI(f"https://api.earthmc.net/v3/aurora/nations?query={input}")
            if response != None:
                response = response[0]
                x = int(response['coordinates']['spawn']['x'])
                z = int(response['coordinates']['spawn']['z'])
            else:
                TextPrinter.print('Town or nation not found.', TextStyle.WARNING)
                time.sleep(.4)
                continue
        
        residents = [res['name'] for res in response['residents']]

        try:
            completed_player_list = []
            with ThreadPoolExecutor(max_workers=40) as executor:
                futures = []
                for i in range(0, len(residents), 100):
                    sublist = residents[i:i + 100]
                    futures.append(executor.submit(Utilities.fetch_player_chunk, sublist))        
                for index, future in enumerate(futures):
                    completed_player_list.extend(future.result())
        except Exception:
            TextPrinter.print('Error, try again later.', TextStyle.WARNING)
            time.sleep(.4)
            continue 

        online_residents = [res['name'] for res in completed_player_list if res['status']['isOnline']]

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print(f'Online in {input.capitalize()}', TextStyle.HEADER)

        if online_residents != []:
            online_list = ', '.join(online_residents)
            TextPrinter.print(online_list, TextStyle.BOLD)
        else:
            TextPrinter.print('No online players.', TextStyle.WARNING)

        input = TextPrinter.input().strip()
        if input == '/b' and len(response) == 1:
            return


def getPlayer():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.guide('Divide players with commas.')
        TextPrinter.print('Player Lookup', TextStyle.HEADER)

        input = TextPrinter.input()
        if input.strip() == '/b':
            return

        result = ','.join(Utilities.queryToList(input))
        response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/players?query={result}')
        if response == None:
            TextPrinter.print('Player not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.print('Player Lookup', TextStyle.HEADER)

            if len(response) > 1:
                TextPrinter.print('Type item index to select.')

                index = 1
                for item in response:
                    player_name = item['name']
                    TextPrinter.print(f'- {player_name} ({index})', TextStyle.ARGUMENT)
                    index += 1

                input = TextPrinter.input()
                if input.strip() == '/b':
                    return
                
                try:
                    selected_index = int(input.strip()) - 1
                except Exception:
                    continue
                
                TextPrinter.clear()
                TextPrinter.guide("'/b' to go back.")
                TextPrinter.print('Player Lookup', TextStyle.HEADER)
            else:
                selected_index = 0

            try:
                player = response[selected_index]
            except Exception:
                TextPrinter.print('Wrong index.', TextStyle.WARNING)
                time.sleep(.4)
                continue

            print(BOLD + 'Name: ' + ENDC + player['name'])
            if player['about']:
                print(BOLD + 'About: ' + ENDC + player['about'])
            
            balance = int(player['stats']['balance'])
            print(BOLD + 'Balance: ' + ENDC + str(balance) + 'g')
            
            print(BOLD + 'Last Online: ' + ENDC + Utilities.epochToDatetime(player['timestamps']['lastOnline']))

            print(BOLD + 'Registered: ' + ENDC + Utilities.epochToDatetime(player['timestamps']['registered']))

            if player['title']:
                print(BOLD + 'Title: ' + ENDC + player['title'])

            if player['town']:
                if player['status']['isMayor']:
                    print(BOLD + 'Town: ' + ENDC + player['town']['name'] + " (mayor)")
                else:
                    print(BOLD + 'Town: ' + ENDC + player['town']['name'])

            if player['nation']:
                if player['status']['isKing']:
                    print(BOLD + 'Nation: ' + ENDC + player['nation']['name'] + " (king)")
                else:
                    print(BOLD + 'Nation: ' + ENDC + player['nation']['name'])
            
            if player['uuid']:
                print(BOLD + 'Uuid: ' + ENDC + player['uuid'])
            
            input = TextPrinter.input().strip()
            if input == '/b' and len(response) == 1:
                return
            

def pirate():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Pirate Towns', TextStyle.HEADER)
        TextPrinter.print('In how many newdays do you want to pirate the town? 0 is next newday.', TextStyle.ARGUMENT)

        input = TextPrinter.input().strip()
        if input == '/b':
            return
        
        try:
            offset = int(input)
        except Exception:
            TextPrinter.print('Invalid input', TextStyle.WARNING)
            time.sleep(.4)
            continue

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Pirate Towns', TextStyle.HEADER)
        TextPrinter.print('This can take a while...', TextStyle.ARGUMENT)

        piratable_towns = Pirate.findRuiningTowns(offset)

        if piratable_towns == None:
            TextPrinter.print('Rate limited, try again in a minute.', TextStyle.ERROR)
            input = TextPrinter.input().strip()
            if input == '/b':
                return
            continue

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Pirate Towns', TextStyle.HEADER)

        sorted_towns = sorted(piratable_towns, key=lambda town: town['stats']['balance'], reverse=True)

        for town in sorted_towns:
            TextPrinter.print('--------', TextStyle.GRAY)
            print(BOLD + 'Town: ' + ENDC + town['name'])
            print(BOLD + 'Balance: ' + ENDC + str(town['stats']['balance']))
            print(BOLD + 'Chunks: ' + ENDC + str(town['stats']['numTownBlocks']))
            
        input = TextPrinter.input().strip()
        if input == '/b':
            return

def newday():
    conn = Utilities.DBstart()
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Newday', TextStyle.HEADER)
        TextPrinter.print('Loading...', TextStyle.ARGUMENT)

        used_cache = False
        if Utilities.getSetting(conn, 'cache_newday') != False:
            fallen_cache, fallen_epoch = Utilities.getCache(conn, 'newday_fallen')
            ruined_cache, ruined_epoch = Utilities.getCache(conn, 'newday_ruined')
            seconds_remaining = Newday.secondsToNextNewday()
            newday_epoch = int(time.time()) + seconds_remaining
            if fallen_cache and ruined_cache:
                if fallen_epoch < newday_epoch and ruined_epoch < newday_epoch:
                    ruined_towns, fallen_towns = ruined_cache, fallen_cache
                    used_cache = True

        if used_cache == False:
            ruined_towns, fallen_towns = Newday.findNewdayTowns()

        if not ruined_towns or not fallen_towns:
            TextPrinter.print('Rate limited, try again in a minute.', TextStyle.WARNING)
            input = TextPrinter.input().strip()
            if input == '/b':
                return
            continue

        if Utilities.getSetting(conn, 'cache_newday') != False:
            Utilities.setCache(conn, 'newday_fallen', fallen_towns, int(time.time()))
            Utilities.setCache(conn, 'newday_ruined', ruined_towns, int(time.time()))

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Newday', TextStyle.HEADER)

        TextPrinter.print('Falling Towns', TextStyle.BLUE)
        for town in fallen_towns:
            TextPrinter.print('--------', TextStyle.GRAY)
            print(BOLD + 'Town: ' + ENDC + town['name'])
            print(BOLD + 'Balance: ' + ENDC + str(town['stats']['balance']))
            print(BOLD + 'Chunks: ' + ENDC + str(town['stats']['numTownBlocks']))

        TextPrinter.print('--------', TextStyle.GRAY)
        TextPrinter.print('Ruined Towns', TextStyle.BLUE)
        for town in ruined_towns:
            TextPrinter.print('--------', TextStyle.GRAY)
            print(BOLD + 'Town: ' + ENDC + town['name'])
            print(BOLD + 'Balance: ' + ENDC + str(town['stats']['balance']))
            print(BOLD + 'Chunks: ' + ENDC + str(town['stats']['numTownBlocks']))
            
        input = TextPrinter.input().strip()
        if input == '/b':
            return
        
def closestSpawn(base_x, base_z):
    def calculate_distance(town):
        x = town['coordinates']['spawn']['x']
        z = town['coordinates']['spawn']['z']
        return math.sqrt((x - base_x) ** 2 + (z - base_z) ** 2)

    response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/nearby/coordinate?x={base_x}&z={base_z}&radius=3500')

    town_list = [x['name'] for x in response]

    try:
        completed_town_list = []
        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = []
            for i in range(0, len(town_list), 100):
                sublist = town_list[i:i + 100]
                futures.append(executor.submit(Utilities.fetch_town_chunk, sublist))
            for index, future in enumerate(futures):
                completed_town_list.extend(future.result())
    except Exception:
        return None

    completed_town_list = [town for town in completed_town_list if 'coordinates' in town and town['coordinates']['spawn']['x'] != None and town['status']['isPublic'] or town['status']['isCapital']]

    sorted_town_list = sorted(completed_town_list, key=calculate_distance)

    return sorted_town_list


def goto():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Goto', TextStyle.HEADER)
        TextPrinter.print('Where do you want to go?', TextStyle.ARGUMENT)

        input = TextPrinter.input().strip()
        if input == '/b':
            return
        
        response = Utilities.fetchAPI(f"https://api.earthmc.net/v3/aurora/towns?query={input}")

        if response != None:
            response = response[0]
            x = int(response['coordinates']['spawn']['x'])
            z = int(response['coordinates']['spawn']['z'])
        else:
            response = Utilities.fetchAPI(f"https://api.earthmc.net/v3/aurora/nations?query={input}")
            if response != None:
                response = response[0]
                x = int(response['coordinates']['spawn']['x'])
                z = int(response['coordinates']['spawn']['z'])
            else:
                TextPrinter.print('Town or nation not found.', TextStyle.WARNING)
                time.sleep(.4)
                continue

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Goto', TextStyle.HEADER)
        TextPrinter.print('Loading...', TextStyle.ARGUMENT)

        nearspawn_list = closestSpawn(x, z)

        page = 1
        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.guide(f"Type '{page + 1}' for the next page.")
            TextPrinter.print('Goto', TextStyle.HEADER)

            if nearspawn_list[page - 1]['status']['isCapital'] == False:
                spawn_to_command = '/t spawn'
                town_name = nearspawn_list[page - 1]['name']
            else:
                spawn_to_command = '/n spawn'
                town_name = nearspawn_list[page - 1]['nation']['name']
            
            TextPrinter.print(f'{spawn_to_command} {town_name}', TextStyle.BOLD)

            input = TextPrinter.input().strip()
            if input == '/b':
                break
            try:
                input = int(input)

            except Exception:
                TextPrinter.print('Invalid page number.', TextStyle.WARNING)
                time.sleep(.4)
                continue

            page = input

        
        
def ruins():
    conn = Utilities.DBstart()
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Ruins', TextStyle.HEADER)
        TextPrinter.print('Loading...', TextStyle.ARGUMENT)

        used_cache = False
        if Utilities.getSetting(conn, 'cache_ruins') != False:
            ruined_cache, ruined_epoch = Utilities.getCache(conn, 'ruins')
            seconds_remaining = Newday.secondsToNextNewday()
            newday_epoch = int(time.time()) + seconds_remaining
            if ruined_cache and ruined_epoch < newday_epoch:
                ruined_towns = ruined_cache
                used_cache = True

        if used_cache == False:
            ruined_towns = Ruins.findRuins()

        if not ruined_towns:
            TextPrinter.print('Rate limited, try again in a minute.', TextStyle.WARNING)
            input = TextPrinter.input().strip()
            if input == '/b':
                return
            continue

        if Utilities.getSetting(conn, 'cache_ruins') != False:
            Utilities.setCache(conn, 'ruins', ruined_towns, int(time.time()))
        
        page = 1
        towns_per_page = 5
        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.guide(f"Type '{page + 1}' for the next page.")
            TextPrinter.print('Ruins', TextStyle.HEADER)

            for town in ruined_towns[(page - 1) * towns_per_page:page * towns_per_page]:
                TextPrinter.print('--------', TextStyle.GRAY)
                # Get town coordinates to nearest whole number
                x_coord = str(round(town['coordinates']['spawn']['x']))
                y_coord = str(round(town['coordinates']['spawn']['y']))
                z_coord = str(round(town['coordinates']['spawn']['z']))
                print(BOLD + 'Town: ' + ENDC + town['name'])
                print(BOLD + 'Chunks: ' + ENDC + str(town['stats']['numTownBlocks']))
                print(BOLD + 'Ruined At: ' + ENDC + Utilities.epochToDatetime(town['timestamps']['ruinedAt'])) 
                print(BOLD + 'Coordinates: ' + ENDC + f'X:{x_coord} Y:{y_coord} Z:{z_coord}')
                
            input = TextPrinter.input().strip()
            if input == '/b':
                return
            try:
                input = int(input)

            except Exception:
                TextPrinter.print('Invalid page number.', TextStyle.WARNING)
                time.sleep(.4)
                continue

            page = input


def overclaim():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Overclaim', TextStyle.HEADER)
        print()
        TextPrinter.print('- Find towns to overclaim from nation (1)', TextStyle.ARGUMENT)
        TextPrinter.print('- Find nations to overclaim town from (2)', TextStyle.ARGUMENT)

        input = TextPrinter.input().strip()
        if input == '/b':
            return
        try:
            selected_setting = int(input)
        except Exception:
            TextPrinter.print('Input has to be a number.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        if selected_setting == 1:
            while True:
                TextPrinter.clear()
                TextPrinter.guide("'/b' to go back.")
                TextPrinter.print('Overclaim', TextStyle.HEADER)
                TextPrinter.print('What nation do you want to overclaim from?', TextStyle.ARGUMENT)

                input = TextPrinter.input().strip()
                if input == '/b':
                    break
                
                response = Utilities.fetchAPI(f"https://api.earthmc.net/v3/aurora/nations?query={input}")

                if response != None:
                    response = response[0]
                else:
                    TextPrinter.print('Nation not found.', TextStyle.WARNING)
                    time.sleep(.4)
                    continue

                TextPrinter.clear()
                TextPrinter.guide("'/b' to go back.")
                TextPrinter.print('Overclaim', TextStyle.HEADER)
                TextPrinter.print('Loading...', TextStyle.ARGUMENT)

                towns = getOverclaim(response)

                if towns == None:
                    TextPrinter.print('Please try again later.', TextStyle.WARNING)
                    time.sleep(.4)
                    continue

                if towns == []:
                    TextPrinter.clear()
                    TextPrinter.guide("'/b' to go back.")
                    TextPrinter.print('Overclaim', TextStyle.HEADER)
                    TextPrinter.print('Empty', TextStyle.BOLD)
                    input = TextPrinter.input().strip()
                    continue

                page = 1
                towns_per_page = 10
                while True:
                    TextPrinter.clear()
                    TextPrinter.guide("'/b' to go back.")
                    TextPrinter.guide(f"Type '{page + 1}' for the next page.")
                    TextPrinter.print('Overclaim', TextStyle.HEADER)

                    header = f"{BOLD}Name{' ' * 17}Chunks{' ' * 10}Residents{ENDC}"
                    TextPrinter.print(header)

                    for town in towns[(page - 1) * towns_per_page:page * towns_per_page]:
                        name = town['name'].ljust(20)
                        num_town_blocks = town['stats']['numTownBlocks']
                        max_town_blocks = town['stats']['maxTownBlocks']
                        chunks = str(f'{num_town_blocks}/{max_town_blocks}').ljust(8)
                        residents = str(town['stats']['numResidents'])
                        row = f"{name}{chunks}{' ' * 12}{residents}"
                        TextPrinter.print(row)

                    input = TextPrinter.input().strip()
                    if input == '/b':
                        break
                    try:
                        input = int(input)

                    except Exception:
                        TextPrinter.print('Invalid page number.', TextStyle.WARNING)
                        time.sleep(.4)
                        continue

                    page = input

        elif selected_setting == 2:
            while True:
                TextPrinter.clear()
                TextPrinter.guide("'/b' to go back.")
                TextPrinter.print('Overclaim', TextStyle.HEADER)
                TextPrinter.print('What town do you want to overclaim?', TextStyle.ARGUMENT)

                input = TextPrinter.input().strip()
                if input == '/b':
                    break
                
                response = Utilities.fetchAPI(f"https://api.earthmc.net/v3/aurora/towns?query={input}")

                if response != None:
                    response = response[0]
                else:
                    TextPrinter.print('Town not found.', TextStyle.WARNING)
                    time.sleep(.4)
                    continue

                TextPrinter.clear()
                TextPrinter.guide("'/b' to go back.")
                TextPrinter.print('Overclaim', TextStyle.HEADER)
                TextPrinter.print('Loading...', TextStyle.ARGUMENT)

                towns = getOverclaimTowns(response)

                if towns == None:
                    TextPrinter.print('Please try again later.', TextStyle.WARNING)
                    time.sleep(.4)
                    continue

                if towns == []:
                    TextPrinter.clear()
                    TextPrinter.guide("'/b' to go back.")
                    TextPrinter.print('Overclaim', TextStyle.HEADER)
                    TextPrinter.print('Empty', TextStyle.BOLD)
                    input = TextPrinter.input().strip()
                    continue

                page = 1
                enemies_per_page = 10
                while True:
                    TextPrinter.clear()
                    TextPrinter.guide("'/b' to go back.")
                    TextPrinter.guide(f"Type '{page + 1}' for the next page.")
                    TextPrinter.print('Overclaim', TextStyle.HEADER)

                    town_name = response['name']
                    TextPrinter.print(f"{town_name}'s Enemies:", TextStyle.BOLD)

                    for town in towns[(page - 1) * enemies_per_page:page * enemies_per_page]:
                        TextPrinter.print(f"- {town}")

                    input = TextPrinter.input().strip()
                    if input == '/b':
                        break
                    try:
                        input = int(input)

                    except Exception:
                        TextPrinter.print('Invalid page number.', TextStyle.WARNING)
                        time.sleep(.4)
                        continue

                    page = input

        else:
            TextPrinter.print('Option not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue




def settings():
    conn = Utilities.DBstart()
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Settings', TextStyle.HEADER)
        print()
        TextPrinter.print(f'- Generate executable (1)', TextStyle.ARGUMENT)

        if Utilities.getSetting(conn, 'collect_locations') != False:
            TextPrinter.print(f'- Collect player location data (2)', TextStyle.GREEN)
        else:
            TextPrinter.print(f'- Collect player location data (2)', TextStyle.RED)

        if Utilities.getSetting(conn, 'collect_trades') != False:
            TextPrinter.print(f'- Collect player trades data (3)', TextStyle.GREEN)
        else:
            TextPrinter.print(f'- Collect player trades data (3)', TextStyle.RED)

        if Utilities.getSetting(conn, 'cache_newday') != False:
            TextPrinter.print(f'- Use caching for /newday (4)', TextStyle.GREEN)
        else:
            TextPrinter.print(f'- Use caching for /newday (4)', TextStyle.RED)

        if Utilities.getSetting(conn, 'cache_ruins') != False:
            TextPrinter.print(f'- Use caching for /ruins (5)', TextStyle.GREEN)
        else:
            TextPrinter.print(f'- Use caching for /ruins (5)', TextStyle.RED)

        input = TextPrinter.input().strip()
        if input == '/b':
            return
        try:
            selected_setting = int(input)
        except Exception:
            TextPrinter.print('Input has to be a number.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        if selected_setting == 1:
            while True:
                TextPrinter.clear()
                TextPrinter.guide("'/b' to go back.")
                TextPrinter.print('Settings', TextStyle.HEADER)
                Generate.generateExe()
                input = TextPrinter.input().strip()
                if input == '/b':
                    break
                continue

        elif selected_setting == 2:
            setting = False
            if Utilities.getSetting(conn, 'collect_locations') != False:
                setting = True

            Utilities.setSetting(conn, 'collect_locations', not setting)
            continue

        elif selected_setting == 3:
            setting = False
            if Utilities.getSetting(conn, 'collect_trades') != False:
                setting = True

            Utilities.setSetting(conn, 'collect_trades', not setting)
            continue

        elif selected_setting == 4:
            setting = False
            if Utilities.getSetting(conn, 'cache_newday') != False:
                setting = True

            Utilities.setSetting(conn, 'cache_newday', not setting)
            continue

        elif selected_setting == 5:
            setting = False
            if Utilities.getSetting(conn, 'cache_ruins') != False:
                setting = True

            Utilities.setSetting(conn, 'cache_ruins', not setting)
            continue

        else:
            TextPrinter.print('Option not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue


def victims():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Victims', TextStyle.HEADER)
        TextPrinter.print('Loading...', TextStyle.ARGUMENT)

        victims = Victims.findVictims()
        
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Victims', TextStyle.HEADER)

        if victims == None:
            TextPrinter.print('Please try again later.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        if victims == []:
            TextPrinter.print('Empty', TextStyle.BOLD)
            input = TextPrinter.input().strip()
            if input == '/b':
                break
            continue

        header = f"{BOLD}Name{' ' * 18}X{' ' * 8}Z{' ' * 10}Timestamp{ENDC}"
        TextPrinter.print(header)

        for player in victims:
            name = player['name'].ljust(20)
            x = str(player['x']).ljust(8)
            y = str(player['z']).ljust(8)
            timestamp = Utilities.epochToDatetime(player['timestamp'] * 1000)
            row = f"{name}{x}{y}{timestamp}"
            TextPrinter.print(row)

        input = TextPrinter.input().strip()
        if input == '/b':
            break

def noPerm():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('No Perm Towns', TextStyle.HEADER)
        TextPrinter.print('Loading...', TextStyle.ARGUMENT)
        
        noperm_towns = getNoPerm()

        if noperm_towns == None:
            TextPrinter.print('Rate limited, try again in a minute.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        if noperm_towns == []:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.print('No Perm Towns', TextStyle.HEADER)
            TextPrinter.print('Empty', TextStyle.BOLD)
            input = TextPrinter.input().strip()
            if input == '/b':
                break
            continue

        noperm_towns = sorted(noperm_towns, key=lambda town: town['stats']['numTownBlocks'], reverse=True)
        page = 1
        towns_per_page = 10
        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.guide(f"Type '{page + 1}' for the next page.")
            TextPrinter.print('No Perm Towns', TextStyle.HEADER)
            
            header = f"{BOLD}Name{' ' * 17}Chunks{' ' * 10}Residents{ENDC}"
            TextPrinter.print(header)

            for town in noperm_towns[(page - 1) * towns_per_page:page * towns_per_page]:
                name = town['name'].ljust(20)
                num_town_blocks = town['stats']['numTownBlocks']
                max_town_blocks = town['stats']['maxTownBlocks']
                chunks = str(f'{num_town_blocks}/{max_town_blocks}').ljust(8)
                residents = str(town['stats']['numResidents'])
                row = f"{name}{chunks}{' ' * 12}{residents}"
                TextPrinter.print(row)

            input = TextPrinter.input().strip()
            if input == '/b':
                return
            try:
                input = int(input)

            except Exception:
                TextPrinter.print('Invalid page number.', TextStyle.WARNING)
                time.sleep(.4)
                continue

            page = input


def forSale():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('For Sale Towns', TextStyle.HEADER)
        TextPrinter.print('Loading...', TextStyle.ARGUMENT)
        
        for_sale_towns = getForSaleTowns()

        if for_sale_towns == None:
            TextPrinter.print('Rate limited, try again in a minute.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        if for_sale_towns == []:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.print('For Sale Towns', TextStyle.HEADER)
            TextPrinter.print('Empty', TextStyle.BOLD)
            input = TextPrinter.input().strip()
            if input == '/b':
                break
            continue

        page = 1
        towns_per_page = 10
        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.guide(f"Type '{page + 1}' for the next page.")
            TextPrinter.print('For Sale Towns', TextStyle.HEADER)
            
            header = f"{BOLD}Name{' ' * 17}Chunks{' ' * 10}Residents{' ' * 10}Price{ENDC}"
            TextPrinter.print(header)

            count = 20
            for town in for_sale_towns[(page - 1) * towns_per_page:page * towns_per_page]:
                if count == 0:
                    break
                count -= 1
                name = town['name'].ljust(20)
                num_town_blocks = town['stats']['numTownBlocks']
                max_town_blocks = town['stats']['maxTownBlocks']
                chunks = str(f'{num_town_blocks}/{max_town_blocks}').ljust(8)
                residents = str(town['stats']['numResidents'])
                price = str(int(town['stats']['forSalePrice']))
                row = f"{name}{chunks}{' ' * 12}{residents}{' ' * 10}{price}g"
                TextPrinter.print(row)

            input = TextPrinter.input().strip()
            if input == '/b':
                return
            try:
                input = int(input)

            except Exception:
                TextPrinter.print('Invalid page number.', TextStyle.WARNING)
                time.sleep(.4)
                continue

            page = input


def trades():
    conn = Utilities.DBstart()

    if Utilities.getSetting(conn, 'collect_trades') == False:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Trades', TextStyle.HEADER)
        TextPrinter.print('Trades tracking is turned off in settings.', TextStyle.WARNING)
        input = TextPrinter.input()
        return

    page = 1
    trades_per_page = 5
    while True:
        trades = Utilities.getAllTradePotentials(conn)
        trades = sorted(trades, key=lambda x: x['timestamp'], reverse=True)
        number_of_pages = Utilities.numberOfPages(trades, trades_per_page)

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.guide(f"Press enter to refresh.")
        TextPrinter.guide(f"Type '{page + 1}' for the next page.")
        TextPrinter.print(f'Trades ({page}/{number_of_pages})', TextStyle.HEADER)

        for trade in trades[(page - 1) * trades_per_page:page * trades_per_page]:
            name = trade['player_name']
            profit = trade['profit']
            potentials = json.loads(trade['potentials'])
            amount = trade['amount']
            potentials = Utilities.listToString(potentials)
            epoch = trade['timestamp']
            timestamp = Utilities.epochToDatetime(epoch * 1000)
            print()
            if profit == True:
                print(BOLD + f"- {name} gave {amount}g to one of these players: {potentials}" + ENDC + GRAY + f' [{timestamp}]' + ENDC)
            else:
                print(BOLD + f"- {name} received {amount}g from one of these players: {potentials}" + ENDC + GRAY + f' [{timestamp}]' + ENDC)

        input = TextPrinter.input().strip()
        if input == '/b':
            return
        
        if input == '':
            continue

        try:
            input = int(input)
        except Exception:
            TextPrinter.print('Invalid page number.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        page = input


def protect():
    conn = Utilities.DBstart()
    global protection_list
    while True:
        if Utilities.getSetting(conn, 'collect_locations') == False:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.print('Protect Players', TextStyle.HEADER)
            TextPrinter.print('Location tracking is turned off in settings.', TextStyle.WARNING)
            input = TextPrinter.input()
            return
        
        try:
            from plyer import notification # type: ignore
        except ImportError:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.print('Protect Players', TextStyle.HEADER)
            TextPrinter.print('Required library not installed, press enter to install.', TextStyle.WARNING)
            input = TextPrinter.input().strip()
            if input == '/b':
                return
            TextPrinter.print("Installing library 'Plyer'...", TextStyle.BLUE)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "plyer"])
            TextPrinter.print("Plyer has been installed.", TextStyle.GREEN)
            time.sleep(1)

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.guide('Divide players with commas.')
        TextPrinter.print('Protect Players', TextStyle.HEADER)

        input = TextPrinter.input().strip()
        if input == '/b':
            return

        result = ','.join(Utilities.queryToList(input))
        response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/players?query={result}')
        if response == None:
            TextPrinter.print('Player not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue
        
        players_string = ','.join(Utilities.queryToList(result))
        protection_list = Utilities.queryToList(input)

        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.guide("Playing in fullscreen may suppress notifications.")
            TextPrinter.print('Protect Players', TextStyle.HEADER)
            TextPrinter.print(f'Protecting: {players_string}', TextStyle.ARGUMENT)

            input = TextPrinter.input().strip()
            if input == '/b':
                protection_list = []
                break


def trustedIn():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Trusted in Towns', TextStyle.HEADER)
        TextPrinter.print('What is your username?', TextStyle.ARGUMENT)

        input = TextPrinter.input().strip()
        if input == '/b':
            return
        
        response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/players?query={input}')
        if response == None:
            TextPrinter.print('Player not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Trusted in Towns', TextStyle.HEADER)
        TextPrinter.print('Loading...', TextStyle.ARGUMENT)

        towns = getTrustedTowns(input)

        if towns == None:
            TextPrinter.print('Please try again later.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        if towns == []:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.print('Trusted in Towns', TextStyle.HEADER)
            TextPrinter.print('Empty', TextStyle.BOLD)
            input = TextPrinter.input().strip()
            continue
        
        page = 1
        items_per_page = 10
        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.guide(f"Type '{page + 1}' for the next page.")
            TextPrinter.print('Trusted in Towns', TextStyle.HEADER)
            print()

            for town in towns[(page - 1) * items_per_page:page * items_per_page]:
                TextPrinter.print(f'- {town}', TextStyle.ARGUMENT)
                
            input = TextPrinter.input().strip()
            if input == '/b':
                break
            try:
                input = int(input)

            except Exception:
                TextPrinter.print('Invalid page number.', TextStyle.WARNING)
                time.sleep(.4)
                continue

            page = input


def joinNation():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Join Nation', TextStyle.HEADER)
        TextPrinter.print('What town?', TextStyle.ARGUMENT)

        input = TextPrinter.input().strip()
        if input == '/b':
            return
        
        response = Utilities.fetchAPI(f'https://api.earthmc.net/v3/aurora/towns?query={input}')
        if response == None:
            TextPrinter.print('Town not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Join Nation', TextStyle.HEADER)
        TextPrinter.print('Loading...', TextStyle.ARGUMENT)

        nations = getJoinNations(response[0])  

        if nations == None:
            TextPrinter.print('Please try again later.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        if nations == []:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.print('Join Nation', TextStyle.HEADER)
            TextPrinter.print('Empty', TextStyle.BOLD)
            input = TextPrinter.input().strip()
            continue

        page = 1
        items_per_page = 10
        while True:
            TextPrinter.clear()
            TextPrinter.guide("'/b' to go back.")
            TextPrinter.guide(f"Type '{page + 1}' for the next page.")
            TextPrinter.print('Join Nation', TextStyle.HEADER)
            
            TextPrinter.print(f"Name{' ' * 17}Distance{' ' * 10}Bonus", TextStyle.BOLD)

            for nation in nations[(page - 1) * items_per_page:page * items_per_page]:
                name = nation['name'].ljust(20)
                distance = int(nation['distance'])
                bonus = nation['nation_bonus']
                
                TextPrinter.print(f"{name}{distance}{' ' * 15}{bonus}")

            input = TextPrinter.input().strip()
            if input == '/b':
                break
            try:
                input = int(input)

            except Exception:
                TextPrinter.print('Invalid page number.', TextStyle.WARNING)
                time.sleep(.4)
                continue

            page = input



# Available commands
COMMANDS = {
    'VP': 'voteparty()',
    'RES': 'getPlayer()', 
    'NATION': 'getNation()',
    'TOWN': 'getTown()',
    'FIND': 'findPlayer()',
    'PIRATE': 'pirate()',
    'NEWDAY': 'newday()',
    'RUINS': 'ruins()',
    'GOTO': 'goto()',
    'VICTIMS': 'victims()',
    'OVERCLAIM': 'overclaim()',
    'ONLINE': 'online()',
    'SETTINGS': 'settings()',
    'FALLINGIN': 'fallingIn()',
    'NOPERM': 'noPerm()',
    'FORSALE': 'forSale()',
    'TRADES': 'trades()',
    'PROTECT': 'protect()',
    'TRUSTEDIN': 'trustedIn()',
    'JOINNATION': 'joinNation()'
}



def tasks():
    global protection_list
    epoch_last_player = int(time.time())
    epoch_last_trade = int(time.time())
    conn = Utilities.DBstart()
    while True:
        epoch_now = int(time.time())
        if Utilities.getSetting(conn, 'collect_locations') != False:
            if epoch_now - epoch_last_player >= 3:
                epoch_last_player = epoch_now
                try:
                    response = Utilities.fetchAPI('https://map.earthmc.net/tiles/players.json')
                    epoch = int(time.time())
                    for item in response['players']:
                        Utilities.insertPlayerData(conn, item['name'].lower(), epoch, item['x'], item['z'])
                except Exception:
                    continue
                for player in protection_list:
                    protectPlayerCheck(conn, player)
                    
        if Utilities.getSetting(conn, 'collect_trades') != False:
            if epoch_now - epoch_last_trade >= 10:
                epoch_last_trade = epoch_now
                getTrades(conn)

        time.sleep(0.2)


# Main loop
def main():
    while True:
        TextPrinter.clear()

        TextPrinter.print(f"""
 ██████╗ ██████╗ ███████╗███╗   ██╗███████╗██████╗ ██╗   ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██╔══██╗╚██╗ ██╔╝
██║   ██║██████╔╝█████╗  ██╔██╗ ██║███████╗██████╔╝ ╚████╔╝ 
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║╚════██║██╔═══╝   ╚██╔╝  
╚██████╔╝██║     ███████╗██║ ╚████║███████║██║        ██║   
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝        ╚═╝                                                       
By vncet                                            V{VERSION} 
        """, TextStyle.GRAY)

        TextPrinter.print('Commands', TextStyle.HEADER)

        commands = [
            '/vp            Votes remaining till voteparty',
            '/res           Get player information',
            '/nation        Get nation information',
            '/town          Get town information',
            '/find          Find player location',
            '/pirate        Find towns you can steal',
            '/newday        Falling and ruined towns next newday',
            '/ruins         Find ruined towns to loot',
            '/goto          Find the best route to a town/nation',
            '/victims       Find players in the wilderness',
            '/overclaim     Towns that you can steal land from',
            '/online        Online players in town or nation',
            '/fallingin     Towns falling in nation',
            '/noperm        Towns with build permissions off',
            '/forsale       For sale towns sorted from low to high',
            "/trades        View player's private trades",
            '/protect       Get notified when player is approaching',
            '/trustedin     Lists towns that have player as trusted',
            '/joinnation    Best nations to join as town',
            '/settings      OpenSpy settings'
        ]

        half = (len(commands) + 1) // 2
        commands1 = commands[:half]
        commands2 = commands[half:]

        max_len_cmd1 = max(len(cmd) for cmd in commands1) + 4

        for i in range(half):
            cmd1 = commands1[i]
            cmd2 = commands2[i] if i < len(commands2) else ''
            print(f'- {cmd1:<{max_len_cmd1}} - {cmd2}')

        command = TextPrinter.input().strip()
        if command.startswith('/'):
            command = command[1:]

        if command != '' and command != 'b':
            command_list = []
            for key in COMMANDS:
                command_list.append(key)

            key = Utilities.findClosestCommand(command.upper(), command_list)
            exec(COMMANDS[key])


if __name__ == "__main__":
    tasks_thread = threading.Thread(target=tasks)
    tasks_thread.daemon = True
    tasks_thread.start()
    
    main()