# Imports 
import requests
import json
import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore


def rss_call(id):
    url = 'https://itunes.apple.com/lookup'
    headers = {'id': id, 'entity': "podcast"}

    r = requests.get(url, params=headers)

    data = r.content
    data_unpacked = json.loads(data)
    podcast_data = data_unpacked['results']
    
    return(podcast_data)


def main():
    # Define firebase shit
    cred = credentials.Certificate("./ServiceAccountKey.json")
    app = firebase_admin.initialize_app(cred)

    # Make request to Tim Cook
    r = requests.get("https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/10/explicit.json")

    data = r.content
    data_unpacked = json.loads(data)
    podcasts = data_unpacked['feed']['results']

    rss_data = rss_call(podcasts[0]['id'])

    print(rss_data)

    '''
    # Yeet the data into Firebase
    for i in podcasts:
        store = firestore.client()
        doc_ref = store.collection(u'podcast_test')
        doc_ref.add(i)
    '''


if __name__ == "__main__":
    main()