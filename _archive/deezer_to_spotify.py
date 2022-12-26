import requests

# Set the client ID and redirect URI for your application
client_id = ''
redirect_uri = ''
DEEZER_APP_SECRET = ''

# Set the permissions that your application is requesting
perms = 'basic_access,email'

# Set the API endpoint for requesting an authorization code
auth_endpoint = 'https://connect.deezer.com/oauth/auth.php'

# Set the parameters for the request
params = {
    'app_id': client_id,
    'redirect_uri': redirect_uri,
    'perms': perms
}

# Send the request to the API
response = requests.get(auth_endpoint, params=params)
print(response.text)

# Check the status code of the response
if response.status_code == 200:
    # If the request was successful, parse the authorization code from the response
    auth_response = response.json()
    auth_code = auth_response['code']
else:
    # If the request was not successful, handle the error
    print('An error occurred: {}'.format(response.status_code))

# SPOTIFY_CLIENT_ID = ''
# SPOTIFY_CLIENT_SECRET = ''

# def get_spotify_link(deezer_link):
#   track_id = deezer_link.split('/')[-1]
#   client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
#   sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
#   results = sp.track(track_id)
#   return results['external_urls']['spotify']

# deezer_link = 'https://deezer.page.link/h2zBJAbsQPWYxHay6'
# spotify_link = get_spotify_link(deezer_link)
# print(spotify_link)