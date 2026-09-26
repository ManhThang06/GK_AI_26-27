from sokoban_map import MapParser
from sokoban_transitionmodel import Trasnitionmodel
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