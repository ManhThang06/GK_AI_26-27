import os
import time
import tracemalloc

# Import các thành phần từ package core
# (Lưu ý: Bạn hãy kiểm tra lại tên class bên trong map_parser.py và heuristic.py để khớp chính xác)
from core.map_parser import MapParser 
from core.sokoban import SokobanProblem, ucs, astar
from core.heuristic import Heuristic 

def run_experiment(map_folder):
    results = []
    
    # Lấy danh sách các file bản đồ trong thư mục map1Agent
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
        
        # ---------------------------------------------------
        # 1. Chạy thuật toán UCS
        # ---------------------------------------------------
        try:
            parser_ucs = MapParser(map_path)
            problem_ucs = SokobanProblem(parser_ucs)
            
            tracemalloc.start()  # Bắt đầu theo dõi bộ nhớ
            start_time = time.perf_counter()  # Bắt đầu đo thời gian
            
            path_ucs, cost_ucs, exp_ucs = ucs(problem_ucs)
            
            end_time = time.perf_counter()
            _, peak_ucs = tracemalloc.get_traced_memory() # Lấy lượng RAM đỉnh điểm
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

        # ---------------------------------------------------
        # 2. Chạy thuật toán A*
        # ---------------------------------------------------
        try:
            parser_astar = MapParser(map_path)
            problem_astar = SokobanProblem(parser_astar)
            
            # Khởi tạo heuristic (Truyền parser hoặc problem tùy thuộc vào cách bạn code Heuristic)
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

    # ---------------------------------------------------
    # 3. In kết quả ra màn hình dạng Bảng
    # ---------------------------------------------------
    print("=" * 90)
    print(f"{'Map Name':<20} | {'Algorithm':<10} | {'Cost':<6} | {'Nodes Exp.':<12} | {'Time (s)':<12} | {'Peak RAM (MB)':<12}")
    print("-" * 90)
    
    for r in results:
        cost_str = str(r['Cost']) if r['Cost'] != float('inf') else 'inf'
        print(f"{r['Map']:<20} | {r['Algo']:<10} | {cost_str:<6} | {r['Expanded']:<12} | {r['Time (s)']:<12.5f} | {r['Peak RAM (MB)']:<12.5f}")
    
    print("=" * 90)

if __name__ == "__main__":
    # Chạy thực nghiệm với thư mục map1Agent
    run_experiment("map1Agent")