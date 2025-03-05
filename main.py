import gi
import os
import pprint
import requests
from io import BytesIO

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gio

from ytdl.single import YouTubeSingle


class MainWindow(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="YouTube Downloader")
        self.set_default_size(400, 300)

        # Main vertical box layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Status label
        self.label = Gtk.Label(label="Quick Downloader")
        vbox.pack_start(self.label, False, False, 4)

        # URL entry field
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter YouTube URL...")
        vbox.pack_start(self.entry, False, False, 4)

        # Search button to fetch thumbnail


        # Download thumbnail button (hidden initially)




        # Apply CSS for red background on download video button
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
            button#download_video {
                background: red;
                color: white;
            }
        """)

        self.search_button = Gtk.Button(label="Search Thumbnail")
        self.search_button.connect("clicked", self.get_thumbnails)
        vbox.pack_start(self.search_button, False, False, 4)
        self.search_button.set_name("download_video")
        context = self.search_button.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


        self.download_button = Gtk.Button(label="Download YouTube Thumbnail")
        self.download_button.set_visible(False)  # Hidden until thumbnail is fetched
        self.download_button.connect("clicked", self.download_thumbnail)
        vbox.pack_start(self.download_button, False, False, 4)
        self.download_button.set_name("download_video")
        context = self.download_button.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Download video button (hidden initially, styled with CSS)
        self.download_button1 = Gtk.Button(label="Download YouTube Video")
        self.download_button1.set_visible(False)  # Hidden until thumbnail is fetched
        self.download_button1.connect("clicked", self.download_video)
        vbox.pack_start(self.download_button1, False, False, 4)
        self.download_button1.set_name("download_video")  # Set a name for CSS targeting
        context = self.download_button1.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Thumbnail display
        self.thumbnail = Gtk.Image()
        vbox.pack_start(self.thumbnail, False, False, 4)

        self.thumbnail_url = None  # Store the URL for downloading later
        self.video_url = None  # Store the video URL

        self.show_all()

    def get_thumbnails(self, event) -> None:
        text = self.entry.get_text().strip()
        pprint.pprint(f"Fetching thumbnail for: {text}")

        try:
            if not text:
                raise ValueError("No URL provided")

            # Update UI to show searching state
            self.label.set_text("Searching...")
            self.search_button.set_sensitive(False)  # Disable search button during fetch

            downloader = YouTubeSingle()
            self.thumbnail_url = downloader.get_thumbnail(text)  # Store thumbnail URL
            self.video_url = text  # Store the original video URL
            pprint.pprint(f"Thumbnail URL: {self.thumbnail_url}")

            # Fetch image data directly from the URL
            response = requests.get(self.thumbnail_url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch thumbnail: HTTP {response.status_code}")

            # Convert raw image data into a Pixbuf
            image_data = response.content
            loader = GdkPixbuf.PixbufLoader()
            loader.write(image_data)
            loader.close()
            pixbuf = loader.get_pixbuf()

            # Set the Pixbuf to the Gtk.Image widget
            self.thumbnail.set_from_pixbuf(pixbuf)
            self.thumbnail.queue_draw()

            # Update UI on success
            self.label.set_text("Thumbnail Found")
            self.download_button.set_visible(True)  # Show thumbnail download button
            self.download_button1.set_visible(True)  # Show video download button
            print(f"✅ Thumbnail loaded from URL: {self.thumbnail_url}")

        except Exception as e:
            self.label.set_text(f"Error: {str(e)}")
            self.thumbnail.clear()  # Clear the image on error
            self.download_button.set_visible(False)  # Hide download buttons
            self.download_button1.set_visible(False)
            print(f"❌ Error fetching thumbnail: {e}")

        finally:
            self.search_button.set_sensitive(True)  # Re-enable search button

    def download_thumbnail(self, event) -> None:
        """Save the thumbnail to disk when the download button is clicked."""
        if not self.thumbnail_url:
            self.label.set_text("No thumbnail to download")
            return

        try:
            response = requests.get(self.thumbnail_url, timeout=10)
            if response.status_code == 200:
                video_id = (self.thumbnail_url.split("/vi/")[1].split("/")[0]
                            if "/vi/" in self.thumbnail_url else "thumbnail")
                image_path = f"{video_id}_thumbnail.jpg"
                with open(image_path, "wb") as f:
                    f.write(response.content)
                self.label.set_text(f"Saved to {image_path}")
                print(f"✅ Thumbnail saved to: {image_path}")
            else:
                raise Exception(f"Download failed: HTTP {response.status_code}")
        except Exception as e:
            self.label.set_text(f"Download error: {str(e)}")
            print(f"❌ Error downloading thumbnail: {e}")

    def download_video(self, event) -> None:
        """Save the video to disk when the download button is clicked."""
        if not self.video_url:
            self.label.set_text("No video URL to download")
            return

        try:
            downloader = YouTubeSingle()
            downloader.download_highest(url=self.video_url)  # Call method on instance
            self.label.set_text("Highest Resolution Video Downloaded")
            print(f"✅ Highest Resolution Video Downloaded from: {self.video_url}")
        except Exception as e:
            self.label.set_text(f"Video download error: {str(e)}")
            print(f"❌ Error downloading video: {e}")

if __name__ == "__main__":
    window = MainWindow()
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()