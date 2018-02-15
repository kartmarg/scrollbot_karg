from threading import Timer,Thread,Event
import json
import socket
import time
import urllib
from sys import exit
import math

try:
    from PIL import Image
except ImportError:
    exit("This script requires the pillow module\nInstall with: sudo pip install pillow")

try:
    import scrollphathd
except ImportError:
    exit("This script requires the scrollhatphd module\Install with: curl https://get.pimoroni.com/scrollphathd | bash")

try:
    import tweepy
    from tweepy import OAuthHandler
except ImportError:
    exit("This script requires tweepy to be installed \nInstall with: sudo pip install tweepy")

try:
    import requests
except ImportError:
    exit("This script requires requests to be installed \nInstall with: sudo pip install requests")

from scrollphathd.fonts import font5x5

global Show_Mouth
global Consumer_Key
global Consumer_Secret
global Access_Token
global Access_Secret
global hashtag
global IMAGE_BRIGHTNESS
global img

IMAGE_BRIGHTNESS = 0.3
img = Image.open("mouth.bmp")
hashtag = "#mkscrollbot"
Show_Mouth = True
Consumer_Key = "zKY68rSx4pJ6AmNAzPvmDsuBz"
Consumer_Secret = "iVRA2fa4vYcbZ3nOY29HQ915Da9BreSuD1MkK2Gup7LcVNSnaa"
Access_Token = "144020900-h1FKItyGrX8B3h6IBzP0mGnryqLuuG6kXCNqmw2l"
Access_Secret = "nmQBqhsHkYPU8Ky0s7sORs7ebPwT0eX9wIAtn07YcYlwa"

class perpetualTimer():
   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

def Hashtag_Search():
    if True:
        auth = OAuthHandler(Consumer_Key,Consumer_Secret)
        auth.set_access_token(Access_Token,Access_Secret)

        api = tweepy.API(auth)

        qtweet = tweepy.Cursor(api.search, q=hashtag).items(1)

        for tweet in qtweet:
            return "         " + (str(tweet.text)).replace(hashtag," ")
    else:
        return False

def print_hashtag():
    hashtag = Hashtag_Search()
    if hashtag != False:
        for x in range(0, 3):
            scroll_message(hashtag)

def get_pixel(x, y):
    p = img.getpixel((x, y))

    if img.getpalette() is not None:
        r, g, b = img.getpalette()[p:p+3]
        p = max(r, g, b)

    return p / 255.0

def get_location():
    res = requests.get('http://ipinfo.io')
    if(res.status_code == 200):
        json_data = json.loads(res.text)
        return json_data
    return {}

def encode(qs):
    val = ""
    try:
        val = urllib.urlencode(qs).replace("+","%20")
    except:
        val = urllib.parse.urlencode(qs).replace("+", "%20")
    return val

def get_weather(address):
    base = "https://query.yahooapis.com/v1/public/yql?"
    query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text=\""+address+"\")"
    qs={"q": query, "format": "json", "env": "store://datatables.org/alltableswithkeys"}

    uri = base + encode(qs)                                        

    res = requests.get(uri)
    if(res.status_code==200):
        json_data = json.loads(res.text)
        return json_data
    return {}

def f_c(farenheit):
    return math.floor((farenheit - 32)*.5556)

def print_weather():
    location = get_location()
    location_string = location["city"] +", " + location["country"]
    print("Location: " + location_string)

    if(location["city"] != None):
        weather = get_weather(location_string)
        output = "        "
        for x in range(0, 2):
            item = weather["query"]["results"]["channel"]["item"]["forecast"][x]
            output = output + " " +  item["day"] +": " + item["text"] + " - L: "+ str(f_c(int(item["low"]))) + "C - H: "+ str(f_c(int(item["high"]))) + "C"

        print(output)
        scroll_message(output)
        return True
    else:
        return False

def clock():
    scrollphathd.clear()
    scrollphathd.show()
    scrollphathd.write_string(
        time.strftime("%H:%M"),
        x=0,
        y=0,
        font=font5x5,
        brightness=IMAGE_BRIGHTNESS
    )
    scrollphathd.show()
    time.sleep(15)

def scroll_message(message):
    scrollphathd.clear()
    scrollphathd.show()
    message_length = scrollphathd.write_string(message, x=0, y=0,brightness=IMAGE_BRIGHTNESS)
    while message_length > 0:
        scrollphathd.show()
        scrollphathd.scroll(1)
        message_length -= 1
        time.sleep(0.04)
    scrollphathd.clear()
    scrollphathd.show()
    time.sleep(0.25)

def Robot_Mouth():
    for x in range(0, scrollphathd.DISPLAY_WIDTH):
        for y in range(0, scrollphathd.DISPLAY_HEIGHT):
            brightness = get_pixel(x, y)
            scrollphathd.pixel(x, 6-y, brightness * IMAGE_BRIGHTNESS)

    start_time = time.time()
    last_weather_time = start_time
    last_tweet_time = start_time
    last_clock_time = start_time

    while Show_Mouth:
        scrollphathd.show()
        time.sleep(0.03)
        scrollphathd.scroll(-1)

        if time.time() - last_clock_time > (30):
            scrollphathd.clear()
            scrollphathd.show()
            clock()
            last_clock_time = time.time()
            for x in range(0, scrollphathd.DISPLAY_WIDTH):
                for y in range(0, scrollphathd.DISPLAY_HEIGHT):
                    brightness = get_pixel(x, y)
                    scrollphathd.pixel(x, 6-y, brightness * IMAGE_BRIGHTNESS)

        if time.time() - last_weather_time > (30*60):
            scrollphathd.clear()
            scrollphathd.show()
            print_weather()
            last_weather_time = time.time()
            for x in range(0, scrollphathd.DISPLAY_WIDTH):
                for y in range(0, scrollphathd.DISPLAY_HEIGHT):
                    brightness = get_pixel(x, y)
                    scrollphathd.pixel(x, 6-y, brightness * IMAGE_BRIGHTNESS)


        if time.time() - last_tweet_time > (5 * 60):
            scrollphathd.clear()
            scrollphathd.show()
            print_hashtag()
            last_tweet_time = time.time()
            for x in range(0, scrollphathd.DISPLAY_WIDTH):
                for y in range(0, scrollphathd.DISPLAY_HEIGHT):
                    brightness = get_pixel(x, y)
                    scrollphathd.pixel(x, 6-y, brightness * IMAGE_BRIGHTNESS)

    scrollphathd.clear()
    scrollphathd.show()

def main():
    scrollphathd.rotate(degrees=180)

    Robot_Mouth()

if __name__ == '__main__':
    main()
