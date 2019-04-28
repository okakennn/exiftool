import sys, os, json
from fractions import Fraction
from PIL import Image, ExifTags, ImageDraw, ImageFont
from PIL.ExifTags import TAGS, GPSTAGS

# python main.py /PATH/TO/PICTURE.jpg

STANDARD_HEIGHT_HORIZONTAL = 4000 #横向き写真の基準縦ピクセル
STANDARD_HEIGHT_VERTICAL = 6000 #縦向き写真の基準縦ピクセル

MARGIN = 30 #基準マージン

FONT_PATH = './var/fonts/SourceHanSansJP-Normal.otf' #フォントパス
FONT_SIZE = 60 #基準フォントサイズ
FONT_OPACITY = 100 #フォント透明度
FONT_COLOR_WHITE = (255, 255, 255) #フォントカラー（白）
FONT_COLOR_BLACK = (0, 0, 0) #フォントカラー（黒）

PHOTOGRAPHER_NAME = 'okaken'

CAMERA_NAME_LIST = './cameraNameList.json'
LENS_NAME_LIST = './lensNameList.json'

OUTPUT_FILE_PREFIX = 'ex_'
OUTPUT_QUALITY = 100

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


def is_vertical_composition(image): #写真が縦構図であればTrue
    if(image.height > image.width):
        return True
    else:
        return False


def detect_camera_name(model): #カメラ名リストを読み込み、型番からカメラ名を返す
    f = open(CAMERA_NAME_LIST, 'r')
    cameraNameList = json.load(f)
    if(model in cameraNameList):
        return cameraNameList[model]["maker"]  + " " +  cameraNameList[model]["name"]
    else: #リストに該当するモデルが存在しないとき
        return model


def detect_lens_name(lensModel): #レンズ名リストを読み込み、型番からレンズ名を返す
    f = open(LENS_NAME_LIST, 'r')
    lensNameList = json.load(f)
    if(lensModel in lensNameList):
        return lensNameList[lensModel]["name"]
    else: #リストに該当するモデルが存在しないとき
        return lensModel     


argvs = sys.argv 
my_img = argvs[1] #引数から写真のパスを取得
exifData = get_exif(my_img)
ExifStr = detect_camera_name(exifData.Model) + ", " + detect_lens_name(exifData.LensModel) + ", " \
        + exifData.ExposureTime + ", f/" + exifData.FNumber + ", ISO" \
            + exifData.ISOSpeedRatings + ", Photo by " + PHOTOGRAPHER_NAME

base = Image.open(my_img).convert('RGBA')
txt = Image.new('RGBA', base.size, (255, 255, 255, 0))
draw = ImageDraw.Draw(txt)
font = ImageFont.truetype(font=FONT_PATH, size=FONT_SIZE)
textw, texth = draw.textsize(ExifStr, font=font)

#左隅に文字を書き込む
draw.text((MARGIN, base.height - texth - MARGIN),ExifStr, font=font, fill=FONT_COLOR_WHITE + (FONT_OPACITY,))
out = Image.alpha_composite(base, txt)
out = out.convert('RGB')

#JPG書き出し
outFileName = OUTPUT_FILE_PREFIX + os.path.basename(my_img)
out.save(os.path.dirname(my_img) + '/' + outFileName, 'JPEG', quality=OUTPUT_QUALITY, optimize=True)