import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import corr_small_multiples_with_ts, pair_plot_with_ts

app.layout = html.Div([
    dcc.Tabs(id="tabs-example",
             value='/apps/corr_small_multiples_with_ts',
             children=[
                dcc.Tab(label='Tab One',
                value='/apps/corr_small_multiples_with_ts'),
                dcc.Tab(label='Tab Two',
                value='/apps/pair_plot_with_ts'),
    ]),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('tabs-example', 'value')])
def display_page(pathname):
    if pathname == '/apps/corr_small_multiples_with_ts':
        return corr_small_multiples_with_ts.layout
    elif pathname == '/apps/pair_plot_with_ts':
        return pair_plot_with_ts.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)