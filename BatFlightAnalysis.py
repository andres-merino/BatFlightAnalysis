import pandas as pd
import numpy as np

import plotly.graph_objects as go

def extract_coordinates(point):
    point = point.strip("()")
    x, y = point.split(", ")
    return int(x), int(y)

def type_point(row):
    # empty
    if 0 in row.values:
        return 0
    # feeding
    elif -2 in row.values:
        return -2
    else:
        return 1
    
def read_data(file):
    # Read the data from the excel file
    data = pd.read_excel(file)

    # Split columns into two
    for column in data.columns:
        data[column + ' (x)'] = data[column].apply(lambda p: extract_coordinates(p)[0])
        data[column + ' (y)'] = data[column].apply(lambda p: extract_coordinates(p)[1])

    # Drop the original columns
    data = data.drop(columns=data.columns[:6])

    # Delete column Right Point 1 y 2 (x)
    data = data.drop(columns=['Right Point 1 (x)', 'Right Point 2 (x)'])

    # Add type column
    data['type'] = data.apply(type_point, axis=1)

    # Delete rows with type 0 values
    data = data[data['type'] != 0]
    data = data.reset_index(drop=True)

    # Change -1 values to nan
    data = data.replace(-1, np.nan)

    # Find first row with the value equal to -2
    feed_o = data.index[data['type'] == -2].tolist()[0]
    # Find last row with the value equal to -2
    feed_f = data.index[data['type'] == -2].tolist()[-1]

    # Change -1 values to nan
    data = data.replace(-2, np.nan)

    # Separate feeding points
    data_bef = data.iloc[:feed_o]
    data_fee = data.iloc[feed_o:feed_f+1]
    data_aft = data.iloc[feed_f+1:]

    # Complete nan by interpolation
    data_bef = data_bef.interpolate()
    data_fee = data_fee.interpolate()
    data_aft = data_aft.interpolate()

    # Recalculate Right Point 1 (y) and Right Point 2 (y)
    data_bef['Left Point 1 (z)'] = 480 - data_bef['Right Point 1 (y)']
    data_bef['Left Point 2 (z)'] = 480 - data_bef['Right Point 2 (y)']
    data_fee['Left Point 1 (z)'] = 480 - data_fee['Right Point 1 (y)']
    data_fee['Left Point 2 (z)'] = 480 - data_fee['Right Point 2 (y)']
    data_aft['Left Point 1 (z)'] = 480 - data_aft['Right Point 1 (y)']
    data_aft['Left Point 2 (z)'] = 480 - data_aft['Right Point 2 (y)']

    return data_bef, data_fee, data_aft

def split_data(data_bef, data_fee, data_aft):
    # Take Left Point 1 and 2 and Right Point a 1 and 2
    flower_bef = data_bef[['Left Point 1 (x)', 'Left Point 1 (y)', 'Left Point 1 (z)']]
    flower_fee = data_fee[['Left Point 1 (x)', 'Left Point 1 (y)', 'Left Point 1 (z)']]
    flower_aft = data_aft[['Left Point 1 (x)', 'Left Point 1 (y)', 'Left Point 1 (z)']]

    bat_bef = data_bef[['Left Point 2 (x)', 'Left Point 2 (y)', 'Left Point 2 (z)']]
    bat_fee = flower_fee
    bat_aft = data_aft[['Left Point 2 (x)', 'Left Point 2 (y)', 'Left Point 2 (z)']]

    # Rename columns
    flower_bef.columns = ['x', 'y', 'z']
    flower_fee.columns = ['x', 'y', 'z']
    flower_aft.columns = ['x', 'y', 'z']

    bat_bef.columns = ['x', 'y', 'z']
    bat_fee.columns = ['x', 'y', 'z']
    bat_aft.columns = ['x', 'y', 'z']

    return flower_bef, flower_fee, flower_aft, bat_bef, bat_fee, bat_aft

def create_scatter3d(data, color, name, showlegend=True):
    return go.Scatter3d(
        x=data['x'],
        y=data['y'],
        z=data['z'],
        mode='lines',
        line=dict(width=4, color=color),
        name=name,
        showlegend=showlegend
    )
