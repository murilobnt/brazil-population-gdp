import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
import pandas as pd
import math

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def fix_lat(line):
    element = line['Latitude']
    region = line['RegiaoBrasil']

    if ',' in str(element):
        return float(str(element).replace(',', '.'))

    result = element / (10**(int(math.log10(abs(element)))-1))

    if region == 'N' or region == 'NE':
        if abs(result) > 18:
            result = result / 10
        return result

    if abs(result) > 35.0:
      result = result / 10
    return result

def fix_lon(element):
    if ',' in str(element):
        return float(str(element).replace(',', '.'))
    return element / (10**(int(math.log10(abs(element)))-1))

def plot_scatter(dataframe):
    scatter = px.scatter_mapbox(dataframe,
                                lat='Latitude',
                                lon='Longitude',
                                text="LocalCidade",
                                zoom=3,
                                size='PopEstimada_2018',
                                mapbox_style='carto-positron')

    scatter.update_layout(margin={'r':0,'t':0,'l':0,'b':0})

    return scatter

df = pd.read_excel('input/Cities_Brazil_IBGE.xlsx')

df['Latitude'] = pd.to_numeric(df.apply(fix_lat, axis=1))
df['Longitude'] = pd.to_numeric(df['Longitude'].apply(fix_lon))
df['Pib_2014'] = pd.to_numeric(df['Pib_2014'].apply(lambda element: float(str(element).replace(',', '.'))))

scatter = plot_scatter(df)

pib_per_region = df[['RegiaoBrasil', 'Pib_2014']].groupby(['RegiaoBrasil'])['Pib_2014'].mean()

bar = px.bar(pib_per_region,
             x=pib_per_region.index,
             y="Pib_2014",
             text="Pib_2014",
             labels={'x':'Região'},
             color=np.arange(0, 5, 1).tolist(), color_continuous_scale=px.colors.sequential.Viridis_r,
             barmode="overlay",
             opacity=1,
             title="PIB Médio das Regiões do Brasil")


bar.update_layout(
    title_font_size=20,
    titlefont=dict(color='black'))
bar.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
bar.update_yaxes(title="PIB Médio", titlefont=dict(color='black'), tickfont=dict(color='black'))
bar.update_xaxes(titlefont=dict(color='black'), tickfont=dict(color='black'))

bar.update_layout(coloraxis_showscale=False)

app.layout = html.Div([
    html.H1("Dados Populacionais do Brasil", style={'text-align':'center', 'color':'black'}),

    dcc.Graph(
        id='population-scatter',
        figure=scatter
    ),
    dcc.Dropdown(
               id='bar-selector',
               options=[
                   {'label': 'Nordeste', 'value': 'NE'},
                   {'label': 'Norte', 'value': 'N'},
                   {'label': 'Centro Oeste', 'value': 'CO'},
                   {'label': 'Sudeste', 'value': 'SE'},
                   {'label': 'Sul', 'value': 'SUL'}
               ],
               placeholder="Região",
               style={'width':"40%"}
           ),
    dcc.Graph(
        id='pib-bar',
        figure=bar),
])

@app.callback(Output(component_id='population-scatter', component_property='figure'),
     [Input(component_id='bar-selector', component_property='value')])
def update(region):
    if region is None:
        return plot_scatter(df)

    update_scatter = df.copy()
    update_scatter = update_scatter[update_scatter.RegiaoBrasil == region]

    return plot_scatter(update_scatter)

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
