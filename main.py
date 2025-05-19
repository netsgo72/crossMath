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
    st.set_page_config(page_title="숫자 채우기 게임", layout="centered")
    st.title("🔢 숫자 채우기 게임")

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
            font-size: 22px;
            font-weight: bold;
            padding: 8px;
            box-sizing: border-box;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden_mask = hide_numbers(st.session_state.grid, max_visible=4)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid, dtype=int)
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None

    st.markdown("### 퍼즐")

    for i in range(3):
        cols = st.columns(4)
        for j in range(3):
            with cols[j]:
                is_hidden = st.session_state.hidden_mask[i, j]
                actual_val = st.session_state.grid[i, j]
                user_val = st.session_state.user_grid[i, j]

                if is_hidden:
                    display = str(user_val) if user_val != 0 else " "
                    if st.session_state.selected_cell == (i, j):
                        st.button(f"[{display}]", key=f"selected_{i}_{j}")
                    else:
                        if st.button(display, key=f"hidden_{i}_{j}"):
                            st.session_state.selected_cell = (i, j)
                            st.rerun()
                            return
                else:
                    st.button(str(actual_val), key=f"visible_{i}_{j}", disabled=True)

        with cols[3]:
            st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[i, :])}</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
    sum_cols = st.columns(4)
    for j in range(3):
        with sum_cols[j]:
            st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[:, j])}</div>', unsafe_allow_html=True)
    with sum_cols[3]:
        st.write("")

    st.markdown("---")

    st.markdown("### 숫자 입력")
    keypad_rows = [st.columns(3) for _ in range(3)]
    num = 1
    for row in keypad_rows:
        for col in row:
            with col:
                if st.session_state.selected_cell is not None:
                    if st.button(str(num), key=f"keypad_{num}"):
                        r, c = st.session_state.selected_cell
                        st.session_state.user_grid[r, c] = num
                        st.session_state.selected_cell = None
                        st.rerun()
                        return
            num += 1

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("정답 확인", use_container_width=True):
            all_correct = True
            is_empty_exists = False
            for r in range(3):
                for c in range(3):
                    if st.session_state.hidden_mask[r, c]:
                        val = st.session_state.user_grid[r, c]
                        if val == 0:
                            is_empty_exists = True
                        if val != st.session_state.grid[r, c]:
                            all_correct = False

            if not all_correct:
                st.error("❌ 일부 숫자가 정답과 다릅니다. 다시 확인해주세요!")
            elif is_empty_exists:
                st.warning("⚠️ 모든 빈칸을 채워주세요! 현재까지 입력한 값은 정답입니다.")
            else:
                st.success("🎉 축하합니다! 모든 숫자를 정확히 맞혔습니다!")

    with col2:
        if st.button("새 게임 시작", use_container_width=True):
            for key in ['grid', 'hidden_mask', 'user_grid', 'selected_cell']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