def create_scatter3d_anim(data, k, color, name, showlegend=True):
    return go.Scatter3d(
        x=data['x'].iloc[:k+1],
        y=data['y'].iloc[:k+1],
        z=data['z'].iloc[:k+1],
        mode='lines+markers',
        marker=dict(size=[0] * (k - 1) + [5], color=color),
        line=dict(width=4, color=color),
        name=name,
        showlegend=showlegend
    )
def create_scatter3d_single(data, k, color, name, showlegend=True):
    return go.Scatter3d(
        x=[data['x'].iloc[k]],
        y=[data['y'].iloc[k]],
        z=[data['z'].iloc[k]],
        mode='markers',
        marker=dict(size=5, color=color),
        name=name,
        showlegend=showlegend
    )

def animate_flower_bat(bat_bef, bat_fee, bat_aft, flower_bef, flower_fee, flower_aft):

    flower = pd.concat([flower_bef, flower_fee, flower_aft])
    bat = pd.concat([bat_bef, bat_fee, bat_aft])
    data = pd.concat([flower, bat])

    # Crear el gráfico 3D interactivo
    fig = go.Figure(
        data=[
            go.Scatter3d(),
            go.Scatter3d(),
            go.Scatter3d(),
            go.Scatter3d(),
            go.Scatter3d(),
            go.Scatter3d(),
            go.Scatter3d(),
            go.Scatter3d(),
            go.Scatter3d(),
            create_scatter3d_single(bat, 0, 'black', 'Murciélago'),
            create_scatter3d_single(flower, 0, 'red', 'Flor'),
            go.Scatter3d(
                x=data['x'], y=data['y'], z=data['z'],
                mode='lines',
                marker=dict(size=0, color='brown'), line=dict(width=0.1),
                name='Trayectoria', showlegend=False
            ),
        ]
    )

    # Agrego los frames
    bef = [go.Frame(
        data=[
            create_scatter3d_anim(bat_bef, k, 'black', 'Aproximación'),
            create_scatter3d_anim(flower_bef, k, 'red', 'Flor', showlegend=False)
        ]
        ) for k in range(len(bat_bef))
    ]

    fee = [go.Frame(
        data=[
            create_scatter3d_anim(bat_fee, k, 'blue', 'Alimentación'),
            create_scatter3d(flower_bef, 'red', 'Flor', showlegend=False),
            create_scatter3d_single(flower_bef, -1, 'red', 'Flor', showlegend=False),
            create_scatter3d(bat_bef, 'black', 'Aproximación'),
            create_scatter3d_single(bat_bef, -1, 'black', 'Murciélago', showlegend=False)
        ]
    ) for k in range(len(bat_fee))]

    # aft = []
    aft = [go.Frame(
        data=[
            create_scatter3d_anim(bat_aft, k, 'black', 'Alejamiento'),
            create_scatter3d_anim(flower_aft, k, 'red', 'Flor', showlegend=False),
            create_scatter3d(flower_bef, 'red', 'Flor', showlegend=False),
            create_scatter3d_single(flower_bef, -1, 'red', 'Flor', showlegend=False),
            create_scatter3d(bat_bef, 'black', 'Aproximación'),
            create_scatter3d_single(bat_bef, -1, 'black', 'Murciélago', showlegend=False),
            create_scatter3d(bat_fee, 'blue', 'Alimentación'),
            create_scatter3d_single(bat_fee, -1, 'blue', 'Alimentación', showlegend=False)
        ]
    ) for k in range(len(bat_aft))]

    fig.frames = bef + fee + aft

    # Configurar el diseño del gráfico
    fig.update_layout(
        scene=dict(
            xaxis_title='x',
            yaxis_title='y',
            zaxis_title='z',
            xaxis=dict(showticklabels=False, dtick=50, backgroundcolor="lightblue", gridwidth=0.5),
            yaxis=dict(showticklabels=False, dtick=50, backgroundcolor="lightblue", gridwidth=0.5),
            zaxis=dict(showticklabels=False, dtick=50, backgroundcolor="lightblue", gridwidth=0.5)
        ),
        title='Trayectoria 3D',
        updatemenus=[dict(
                type="buttons", 
                y=1.5, x=0.8, xanchor='left', yanchor='bottom',
                buttons=[
                    dict(
                        label='Play', method='animate',
                        args=[None, dict(frame=dict(duration=200, redraw=True))]
                    )
                ]
        )],
    )

    # Show the plot
    fig.show()