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
                valid_mask = False
                break
            if np.sum(~hidden_mask[:, i]) == 3:
                valid_mask = False
                break
        if valid_mask:
            return hidden_mask

def main():
    st.set_page_config(layout="wide") # 넓은 레이아웃 사용
    st.title("숫자 채우기 게임")

    st.markdown("""
        <style>
        /* 그리드 셀 버튼 (기본) */
        .grid-cell-wrapper .stButton>button {
            width: 100px;
            height: 100px;
            font-size: 60px; /* 숫자 크기 대폭 증가 */
            line-height: 100px; /* 수직 중앙 정렬 */
            text-align: center;
            padding: 0;
            margin: 0px;
            border: 2px solid #ccc; /* 기본 테두리 */
            overflow: hidden;
            display: flex; /* Flexbox로 내부 컨텐츠 정렬 */
            align-items: center; /* 수직 중앙 */
            justify-content: center; /* 수평 중앙 */
        }

        /* 활성화된 (선택된) 그리드 셀 버튼 */
        .grid-cell-wrapper.selected .stButton>button {
            border: 3px solid RoyalBlue !important;
            background-color: AliceBlue !important;
        }
        
        /* 비활성화된(disabled) 그리드 셀 버튼 (원래 보이는 숫자) */
        .grid-cell-wrapper .stButton>button:disabled {
            background-color: #f0f0f0 !important; /* 비활성 배경색 */
            color: #555 !important; /* 비활성 글자색 */
            border-color: #d0d0d0 !important; /* 비활성 테두리색 */
        }

        /* 숫자 패널 버튼들을 감싸는 div */
        .number-panel-buttons-wrapper .stButton>button {
            margin-bottom: 8px !important;
            font-size: 18px;
            height: 40px; /* 버튼 높이 조절 */
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

    # 세션 상태 초기화
    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden_mask = hide_numbers(st.session_state.grid, max_visible=4)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid, dtype=int)
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None

    # 메인 레이아웃: 좌측 그리드 영역 | 우측 숫자 패널
    grid_area, panel_area = st.columns([3, 0.8]) # 비율 조정 (예: 3:1 또는 4:1)

    with grid_area:
        # 3x3 그리드와 각 행의 합계 표시
        for i in range(3):
            row_cols = st.columns(4, gap="small") 
            for j in range(3):
                with row_cols[j]:
                    is_hidden_cell = st.session_state.hidden_mask[i, j]
                    actual_value = st.session_state.grid[i, j]
                    user_value = st.session_state.user_grid[i, j]
                    is_currently_selected = (st.session_state.selected_cell == (i,j))

                    wrapper_class = "grid-cell-wrapper"
                    if is_currently_selected and is_hidden_cell: # 수정 가능한 셀이 선택된 경우에만 selected 클래스 적용
                        wrapper_class += " selected"
                    
                    st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
                    
                    if is_hidden_cell:
                        display_label = str(user_value) if user_value != 0 else " "
                        if st.button(display_label, key=f"btn_cell_{i}_{j}", use_container_width=True):
                            if is_currently_selected:
                                st.session_state.selected_cell = None # 이미 선택된 셀을 다시 클릭하면 선택 해제
                            else:
                                st.session_state.selected_cell = (i,j) # 새로운 셀 선택
                            st.rerun()
                    else:
                        st.button(str(actual_value), key=f"btn_cell_{i}_{j}", disabled=True, use_container_width=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with row_cols[3]: 
                row_sum = np.sum(st.session_state.grid[i, :])
                st.markdown(f'<div class="sum-cell" title="행 {i+1} 합계">합계: {row_sum}</div>', unsafe_allow_html=True)

        # 각 열의 합계 및 대각선 합계 표시
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
        for num_val_panel in range(1, 10):
            if st.button(str(num_val_panel), key=f"panel_num_{num_val_panel}", use_container_width=True):
                if st.session_state.selected_cell:
                    r, c = st.session_state.selected_cell
                    if st.session_state.hidden_mask[r,c]: # 숨겨진 셀에만 입력 가능
                        st.session_state.user_grid[r,c] = num_val_panel
                        # 숫자 입력 후에도 셀 선택 유지 (연속 변경 가능)
                        # st.session_state.selected_cell = None # 필요시 주석 해제하여 입력 후 선택 해제
                        st.rerun()
        
        if st.button("지우기", key="panel_clear_btn", use_container_width=True):
            if st.session_state.selected_cell:
                r, c = st.session_state.selected_cell
                if st.session_state.hidden_mask[r,c]: # 숨겨진 셀에만 입력 가능
                    st.session_state.user_grid[r,c] = 0
                    # st.session_state.selected_cell = None # 필요시 주석 해제
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 컨트롤 버튼 (그리드 영역 아래 또는 전체 너비로 배치 가능)
    st.markdown("---") 
    col1, col2 = st.columns(2)
    with col1:
        if st.button("정답 확인", use_container_width=True):
            all_correct = True
            is_empty_exists = False
            for r_idx in range(3):
                for c_idx in range(3):
                    if st.session_state.hidden_mask[r_idx, c_idx]: 
                        if st.session_state.user_grid[r_idx, c_idx] == 0: 
                            is_empty_exists = True
                        if st.session_state.user_grid[r_idx, c_idx] != st.session_state.grid[r_idx, c_idx]:
                            all_correct = False
            if not all_correct:
                st.error("일부 숫자가 정답과 다릅니다. 다시 확인해주세요!")
            elif is_empty_exists and all_correct : 
                 st.warning("모든 빈칸을 채워주세요! 현재까지 입력한 값은 정답입니다.")
            else: 
                 st.success("축하합니다! 모든 숫자를 정확히 맞혔습니다!")
    with col2:
        if st.button("새 게임 시작", use_container_width=True):
            keys_to_reset = ['grid', 'hidden_mask', 'user_grid', 'selected_cell']
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            # return # st.rerun()이 호출되면 스크립트 실행이 중지되므로 명시적 return 불필요

if __name__ == "__main__":
    main()
