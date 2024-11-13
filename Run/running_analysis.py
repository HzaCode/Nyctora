

import time
from datetime import datetime, timezone
from stravalib.client import Client

CLIENT_ID =  #  Strava Client ID
CLIENT_SECRET = ''
ACCESS_TOKEN = ''
REFRESH_TOKEN = ''
TOKEN_EXPIRES_AT = ''

MAX_HEART_RATE = 
THRESHOLD_HEART_RATE = 0.85 * MAX_HEART_RATE
RESTING_HEART_RATE = 60

def calculate_pace(distance_meters, moving_time_seconds):
    if moving_time_seconds == 0:
        return 0
    pace_seconds_per_km = (moving_time_seconds / distance_meters) * 1000
    return pace_seconds_per_km / 60

def get_token_expires_at_epoch(token_expires_at_str):
    return int(datetime.strptime(token_expires_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp())

def refresh_strava_token(client):
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

def main():
    token_expires_at_epoch = get_token_expires_at_epoch(TOKEN_EXPIRES_AT)

    client = Client()
    client.access_token = ACCESS_TOKEN
    client.refresh_token = REFRESH_TOKEN
    client.token_expires_at = token_expires_at_epoch

    refresh_strava_token(client)

    heart_rate_zones = [
        {'name': 'Zone 1', 'min': 0, 'max': 100},
        {'name': 'Zone 2', 'min': 100, 'max': 120},
        {'name': 'Zone 3', 'min': 120, 'max': 140},
        {'name': 'Zone 4', 'min': 140, 'max': 160},
        {'name': 'Zone 5', 'min': 160, 'max': 180},
    ]

    target_month = ''

    activities = client.get_activities(limit=100)

    running_data = []

    total_time_in_zones = {zone['name']: 0 for zone in heart_rate_zones}

    for activity in activities:
        if activity.type == 'Run':
            date = activity.start_date_local.strftime('%Y/%m/%d')
            activity_month = activity.start_date_local.strftime('%Y-%m')
            if activity_month != target_month:
                continue

            distance = activity.distance.num / 1000.0
            duration_seconds = activity.moving_time.seconds
            duration_minutes = duration_seconds / 60
            pace = calculate_pace(activity.distance.num, duration_seconds)

            average_heartrate = activity.average_heartrate
            average_speed = activity.average_speed.num

            # Efficiency Factor (EF)
            if average_heartrate and average_speed:
                ef = average_speed / average_heartrate
            else:
                ef = None

            # Heart Rate Reserve Percentage (HRR%)
            if average_heartrate:
                hrr_percent = (average_heartrate - RESTING_HEART_RATE) / (MAX_HEART_RATE - RESTING_HEART_RATE)
            else:
                hrr_percent = None

            # Intensity Factor (IF)
            if average_heartrate:
                if THRESHOLD_HEART_RATE != RESTING_HEART_RATE:
                    intensity_factor = (average_heartrate - RESTING_HEART_RATE) / (THRESHOLD_HEART_RATE - RESTING_HEART_RATE)
                else:
                    intensity_factor = None
            else:
                intensity_factor = None

            # hrTSS (Heart Rate Training Stress Score)
            if average_heartrate and intensity_factor and hrr_percent and intensity_factor != 0:
                hrTSS = (duration_seconds * intensity_factor * hrr_percent) / (intensity_factor * 3600) * 100
            else:
                hrTSS = None

            # Volume Intensity
            duration_hours = duration_seconds / 3600
            if average_heartrate:
                volume_intensity = duration_hours * average_heartrate
            else:
                volume_intensity = None

            # EPOC (Excess Post-exercise Oxygen Consumption) - Simplified estimate
            if average_heartrate:
                intensity = (average_heartrate - RESTING_HEART_RATE) / (MAX_HEART_RATE - RESTING_HEART_RATE)
                epoc = intensity * duration_minutes
            else:
                epoc = None

            streams = client.get_activity_streams(activity.id, types=['heartrate'], resolution='medium')
            heartrate_stream = streams.get('heartrate')

            if heartrate_stream is not None:
                heartrate_data = heartrate_stream.data
                time_per_point = duration_seconds / len(heartrate_data)

                time_in_zones = {zone['name']: 0 for zone in heart_rate_zones}

                for hr in heartrate_data:
                    for zone in heart_rate_zones:
                        if zone['min'] <= hr < zone['max']:
                            time_in_zones[zone['name']] += time_per_point
                            break

                for zone_name in total_time_in_zones:
                    total_time_in_zones[zone_name] += time_in_zones[zone_name]
            else:
                time_in_zones = {}

            running_data.append({
                'date': date,
                'distance': distance,
                'duration': duration_minutes,
                'pace': pace,
                'ef': ef,
                'hrTSS': hrTSS,
                'hrr_percent': hrr_percent,
                'intensity_factor': intensity_factor,
                'volume_intensity': volume_intensity,
                'epoc': epoc,
                'time_in_zones': time_in_zones
            })

    for run in running_data:
        print(run)

    print(f"\nTotal time spent in heart rate zones for {target_month}:")
    for zone_name, total_time in total_time_in_zones.items():
        total_minutes = total_time / 60
        print(f"{zone_name}: {total_minutes:.2f} minutes")

if __name__ == "__main__":
    main()
