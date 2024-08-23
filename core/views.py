import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from django.shortcuts import render
from .models import VolatilityChat

def calculate_supertrend(df, period=1, multiplier=3):
    # Convert 'Decimal' to 'float' for calculations
    hl2 = (df['high'].astype(float) + df['low'].astype(float)) / 2
    atr = (df['high'].rolling(window=period).max().astype(float) - df['low'].rolling(window=period).min().astype(float)) / 2

    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    supertrend = [True] * len(df)

    for i in range(1, len(df)):
        if df['close'][i] > upper_band[i - 1]:
            supertrend[i] = True
        elif df['close'][i] < lower_band[i - 1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i - 1]

            if supertrend[i] and lower_band[i] < lower_band[i - 1]:
                lower_band[i] = lower_band[i - 1]
            if not supertrend[i] and upper_band[i] > upper_band[i - 1]:
                upper_band[i] = upper_band[i - 1]

    df['supertrend'] = lower_band.where(pd.Series(supertrend), upper_band)
    df['upper_band'] = upper_band
    df['lower_band'] = lower_band
    df['hl2'] = hl2
    df['trend_direction'] = supertrend

    return df

def chart_view(request):
    data = VolatilityChat.objects.all().order_by('date', 'time')
    df = pd.DataFrame(list(data.values()))

    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
    df = calculate_supertrend(df)

    max_high = df['high'].max()
    min_low = df['low'].min()
    center_line_value = (max_high + min_low) / 2

    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df['datetime'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='Candles',
        visible='legendonly',  # Initially hidden
    ))

    # OHLC bars
    fig.add_trace(go.Ohlc(
        x=df['datetime'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='OHLC Bars',
        opacity=1
    ))

    # Supertrend Line
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['supertrend'],
        mode='lines',
        line=dict(color='orange', width=2),
        name='Supertrend'
    ))

    # Upper Band (Visible during uptrend)
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['upper_band'].where(df['trend_direction'] == True),
        mode='lines',
        line=dict(color='green', width=1),
        name='Upper Band',
        visible='legendonly'
    ))

    # Center Line (Average of max high and min low)
    fig.add_trace(go.Scatter(
        x=[df['datetime'].min(), df['datetime'].max()],
        y=[center_line_value, center_line_value],
        mode='lines',
        line=dict(color='blue', width=1, dash='dash'),
        name='Center Line (Average of Max and Min)'
    ))

    # Background Fill - Green Area (Uptrend)
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['supertrend'].where(df['trend_direction'] == True),
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(0, 255, 0, 0.2)',  # Green with transparency
        name='Uptrend',
    ))

    # Background Fill - Red Area (Downtrend)
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['supertrend'].where(df['trend_direction'] == False),
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(255, 0, 0, 0.2)',  # Red with transparency
        name='Downtrend',
    ))

    # Expanding the x-axis range
    first_date = df['datetime'].min() - pd.Timedelta(hours=1)  # Add padding on the left
    last_date = df['datetime'].max() + pd.Timedelta(hours=1)   # Add padding on the right

    fig.update_layout(
        title='VOLATILITYCHART',
        yaxis_title='Price (INR)',
        xaxis_rangeslider_visible=False,
        height=700,
        margin=dict(l=40, r=40, t=50, b=40),  # Margin to ensure no cutting
        xaxis=dict(range=[first_date, last_date]),  # Extend x-axis range to include padding
    )

    chart_html = fig.to_html(full_html=True)
    return render(request, 'core/chart.html', {'chart_html': chart_html})
