from datetime import datetime, timedelta
import pandas as pd
from django.http import JsonResponse
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from django.shortcuts import render, redirect
from .models import VolatilityChat
from django.db import connections

def calculate_supertrend(df, period=1, multiplier=3):
    # Convert all relevant columns to float for calculations
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)

    df['hl2'] = (df['high'] + df['low']) / 2
    df['atr'] = (df['high'].rolling(window=period).max() - df['low'].rolling(window=period).min()) / 2
    df['upper_band'] = df['hl2'] + (multiplier * df['atr'])
    df['lower_band'] = df['hl2'] - (multiplier * df['atr'])

    supertrend = pd.Series([True] * len(df))
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['upper_band'].iloc[i - 1]:
            supertrend.iloc[i] = True
        elif df['close'].iloc[i] < df['lower_band'].iloc[i - 1]:
            supertrend.iloc[i] = False
        else:
            supertrend.iloc[i] = supertrend.iloc[i - 1]
            df.loc[i, 'lower_band'] = min(df['lower_band'].iloc[i], df['lower_band'].iloc[i - 1])
            df.loc[i, 'upper_band'] = max(df['upper_band'].iloc[i], df['upper_band'].iloc[i - 1])

    df['supertrend'] = df['lower_band'].where(supertrend, df['upper_band'])
    df['trend_direction'] = supertrend

    return df

def table_exists(table_name):
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = %s",
                       [connections['default'].settings_dict['NAME'], table_name])
        return cursor.fetchone()[0] > 0

def check_table_exists_and_return_name(now, max_checks=20):
    for _ in range(max_checks):
        table_name = now.strftime('%Y%m%d')
        if table_exists(table_name):
            return table_name
        now -= timedelta(days=1)
    return None

def chart_view(request):
    now = datetime.now()
    table_name = check_table_exists_and_return_name(now)

    if not table_name:
        return render(request, 'core/chart.html', {'message': 'There is no table available'})

    VolatilityModel = VolatilityChat.for_table(table_name)
    data = VolatilityModel.objects.all().order_by('date', 'time')
    date_filter = request.GET.get('date', '')
    symbol_filter = request.GET.get('symbol', '')

    if date_filter:
        try:
            date_filter = datetime.strptime(date_filter, '%Y%m%d').strftime('%Y-%m-%d')
        except ValueError:
            date_filter = ''
    if date_filter:
        data = data.filter(date=date_filter)
    if symbol_filter:
        data = data.filter(symbol=symbol_filter)

    df = pd.DataFrame(list(data.values()))

    # Ensure 'datetime' is correctly formatted
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
    df = calculate_supertrend(df)

    max_high = df['high'].max()
    min_low = df['low'].min()
    center_line_value = (max_high + min_low) / 2

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.8, 0.2],  # Adjust height ratio between main chart and indicator
        vertical_spacing=0.01
    )
    fig.add_trace(go.Candlestick(
        x=df['datetime'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='Candles',
        visible='legendonly',
    ))

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

    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['indicator1_on_chart'],
        mode='lines',
        line=dict(color='orange', width=2),
        name='Supertrend'
    ))

    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['upper_band'].where(df['trend_direction']),
        mode='lines',
        line=dict(color='green', width=1),
        name='Upper Band',
        visible='legendonly'
    ))

    fig.add_trace(go.Scatter(
        x=[df['datetime'].min(), df['datetime'].max()],
        y=[center_line_value] * 2,
        mode='lines',
        line=dict(color='blue', width=1, dash='dash'),
        name='Center Line'
    ))

    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['supertrend'].where(df['trend_direction']),
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(0, 255, 0, 0.2)',
        name='Uptrend',
    ))

    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['supertrend'].where(~df['trend_direction']),
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(255, 0, 0, 0.2)',
        name='Downtrend',
    ))
    df['indicator2_on_chart'] = df['indicator2_on_chart'].astype(float)

    df['arrow_color'] = df['indicator2_on_chart'].apply(
        lambda x: 'green' if x == 1.00 else 'red' if x == 2.00 else None
    )

    df['arrow_symbol'] = df['indicator2_on_chart'].apply(
        lambda x: 'arrow-up' if x == 1.00 else 'arrow-down' if x == 2.00 else None
    )

    arrow_df = df[(df['arrow_symbol'] == 'arrow-up') | (df['arrow_symbol'] == 'arrow-down')]

    if not arrow_df.empty:
        fig.add_trace(go.Scatter(
            x=arrow_df['datetime'],
            y=arrow_df['high'],
            mode='markers',
            marker=dict(
                color=arrow_df['arrow_color'],
                size=10,
                symbol=arrow_df['arrow_symbol'],
            ),
            name='Signal Arrows'
        ))
    indicator2_df = df[df['indicator2_on_chart'] > 0]
    if not indicator2_df.empty:
        fig.add_trace(go.Scatter(
            x=indicator2_df['datetime'],
            y=indicator2_df['indicator1_in_pane_below'],
            mode='lines',
            line=dict(color='blue', width=2),  # Adjust line style
            name='Indicator2'
        ), row=2, col=1)

    fig.update_layout(
        title='VOLATILITYCHART',
        yaxis_title='Price (INR)',
        xaxis_rangeslider_visible=False,
        height=700,
        margin=dict(l=40, r=40, t=50, b=40),
    )

    chart_html = fig.to_html(full_html=False)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check for AJAX request
        return JsonResponse({'chart_html': chart_html})  # Return only char
    return render(request, 'core/chart.html', {'chart_html': chart_html})

def home(request):
    now = datetime.now()
    table_name = check_table_exists_and_return_name(now)

    if not table_name:
        return render(request, 'core/home.html', {'message': 'There is no table available'})

    volatility_chart = VolatilityChat.for_table(table_name)
    symbols = volatility_chart.objects.values('symbol').distinct()
    dates = volatility_chart.objects.values('date').distinct()

    selected_date = request.GET.get('date')
    selected_symbol = request.GET.get('symbol')

    if selected_date or selected_symbol:
        return redirect('chart', date=selected_date, symbol=selected_symbol)

    return render(request, 'core/home.html', {
        'symbols': symbols,
        'dates': dates,
        'selected_date': selected_date,
        'selected_symbol': selected_symbol,
    })