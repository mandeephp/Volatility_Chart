# import os
# import django
# import csv
# from datetime import datetime
# from decimal import Decimal
#
# # Set the default Django settings module
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volatilitychart.settings')  # Replace with your project settings
#
# # Initialize Django
# django.setup()
#
# # Now import the model
# from core.models import VolatilityChat  # Update 'core' with your actual app name
#
# # Define the file path
# csv_file_path = 'chart_data.csv'
#
# # Function to save data from CSV to the VolatilityChat model
# def load_csv_to_model(file_path):
#     with open(file_path, mode='r') as file:
#         reader = csv.DictReader(file)
#
#         for row in reader:
#             try:
#                 # Parse the date and time
#                 date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
#                 time = datetime.strptime(row['Time'], '%H:%M:%S').time()
#
#                 # Create and save the VolatilityChat object
#                 VolatilityChat.objects.create(
#                     id=int(row['Counter']),
#                     date=date,
#                     time=time,
#                     open=Decimal(row['OpenOfCandle']),
#                     high=Decimal(row['HighOfCandle']),
#                     low=Decimal(row['LowOfCandle']),
#                     close=Decimal(row['CloseOfCandle']),
#                     indicator1_on_chart=Decimal(row['Indicator1_OnChart']) if row['Indicator1_OnChart'] else None,
#                     indicator2_on_chart=Decimal(row['Indicator2_OnChart']) if row['Indicator2_OnChart'] else None,
#                     indicator1_in_pane_below=Decimal(row['Indicator1_InPanelBelow']) if row['Indicator1_InPanelBelow'] else None,
#                     symbol=row['Symbol'],  # Save the symbol from the CSV
#                 )
#             except Exception as e:
#                 print(f"Error processing row {row}: {e}")
#
# # Run the function to load data from CSV
# load_csv_to_model(csv_file_path)
#
#
# #for create dump data
# import csv
# import random
# from datetime import datetime, timedelta
#
# # Define the file path
# file_path = 'chart_data.csv'
#
# # Helper function to generate datetime incrementing by 1 minute
# def generate_datetime_series(start, minutes_increment):
#     return start + timedelta(minutes=minutes_increment)
#
# # Define the start date and range
# start_date = datetime(2024, 8, 18, 9, 15, 0)  # Start date
# total_data_count = 300  # Generate exactly 300 rows
#
# # Open the file for writing
# with open(file_path, mode='w', newline='') as file:
#     writer = csv.writer(file)
#
#     # Write the header
#     writer.writerow([
#         'Date', 'Time', 'OpenOfCandle', 'HighOfCandle', 'LowOfCandle', 'CloseOfCandle',
#         'Indicator1_OnChart', 'Indicator2_OnChart', 'Indicator1_InPanelBelow', 'Symbol', 'Counter'
#     ])
#
#     # Generate 300 rows of data
#     for counter in range(1, total_data_count + 1):
#         # Generate the datetime for each minute increment
#         date_time = generate_datetime_series(start_date, counter - 1)
#
#         # Generate candle data
#         open_price = round(random.uniform(700, 800), 2)
#         high_price = round(random.uniform(open_price, 800), 2)  # High must be >= Open
#         low_price = round(random.uniform(400, open_price), 2)  # Low must be <= Open
#         close_price = round(random.uniform(low_price, high_price), 2)  # Close must be between Low and High
#
#         # Sequentially assign symbol (e.g., SYMBOL1, SYMBOL2, ..., SYMBOL300)
#         symbol = f"SYMBOL_{counter}"
#
#         # Create the row
#         row = [
#             date_time.strftime('%Y-%m-%d'),  # Date
#             date_time.strftime('%H:%M:%S'),  # Time
#             open_price,
#             high_price,
#             low_price,
#             close_price,
#             round(random.uniform(0, 100), 2),  # Indicator 1 on chart
#             round(random.uniform(0, 100), 2),  # Indicator 2 on chart
#             round(random.uniform(0, 100), 2),  # Indicator 1 in panel below
#             symbol,  # Symbol
#             counter  # Global counter
#         ]
#
#         # Write the row to the CSV file
#         writer.writerow(row)
#
# print(f'Generated {total_data_count} rows of dummy data saved to {file_path}')
#
