from libs.utilities import Utilities
from concurrent.futures import ThreadPoolExecutor


@staticmethod
def getOverclaim(from_nation):
    nation_list = [x['name'] for x in from_nation['enemies']]

    try:
        completed_nation_list = []
        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = []
            for i in range(0, len(nation_list), 100):
                sublist = nation_list[i:i + 100]
                futures.append(executor.submit(Utilities.fetch_nation_chunk, sublist))
            for index, future in enumerate(futures):
                completed_nation_list.extend(future.result())
        
        town_list = []
        for nation in completed_nation_list:
            town_list_temp = [x['name'] for x in nation['towns']]
            for town in town_list_temp:
                town_list.append(town)

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

    return overclaimable_towns