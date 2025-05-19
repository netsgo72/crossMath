import streamlit as st
import numpy as np
import random

def initialize_grid():
    # 3x3 그리드에 1-9 사이의 랜덤 숫자 생성
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    grid = np.array(numbers).reshape(3, 3)
    return grid

def calculate_sums(grid):
    row_sums = np.sum(grid, axis=1)
    col_sums = np.sum(grid, axis=0)
    return row_sums, col_sums

def hide_numbers(grid, difficulty=0.5):
    # difficulty에 따라 숨길 숫자의 개수 결정 (0.5 = 절반의 숫자를 숨김)
    hidden = np.zeros_like(grid, dtype=bool)
    total_cells = grid.size
    num_to_hide = int(total_cells * difficulty)
    
    # 랜덤하게 숨길 위치 선택
    positions = list(range(total_cells))
    random.shuffle(positions)
    for pos in positions[:num_to_hide]:
        row = pos // 3
        col = pos % 3
        hidden[row, col] = True
    
    return hidden

def main():
    st.title("초등학생 덧셈 연습 게임")
    
    # CSS 스타일 추가 (셀 크기 4배, 근접)
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
        st.session_state.hidden = hide_numbers(st.session_state.grid)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid)
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None
    
    # 그리드 표시
    st.write("### 숫자 그리드")
    
    # 3x3 그리드와 합계를 표시하는 테이블 생성
    for i in range(3):
        cols = st.columns(4, gap="small")
        for j in range(3):
            with cols[j]:
                if st.session_state.hidden[i, j]:
                    cell_value = st.session_state.user_grid[i, j]
                    if st.session_state.selected_cell == (i, j):
                        # 드롭다운 표시
                        selected = st.selectbox(
                            "숫자 선택",
                            options=[""] + list(range(1, 10)),
                            key=f"select_{i}_{j}",
                            index=0 if cell_value == 0 else cell_value,
                        )
                        if selected != "" and selected != cell_value:
                            st.session_state.user_grid[i, j] = selected
                            st.session_state.selected_cell = None
                            st.experimental_rerun()
                    else:
                        # 빈 버튼 또는 입력된 숫자 버튼
                        label = "" if cell_value == 0 else str(cell_value)
                        if st.button(label, key=f"btn_{i}_{j}"):
                            st.session_state.selected_cell = (i, j)
                else:
                    # 보이는 숫자
                    st.button(str(st.session_state.grid[i, j]), key=f"btn_visible_{i}_{j}", disabled=True)
        
        # 행의 합계
        with cols[3]:
            st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[i])}</div>', unsafe_allow_html=True)
    
    # 열의 합계 표시
    col_sums = st.columns(4, gap="small")
    for j in range(3):
        with col_sums[j]:
            st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[:, j])}</div>', unsafe_allow_html=True)
    
    # 정답 확인
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
    
    # 새 게임 시작
    if st.button("새 게임 시작"):
        st.session_state.grid = initialize_grid()
        st.session_state.hidden = hide_numbers(st.session_state.grid)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid)
        st.session_state.selected_cell = None
        st.experimental_rerun()

if __name__ == "__main__":
    main() 
