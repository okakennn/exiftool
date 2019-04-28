import sys, os
from fractions import Fraction
from PIL import Image, ExifTags, ImageDraw, ImageFont
from PIL.ExifTags import TAGS, GPSTAGS

class ExifDataObj(object):
    # Exifデータ格納用オブジェクト
    # コンストラクタ
    def __init__(self, filename):
        self.filename = filename
        self.Model = None   
        self.LensModel = None
        self.ExposureTime = None
        self.FNumber = None
        self.ISOSpeedRatings = None


def get_exif(filePath):#指定されたjpgのExifを取得

    img = Image.open(filePath)
    exif = img._getexif()

    exifData = ExifDataObj(filePath)

    for id, value in exif.items():
        if TAGS.get(id) == "Model":
            exifData.Model = value
        elif TAGS.get(id) == "LensModel": 
            exifData.LensModel = str(value)
        elif TAGS.get(id) == "ExposureTime":
            shutter = str(Fraction(value[0], value[1]))
            exifData.ExposureTime = shutter
        elif TAGS.get(id) == "FNumber":
            fn = str(value[0]/value[1])
            exifData.FNumber = fn
        elif TAGS.get(id) == "ISOSpeedRatings":
            exifData.ISOSpeedRatings = str(value)

    return exifData

argvs = sys.argv 
my_img = argvs[1] #引数から写真のパスを取得
exifData = get_exif(my_img)
#書き込み文字列整理 ex)ILCE-7M2, FE 24-105mm F4 G OSS, 1/2000, f/4.0, ISO100
ExifStr = exifData.Model + ", " + exifData.LensModel + ", " \
        + exifData.ExposureTime + "s, f/" + exifData.FNumber + ", ISO" \
            + exifData.ISOSpeedRatings + ", photo by okaken"
print (ExifStr)

base = Image.open(my_img).convert('RGBA')
fonts = '/root/.fonts/AppleGothic.ttf'  #フォントパス指定
fontsize = 80  #文字の大きさ
opacity = 192  #文字の透明度
color = (255, 255, 255)  #文字の色

txt = Image.new('RGBA', base.size, (255, 255, 255, 0))
draw = ImageDraw.Draw(txt)
fnt = ImageFont.truetype(font=fonts, size=fontsize)
textw, texth = draw.textsize(ExifStr, font=fnt)
#左隅に文字を書き込む
draw.text((0, base.height - texth),ExifStr, font=fnt, fill=color + (opacity,))
out = Image.alpha_composite(base, txt)
out = out.convert('RGB')

#ファイル名にex_を付与してJPG書き出し
outFileName = 'ex_' + os.path.basename(my_img)
out.save(os.path.dirname(my_img) + '/' + outFileName, 'JPEG', quality=95, optimize=True)