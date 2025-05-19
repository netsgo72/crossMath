import streamlit as st
import numpy as np
import random

def initialize_grid():
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    return np.array(numbers).reshape(3, 3)

def hide_numbers(grid, max_visible=4):
    while True:
        hidden = np.ones_like(grid, dtype=bool)
        positions = list(range(9))
        random.shuffle(positions)
        for pos in positions[:max_visible]:
            row, col = divmod(pos, 3)
            hidden[row, col] = False
        valid = True
        for i in range(3):
            if np.sum(~hidden[i, :]) == 3 or np.sum(~hidden[:, i]) == 3:
                valid = False
                break
        if valid:
            return hidden

def main():
    st.set_page_config(layout="centered")
    st.title("숫자 채우기 게임")

    # 스타일 적용
    st.markdown("""
    <style>
    .grid-button .stButton>button {
        width: 100px;
        height: 100px;
        font-size: 32px;
        padding: 0;
        margin: 1px;
    }

    .sum-cell {
        width: 100px;
        height: 100px;
        font-size: 20px;
        font-weight: bold;
        padding: 4px;
        line-height: 1.2;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        border: 1px solid #ccc;
        box-sizing: border-box;
        overflow-wrap: break-word;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

    # 상태 초기화
    if "grid" not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden = hide_numbers(st.session_state.grid)
        st.session_state.user_grid = np.zeros((3, 3), dtype=int)
        st.session_state.selected = None
        st.session_state.pending = None

    # 선택된 셀에 값 반영
    if st.session_state.selected and st.session_state.pending:
        r, c = st.session_state.selected
        st.session_state.user_grid[r, c] = st.session_state.pending
        st.session_state.selected = None
        st.session_state.pending = None
        st.experimental_rerun()

    # 3x3 셀 + 행 합계
    for i in range(3):
        cols = st.columns(4)
        for j in range(3):
            with cols[j]:
                key = f"{i}_{j}"
                st.markdown('<div class="grid-button">', unsafe_allow_html=True)
                if st.session_state.hidden[i, j]:
                    val = st.session_state.user_grid[i, j]
                    if st.session_state.selected == (i, j):
                        opt = st.selectbox(
                            "선택",
                            options=[""] + [str(n) for n in range(1, 10)],
                            index=val if val else 0,
                            key=f"sel_{key}"
                        )
                        if opt != "":
                            st.session_state.pending = int(opt)
                            st.experimental_rerun()
                    else:
                        label = str(val) if val else ""
                        if st.button(label, key=f"btn_{key}"):
                            st.session_state.selected = (i, j)
                else:
                    st.button(str(st.session_state.grid[i, j]), key=f"btn_vis_{key}", disabled=True)
                st.markdown('</div>', unsafe_allow_html=True)
        with cols[3]:
            row_sum = np.sum(st.session_state.grid[i])
            st.markdown(f'<div class="sum-cell">합계: {row_sum}</div>', unsafe_allow_html=True)

    # 열 합계 + 대각선
    col_sums = st.columns(4)
    for j in range(3):
        with col_sums[j]:
            col_sum = np.sum(st.session_state.grid[:, j])
            st.markdown(f'<div class="sum-cell">합계: {col_sum}</div>', unsafe_allow_html=True)
    with col_sums[3]:
        diag_sum = np.trace(st.session_state.grid)
        st.markdown(f'<div class="sum-cell">↘ 합계: {diag_sum}</div>', unsafe_allow_html=True)

    # 버튼들
    col_btns = st.columns(2)
    with col_btns[0]:
        if st.button("정답 확인"):
            correct = all(
                not st.session_state.hidden[i, j] or
                st.session_state.user_grid[i, j] == st.session_state.grid[i, j]
                for i in range(3) for j in range(3)
            )
            if correct:
                st.success("정답입니다!")
            else:
                st.error("틀린 숫자가 있습니다.")
    with col_btns[1]:
        if st.button("새 게임 시작"):
            for key in ["grid", "hidden", "user_grid", "selected", "pending"]:
                st.session_state.pop(key, None)
            st.experimental_rerun()

if __name__ == "__main__":
    main()
