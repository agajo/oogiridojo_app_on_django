from PIL import Image, ImageDraw, ImageFont
import io
import re
import base64
import textwrap

#string型を3つ受け取り、PILのImage型を返す
def make_santen_picture(odai,answer,answer_picture=""):
  #下地
  image_offset = 0
  if(answer_picture != ""):
    image_offset = 300 - 10 #画像の縦サイズ-「回答：」の縦幅
  im = Image.new("RGB",(650,image_offset+275),"white")
  draw = ImageDraw.Draw(im)
  fnt  = ImageFont.truetype('./management/commands/sawarabi-mincho-medium.ttf',20)
  fnt2 = ImageFont.truetype('./management/commands/sawarabi-mincho-medium.ttf',15)
  fnt3 = ImageFont.truetype('./management/commands/sawarabi-mincho-medium.ttf',13)

  #お題描画
  draw.rectangle(((10,10),(640,110)),fill="pink")
  draw.text((12,12),"お題：",font=fnt2,fill="#444444")
  odai_texts = textwrap.fill(odai,width=27)
  odai_size = draw.textsize(odai_texts,font=fnt)
  draw.text((10+(630-odai_size[0])/2,15+(100-odai_size[1])/2),odai_texts,font=fnt,align="center",fill="#111122")

  #回答描画
  draw.rectangle(((10,120),(640,120+image_offset+130)),fill="#ddeeff")
  draw.text((12,122),"回答：",font=fnt2,fill="#444444")
  if(answer_picture != ""):
    image_data_bytes = re.sub('^data:image/.+;base64,','',answer_picture).encode('utf-8')
    image_data = base64.b64decode(image_data_bytes)
    im2 = Image.open(io.BytesIO(image_data))
    im.paste(im2,(190,125))
  answer_texts = textwrap.fill(answer,width=27)
  answer_size = draw.textsize(answer_texts,font=fnt)
  draw.text((10+(630-answer_size[0])/2,130+image_offset+(130-answer_size[1])/2),answer_texts,font=fnt,align="center",fill="#111122")

  #サイト情報描画
  draw.text((440,image_offset+250),"oka-ryunoske.work/oogiridojo",font=fnt3,fill="#999999")

  #出力
  return im
