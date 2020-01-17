# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly import tools

from app import app

import os
import numpy as np
import pandas as pd
import textwrap

from load_process_data import load_data
wdi_indicator_code_name_topic, wdi_country_code_name, wdi_country, wdi, wdi_pivot, corr_matrix, corr_matrix_sign, corr_sig_matrix = load_data()

available_indicators = wdi.index.get_level_values(1).unique()
figheight = 800

plotly_colors = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]

layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='School enrollment, secondary (% gross)'
            ),
            dcc.RadioItems(
                id='crossfilter-xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='Access to electricity (% of population)'
            ),
            dcc.RadioItems(
                id='crossfilter-yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'Niger'}]}
        )
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '48%'}),

    html.Div(dcc.Slider(
        id='crossfilter-year--slider',
        min=wdi.columns.astype(int).min(),
        max=wdi.columns.astype(int).max(),
        value=2017,
        marks={str(year): str(year) for idx,year in enumerate(wdi.columns) if idx%5==0},
        step=1
    ), style={'width': '48%', 'padding': '0px 20px 20px 20px'})
])


@app.callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    [Input('crossfilter-xaxis-column', 'value'),
     Input('crossfilter-yaxis-column', 'value'),
     Input('crossfilter-xaxis-type', 'value'),
     Input('crossfilter-yaxis-type', 'value'),
     Input('crossfilter-year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    dff = wdi[str(year_value)]

    return {
        'data': [dict(
            x=dff[dff.index.get_level_values(1)==xaxis_column_name],
            y=dff[dff.index.get_level_values(1)==yaxis_column_name],
            text=dff[dff.index.get_level_values(1)==yaxis_column_name].index.get_level_values(0).values,
            customdata=dff[dff.index.get_level_values(1)==yaxis_column_name].index.get_level_values(0).values,
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': dict(
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
            height=450,
            hovermode='closest'
        )
    }


def create_time_series(dff, axis_type, title):
    return {
        'data': [dict(
            x=dff.columns.astype(int).values,
            y=dff.values[0],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }


@app.callback(
    Output('x-time-series', 'figure'),
    [Input('crossfilter-indicator-scatter', 'hoverData'),
     Input('crossfilter-xaxis-column', 'value'),
     Input('crossfilter-xaxis-type', 'value')])
def update_x_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata']
    dff = wdi[wdi.index.get_level_values(0)==country_name].copy()
    dff = dff[dff.index.get_level_values(1)==xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)


@app.callback(
    Output('y-time-series', 'figure'),
    [Input('crossfilter-indicator-scatter', 'hoverData'),
     Input('crossfilter-yaxis-column', 'value'),
     Input('crossfilter-yaxis-type', 'value')])
def update_y_timeseries(hoverData, yaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata']
    dff = wdi[wdi.index.get_level_values(0)==country_name].copy()
    dff = dff[dff.index.get_level_values(1)==yaxis_column_name]
    return create_time_series(dff, axis_type, yaxis_column_name)
