from sokoban_state import State

class Trasnitionmodel:
    def __init__(self, map_data):
        self.walls = map_data.walls
        self.goals = map_data.goals
        self.initial_state = State(map_data.initial_agent, map_data.initial_boxes)
        
        # Actions = {N, E, W, S}
        self.actions = {
            'N_Len': (0, -1),
            'S_Xuong': (0, 1),
            'E_Phai':  (1, 0),
            'W_Trai':  (-1, 0)
        }

    def goal_test(self, state):
        # Mọi box phải ở vị trí D. Do self.goals cũng là một set tọa độ, 
        # ta chỉ cần so sánh bằng.
        return state.boxes == self.goals

    def get_successors(self, state):
        """
        Transition-model: Kiểm tra tường, đẩy box hợp lệ[cite: 11].
        """
        successors = []
        
        for action_name, (d_col, d_row) in self.actions.items():
            new_agent_pos = (state.agent_pos[0] + d_col, state.agent_pos[1] + d_row)
            # Trường hợp 1: Agent đi vào tường -> Không hợp lệ
            if new_agent_pos in self.walls:
                continue
            # Trường hợp 2: Agent đẩy vào một box
            if new_agent_pos in state.boxes:
                new_box_pos = (new_agent_pos[0] + d_col, new_agent_pos[1] + d_row)
                
                # Nếu đằng sau box là tường HOẶC là một box khác -> Không đẩy được
                if new_box_pos in self.walls or new_box_pos in state.boxes:
                    continue
                # Di chuyển agent và cập nhật vị trí box đó
                new_boxes = set(state.boxes)
                new_boxes.remove(new_agent_pos)
                new_boxes.add(new_box_pos)
                
                new_state = State(new_agent_pos, new_boxes)
                successors.append((action_name, new_state, 1)) # Path-cost = 1/bước[cite: 11]              
            # Trường hợp 3: Agent đi vào ô trống hoặc ô đích (D)
            else:
                new_state = State(new_agent_pos, state.boxes)
                successors.append((action_name, new_state, 1)) # Path-cost = 1/bước[cite: 11]

        return successors