import chessdotcom as cdc
from typing import List, Dict
import datetime
import pgn.pgn as pgn
import re
import numpy as np
from multiprocessing import Pool

class Loader:

    def __init__(self, player_name: str, nproc: int = 8):
        self.player_name: str = player_name
        self.all_games: List[pgn.PGNGame] = []
        self.move_lengths: np.ndarray = np.array([])
        self.nproc: int = nproc


    def get_games(self, year: int, month: int) -> List[pgn.PGNGame]:
        print(year, month)
        try:
            games_pgn = cdc.get_player_games_by_month_pgn(self.player_name, year, month).json
            return pgn.loads(games_pgn["pgn"]["pgn"])
        except Exception as e:
            print(e)
            return []


    def get_all_games(self) -> List[pgn.PGNGame]:
        if len(self.all_games) != 0:
            return self.all_games
        info = cdc.get_player_profile(self.player_name).json
        start_date = datetime.date.fromtimestamp(info["player"]["joined"])
        current_date = datetime.date.today()
        requests = []
        for year in range(start_date.year, current_date.year+1):
            for month in range(1,12):
                requests.append( (year, month) )
        
        with Pool(self.nproc) as p:
            r = p.starmap(self.get_games, requests)
        self.all_games = [game for games in r for game in games] 
        return self.all_games 


    def get_move_quantile(self, timecontrol: str = "600", q: float = 0.5) -> int:
        if len(self.move_lengths) != 0:
            return np.quantile(self.move_lengths, q)

        def extract(s: str) -> int:
            m = re.search(r'.*?(?P<hour>\d+):(?P<min>\d+):(?P<sec>\d+)', s)
            return int(m.group("hour")) * 60 * 60 + int(m.group("min")) * 60 + int(m.group("sec"))

        lengths = []
        for game in self.all_games:
            start = 1 if game.white == self.player_name else 3
            if game.timecontrol != timecontrol:
                continue
            move_stamps = list(map( extract , game.moves[start:-1:4]))
            lengths.extend([move_stamps[i-1] - move_stamps[i] for i in range(1,len(move_stamps))])
        self.move_lengths = np.array(sorted(lengths))
        return np.quantile(self.move_lengths, q)



    
    def get_slowest_games(self, timecontrol: str = "600") -> List[pgn.PGNGame]:
        return



if __name__ == "__main__":
    l = Loader("TimSPoulsen")
    all_games = l.get_all_games()
    l.get_move_quantile()
    print(len(all_games))