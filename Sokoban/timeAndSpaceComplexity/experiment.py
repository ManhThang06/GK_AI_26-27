import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import os
import time
import tracemalloc

from core.map_parser import MapParser 
from core.sokoban import SokobanProblem, ucs, astar
from core.heuristic import Heuristic 

def run_experiment(map_folder):
    results = []
    
    if not os.path.exists(map_folder):
        print(f"Không tìm thấy thư mục: {map_folder}")
        return
        
    map_files = sorted([f for f in os.listdir(map_folder) if f.endswith('.txt')])
    
    if not map_files:
        print(f"Không có file .txt nào trong thư mục {map_folder}")
        return

    print(f"Bắt đầu thực nghiệm trên {len(map_files)} bản đồ...\n")

    for map_file in map_files:
        map_path = os.path.join(map_folder, map_file)

        try:
            parser_ucs = MapParser(map_path)
            problem_ucs = SokobanProblem(parser_ucs)
            
            tracemalloc.start()  
            start_time = time.perf_counter()
            
            path_ucs, cost_ucs, exp_ucs = ucs(problem_ucs)
            
            end_time = time.perf_counter()
            _, peak_ucs = tracemalloc.get_traced_memory() 
            tracemalloc.stop()
            
            time_ucs = end_time - start_time
            peak_ram_ucs_mb = peak_ucs / (1024 * 1024)
            
            results.append({
                "Map": map_file,
                "Algo": "UCS",
                "Cost": cost_ucs,
                "Expanded": exp_ucs,
                "Time (s)": time_ucs,
                "Peak RAM (MB)": peak_ram_ucs_mb
            })
        except Exception as e:
            print(f"[Lỗi] UCS trên {map_file}: {e}")

        try:
            parser_astar = MapParser(map_path)
            problem_astar = SokobanProblem(parser_astar)
            
            heuristic = Heuristic(parser_astar.board_matrix, parser_astar.goals) 
            
            tracemalloc.start()
            start_time = time.perf_counter()
            
            path_astar, cost_astar, exp_astar = astar(problem_astar, heuristic)
            
            end_time = time.perf_counter()
            _, peak_astar = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            time_astar = end_time - start_time
            peak_ram_astar_mb = peak_astar / (1024 * 1024)
            
            results.append({
                "Map": map_file,
                "Algo": "A*",
                "Cost": cost_astar,
                "Expanded": exp_astar,
                "Time (s)": time_astar,
                "Peak RAM (MB)": peak_ram_astar_mb
            })
        except Exception as e:
            print(f"[Lỗi] A* trên {map_file}: {e}")

    print("=" * 90)
    print(f"{'Map Name':<20} | {'Algorithm':<10} | {'Cost':<6} | {'Nodes Exp.':<12} | {'Time (s)':<12} | {'Peak RAM (MB)':<12}")
    print("-" * 90)
    
    for r in results:
        cost_str = str(r['Cost']) if r['Cost'] != float('inf') else 'inf'
        print(f"{r['Map']:<20} | {r['Algo']:<10} | {cost_str:<6} | {r['Expanded']:<12} | {r['Time (s)']:<12.5f} | {r['Peak RAM (MB)']:<12.5f}")
    
    print("=" * 90)

if __name__ == "__main__":
    run_experiment("map1Agent")