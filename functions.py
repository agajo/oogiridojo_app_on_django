import random

def rkatakana():
    return chr(random.choice([x for x in range(ord(str('ァ')),ord(str('ン')))]))

def rfamilast():
    return random.choice("木元本田水山井泉内村尾上下中賀垣笠瀬川河倉蔵坂阪崎橋澤沢島嶋谷道沼浦原間宮森林")

def rfirslast():
    return random.choice("子男彦美実恵香希花菜奈江乃佳太雄樹輝明郎人斗也丸夫馬真文信伸悟次助介輔則典平")

def rname():
    return rkatakana()+rkatakana()+rfamilast()+" "+rkatakana()+rkatakana()+rfirslast()
