from sokoban_map import MapParser
from sokoban_transitionmodel import Trasnitionmodel
from two_agent_problem import TwoAgentProblem
if __name__ == "__main__":
    # 1. Nạp file bản đồ example_map.txt vào MapParser
    map_data = MapParser('example_map.txt')
    print("Check map")
    print(f"Vi tri Agent ban dau: {map_data.initial_agent}")
    print(f"Toa do cac Box: {map_data.initial_boxes}")
    print(f"Toa do cac Dich (D): {map_data.goals}")
    # 2. Đưa dữ liệu map vào Động cơ luật chơi (Problem)
    problem = Trasnitionmodel(map_data)
    # 3. Lấy thử các hướng đi hợp lệ từ trạng thái xuất phát
    successors = problem.get_successors(problem.initial_state)
    print("\n Check trasnitionmodel")
    print(f"Tu vi tri ban dau, Agent co {len(successors)} hanh dong hop le:")
    for action, next_state, cost in successors:
        print(f" - Neu di {action} -> Vi tri Agent moi: {next_state.agent_pos}")
    print("\n=== TEST TUẦN 2: 2 TÁC TỬ ĐỒNG THỜI ===")
    initial_a = map_data.initial_agent
    initial_b = (initial_a[1], initial_a[0] + 1) # Tạm xếp B đứng ngay cạnh A
    
    # Khởi tạo engine 2 tác tử với giới hạn 50 bước
    problem_2 = TwoAgentProblem(map_data, initial_a, initial_b, n_steps=50)
    
    print(f"Trạng thái ban đầu - Agent A: {problem_2.initial_state.agent_a_pos}, Agent B: {problem_2.initial_state.agent_b_pos}")
    
    # Thử nghiệm hành động đồng thời
    action_a = 'East'
    action_b = 'Wait'
    
    next_state_2 = problem_2.transition_model(problem_2.initial_state, action_a, action_b)
    print(f"Sau khi A đi {action_a}, B đi {action_b}:")
    print(f" -> Agent A mới: {next_state_2.agent_a_pos}, Agent B mới: {next_state_2.agent_b_pos}")
