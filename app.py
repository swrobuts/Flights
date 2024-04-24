import dash
import dash_bootstrap_components as dbc
from dash import html

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(style={'backgroundColor': '#ffffff', 'color': '#333333'}, children=[
    dbc.Navbar(
        dbc.Container(
            [
                html.Div(style={'width': '60px'}),  # Kleiner Platzhalter für das Icon, falls benötigt
                dbc.Nav(
                    [
                        dbc.DropdownMenu(
                            [
                                dbc.DropdownMenuItem(page["name"], href=page["path"], style={'color': '#333333'})
                                for page in dash.page_registry.values()
                                if page["module"] != "pages.not_found_404"
                            ],
                            nav=True,
                            in_navbar=True,
                            label="More Pages",
                            align_end=True,  # Menü auf der rechten Seite
                            style={'color': '#333333'}
                        )
                    ],
                    className="ms-auto",  # Navigationslinks auf der rechten Seite
                    navbar=True,
                    style={'color': '#333333'}
                ),
            ],
            fluid=True,  # Container geht über die volle Breite
        ),
        color="light",
        dark=False,
        style={'backgroundColor': '#ffffff', 'color': '#333333', 'marginBottom': '1px'},  # Kontrolle über den unteren Rand
    ),
    dbc.Container(
        [dash.page_container],
        fluid=True,
        style={'backgroundColor': '#ffffff', 'color': '#333333'}
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
