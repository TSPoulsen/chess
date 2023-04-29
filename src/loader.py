import chessdotcom as cdc
from typing import List, Dict
import datetime
import pgn.pgn as pgn
import asyncio
from multiprocessing import Pool

def __get_games(player_name: str, year: int, month: int) -> List[pgn.PGNGame]:
    print(year, month)
    try:
        games_pgn = cdc.get_player_games_by_month_pgn(player_name, year, month).json
        return pgn.loads(games_pgn["pgn"]["pgn"])
    except Exception as e:
        print(e)
        return []


def get_all_games(player_name: str) -> List[pgn.PGNGame]:
    info = cdc.get_player_profile(player_name).json
    start_date = datetime.date.fromtimestamp(info["player"]["joined"])
    current_date = datetime.date.today()
    requests = []
    for year in range(start_date.year, current_date.year+1):
        for month in range(1,12):
            requests.append((player_name, year, month))
    
    print(len(requests))
    with Pool(8) as p:
        r = p.starmap(__get_games, requests)
    r = [game for games in r for game in games] 
    print(len(r))
    return r



if __name__ == "__main__":
    all_games = get_all_games("MagnusCarlsen")
    print(len(all_games))