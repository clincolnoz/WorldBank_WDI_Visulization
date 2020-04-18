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
wdi_indicator_code_name_topic, wdi_country, wdi, wdi_pivot, corr_matrix, corr_matrix_sign, corr_sig_matrix = load_data()

figheight = 750

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

n_plots_lst = [1,2,4,6,9,12,16,20,25,30]

layout = html.Div([
    # html.Div([
    #     html.H1("World Bank - World Development Indicators: Indicator Correlation")
    #     ],
    #     className="row",
    #     style={'textAlign': "center"}
    # ),
    html.Div([
        html.Label('Indicator to interest'),
        dcc.Dropdown(
            id="selected-indicator-to-corr",
            options=[{"label": i, "value": i} for i in wdi_pivot.columns],
            value='Access to electricity (% of population)',
            #style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "80%"}
        ),
        html.Label('Topics to exclude'),
        dcc.Dropdown(
            id="selected-topic-to-exclude",
            options=[{"label": i, "value": i} for i in wdi_indicator_code_name_topic['topic_prefix'].fillna('NaN').unique()],
            value=['Health'],
            #style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "80%"},
            multi=True
        ),
    ],
    style={'width': '48%', 'display': 'inline-block'}),
    html.Div([
        html.Label('Number of subplots'),
        dcc.Slider(
            id = 'n_plots',
            min=min(n_plots_lst),
            max=max(n_plots_lst),
            step=None,
            marks={n: str(n) for n in n_plots_lst},
            value=9,
        ),
        # html.Br(),
        html.Label('Currently showing page:'),
        dcc.Dropdown(
            id = 'n_pages',
            # min=1,
            # max=(wdi_pivot.shape[1]-2)//12,
            #step=None,
            options=[{"label": n, "value": n} for n in range(1,np.ceil((wdi_pivot.shape[1]-2)/12).astype(int)+1)],
            value=1,
        )
        # html.Label('Number of plot pages'),
        # dcc.Slider(
        #     id = 'n_pages',
        #     min=1,
        #     max=(wdi_pivot.shape[1]-2)//12,
        #     #step=None,
        #     marks={n: str(n) for n in range(1,np.ceil((wdi_pivot.shape[1]-2)/12).astype(int)+1)},
        #     value=1,
        # )
    ],
    style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id="my-graph",
                  hoverData={'points': [{'customdata': ['School enrollment, secondary (% gross)','Niger']}]}
        )
    ], style={'display': 'inline-block', 'width': '73%'}),
    html.Div([
        dcc.Graph(id='x-time-series-corr'),
        dcc.Graph(id='y-time-series-corr'),
        #dcc.Graph(id='cmp-time-series-corr'),
    ], style={'display': 'inline-block', 'width': '23%'}),
])

@app.callback(
    [Output("n_pages", "value"),
    Output("n_pages", "max"),
    Output("n_pages", "marks"),],
    [Input("selected-topic-to-exclude", "value"),
    Input("n_plots", "value"),])
