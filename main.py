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
        valid_mask = True
        for i in range(3):
            if np.sum(~hidden_mask[i, :]) == 3:
                valid_mask = False; break
            if np.sum(~hidden_mask[:, i]) == 3:
                valid_mask = False; break
        if valid_mask:
            return hidden_mask

def main():
    st.set_page_config(layout="wide")
    st.title("숫자 채우기 게임")

    st.markdown("""
        <style>
        /* 그리드 셀 버튼 (기본) */
        .grid-cell-wrapper .stButton>button {
            width: 100px;  /* 고정 너비 */
            height: 100px; /* 고정 높이 */
            font-size: 60px; 
            padding: 0;
            margin: 0px;
            border: 2px solid #ccc; 
            overflow: hidden;
            display: flex; 
            align-items: center; 
            justify-content: center; 
            line-height: 1; /* Flex 사용 시 line-height는 1 또는 normal */
        }

        /* 활성화된 (선택된) 그리드 셀 버튼 */
        .grid-cell-wrapper.selected .stButton>button {
            border: 3px solid RoyalBlue !important; /* 이전 스타일 유지 */
            background-color: AliceBlue !important; /* 이전 스타일 유지 */
        }
        
        /* 비활성화된 그리드 셀 버튼 (원래 보이는 숫자) */
        .grid-cell-wrapper .stButton>button:disabled {
            background-color: #f0f0f0; 
            color: #555; 
            border-color: #d0d0d0; 
        }

        /* 숫자 패널 버튼들을 감싸는 div */
        .number-panel-buttons-wrapper {
            padding-top: 5px; /* 숫자판 제목과의 간격 */
        }
        
        /* 숫자 패널의 1-9 숫자 버튼 */
        .number-panel-buttons-wrapper .stButton[key*="panel_num_"]>button {
            aspect-ratio: 1 / 1; /* 정사각형 모양 */
            font-size: 18px; 
            /* margin-bottom은 st.columns의 gap으로 처리 */
        }
        
        /* 숫자 패널의 "지우기" 버튼 */
        .number-panel-buttons-wrapper .stButton[key*="panel_clear_btn"]>button {
            font-size: 16px;
            height: 40px; 
            margin-top: 8px; /* 숫자 그리드와의 간격 */
        }

        /* 합계 셀 스타일 */
        .sum-cell {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100px; 
            height: 100px; 
            font-size: 20px; 
            font-weight: bold;
            padding: 8px;
            box-sizing: border-box; 
            border: 1px solid #eee; 
            background-color: #f9f9f9; 
        }
        </style>
    """, unsafe_allow_html=True)

    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden_mask = hide_numbers(st.session_state.grid, max_visible=4)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid, dtype=int)
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None

    grid_area, panel_area = st.columns([3, 0.9]) # 비율 조정 (패널이 너무 좁지 않도록)

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
                        # use_container_width=True 제거하여 버튼 크기 고정
                        if st.button(display_label, key=f"btn_cell_{i}_{j}"): 
                            if is_currently_selected:
                                st.session_state.selected_cell = None 
                            else:
                                st.session_state.selected_cell = (i,j)
                            st.rerun()
                    else:
                        # use_container_width=True 제거
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
            st.markdown(f'<div class="sum-cell" title="대각선 합계 (좌상-우하)">↘ 합계: {main_diag_sum}</div>', unsafe_allow_html=True)

    with panel_area:
        st.subheader("숫자판")
        st.markdown('<div class="number-panel-buttons-wrapper">', unsafe_allow_html=True)
        
        # 3x3 숫자 버튼 그리드
        for r_panel in range(3):
            panel_row_cols = st.columns(3, gap="small") # 패널 내부 컬럼 간격 조정
            for c_panel in range(3):
                num_val_panel = r_panel * 3 + c_panel + 1
                with panel_row_cols[c_panel]:
                    if st.button(str(num_val_panel), key=f"panel_num_{num_val_panel}", use_container_width=True):
                        if st.session_state.selected_cell:
                            r, c = st.session_state.selected_cell
                            if st.session_state.hidden_mask[r,c]:
                                st.session_state.user_grid[r,c] = num_val_panel
                                st.rerun()
        
        # "지우기" 버튼 (3x3 그리드 아래)
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
            for r_idx in range(3):
                for c_idx in range(3):
                    if st.session_state.hidden_mask[r_idx, c_idx]: 
                        if st.session_state.user_grid[r_idx, c_idx] == 0: is_empty_exists = True
                        if st.session_state.user_grid[r_idx, c_idx] != st.session_state.grid[r_idx, c_idx]: all_correct = False
            if not all_correct: st.error("일부 숫자가 정답과 다릅니다. 다시 확인해주세요!")
            elif is_empty_exists and all_correct: st.warning("모든 빈칸을 채워주세요! 현재까지 입력한 값은 정답입니다.")
            else: st.success("축하합니다! 모든 숫자를 정확히 맞혔습니다!")
    with col2:
        if st.button("새 게임 시작", use_container_width=True):
            keys_to_reset = ['grid', 'hidden_mask', 'user_grid', 'selected_cell']
            for key in keys_to_reset:
                if key in st.session_state: del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
