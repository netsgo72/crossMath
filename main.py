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
        
        # 현재 보이는 셀(False인 셀)을 기준으로 유효성 검사
        # 어떤 행이나 열에도 3개의 숫자가 모두 보이지 않는지 확인
        valid_mask = True
        for i in range(3):
            if np.sum(~hidden_mask[i, :]) == 3:  # 행에 보이는 숫자가 3개인 경우
                valid_mask = False
                break
            if np.sum(~hidden_mask[:, i]) == 3:  # 열에 보이는 숫자가 3개인 경우
                valid_mask = False
                break
        
        if valid_mask:
            # 실제 보이는 숫자가 max_visible과 다를 수 있음 (조건 때문에 더 적게 보일 수 있음)
            # 만약 정확히 max_visible 개수를 원한다면 로직 수정 필요.
            # 현재는 max_visible "이하"가 되며, 행/열 3개 동시 표시 방지 우선.
            # 만약 항상 max_visible 개수를 보이게 하고 싶다면, 조건 만족하는 조합을 찾을 때까지 반복해야 함.
            # 현재 로직은 max_visible개를 우선 보이게 한 후, 조건에 안 맞으면 다시 시도.
            # 이 로직으로도 충분히 빠르게 찾아짐.
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
            width: 100px; /* 버튼과 너비 유사하게 */
            height: 100px; /* 버튼과 높이 유사하게 */
            font-size: 22px;
            font-weight: bold;
            padding: 8px;
            box-sizing: border-box; /* 패딩 포함 크기 계산 */
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(4, 100px); /* 3개 셀 + 합계 셀 */
            gap: 5px; /* 열 간 간격 */
        }
        .row-container {
            display: contents; /* grid-template-columns를 부모로부터 상속받도록 함 */
        }
        .sum-row-container {
             display: grid;
             grid-template-columns: repeat(3, 100px); /* 합계 셀만 */
             gap: 5px; /* 열 간 간격 */
             margin-top: 5px; /* 그리드와의 간격 */
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
    if 'pending_value' not in st.session_state:
        st.session_state.pending_value = None

    # 드롭다운에서 값이 선택된 경우, 그 값을 user_grid에 반영하고 상태 초기화
    if st.session_state.pending_value is not None and st.session_state.selected_cell is not None:
        r, c = st.session_state.selected_cell
        st.session_state.user_grid[r, c] = st.session_state.pending_value
        st.session_state.selected_cell = None
        st.session_state.pending_value = None
        st.rerun() # st.experimental_rerun() 대신 st.rerun() 사용
        return

    # 3x3 그리드와 각 행의 합계 표시
    for i in range(3):
        cols = st.columns(4) # gap 인자 제거하고 CSS로 처리 가능 또는 그대로 사용
        for j in range(3):
            with cols[j]:
                is_hidden_cell = st.session_state.hidden_mask[i, j]
                actual_value = st.session_state.grid[i, j]
                user_value = st.session_state.user_grid[i, j]

                if is_hidden_cell:
                    if st.session_state.selected_cell == (i, j):
                        # 이 셀이 선택된 경우 드롭다운 표시
                        options = [""] + [str(n) for n in range(1, 10)]
                        current_display_value = str(user_value) if user_value != 0 else ""
                        try:
                            current_idx = options.index(current_display_value)
                        except ValueError: # 혹시 모를 오류 방지
                            current_idx = 0

                        selected_str = st.selectbox(
                            label="숫자 선택", # label은 보이지 않지만 필요
                            options=options,
                            index=current_idx,
                            key=f"select_{i}_{j}",
                            label_visibility="collapsed" # label 숨기기
                        )
                        if selected_str != current_display_value: # 값이 변경된 경우
                            if selected_str == "":
                                st.session_state.pending_value = 0 # 빈칸 선택은 0으로 처리
                            else:
                                st.session_state.pending_value = int(selected_str)
                            st.rerun()
                            return
                    else:
                        # 숨겨진 셀이고, 선택되지 않은 경우: 버튼으로 표시 (사용자 입력 값 또는 빈칸)
                        display_label = str(user_value) if user_value != 0 else " "
                        if st.button(display_label, key=f"btn_hidden_{i}_{j}"):
                            st.session_state.selected_cell = (i, j)
                            st.rerun()
                            return
                else:
                    # 원래부터 보이는 숫자 (수정 불가)
                    st.button(str(actual_value), key=f"btn_visible_{i}_{j}", disabled=True)
        
        with cols[3]: # 해당 행의 숫자 합계
            # 사용자가 입력한 값을 포함하여 합계를 보여줄지, 아니면 정답 기준으로 보여줄지 결정
            # 현재는 정답 기준 합계
            row_sum = np.sum(st.session_state.grid[i, :])
            st.markdown(f'<div class="sum-cell">합계: {row_sum}</div>', unsafe_allow_html=True)

    # 각 열의 합계 표시
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True) # 간격 추가
    cols_sum_row = st.columns(4) # 합계 행을 위한 컬럼 (마지막은 비워둠)
    for j in range(3):
        with cols_sum_row[j]:
            col_sum = np.sum(st.session_state.grid[:, j])
            st.markdown(f'<div class="sum-cell">합계: {col_sum}</div>', unsafe_allow_html=True)
    with cols_sum_row[3]: # 마지막 열 합계 표시 공간 비워두거나 다른 정보
        st.write("")


    # 컨트롤 버튼
    st.markdown("---") # 구분선
    col1, col2 = st.columns(2)

    with col1:
        if st.button("정답 확인", use_container_width=True):
            all_correct = True
            is_empty_exists = False
            for r in range(3):
                for c in range(3):
                    if st.session_state.hidden_mask[r, c]: # 숨겨졌던 셀만 확인
                        if st.session_state.user_grid[r, c] == 0: # 사용자가 입력하지 않은 셀
                            is_empty_exists = True
                        if st.session_state.user_grid[r, c] != st.session_state.grid[r, c]:
                            all_correct = False
            
            if not all_correct:
                st.error("일부 숫자가 정답과 다릅니다. 다시 확인해주세요!")
            elif is_empty_exists and all_correct : # 모든 보이는 답이 정답이지만 빈칸이 있는 경우
                 st.warning("모든 빈칸을 채워주세요! 현재까지 입력한 값은 정답입니다.")
            else: # all_correct is True and no empty cells among hidden ones
                 st.success("축하합니다! 모든 숫자를 정확히 맞혔습니다!")


    with col2:
        if st.button("새 게임 시작", use_container_width=True):
            # 모든 관련 세션 상태 초기화
            keys_to_reset = ['grid', 'hidden_mask', 'user_grid', 'selected_cell', 'pending_value']
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            return

if __name__ == "__main__":
    main()
