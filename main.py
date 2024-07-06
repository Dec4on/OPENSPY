import threading
import time
from libs.printer import TextPrinter, TextStyle 
from libs.utilities import Utilities
from libs.pirate import Pirate
from libs.newday import Newday
from libs.ruins import Ruins
from libs.victims import Victims
from libs.generateExe import Generate
from libs.overclaim import getOverclaim
from libs.fallingin import getTownsFallingIn
from libs.noperm import getNoPerm
from libs.forsale import getForSaleTowns
import math
from concurrent.futures import ThreadPoolExecutor

# Global variables
VERSION = 1.2

BOLD = '\033[1m'
ENDC = '\033[0m'

def findPlayer():
    conn = Utilities.DBstart()
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
                print(BOLD + 'Diplomat: ' + ENDC + Utilities.listToString(formatted_list))

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
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Newday', TextStyle.HEADER)
        TextPrinter.print('This can take a while...', TextStyle.ARGUMENT)

        ruined_towns, fallen_towns = Newday.findNewdayTowns()

        if not ruined_towns or not fallen_towns:
            TextPrinter.print('Rate limited, try again in a minute.', TextStyle.WARNING)
            input = TextPrinter.input().strip()
            if input == '/b':
                return
            continue

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
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Ruins', TextStyle.HEADER)
        TextPrinter.print('This can take a while...', TextStyle.ARGUMENT)

        ruined_towns = Ruins.findRuins()

        if not ruined_towns:
            TextPrinter.print('Rate limited, try again in a minute.', TextStyle.WARNING)
            input = TextPrinter.input().strip()
            if input == '/b':
                return
            continue
        
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Ruins', TextStyle.HEADER)

        for town in ruined_towns:
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


def overclaim():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Overclaimable Towns', TextStyle.HEADER)
        TextPrinter.print('What nation do you want to overclaim from?', TextStyle.ARGUMENT)

        input = TextPrinter.input().strip()
        if input == '/b':
            return
        
        response = Utilities.fetchAPI(f"https://api.earthmc.net/v3/aurora/nations?query={input}")

        if response != None:
            response = response[0]
        else:
            TextPrinter.print('Nation not found.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Overclaimable Towns', TextStyle.HEADER)
        TextPrinter.print('This can take a while...', TextStyle.ARGUMENT)

        towns = getOverclaim(response)

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Overclaimable Towns', TextStyle.HEADER)

        if towns == None:
            TextPrinter.print('Please try again later.', TextStyle.WARNING)
            time.sleep(.4)
            continue

        if towns == []:
            TextPrinter.print('Empty', TextStyle.BOLD)
            input = TextPrinter.input().strip()
            if input == '/b':
                break
            continue

        header = f"{BOLD}Name{' ' * 17}Chunks{' ' * 10}Residents{ENDC}"
        TextPrinter.print(header)

        for town in towns:
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


def settings():
    while True:
        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('Settings', TextStyle.HEADER)
        print()
        TextPrinter.print(f'- Generate executable (1)', TextStyle.ARGUMENT)
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
        else:
            TextPrinter.print('No setting found with number.', TextStyle.WARNING)
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

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('No Perm Towns', TextStyle.HEADER)

        if noperm_towns == []:
            TextPrinter.print('Empty', TextStyle.BOLD)
            input = TextPrinter.input().strip()
            if input == '/b':
                break
            continue

        noperm_towns = sorted(noperm_towns, key=lambda town: town['stats']['numTownBlocks'], reverse=True)

        header = f"{BOLD}Name{' ' * 17}Chunks{' ' * 10}Residents{ENDC}"
        TextPrinter.print(header)

        for town in noperm_towns:
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

        TextPrinter.clear()
        TextPrinter.guide("'/b' to go back.")
        TextPrinter.print('For Sale Towns', TextStyle.HEADER)

        if for_sale_towns == []:
            TextPrinter.print('Empty', TextStyle.BOLD)
            input = TextPrinter.input().strip()
            if input == '/b':
                break
            continue

        header = f"{BOLD}Name{' ' * 17}Chunks{' ' * 10}Residents{' ' * 10}Price{ENDC}"
        TextPrinter.print(header)

        count = 20
        for town in for_sale_towns:
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
            break    


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
    'FORSALE': 'forSale()'
}


def tasks():
    conn = Utilities.DBstart()
    while True:
        try:
            response = Utilities.fetchAPI('https://map.earthmc.net/tiles/players.json')
            epoch = int(time.time())
            for item in response['players']:
                Utilities.insertPlayerData(conn, item['name'].lower(), epoch, item['x'], item['z'])
            time.sleep(3)
        except Exception:
            time.sleep(3)


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