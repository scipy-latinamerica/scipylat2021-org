import os
import json

from dataclasses import dataclass
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


FONT_1 = ImageFont.truetype('fonts/Poppins-Bold.ttf', 38)
FONT_2 = ImageFont.truetype('fonts/Poppins-Medium.ttf', 30)


@dataclass
class Talk:
    author: str
    author_avatar: str
    title: str
    description: str

    @property
    def banner_title():
        pass


def split_text(limite, texto):
    if len(texto) < limite:
        return texto

    texto_completo = []
    linha = ''
    for palavra in texto.split(' '):
        if len(palavra) + len(linha) < limite-1:
            linha = f"{linha}{palavra} "
        else:
            texto_completo.append(linha)
            linha = palavra

    texto_completo.append(linha)
    return '\n'.join(texto_completo)


def create_instagram_banner(talk: Talk, output='talks-instagram-banners'):

    art = Image.open('background-instagram.png')
    mask = Image.open('background-instagram-mask.png').resize((753, 753)).convert('L')
    photo = Image.open(talk.author_avatar).resize(mask.size)

    draw = ImageDraw.Draw(art)
    draw.text((66, 216), talk.author, ('#5c1dff'), font=FONT_1)
    draw.text((66, 307), split_text(30, talk.description)[:295], ('#5c1dff'),
              font=FONT_2, spacing=10)
    talk_title = split_text(44, " " * 17 + talk.title)
    draw.text((66, 790), talk.title, ('#5c1dff'), font=FONT_1)

    file_name = '../{}/{}_{}.png'.format(
        output, talk.author.lower(), talk_title.strip()
    ).replace(" ", "-")

    art.paste(photo, (597, 94), mask)
    art.save(file_name)


def create_twitter_banner(talk: Talk, output='talks-twitter-banners'):
    art = Image.open('background-twitter.png')
    mask = Image.open('background-twitter-mask.png').resize((753, 753)).convert('L')
    photo = Image.open(talk.author_avatar).resize(mask.size)

    draw = ImageDraw.Draw(art)
    draw.text((66, 216), talk.author, ('#5c1dff'), font=FONT_1)
    draw.text((66, 307), split_text(30, talk.description)[:295], ('#5c1dff'),
              font=FONT_2, spacing=10)
    talk_title = split_text(44, " " * 17 + talk.title)
    draw.text((66, 790), talk.title, ('#5c1dff'), font=FONT_1)

    file_name = '../{}/{}_{}.png'.format(
        output, talk.author.lower(), talk_title.strip()
    ).replace(" ", "-")

    art.paste(photo, (597, 94), mask)
    art.save(file_name)


if __name__ == '__main__':

    banner_paths = [
        'talks-twitter-banners',
        'talks-instagram-banners'
    ]
    for path in banner_paths:
        os.makedirs(f'../{path}/', exist_ok=True)

    with open("../programacao.json", 'r') as f:
        programacao = json.load(f)

    for talk in [Talk(**item) for item in programacao]:
        try:
            create_instagram_banner(talk)
            create_twitter_banner(talk)
        except Exception as e:
            raise e
