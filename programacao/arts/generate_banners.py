import os
import json
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from dateutil import parser


FONT_1 = ImageFont.truetype('fonts/SourceSansPro-SemiBold.ttf', 50)
FONT_2 = ImageFont.truetype('fonts/SourceSansPro-Regular.ttf', 48)
FONT_3 = ImageFont.truetype('fonts/Lato-Italic.ttf', 36)

COLOR_1 = "#3c3c3b"
COLOR_2 = "#00c74e"


@dataclass
class Talk:
    author: str
    title: str
    job: str
    activity_type: str
    presentation_time: datetime

    @property
    def activity_id(self):
        only_ascii = unicodedata.normalize('NFKD', self.name).encode('ascii', 'ignore').decode('ascii')
        return only_ascii.lower().replace(' ', '-')

    @property
    def conference_day(self):
        FORMAT_SCHEDULE = "%d | %b"
        return self.presentation_time.strftime(FORMAT_SCHEDULE)

    @property
    def conference_hour(self):
        FORMAT_SCHEDULE = "%H h"
        return self.presentation_time.strftime(FORMAT_SCHEDULE)

    @property
    def avatar(self):
        return f'{self.activity_id}.png'

    @property
    def author_avatar(self):
        return (f"./../avatars/{self.activity_id}/{self.avatar}")

    @property
    def first_name(self):
        names = self.author.split()
        return names[0].title()

    @property
    def last_name(self):
        names = self.author.split()
        return names[-1].title()

    @property
    def name(self):
        names = self.author.split()
        if len(names) == 1:
            return '{0}'.format(self.first_name)
        return '{0} {1}'.format(self.first_name, self.last_name)

    @property
    def author_job(self, threshold=45):
        if self.job:
            if len(self.name) + len(self.job) > threshold:
                return [f'{self.name}', f'{self.job}']
            return [f'{self.name} - {self.job}']
        return [f'{self.name}']

    @property
    def splitted_title(self, threshold=45):
        if len(self.title) < threshold:
            return [self.title]

        multiline_title = []
        line = ''
        for word in self.title.split(' '):
            if len(word) + len(line) < threshold - 1:
                line = f"{line} {word} "
            else:
                multiline_title.append(line)
                line = word

        multiline_title.append(line)
        return multiline_title


def create_instagram_banner(talk: Talk, background='background-instagram-1.png',
                            output='talks-instagram-banners'):

    resize_factor = 1.8
    art = Image.open(background)
    photo = Image.open(talk.author_avatar).convert('RGBA')
    new_size = (
        int(photo.size[0] * resize_factor),
        int(photo.size[1] * resize_factor)
    )
    photo = photo.resize(new_size)
    mask = Image.alpha_composite(
        Image.new("RGBA", photo.size),
        photo.convert('RGBA')
    )
    width, height = photo.size

    draw = ImageDraw.Draw(art)

    coors = (540, 600)
    for line in talk.splitted_title:
        text_width, text_height = draw.textsize(line, FONT_1)
        draw.text(coors, line, (COLOR_1), font=FONT_1, anchor="mm")
        coors = (coors[0], coors[1] + text_height)

    # (540, 800)
    coors = (coors[0], coors[1] + 15)
    for line in talk.author_job:
        text_width, text_height = draw.textsize(line, FONT_1)
        draw.text(coors, line, (COLOR_2), font=FONT_3, anchor="mm")
        coors = (coors[0], coors[1] + text_height)

    draw.text((90, 970), talk.activity_type.upper(), (COLOR_1), font=FONT_1, anchor="lm")
    draw.text((540, 970), talk.conference_day.upper(), (COLOR_1), font=FONT_1, anchor="mm")
    draw.text((990, 970), talk.conference_hour.upper(), (COLOR_1), font=FONT_1, anchor="rm")

    art.paste(photo, (540 - int(width / 2), 354 - int(height / 2)), mask)

    file_name = f'../{output}/{talk.activity_id}_{background}'
    art.save(file_name)


if __name__ == '__main__':

    banner_paths = [
        'talks-instagram-banners'
    ]
    for path in banner_paths:
        os.makedirs(f'../{path}/', exist_ok=True)

    with open("../programacao.json", 'r') as f:
        programacao = json.load(f)

    talks = []
    for item in programacao:
        talks.append(
            Talk(**{'author': item['full_name'],
                    'title': item['title'],
                    'job': item['job_title'],
                    'activity_type': item['activity_type'],
                    'presentation_time': parser.parse(item['presentation_time'])
                    })
        )

    for talk in talks:
        try:
            for n in range(1, 4):
                create_instagram_banner(talk, background=f'background-instagram-{n}.png')
        except Exception as e:
            raise e
