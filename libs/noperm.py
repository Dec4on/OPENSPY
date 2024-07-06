from concurrent.futures import ThreadPoolExecutor
from libs.utilities import Utilities


def getNoPerm():
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

        perm_on_towns = [town for town in completed_town_list if town['perms']['build'] == [True, True, True, True]]
        return perm_on_towns
    
    except Exception:
        return None