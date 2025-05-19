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
    """
    그리드의 숫자 중 일부를 숨깁니다.
    - 최대 max_visible개의 숫자만 보이도록 합니다.
    - 한 행이나 열에 3개의 숫자가 모두 보이는 경우가 없도록 합니다.
    """
    while True:
        hidden_mask = np.ones_like(grid, dtype=bool)  # True는 숨겨진 셀
        positions = list(range(grid.size))
        random.shuffle(positions)
        
        visible_count = 0
        for pos in positions:
            if visible_count < max_visible:
                row, col = pos // 3, pos % 3
                hidden_mask[row, col] = False # False는 보이는 셀
                visible_count += 1
            else:
                break
        
        valid_mask = True
        for i in range(3):
            if np.sum(~hidden_mask[i, :]) == 3:  # 행에 보이는 숫자가 3개인 경우
                valid_mask = False
                break
            if np.sum(~hidden_mask[:, i]) == 3:  # 열에 보이는 숫자가 3개인 경우
                valid_mask = False
                break
        
        if valid_mask:
            return hidden_mask


def main():
    st.title("숫자 채우기 게임")

    st.markdown("""
        <style>
        .stButton>button {
            width: 100px;
            height: 100px;
            font-size: 32px;
            margin: 1px;
            padding: 0;
        }
        .sum-cell {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100px; 
            height: 100px; 
            font-size: 20px; /* 폰트 크기 약간 줄임 */
            font-weight: bold;
            padding: 8px;
            box-sizing: border-box; 
            border: 1px solid #eee; /* 셀 구분선 추가 */
            background-color: #f9f9f9; /* 배경색 약간 추가 */
        }
        /* Streamlit 컬럼 간 기본 간격을 사용하거나, 필요시 CSS로 조정 */
        </style>
    """, unsafe_allow_html=True)

    # 세션 상태 초기화
    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden_mask = hide_numbers(st.session_state.grid, max_visible=4)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid, dtype=int)
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None
    if 'pending_value' not in st.session_state:
        st.session_state.pending_value = None

    # 드롭다운에서 값이 선택된 경우, 그 값을 user_grid에 반영하고 상태 초기화
    if st.session_state.pending_value is not None and st.session_state.selected_cell is not None:
        r, c = st.session_state.selected_cell
        st.session_state.user_grid[r, c] = st.session_state.pending_value
        st.session_state.selected_cell = None
        st.session_state.pending_value = None
        st.rerun() 
        return

    # 3x3 그리드와 각 행의 합계 표시
    for i in range(3):
        cols = st.columns(4) 
        for j in range(3):
            with cols[j]:
                is_hidden_cell = st.session_state.hidden_mask[i, j]
                actual_value = st.session_state.grid[i, j]
                user_value = st.session_state.user_grid[i, j]

                if is_hidden_cell:
                    if st.session_state.selected_cell == (i, j):
                        options = [""] + [str(n) for n in range(1, 10)]
                        current_display_value = str(user_value) if user_value != 0 else ""
                        try:
                            current_idx = options.index(current_display_value)
                        except ValueError: 
                            current_idx = 0

                        selected_str = st.selectbox(
                            label="숫자 선택",
                            options=options,
                            index=current_idx,
                            key=f"select_{i}_{j}",
                            label_visibility="collapsed"
                        )
                        if selected_str != current_display_value: 
                            if selected_str == "":
                                st.session_state.pending_value = 0 
                            else:
                                st.session_state.pending_value = int(selected_str)
                            st.rerun()
                            return
                    else:
                        display_label = str(user_value) if user_value != 0 else " "
                        if st.button(display_label, key=f"btn_hidden_{i}_{j}"):
                            st.session_state.selected_cell = (i, j)
                            st.rerun()
                            return
                else:
                    st.button(str(actual_value), key=f"btn_visible_{i}_{j}", disabled=True)
        
        with cols[3]: 
            row_sum = np.sum(st.session_state.grid[i, :])
            st.markdown(f'<div class="sum-cell" title="행 {i+1} 합계">합계: {row_sum}</div>', unsafe_allow_html=True)

    # 각 열의 합계 및 대각선 합계 표시
    st.markdown('<div style="margin-top: 5px;"></div>', unsafe_allow_html=True) 
    sum_display_cols = st.columns(4)

    # 열 합계
    for j in range(3):
        with sum_display_cols[j]:
            col_sum = np.sum(st.session_state.grid[:, j])
            st.markdown(f'<div class="sum-cell" title="열 {j+1} 합계">합계: {col_sum}</div>', unsafe_allow_html=True)

    # 대각선 합계 (왼쪽 위에서 오른쪽 아래)
    with sum_display_cols[3]:
        main_diag_sum = np.trace(st.session_state.grid) # grid[0,0] + grid[1,1] + grid[2,2]
        st.markdown(f'<div class="sum-cell" title="대각선 합계 (좌상-우하)">↘ 합계: {main_diag_sum}</div>', unsafe_allow_html=True)


    # 컨트롤 버튼
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
            keys_to_reset = ['grid', 'hidden_mask', 'user_grid', 'selected_cell', 'pending_value']
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            return

if __name__ == "__main__":
    main()
