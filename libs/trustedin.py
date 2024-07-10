from concurrent.futures import ThreadPoolExecutor
from libs.utilities import Utilities


@staticmethod
def getTrustedTowns(player_name):
    all_towns = Utilities.fetchAPI('https://api.earthmc.net/v3/aurora/towns')

    all_towns = [town['name'] for town in all_towns]

    try:
        completed_town_list = []
        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = []
            for i in range(0, len(all_towns), 100):
                sublist = all_towns[i:i + 100]
                futures.append(executor.submit(Utilities.fetch_town_chunk, sublist))        
            for index, future in enumerate(futures):
                completed_town_list.extend(future.result())
    except Exception:
        return None
    
    trusted_towns = []
    for town in completed_town_list:
        if town['trusted']:
            trusted_players = [x['name'] for x in town['trusted']]
            if player_name in trusted_players:
                trusted_towns.append(town['name'])

    return trusted_towns