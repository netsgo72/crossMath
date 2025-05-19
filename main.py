import streamlit as st
import numpy as np
import random

def initialize_grid():
    """1부터 9까지의 숫자로 3x3 그리드를 초기화합니다."""
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    grid = np.array(numbers).reshape(3, 3)
    return grid

def hide_numbers(grid, max_visible=4):
    """그리드의 숫자 중 일부를 숨깁니다."""
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
        
        # Sudoku-like rule: Ensure no full row or column is initially revealed if it would solve other cells too easily.
        # This specific check prevents any row or column from having all 3 numbers visible initially.
        valid_mask = True
        for i in range(3):
            if np.sum(~hidden_mask[i, :]) == 3: # if all 3 in a row are visible
                valid_mask = False; break
            if np.sum(~hidden_mask[:, i]) == 3: # if all 3 in a col are visible
                valid_mask = False; break
        if valid_mask:
            return hidden_mask

def main():
    st.set_page_config(layout="wide")
    st.title("숫자 채우기 게임")

    # Define a common size for interactive cells
    cell_size = "70px"
    grid_cell_font_size = "35px"
    panel_cell_font_size = "24px" # Panel numbers can have a slightly smaller font
    sum_cell_font_size = "18px"

    st.markdown(f"""
        <style>
        /* 그리드 셀 버튼 (기본) */
        .grid-cell-wrapper .stButton>button {{
            width: {cell_size};
            height: {cell_size};
            font-size: {grid_cell_font_size};
            padding: 0;
            margin: 0px;
            border: 2px solid #ccc;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1;
        }}

        /* 활성화된 (선택된) 그리드 셀 버튼 */
        .grid-cell-wrapper.selected .stButton>button {{
            border: 3px solid RoyalBlue !important;
            background-color: AliceBlue !important;
        }}
        
        /* 비활성화된 그리드 셀 버튼 (원래 보이는 숫자) */
        .grid-cell-wrapper .stButton>button:disabled {{
            background-color: #f0f0f0;
            color: #555;
            border-color: #d0d0d0;
        }}

        /* 숫자 패널 버튼들을 감싸는 div */
        .number-panel-buttons-wrapper {{
            padding-top: 5px; /* 숫자판 제목과의 간격 */
        }}
        
        /* 숫자 패널의 1-9 숫자 버튼 */
        .number-panel-buttons-wrapper .stButton[key*="panel_num_"]>button {{
            width: {cell_size};            /* Match grid cell */
            height: {cell_size};           /* Match grid cell */
            font-size: {panel_cell_font_size}; /* Panel font size */
            padding: 0;             /* Match grid cell */
            margin: 0px;            /* Match grid cell */
            border: 2px solid #ccc; /* Match grid cell */
            overflow: hidden;       /* Match grid cell */
            display: flex;          /* Match grid cell */
            align-items: center;    /* Match grid cell */
            justify-content: center;/* Match grid cell */
            line-height: 1;         /* Match grid cell */
        }}
        
        /* 숫자 패널의 "지우기" 버튼 */
        .number-panel-buttons-wrapper .stButton[key*="panel_clear_btn"]>button {{
            font-size: 16px;
            height: 40px; 
            margin-top: 8px; /* 숫자 그리드와의 간격 */
        }}

        /* 합계 셀 스타일 */
        .sum-cell {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: {cell_size}; /* Match grid cell */
            height: {cell_size}; /* Match grid cell */
            font-size: {sum_cell_font_size}; 
            font-weight: bold;
            padding: 8px; /* Keep some padding for text */
            box-sizing: border-box; 
            border: 1px solid #eee; 
            background-color: #f9f9f9; 
        }}
        </style>
    """, unsafe_allow_html=True)

    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden_mask = hide_numbers(st.session_state.grid, max_visible=random.randint(3,5)) # Vary visible numbers
        st.session_state.user_grid = np.zeros_like(st.session_state.grid, dtype=int)
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None

    grid_area, panel_area = st.columns([3, 1]) # Adjusted ratio slightly for potentially wider panel

    with grid_area:
        for i in range(3):
            row_cols = st.columns(4, gap="small") 
            for j in range(3):
                with row_cols[j]:
                    is_hidden_cell = st.session_state.hidden_mask[i, j]
                    actual_value = st.session_state.grid[i, j]
                    user_value = st.session_state.user_grid[i, j]
                    is_currently_selected = (st.session_state.selected_cell == (i,j))

                    wrapper_class = "grid-cell-wrapper"
                    if is_currently_selected and is_hidden_cell:
                        wrapper_class += " selected"
                    
                    st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
                    
                    if is_hidden_cell:
                        display_label = str(user_value) if user_value != 0 else " "
                        if st.button(display_label, key=f"btn_cell_{i}_{j}"): 
                            if is_currently_selected:
                                st.session_state.selected_cell = None 
                            else:
                                st.session_state.selected_cell = (i,j)
                            st.rerun()
                    else:
                        st.button(str(actual_value), key=f"btn_cell_{i}_{j}", disabled=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with row_cols[3]: 
                row_sum = np.sum(st.session_state.grid[i, :])
                st.markdown(f'<div class="sum-cell" title="행 {i+1} 합계">합계: {row_sum}</div>', unsafe_allow_html=True)

        st.markdown('<div style="margin-top: 5px;"></div>', unsafe_allow_html=True) 
        sum_display_cols = st.columns(4, gap="small")
        for j_sum_col in range(3):
            with sum_display_cols[j_sum_col]:
                col_sum = np.sum(st.session_state.grid[:, j_sum_col])
                st.markdown(f'<div class="sum-cell" title="열 {j_sum_col+1} 합계">합계: {col_sum}</div>', unsafe_allow_html=True)
        with sum_display_cols[3]:
            main_diag_sum = np.trace(st.session_state.grid)
            anti_diag_sum = np.trace(np.fliplr(st.session_state.grid))
            st.markdown(f'<div class="sum-cell" title="대각선 합계 (좌상-우하 / 우상-좌하)">↘ {main_diag_sum}<br>↙ {anti_diag_sum}</div>', unsafe_allow_html=True)


    with panel_area:
        st.subheader("숫자판")
        st.markdown('<div class="number-panel-buttons-wrapper">', unsafe_allow_html=True)
        
        for r_panel in range(3):
            panel_row_cols = st.columns(3, gap="small") 
            for c_panel in range(3):
                num_val_panel = r_panel * 3 + c_panel + 1
                with panel_row_cols[c_panel]:
                    # REMOVED use_container_width=True
                    if st.button(str(num_val_panel), key=f"panel_num_{num_val_panel}"):
                        if st.session_state.selected_cell:
                            r, c = st.session_state.selected_cell
                            if st.session_state.hidden_mask[r,c]:
                                # Prevent placing a number if it's already used in the same row/col/original grid
                                is_duplicate_in_row = num_val_panel in st.session_state.user_grid[r, :] and st.session_state.user_grid[r,c] != num_val_panel
                                is_duplicate_in_col = num_val_panel in st.session_state.user_grid[:, c] and st.session_state.user_grid[r,c] != num_val_panel
                                # Check against initially visible numbers as well
                                is_duplicate_in_visible_row = num_val_panel in st.session_state.grid[r, ~st.session_state.hidden_mask[r,:]]
                                is_duplicate_in_visible_col = num_val_panel in st.session_state.grid[~st.session_state.hidden_mask[:,c], c]
                                
                                is_num_already_in_original_grid = num_val_panel in st.session_state.grid[~st.session_state.hidden_mask]

                                if num_val_panel in st.session_state.user_grid and st.session_state.user_grid[r,c] != num_val_panel: # if num exists elsewhere in user entries
                                    st.toast(f"⚠️ 숫자 {num_val_panel}은 이미 사용되었습니다.", icon="⚠️")
                                elif num_val_panel in st.session_state.grid[~st.session_state.hidden_mask]: # if num exists in original visible numbers
                                     st.toast(f"🚫 숫자 {num_val_panel}은 이미 보이는 숫자에 있습니다.", icon="🚫")
                                else:
                                    st.session_state.user_grid[r,c] = num_val_panel
                                    st.rerun()
        
        if st.button("지우기", key="panel_clear_btn", use_container_width=True):
            if st.session_state.selected_cell:
                r, c = st.session_state.selected_cell
                if st.session_state.hidden_mask[r,c]:
                    st.session_state.user_grid[r,c] = 0
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---") 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("정답 확인", use_container_width=True):
            all_correct = True; is_empty_exists = False
            # Check only hidden cells
            hidden_indices = np.where(st.session_state.hidden_mask)
            if hidden_indices[0].size == 0: # Should not happen if hide_numbers works
                 st.info("모든 숫자가 처음부터 공개되어 있습니다!")
            else:
                for r_idx, c_idx in zip(hidden_indices[0], hidden_indices[1]):
                    if st.session_state.user_grid[r_idx, c_idx] == 0: 
                        is_empty_exists = True
                    if st.session_state.user_grid[r_idx, c_idx] != st.session_state.grid[r_idx, c_idx] and st.session_state.user_grid[r_idx, c_idx] != 0 :
                        all_correct = False # Mark incorrect only if a wrong number is filled
                    # If it's empty, it's not "incorrect" for this check, but "incomplete"

                if not all_correct: 
                    st.error("일부 숫자가 정답과 다릅니다. 다시 확인해주세요!")
                elif is_empty_exists: # Some are empty, but filled ones are correct
                    st.warning("모든 빈칸을 채워주세요! 현재까지 입력한 값은 정답과 일치합니다.")
                else: # All hidden cells are filled and correct
                    st.success("축하합니다! 모든 숫자를 정확히 맞혔습니다! 🎉")
    with col2:
        if st.button("새 게임 시작", use_container_width=True):
            keys_to_reset = ['grid', 'hidden_mask', 'user_grid', 'selected_cell']
            for key in keys_to_reset:
                if key in st.session_state: del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
