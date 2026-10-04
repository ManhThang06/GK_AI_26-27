import os
from collections import deque
from core.map_parser import MapParser
from core.sokoban import SokobanProblem, ucs
from core.heuristic import Heuristic

def collect_reachable_states(problem, target_count=30, skip_step=3):
    visited = set([problem.initial_state])
    queue = deque([problem.initial_state])
    states = []
    counter = 0

    while queue and len(states) < target_count:
        state = queue.popleft()
        
        if counter % skip_step == 0:
            states.append(state)
        counter += 1
        
        for action, next_state, _ in problem.successors(state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append(next_state)
                
    return states

def get_optimal_cost_h_star(problem, state):
    original_initial = problem.initial_state
    problem.initial_state = state
    
    path, cost, _ = ucs(problem)
    
    problem.initial_state = original_initial
    return cost

def verify_heuristic_properties(map_folder):
    if not os.path.exists(map_folder):
        print(f"Không tìm thấy thư mục: {map_folder}")
        return

    map_files = sorted([f for f in os.listdir(map_folder) if f.endswith('.txt')])

    for map_file in map_files:
        map_path = os.path.join(map_folder, map_file)
        parser = MapParser(map_path)
        problem = SokobanProblem(parser)
        heuristic = Heuristic(parser.board_matrix, parser.goals)

        print(f"\n[+] Kiểm tra bản đồ: {map_file}")
        
        sample_states = collect_reachable_states(problem, target_count=30, skip_step=3)
        print(f"    - Đã thu thập {len(sample_states)} trạng thái để thực nghiệm.")

        consistency_violations = 0
        total_transitions = 0
        
        for state in sample_states:
            h_n = heuristic.evaluate(state.boxes)
            if h_n == float("inf"):
                continue  
                
            for action, next_state, cost in problem.successors(state):
                h_next = heuristic.evaluate(next_state.boxes)
                if h_next == float("inf"):
                    continue
                    
                total_transitions += 1
                if h_n > cost + h_next:
                    consistency_violations += 1

        admissibility_violations = 0
        valid_h_star_count = 0

        for state in sample_states:
            h_n = heuristic.evaluate(state.boxes)
            if h_n == float("inf"):
                continue

            h_star = get_optimal_cost_h_star(problem, state)
            if h_star != float("inf"):
                valid_h_star_count += 1
                if h_n > h_star:
                    admissibility_violations += 1

        is_admissible = (admissibility_violations == 0)
        is_consistent = (consistency_violations == 0)

        print(f"    - Kết quả Consistency : {'THỎA MÃN' if is_consistent else 'VI PHẠM'}")
        print(f"      (Số chuyển vị vi phạm: {consistency_violations}/{total_transitions})")
        
        print(f"    - Kết quả Admissibility: {'THỎA MÃN' if is_admissible else 'VI PHẠM'}")
        print(f"      (Số trạng thái vi phạm: {admissibility_violations}/{valid_h_star_count})")

if __name__ == "__main__":
    verify_heuristic_properties("map1Agent")