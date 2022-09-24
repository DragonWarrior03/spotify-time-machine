from bs4 import BeautifulSoup
import requests
class obtain_bill_board:
    def __init__(self,date):
        self.URL = f"https://www.billboard.com/charts/hot-100/{date}"
        self.response = requests.get(url=self.URL)
        self.webpage = self.response.text
        self.soup = BeautifulSoup(self.webpage, "html.parser")
        self.all_song_tags = self.soup.select(selector="li h3")
        self.all_artist_tags = self.soup.select(".c-label ")
        self.all_songs = []
        self.all_artists = []

        for item in self.all_song_tags:
            text = item.getText()
            text = text.replace("\n\n\t\n\t\n\t\t\n\t\t\t\t\t", "")
            text = text.replace("\t\t\n\t\n", "")
            self.all_songs.append(text)

        for item in self.all_artist_tags:
            text = item.getText()
            text = text.replace("\n\t\n\t", "")
            text = text.replace("\n", "")
            text=text.replace("%2C","")
            if text!="RE-ENTRY" and text!="NEW":
                self.all_artists.append(text)

        for n in range(6):
            for item in self.all_artists:
                if item == "NEW" or item == "-" or item.isdigit() or item.isnumeric():
                    self.all_artists.remove(item)



