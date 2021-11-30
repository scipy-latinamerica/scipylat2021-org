#!/usr/bin/env python
# coding: utf-8

from dataclasses import dataclass
from oauth2client.service_account import ServiceAccountCredentials
from shutil import copyfile
from typing import Optional
import gspread
import json
import os
import pandas as pd
import random
import unicodedata


@dataclass
class Talk:
    author: str
    author_avatar: str
    title: str
    description: str


@dataclass
class Activity:
    id: int
    full_name: Optional[str]
    gender: Optional[str]
    ethnics: Optional[str]
    country: Optional[str]
    about_author: Optional[str]
    title: Optional[str]
    topics: Optional[str]
    description: Optional[str]
    presented_before: Optional[str]
    requirements: Optional[str]
    audience_level: Optional[str]
    language: Optional[str]
    e_mail: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    twitter: Optional[str]
    activity_type: Optional[str]
    name_or_nickname: Optional[str]
    pronouns: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    bio: Optional[str]
    timezone: Optional[str]
    presentation_time: Optional[str]
    duration: Optional[str]
    hide: Optional[str]

    @property
    def activity_id(self):
        only_ascii = unicodedata.normalize('NFKD', self.name).encode('ascii', 'ignore').decode('ascii')
        return only_ascii.lower().replace(' ', '-')

    @property
    def avatar(self):
        return f'{self.activity_id}.png'

    @property
    def avatar_hover(self):
        return f'{self.activity_id}-hover.png'

    @property
    def first_name(self):
        names = self.full_name.split()
        return names[0].title()

    @property
    def last_name(self):
        names = self.full_name.split()
        return names[-1].title()

    @property
    def name(self):
        names = self.full_name.split()
        if len(names) == 1:
            return '{0}'.format(self.first_name)
        return '{0} {1}'.format(self.first_name, self.last_name)

    @property
    def social(self):
        social = []
        if self.linkedin:
            social.append(
                "#### social ####\nsocial_network: linkedin\n----\nlink: {}\n".format(self.linkedin)
            )

        if self.github:
            social.append(
                "#### social ####\nsocial_network: github\n----\nlink: {}\n".format(self.github)
            )

        if self.twitter:
            social.append(
                "#### social ####\nsocial_network: twitter\n----\nlink: {}\n".format(self.twitter)
            )
        return ''.join(social)

    @property
    def fields_mapping(self):
        return {
            'name': self.name,
            'pronouns': self.pronouns,
            'avatar': self.avatar,
            'avatar_hover': self.avatar_hover,
            'bio': self.bio,
            'company': self.company,
            'job': self.job_title,
            'social': self.social,
            'type': self.activity_type,
            'level': self.audience_level,
            'language': self.language,
            'title': self.title,
            'description': self.description,
            'published': 'false',
            'topic': self.topics,
            'presentation_time': self.presentation_time,
            'duration': self.duration,
            'hide': self.hide,
        }

    def export(self):
        os.makedirs(f'palestrantes/{self.activity_id}')
        try:
            copyfile(f"./../avatars/{self.activity_id}/{self.avatar}",
                     f'palestrantes/{self.activity_id}/{self.avatar}')
            copyfile(f"./../avatars/{self.activity_id}/{self.avatar_hover}",
                     f'palestrantes/{self.activity_id}/{self.avatar_hover}')
        except Exception:
            copyfile("avatar-placehold.png", f'palestrantes/{self.activity_id}/{self.avatar}')
            copyfile("avatar-placehold.png", f'palestrantes/{self.activity_id}/{self.avatar_hover}')

        with open(f'palestrantes/{self.activity_id}/contents.lr', 'w') as f:
            for field, value in self.fields_mapping.items():
                f.write('{}: {}\n'.format(field, value))
                f.write('---\n')


def download():
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    wks = client.open_by_key('1L5Zzp1WRrDiTidw8-poqnFT3BvaABJJfC-ZSLCkPHMo')
    worksheet = wks.worksheet("palestrantes")
    records = worksheet.get_all_records()

    with open("../programacao.json", 'w') as f:
        json.dump(records, f)


def generate_schedule():
    programacao = pd.read_json("../programacao.json")

    for n, row in enumerate(programacao.iterrows()):
        print(n, row[1]['full_name'].lower())
        Activity(**row[1]).export()


def print_email_list():
    programacao = pd.read_json("../programacao.json")
    for row in programacao.iterrows():
        print(row[1]["full_name"].lower(), ';', row[1]["e-mail"])


def generate_mailchimp_list():
    programacao = pd.read_json("../programacao.json")
    mail_chimp_campaign = programacao[['full_name', 'e_mail', 'title', 'activity_type', 'language']]
    mail_chimp_campaign['first_name'] = programacao['full_name'].apply(lambda x: x.split()[0].title())
    mail_chimp_campaign['last_name'] = programacao['full_name'].apply(lambda x: x.split()[-1].title())
    mail_chimp_campaign[mail_chimp_campaign['activity_type'] == 'talk'].to_csv('mailchimp_campaign_talks.csv', sep=',', header=True, index=False)
    mail_chimp_campaign[mail_chimp_campaign['activity_type'] == 'tutorial'].to_csv('mailchimp_campaign_tutorials.csv', sep=',', header=True, index=False)


if __name__ == '__main__':
    if not os.path.exists("../programacao.json"):
        download()
    generate_schedule()
