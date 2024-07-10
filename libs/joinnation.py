import math
from concurrent.futures import ThreadPoolExecutor
from libs.utilities import Utilities


def getNationBonus(town, completed_nation_list):
    nation_data = None
    for nation in completed_nation_list:
        if nation['capital']['name'] == town['name']:
            nation_data = nation
    if nation_data:
        num_residents = int(nation_data['stats']['numResidents'])
        if num_residents >= 20 and num_residents < 40:
            nation_bonus = 10
        elif num_residents >= 40 and num_residents < 60:
            nation_bonus = 30
        elif num_residents >= 60 and num_residents < 120:
            nation_bonus = 50
        elif num_residents >= 200:
            nation_bonus = 100
        else:
            nation_bonus = 0
        return nation_bonus
        


@staticmethod
def getJoinNations(our_town):
    all_nations = Utilities.fetchAPI('https://api.earthmc.net/v3/aurora/nations')
    nation_list = [x['name'] for x in all_nations]

    try:
        completed_nation_list = []
        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = []
            for i in range(0, len(nation_list), 100):
                sublist = nation_list[i:i + 100]
                futures.append(executor.submit(Utilities.fetch_nation_chunk, sublist))
            for index, future in enumerate(futures):
                completed_nation_list.extend(future.result())

        capitals = [nation['capital']['name'] for nation in completed_nation_list if nation['status']['isOpen']]

        completed_town_list = []
        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = []
            for i in range(0, len(capitals), 100):
                sublist = capitals[i:i + 100]
                futures.append(executor.submit(Utilities.fetch_town_chunk, sublist))        
            for index, future in enumerate(futures):
                completed_town_list.extend(future.result())

    except Exception:
        return None
    
    print(our_town)
    x = int(our_town['coordinates']['homeBlock'][0]) * 16
    z = int (our_town['coordinates']['homeBlock'][1]) * 16

    join_nation_list = []
    for town in completed_town_list:
        homeblock_x = int(town['coordinates']['homeBlock'][0]) * 16
        homeblock_z = int (town['coordinates']['homeBlock'][1]) * 16
        distance = math.sqrt((homeblock_x - x) ** 2 + (homeblock_z - z) ** 2)
        if distance < 3000:
            nation_bonus = getNationBonus(town, completed_nation_list)
            join_nation_list.append({
                'name': town['nation']['name'],
                'nation_bonus': nation_bonus,
                'distance': distance
            })

    join_nation_list = sorted(join_nation_list, key=lambda k: k['nation_bonus'], reverse=True)
    
    return join_nation_list