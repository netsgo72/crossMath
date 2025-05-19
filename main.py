import streamlit as st
import numpy as np
import random

# 숫자 그리드 초기화
def initialize_grid():
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    grid = np.array(numbers).reshape(3, 3)
    return grid

# 일부 숫자 숨기기
def hide_numbers(grid, max_visible=4):
    while True:
        hidden = np.ones_like(grid, dtype=bool)
        positions = list(range(grid.size))
        random.shuffle(positions)
        for pos in positions[:max_visible]:
            row = pos // 3
            col = pos % 3
            hidden[row, col] = False

        valid = True
        for i in range(3):
            if np.sum(~hidden[i, :]) == 3 or np.sum(~hidden[:, i]) == 3:
                valid = False
                break
        if valid:
            return hidden

def main():
    st.set_page_config(layout="wide")
    st.title("숫자 채우기 게임")

    # CSS 스타일 정의
    st.markdown("""
        <style>
        .cell-button > button {
            width: 100px;
            height: 100px;
            font-size: 32px;
            padding: 0;
            margin: 2px;
        }
        .sum-cell {
            width: 100px;
            height: 100px;
            font-size: 22px;
            font-weight: bold;
            padding: 8px;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            border: 1px solid #ddd;
            background-color: #f8f8f8;
        }
        </style>
    """, unsafe_allow_html=True)

    # 세션 상태 초기화
    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden = hide_numbers(st.session_state.grid)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid)
        st.session_state.selected = None
        st.session_state.pending = None

    # 선택된 셀 처리
    if st.session_state.pending is not None and st.session_state.selected is not None:
        i, j = st.session_state.selected
        st.session_state.user_grid[i, j] = st.session_state.pending
        st.session_state.selected = None
        st.session_state.pending = None
        st.experimental_rerun()
        return

    # 숫자 그리드 표시
    for i in range(3):
        cols = st.columns(4, gap="small")
        for j in range(3):
            with cols[j]:
                key = f"btn_{i}_{j}"
                if st.session_state.hidden[i, j]:
                    label = str(int(st.session_state.user_grid[i, j])) if st.session_state.user_grid[i, j] != 0 else ""
                    if st.button(label, key=key):
                        st.session_state.selected = (i, j)
                        st.experimental_rerun()
                else:
                    st.button(str(int(st.session_state.grid[i, j])), key=key + "_v", disabled=True)
        # 오른쪽 행 합계
        with cols[3]:
            st.markdown(f'<div class="sum-cell">합계:<br>{np.sum(st.session_state.grid[i])}</div>', unsafe_allow_html=True)

    # 하단 열 합계
    col_sums = st.columns(4, gap="small")
    for j in range(3):
        with col_sums[j]:
            st.markdown(f'<div class="sum-cell">합계:<br>{np.sum(st.session_state.grid[:, j])}</div>', unsafe_allow_html=True)

    with col_sums[3]:
        st.write("")  # 공백

    st.write("---")

    # 선택된 셀 표시
    if st.session_state.selected:
        i, j = st.session_state.selected
        st.markdown(f"🟡 선택된 셀: ({i+1}, {j+1})")

        # 숫자 키패드 (1~9)
        keypad = [st.columns(3) for _ in range(3)]
        for row in range(3):
            for col in range(3):
                num = row * 3 + col + 1
                if keypad[row][col].button(str(num), key=f"keypad_{num}"):
                    st.session_state.pending = num
                    st.experimental_rerun()

    # 정답 확인 버튼
    if st.button("정답 확인"):
        correct = True
        for i in range(3):
            for j in range(3):
                if st.session_state.hidden[i, j]:
                    if st.session_state.user_grid[i, j] != st.session_state.grid[i, j]:
                        correct = False
        if correct:
            st.success("🎉 축하합니다! 모든 답이 맞았습니다!")
        else:
            st.error("❌ 아직 틀린 답이 있습니다. 다시 시도해보세요!")

    if st.button("🔄 새 게임 시작"):
        st.session_state.grid = initialize_grid()
        st.session_state.hidden = hide_numbers(st.session_state.grid)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid)
        st.session_state.selected = None
        st.session_state.pending = None
        st.experimental_rerun()

if __name__ == "__main__":
    main()
