from libs.utilities import Utilities
from concurrent.futures import ThreadPoolExecutor


@staticmethod
def getOverclaim():
    all_towns = Utilities.fetchAPI('https://api.earthmc.net/v3/aurora/towns')
    town_list = [x['name'] for x in all_towns]
    
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

    overclaimable_towns = [town for town in completed_town_list if town and town['status']['isOverClaimed'] and not town['status']['hasOverclaimShield']]
    overclaimable_towns = sorted(overclaimable_towns, key=lambda town: town['stats']['numResidents'], reverse=True)
    
    final_return = []
    count = 20
    for town in overclaimable_towns:
        if count == 0:
            break
        final_return.append(town)
        count -= 1

    return final_return