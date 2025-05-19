import streamlit as st
import numpy as np
import random

def initialize_grid():
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    grid = np.array(numbers).reshape(3, 3)
    return grid

def hide_numbers(grid, max_visible=4):
    while True:
        hidden_mask = np.ones_like(grid, dtype=bool)
        positions = list(range(grid.size))
        random.shuffle(positions)
        visible_count = 0
        for pos in positions:
            if visible_count < max_visible:
                row, col = pos // 3, pos % 3
                hidden_mask[row, col] = False
                visible_count += 1
            else:
                break

        valid_mask = True
        for i in range(3):
            if np.sum(~hidden_mask[i, :]) == 3 or np.sum(~hidden_mask[:, i]) == 3: 
                valid_mask = False
                break
        if valid_mask:
            return hidden_mask

def main():
    st.set_page_config(page_title="숫자 채우기 게임", layout="wide")
    st.title("🔢 숫자 채우기 게임")

    st.markdown("""
        <style>
        /* Default style for puzzle grid buttons */
        .stButton>button {
            width: 100px;
            height: 100px;
            font-size: 96px;
            margin: 0px;  /* MODIFIED: Set to 0px to minimize gap */
            padding: 0px; /* Ensure no internal padding affects spacing */
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
            overflow: hidden;
            border-width: 2px !important; /* Kept existing border */
            box-sizing: border-box; /* ADDED: Ensures width/height include border and padding */
        }
        .sum-cell {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100px;
            height: 100px;
            font-size: 22px;
            font-weight: bold;
            padding: 8px;
            box-sizing: border-box; /* Already border-box */
            border: 1px solid #ccc;
            margin: 0px; /* Ensure sum cells also have no margin if they are part of tight layout */
        }
        /* Specific style for keypad buttons */
        .keypad-container .stButton>button {
            width: 50px;
            height: 50px;
            font-size: 16px;
            margin: 1px; /* Keypad button margin can remain as is, or set to 0 if desired */
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
            box-sizing: border-box; /* Good practice for keypad buttons too */
        }
        
        /* For reducing gap between columns in the puzzle area */
        .puzzle-area .stHorizontalBlock {
            gap: 0px !important; /* Streamlit column gap set to 0 */
        }
        </style>
    """, unsafe_allow_html=True)

    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden_mask = hide_numbers(st.session_state.grid, max_visible=4)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid, dtype=int)
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None

    left_col, right_col = st.columns([2, 1]) 

    with left_col:
        st.markdown("### 퍼즐")
        st.markdown('<div class="puzzle-area">', unsafe_allow_html=True)

        for i in range(3): 
            cols = st.columns(4) 
            for j in range(3): 
                with cols[j]:
                    is_hidden = st.session_state.hidden_mask[i, j]
                    actual_val = st.session_state.grid[i, j]
                    user_val = st.session_state.user_grid[i, j]

                    if is_hidden:
                        display_val = str(user_val) if user_val != 0 else " "
                        if st.session_state.selected_cell == (i, j):
                            # MODIFIED: Disabled this button as it's an indicator
                            st.button(f"[{display_val}]", key=f"selected_{i}_{j}_indicator", help="선택된 셀", disabled=True)
                        else:
                            if st.button(display_val, key=f"hidden_{i}_{j}"):
                                st.session_state.selected_cell = (i, j)
                                st.rerun()
                                return 
                    else: 
                        st.button(str(actual_val), key=f"visible_{i}_{j}", disabled=True)
            
            with cols[3]: 
                st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[i, :])}</div>', unsafe_allow_html=True)

        # This explicit spacer creates a 10px vertical gap. Remove or set to 0 if sums should also touch grid.
        st.markdown('<div style="margin-top: 0px;"></div>', unsafe_allow_html=True) # MODIFIED for tighter packing

        sum_cols_display = st.columns(4) 
        for j in range(3):
            with sum_cols_display[j]:
                st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[:, j])}</div>', unsafe_allow_html=True)
        with sum_cols_display[3]: 
            st.markdown('<div class="sum-cell" style="visibility: hidden;"></div>', unsafe_allow_html=True) # Placeholder for alignment

        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown("### 숫자 입력")
        st.markdown('<div class="keypad-container">', unsafe_allow_html=True)
        
        keypad_layout_rows = [st.columns(3) for _ in range(3)]
        current_num = 1
        for row_of_cols in keypad_layout_rows:
            for col_object in row_of_cols:
                with col_object:
                    is_disabled = st.session_state.selected_cell is None
                    if st.button(str(current_num), key=f"keypad_{current_num}", disabled=is_disabled):
                        if not is_disabled:
                            r_selected, c_selected = st.session_state.selected_cell
                            st.session_state.user_grid[r_selected, c_selected] = current_num
                            st.session_state.selected_cell = None
                            st.rerun()
                            return
                current_num += 1
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    col1_action, col2_action = st.columns(2)
    with col1_action:
        if st.button("정답 확인", use_container_width=True):
            num_incorrectly_filled_hidden_cells = 0
            num_empty_hidden_cells = 0
            any_hidden_cell_exists = False

            for r_idx in range(3):
                for c_idx in range(3):
                    if st.session_state.hidden_mask[r_idx, c_idx]: 
                        any_hidden_cell_exists = True
                        user_value = st.session_state.user_grid[r_idx, c_idx]
                        actual_value = st.session_state.grid[r_idx, c_idx]

                        if user_value != 0: 
                            if user_value != actual_value:
                                num_incorrectly_filled_hidden_cells += 1
                        else: 
                            num_empty_hidden_cells += 1
            
            if not any_hidden_cell_exists:
                 st.info("💡 모든 숫자가 이미 공개되어 있습니다!")
            elif num_incorrectly_filled_hidden_cells > 0:
                st.error("❌ 일부 숫자가 정답과 다릅니다. 다시 확인해주세요!")
            elif num_empty_hidden_cells > 0 : 
                st.warning("⚠️ 모든 빈칸을 채워주세요! 현재까지 입력한 값은 정답입니다.")
            else: 
                st.success("🎉 축하합니다! 모든 숫자를 정확히 맞혔습니다!")

    with col2_action:
        if st.button("새 게임 시작", use_container_width=True):
            for key_to_clear in ['grid', 'hidden_mask', 'user_grid', 'selected_cell']:
                if key_to_clear in st.session_state:
                    del st.session_state[key_to_clear]
            st.rerun()

if __name__ == "__main__":
    main()
