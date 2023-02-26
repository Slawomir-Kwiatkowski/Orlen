import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def fetch_data(product_id, current_date):
        url = f'https://tool.orlen.pl/api/wholesalefuelprices/'\
                    f'ByProduct?productId={product_id}'\
                        f'&from=2000-01-01'\
                            f'&to={current_date}'
        try:
            response = requests.get(url)
        except requests.RequestException:
            return None
        else:
            return response.json()

def json_to_df(data):
    df = pd.json_normalize(data)
    df = df[['effectiveDate', 'value']]
    df['effectiveDate'] = pd.to_datetime(df['effectiveDate'])
    df['value'] = df['value'].astype(int)
    df.set_index(df['effectiveDate'], inplace=True)
    df.sort_index(inplace=True)
    return df

def draw_chart():
    fig, ax = plt.subplots()
    ax.set_title(f'Orlen - Wholesale prices: {self.fuel} [zł/m3] - {year} rok')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    fig.autofmt_xdate()
    ax.grid(True)
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))
    textstr='(c) S.Kwiatkowski'
    props = dict(boxstyle='round', alpha=0.5)
    ax.plot(dates, prices, c='#CA3F62')
    ax.text(0.8, 0.95, textstr, transform=ax.transAxes, fontsize=8,
        verticalalignment='top', bbox=props)
    canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)