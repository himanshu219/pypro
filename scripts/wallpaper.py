import requests
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
from optparse import OptionParser
import sys
import json

BASE_WALLPAPER='/home/himanshu/Pictures/basewallpaper.png'
OUTPUT_WALLPAPER='/home/himanshu/Pictures/mywallpaper.png'
FONT_DIR='/usr/share/fonts/truetype/open-sans-elementary/'

def get_quote():
    try:
        resp = requests.get('http://quotes.rest/qod.json')
        data = resp.json()
        quote = resp.json()['contents']['quotes'][0]['quote']
        author = resp.json()['contents']['quotes'][0]['author']
        category = resp.json()['contents']['quotes'][0]['category']
        print '%s -- %s ( %s )' % (quote, author, category)
        return quote, author
    except:
        return 'I think it is often easier to make progress on mega-ambitious dreams. Since no one else is crazy enough to do it, you have little competition. In fact, there are so few people this crazy that I feel like I know them all by first name.', 'Larry Page'

def split_quotes(quote, nsw):
    quote = quote.decode('utf-8', 'ignore')
    res = []
    #import pdb;pdb.set_trace()
    while len(quote) > 0:
        sq = quote.split(' ', nsw)
        quote = sq[-1:][0] if len(sq) > 10 else ''
        res.append(' '.join(sq[:min(10, len(sq))]))
    print res
    return res

def draw_image(quotelines, author, fs, x, y, aw, ft='OpenSans-BoldItalic.ttf'):    
    isagree = raw_input('Do you want to change the quote y/n')
    if isagree:     
        img = Image.open(BASE_WALLPAPER)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        if x == -1:
            x = width/2
        if aw == -1:
            aw = width/2
        font = ImageFont.truetype(FONT_DIR+ft, fs)
        for i,qt in enumerate(quotelines):
            draw.text((x, y+i*fs*2),qt,(255,255,255),font=font)
        
        #todo author
        draw.text((x+aw-len(author)-3, y+(i+1)*fs*2),'---%s'%(author),(255,255,255),font=font)

        img.save(OUTPUT_WALLPAPER)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-x", type="int", dest="x",
                  help="enter x coordinate", action="store", default=-1)
    parser.add_option("-y", type="int", dest="y",
                  help="enter y coordinate", action="store", default=130)
    parser.add_option("-n", type="int", dest="n",
                  help="enter no of split words", action="store", default=10)
    parser.add_option("-s", type="int", dest="s",
                  help="enter font size", action="store", default=30)
    parser.add_option("-a", type="int", dest="a",
                  help="enter font size", action="store", default=-1)
    parser.add_option("-c", dest="custom",
                  help="custom author & quote", action="store_true", default=False)
    (options, args) = parser.parse_args(sys.argv[1:])

    fs = options.s
    x = options.x
    y = options.y
    nsw = options.n
    aw = options.a
    #ft = str(sys.argv[5]) if len(sys.argv) > 5 else 'OpenSans-BoldItalic.ttf'
    #import pdb;pdb.set_trace()
    if not options.custom:
        quote, author = get_quote()
    else:
        quote = raw_input('Enter Quote:')
        author = raw_input('Enter Author:')
    quotelines = split_quotes(quote, nsw)
    draw_image(quotelines, author, fs, x, y, aw)
