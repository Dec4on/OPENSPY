from concurrent.futures import ThreadPoolExecutor
from libs.utilities import Utilities


def getForSaleTowns():
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

        town_list = [town for town in completed_town_list if town['stats']['forSalePrice']]

        sorted_town_list = sorted(town_list, key=lambda town: town['stats']['forSalePrice'], reverse=False)

        return sorted_town_list
    
    except Exception:
        return None