def update_plot_pages(topic_to_exclude,n_subplots):
    len_exclude_names = len(wdi_indicator_code_name_topic.loc[wdi_indicator_code_name_topic['topic_prefix'].isin(topic_to_exclude)].index)
    max_ = np.ceil((wdi_pivot.shape[1]-2-len_exclude_names)/n_subplots).astype(int)
    marks_ = {n: str(n) for n in range(1,max_+1,max_//25)}
    return 1, max_, marks_

@app.callback(
    Output("my-graph", "figure"),
    [Input("selected-indicator-to-corr", "value"),
    Input("selected-topic-to-exclude", "value"),
    Input("n_plots", "value"),
    Input("n_pages", "value"),
    Input("n_pages", "max"),
    ])
def update_figure(indicator_to_corr,topic_to_exclude,n_subplots,page_n,n_page_max):
    nrows = np.floor(np.sqrt(n_subplots)).astype(int).item()
    ncols = np.ceil(np.sqrt(n_subplots)).astype(int).item()
    sort_index = corr_matrix.sort_values(indicator_to_corr,ascending=False).index
    selected_topk=corr_matrix.loc[sort_index,sort_index].iloc[:,0]
    exclude_names = wdi_indicator_code_name_topic.loc[wdi_indicator_code_name_topic['topic_prefix'].isin(topic_to_exclude)].index
    selected_topk=selected_topk.loc[(~selected_topk.index.isin(exclude_names))|(selected_topk.index==indicator_to_corr)]
    if page_n==n_page_max:
        n_subplots_to_plot = (wdi_pivot.shape[1]-2-len(exclude_names))%(n_page_max-1)
    else:
        n_subplots_to_plot = n_subplots
    idxi = 1+(page_n-1)*n_subplots
    idxf = 1+n_subplots_to_plot+(page_n-1)*n_subplots

    subplot_titles = []
    for x in selected_topk.index[idxi:idxf]:
        if x<selected_topk.index[0]:
            psig = str(corr_sig_matrix.loc[x,selected_topk.index[0]])
            r_corr = str(corr_sig_matrix.loc[selected_topk.index[0],x])
        else:
            psig = str(corr_sig_matrix.loc[selected_topk.index[0],x])
            r_corr = str(corr_sig_matrix.loc[x,selected_topk.index[0]])
        if len(textwrap.wrap(x + '...; ' + r_corr + '; ' + psig, width=30))>3:
            subplot_titles=subplot_titles+['<br>'.join(textwrap.wrap(x,width=30)[:2] + ['...; ' + r_corr + '; ' + psig])]
        else:
            subplot_titles=subplot_titles+['<br>'.join(textwrap.wrap(x + '; ' + r_corr + '; ' + psig, width=30))]
    scatter_corr = tools.make_subplots(
        rows = nrows,
        cols = ncols,
        subplot_titles=tuple(subplot_titles),
        vertical_spacing=.1,
    )
    for idx in range(n_subplots_to_plot):
        for l,k in enumerate(wdi_pivot.Region.unique()):
            if idx==0:
                showlegend = True
            else:
                showlegend = False
            scatter_corr.add_trace(
                go.Scatter(
                    x=wdi_pivot.loc[wdi_pivot['Region']==k,selected_topk.index[idx+idxi]],
                    y=wdi_pivot.loc[wdi_pivot['Region']==k,selected_topk.index[0]],
                    text=wdi_pivot.loc[wdi_pivot['Region']==k].index,
                    customdata=[[selected_topk.index[idx+idxi], country] for country in wdi_pivot.loc[wdi_pivot['Region']==k].index],
                    mode='markers',
                    opacity=0.6,
                    marker={'size': 8, 'color':plotly_colors[l%len(plotly_colors)]},
                    legendgroup=k,
                    name=k,
                    showlegend=showlegend,
                ),
                idx//ncols+1,
                idx%ncols+1
            )
    scatter_corr['layout']['height'] = figheight
    scatter_corr['layout']['title']['text'] = selected_topk.index[0] + ' Vs ...; correlation; *** (0.001), ** (0.01), * (0.05)'
    scatter_corr['layout']['legend']['orientation'] = 'h'
    for i in scatter_corr['layout']['annotations']:
        i['font'] = dict(size=10,color='#4b4b4b')
    return scatter_corr

def create_time_series(dff, axis_type, title):
    return {
        'data': [dict(
            x=dff.columns.astype(int).values,
            y=dff.values[0],
            mode='lines+markers'
        )],
        'layout': {
            'height': figheight/2,
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
    Output('x-time-series-corr', 'figure'),
    [Input('my-graph', 'hoverData')])
def update_x_timeseries(hoverData):
    xaxis_column_name, country_name = hoverData['points'][0]['customdata']
    dff = wdi[wdi.index.get_level_values(0)==country_name].copy()
    dff = dff[dff.index.get_level_values(1)==xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    axis_type='Linear'
    return create_time_series(dff, axis_type, title)


@app.callback(
    Output('y-time-series-corr', 'figure'),
    [Input('my-graph', 'hoverData'),
     Input('selected-indicator-to-corr', 'value')])
def update_y_timeseries(hoverData, yaxis_column_name):
    country_name = hoverData['points'][0]['customdata'][1]
    dff = wdi[wdi.index.get_level_values(0)==country_name].copy()
    dff = dff[dff.index.get_level_values(1)==yaxis_column_name]
    axis_type='Linear'
    return create_time_series(dff, axis_type, yaxis_column_name)


# @app.callback(
#     Output('cmp-time-series-corr', 'figure'),
#     [Input('my-graph', 'hoverData'),
#      Input('selected-indicator-to-corr', 'value')])
# def update_cmp_timeseries(hoverData, yaxis_column_name):
#     axis_type='linear'
#     xaxis_column_name, country_name = hoverData['points'][0]['customdata']
#     dff = wdi[wdi.index.get_level_values(0)==country_name].copy()
#     dffy = dff[dff.index.get_level_values(1)==yaxis_column_name].copy()
#     dffx = dff[dff.index.get_level_values(1)==xaxis_column_name].copy()
#     dffx[dffx.index.get_level_values(1)==xaxis_column_name] = corr_matrix_sign.loc[xaxis_column_name,yaxis_column_name] * dffx[dffx.index.get_level_values(1)==xaxis_column_name]
#     title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
#     cmp_xy=tools.make_subplots(rows=1,cols=1)
#     cmp_xy.append_trace(
#         go.Scatter(
#             x=dffx.columns.astype(int).values,
#             y=dffx.values[0],
#             mode='lines+markers'
#             #name=str(xaxis_column_name),
#         ),
#         1,1,
#     )
#     cmp_xy.append_trace(
#         go.Scatter(
#             x=dffy.columns.astype(int).values,
#             y=dffy.values[0],
#             mode='lines+markers'
#             #name=str(yaxis_column_name),
#         ),
#         1,1,
#     )
#     with cmp_xy.batch_update():
#         cmp_xy.data[0].update(yaxis='y1')
#         cmp_xy.layout.update(yaxis5=dict(overlaying='y1',
#                                     side='right',
#                                     anchor='x1',
#                                     showgrid=False,
#                                     title='right title'),
#                         hovermode='closest')
#     return cmp_xy