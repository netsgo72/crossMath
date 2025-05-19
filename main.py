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
    st.set_page_config(layout="wide")
    st.title("숫자 채우기 게임")

    st.markdown("""
    <style>
    .grid-cell-wrapper .stButton>button {
        width: 100px !important;
        height: 100px !important;
        font-size: 40px;
        padding: 8px;
        margin: 0px;
        border: 1px solid #ccc;
        box-sizing: border-box;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
    }

    .grid-cell-wrapper.selected .stButton>button {
        border: 3px solid RoyalBlue !important; 
        background-color: AliceBlue !important;
    }

    .grid-cell-wrapper .stButton>button:disabled {
        background-color: #f0f0f0; 
        color: #555; 
        border: 1px solid #d0d0d0; 
    }

    .number-panel-buttons-wrapper {
        padding-top: 5px; 
    }

    .number-panel-buttons-wrapper .stButton[key*="panel_num_"]>button {
        aspect-ratio: 1 / 1; 
        font-size: 18px; 
    }

    .number-panel-buttons-wrapper .stButton[key*="panel_clear_btn"]>button {
        font-size: 16px;
        height: 40px; 
        margin-top: 8px; 
    }

    .sum-cell {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100px !important;
        height: 100px !important;
        font-size: 40px;
        font-weight: bold;
        padding: 8px;
        box-sizing: border-box;
        border: 1px solid #ccc;
        background-color: #f9f9f9;
        margin: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

    if 'grid' not in st.session_state:
        st.session_state.grid = initialize_grid()
        st.session_state.hidden_mask = hide_numbers(st.session_state.grid, max_visible=4)
        st.session_state.user_grid = np.zeros_like(st.session_state.grid, dtype=int)
    if 'selected_cell' not in st.session_state:
        st.session_state.selected_cell = None

    grid_area, panel_area = st.columns([3, 0.9]) 

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
                        if st.button(display_label, key=f"btn_cell_{i}_{j}"): 
                            if is_currently_selected:
                                st.session_state.selected_cell = None 
                            else:
                                st.session_state.selected_cell = (i,j) 
                            st.rerun()
                    else:
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
            st.markdown(f'<div class="sum-cell" title="대각선 합계 (좌상-우
