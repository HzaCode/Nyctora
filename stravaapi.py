from stravalib.client import Client
import time
from datetime import datetime, timezone

# Parameters and credentials
CLIENT_ID =  # 
CLIENT_SECRET = ''  # 
ACCESS_TOKEN = ''  #
REFRESH_TOKEN = ''  # 
TOKEN_EXPIRES_AT = ''  # 

# Convert TOKEN_EXPIRES_AT to epoch time
token_expires_at_epoch = int(datetime.strptime(TOKEN_EXPIRES_AT, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp())

# Initialize the Strava client
client = Client()
client.access_token = ACCESS_TOKEN
client.refresh_token = REFRESH_TOKEN
client.token_expires_at = token_expires_at_epoch

# Function to convert pace from meters per second to minutes per kilometer
def calculate_pace(distance_meters, moving_time_seconds):
    if moving_time_seconds == 0:
        return 0
    pace_seconds_per_km = (moving_time_seconds / distance_meters) * 1000
    return pace_seconds_per_km / 60  # Convert to minutes

# Check if the token is expired and refresh if necessary
current_time = time.time()
if current_time > client.token_expires_at:
    refresh_response = client.refresh_access_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        refresh_token=REFRESH_TOKEN
    )
    client.access_token = refresh_response['access_token']
    client.refresh_token = refresh_response['refresh_token']
    client.token_expires_at = refresh_response['expires_at']

# Fetch activities
activities = client.get_activities(limit=100)  

running_data = []

for activity in activities:
    if activity.type == 'Run':  # Filter for running activities
        date = activity.start_date_local.strftime('%Y/%m/%d')
        distance = activity.distance.magnitude / 1000.0  # Convert meters to kilometers
        duration = activity.moving_time.seconds / 60  # Convert seconds to minutes
        pace = calculate_pace(activity.distance.magnitude(), activity.moving_time.seconds)
        
        running_data.append({
            'date': date,
            'distance': distance,
            'duration': duration,
            'pace': pace
        })

# Output the collected running data
for run in running_data:
    print(run)
