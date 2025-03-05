from pytubefix import YouTube

class YouTubeSingle:
    def __init__(self) -> None:
        print("Script Started ....")

    def download_highest(self, url: str) -> None:
        try:
            yt = YouTube(url).streams.get_highest_resolution()
            yt.download(output_path='/home/jprashik/Downloads/youtube/')

        except Exception as e:
            print(e)

    def get_thumbnail(self, url: str) -> None:
        try:
            video = YouTube(url)
            thumbnail = video.thumbnail_url
            print(thumbnail)
            return thumbnail
        except Exception as e:
            print(e)