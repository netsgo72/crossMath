import streamlit as st
import numpy as np
import random

def initialize_grid():
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    grid = np.array(numbers).reshape(3, 3)
    return grid

def hide_numbers(grid, max_visible=4):
    # 9칸 중 max_visible개만 보이도록 나머지는 숨김
    hidden = np.ones_like(grid, dtype=bool)
    positions = list(range(grid.size))
    random.shuffle(positions)
    for pos in positions[:max_visible]:
        row = pos // 3
        col = pos % 3
        hidden[row, col] = False
    return hidden

def main():
    st.title("숫자 그리드")

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
            font-size: 22px;
            font-weight: bold;
            padding: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 세션 상태 안전 초기화
    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden = hide_numbers(st.session_state.grid, max_visible=4)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid)
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None

    # 드롭다운에서 값이 선택된 경우, 그 값을 반영
    if 'pending_value' not in st.session_state:
        st.session_state.pending_value = None
    if st.session_state.pending_value is not None and st.session_state.selected_cell is not None:
        i, j = st.session_state.selected_cell
        st.session_state.user_grid[i, j] = st.session_state.pending_value
        st.session_state.selected_cell = None
        st.session_state.pending_value = None
        st.experimental_rerun()

    # 3x3 그리드와 합계 표시
    for i in range(3):
        cols = st.columns(4, gap="small")
        for j in range(3):
            with cols[j]:
                if st.session_state.hidden[i, j]:
                    cell_value = st.session_state.user_grid[i, j]
                    if st.session_state.selected_cell == (i, j):
                        # 드롭다운 표시 (문자열 리스트)
                        selected = st.selectbox(
                            "숫자 선택",
                            options=[""] + [str(n) for n in range(1, 10)],
                            key=f"select_{i}_{j}",
                            index=0 if cell_value == 0 else cell_value,
                        )
                        if selected != "" and (cell_value == 0 or int(selected) != cell_value):
                            st.session_state.pending_value = int(selected)
                    else:
                        label = "" if cell_value == 0 else str(cell_value)
                        if st.button(label, key=f"btn_{i}_{j}"):
                            st.session_state.selected_cell = (i, j)
                else:
                    st.button(str(st.session_state.grid[i, j]), key=f"btn_visible_{i}_{j}", disabled=True)
        with cols[3]:
            st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[i])}</div>', unsafe_allow_html=True)

    col_sums = st.columns(4, gap="small")
    for j in range(3):
        with col_sums[j]:
            st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[:, j])}</div>', unsafe_allow_html=True)

    if st.button("정답 확인"):
        correct = True
        for i in range(3):
            for j in range(3):
                if st.session_state.hidden[i, j]:
                    if st.session_state.user_grid[i, j] != st.session_state.grid[i, j]:
                        correct = False
                        break
        if correct:
            st.success("축하합니다! 모든 답이 맞았습니다!")
        else:
            st.error("아직 몇 개의 답이 틀렸습니다. 다시 시도해보세요!")

    if st.button("새 게임 시작"):
        st.session_state.grid = initialize_grid()
        st.session_state.hidden = hide_numbers(st.session_state.grid, max_visible=4)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid)
        st.session_state.selected_cell = None
        st.session_state.pending_value = None
        st.experimental_rerun()

if __name__ == "__main__":
    main()
