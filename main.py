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
    
    # CSS 스타일 추가
    st.markdown("""
        <style>
        .stButton>button {
            width: 100px;
            height: 100px;
            font-size: 24px;
            margin: 2px;
            padding: 0;
        }
        .sum-cell {
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 세션 상태 초기화
    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden = hide_numbers(st.session_state.grid)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid)
        st.session_state.selected_cell = None
    
    # 그리드 표시
    st.write("### 숫자 그리드")
    
    # 3x3 그리드와 합계를 표시하는 테이블 생성
    for i in range(3):
        cols = st.columns(4)  # 3개의 숫자 + 1개의 합계
        for j in range(3):
            with cols[j]:
                if st.session_state.hidden[i, j]:
                    # 숨겨진 숫자 위치
                    if st.session_state.user_grid[i, j] == 0:
                        if st.button("□", key=f"btn_{i}_{j}"):
                            st.session_state.selected_cell = (i, j)
                    else:
                        if st.button(str(st.session_state.user_grid[i, j]), key=f"btn_{i}_{j}"):
                            st.session_state.selected_cell = (i, j)
                else:
                    # 보이는 숫자
                    st.button(str(st.session_state.grid[i, j]), key=f"btn_visible_{i}_{j}", disabled=True)
        
        # 행의 합계
        with cols[3]:
            st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[i])}</div>', unsafe_allow_html=True)
    
    # 열의 합계 표시
    col_sums = st.columns(4)
    for j in range(3):
        with col_sums[j]:
            st.markdown(f'<div class="sum-cell">합계: {np.sum(st.session_state.grid[:, j])}</div>', unsafe_allow_html=True)
    
    # 숫자 선택 패널
    if st.session_state.selected_cell is not None:
        st.write("### 숫자 선택")
        num_cols = st.columns(3)
        for num in range(1, 10):
            with num_cols[(num-1) % 3]:
                if st.button(str(num), key=f"num_{num}"):
                    i, j = st.session_state.selected_cell
                    st.session_state.user_grid[i, j] = num
                    st.session_state.selected_cell = None
                    st.experimental_rerun()
    
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
