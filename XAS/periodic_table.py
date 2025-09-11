import ipywidgets as widgets

elements = {
    (0, 0): 'H',   (0, 17): 'He',
    (1, 0): 'Li',  (1, 1): 'Be', (1, 12): 'B',  (1, 13): 'C', (1, 14): 'N', (1, 15): 'O', (1, 16): 'F', (1, 17): 'Ne',
    (2, 0): 'Na',  (2, 1): 'Mg', (2, 12): 'Al', (2, 13): 'Si', (2, 14): 'P', (2, 15): 'S', (2, 16): 'Cl', (2, 17): 'Ar',

    (3, 0): 'K',   (3, 1): 'Ca', (3, 2): 'Sc', (3, 3): 'Ti', (3, 4): 'V', (3, 5): 'Cr', (3, 6): 'Mn', (3, 7): 'Fe',
    (3, 8): 'Co',  (3, 9): 'Ni', (3,10): 'Cu', (3,11): 'Zn', (3,12): 'Ga', (3,13): 'Ge', (3,14): 'As', (3,15): 'Se',
    (3,16): 'Br',  (3,17): 'Kr',

    (4, 0): 'Rb',  (4, 1): 'Sr', (4, 2): 'Y', (4, 3): 'Zr', (4, 4): 'Nb', (4, 5): 'Mo', (4, 6): 'Tc', (4, 7): 'Ru',
    (4, 8): 'Rh',  (4, 9): 'Pd', (4,10): 'Ag', (4,11): 'Cd', (4,12): 'In', (4,13): 'Sn', (4,14): 'Sb', (4,15): 'Te',
    (4,16): 'I',   (4,17): 'Xe',

    (5, 0): 'Cs',  (5, 1): 'Ba',             (5, 3): 'Hf',  (5, 4): 'Ta', (5, 5): 'W',  (5, 6): 'Re', (5, 7): 'Os', (5, 8): 'Ir',
    (5, 9): 'Pt',  (5,10): 'Au', (5,11): 'Hg', (5,12): 'Tl', (5,13): 'Pb', (5,14): 'Bi', (5,15): 'Po', (5,16): 'At',  (5,17): 'Rn',
    
    (6, 0): 'Fr',  (6, 1): 'Ra',             (6, 3): 'Rf',  (6, 4): 'Db', (6, 5): 'Sg', (6, 6): 'Bh', (6, 7): 'Hs', (6, 8): 'Mt',
    (6, 9): 'Ds',  (6,10): 'Rg', (6,11): 'Cn', (6,12): 'Nh', (6,13): 'Fl', (6,14): 'Mc', (6,15): 'Lv', (6,16): 'Ts',  (6,17): 'Og',
    # Lanthanoide
    (8, 3): 'La', (8, 4): 'Ce', (8, 5): 'Pr', (8, 6): 'Nd', (8, 7): 'Pm', (8, 8): 'Sm', (8, 9): 'Eu',
    (8,10): 'Gd', (8,11): 'Tb', (8,12): 'Dy', (8,13): 'Ho', (8,14): 'Er', (8,15): 'Tm', (8,16): 'Yb', (8,17): 'Lu',
    # Actinoide
    (9, 3): 'Ac', (9, 4): 'Th', (9, 5): 'Pa', (9, 6): 'U', (9, 7): 'Np', (9, 8): 'Pu', (9, 9): 'Am',
    (9,10): 'Cm', (9,11): 'Bk', (9,12): 'Cf', (9,13): 'Es', (9,14): 'Fm', (9,15): 'Md', (9,16): 'No', (9,17): 'Lr',
}

k_edge_data = {
    'Cr': 5.989,
    'Mn': 6.539,
    'Fe': 7.112,
    'Co': 7.709,
    'Ni': 8.333,
    'Cu': 8.979,
    'Zn': 9.659,
    'Ga': 10.367,
    'Ge': 11.103,
    'As': 11.867,
    'Se': 12.658,
    'Br': 13.474,
    'Kr': 14.327,
    'Rb': 15.200,
    'Sr': 16.105,
    'Y': 17.038,
    'Zr': 18.008,
    'Nb': 19.000,
    'Mo': 20.000,
}

def create_button(symbol, button_function):
    btn = widgets.Button(description=symbol, layout=widgets.Layout(width='40px'))
    if k_edge_data.get(symbol):
        btn.style.button_color = "#aaa"
    else:
        btn.style.button_color = "#eee"
    btn.on_click(lambda b: button_function(symbol))
    return btn

def create_periodic_table(button_function):
    grid = [[None for _ in range(18)] for _ in range(10)]
    # place buttons in grid
    for (row, col), symbol in elements.items():
        grid[row][col] = create_button(symbol, button_function)
    flat_grid = []
    for row in grid:
        for cell in row:
            if cell is None:
                cell = widgets.Label(value='', layout=widgets.Layout(width='40px'))
            flat_grid.append(cell)
    # show grid
    gridbox = widgets.GridBox(
        flat_grid,
        layout=widgets.Layout(
            grid_template_columns="repeat(18, 40px)",
            grid_template_rows="repeat(7, 40px)",
            grid_gap="2px 2px"
        )
    )
    return gridbox

