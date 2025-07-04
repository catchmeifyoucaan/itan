from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import google.generativeai as genai
import asyncio
import json
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Extended Orisha data structure with 18 deities
ORISHA_DATA = {
    "obatala": {
        "name": "Ọbàtálá",
        "yoruba_name": "Ọbàtálá",
        "domains": ["Creation", "Humankind", "Purity", "Peace", "The Mind"],
        "colors": ["White"],
        "symbols": ["White Cloth", "Dove", "Snail Shell"],
        "sacred_number": 8,
        "story": "The great creator deity commissioned by Olódùmarè to shape the world and humanity. Known as the sculptor of human forms and the compassionate guardian of all people with disabilities.",
        "yoruba_story": "Òrìṣà àgbà tí Olódùmarè rán láti dá ayé àti ẹ̀dá. Ó ni àìní fun gbogbo ènìyàn tí wọ́n ní àlàáfíà.",
        "diaspora": {
            "santeria": "Our Lady of Mercy",
            "location": "Cuba, Puerto Rico"
        },
        "constellation_position": {"x": 50, "y": 30}
    },
    "shango": {
        "name": "Ṣàngó",
        "yoruba_name": "Ṣàngó",
        "domains": ["Thunder", "Lightning", "Fire", "Justice", "Virility", "Dance"],
        "colors": ["Red", "White"],
        "symbols": ["Double-headed Axe (Oṣè)", "Ram", "Thunderstones"],
        "sacred_number": 16,
        "story": "The powerful Òrìṣà of thunder and lightning, once the fourth Alaafin of the Ọ̀yọ́ Empire. Known for his fiery temperament and his three wives: Ọ̀ṣun, Oya, and Ọbà.",
        "yoruba_story": "Òrìṣà àrá àti mọ̀nàmọ́ná tí ó jẹ́ ọba Ọ̀yọ́ rí. Ó ní aya mẹ́ta: Ọ̀ṣun, Oya, àti Ọbà.",
        "diaspora": {
            "santeria": "St. Barbara",
            "location": "Cuba, Brazil, Trinidad"
        },
        "constellation_position": {"x": 75, "y": 25}
    },
    "ogun": {
        "name": "Ògún",
        "yoruba_name": "Ògún",
        "domains": ["Iron", "War", "Technology", "Hunters", "Blacksmiths", "Truth"],
        "colors": ["Green", "Black"],
        "symbols": ["Machete", "Iron Implements", "Dog"],
        "sacred_number": 7,
        "story": "The master of iron and technology, the divine blacksmith who opened the path for civilization. Patron of all who work with metal and the guardian of truth and oaths.",
        "yoruba_story": "Ológun irin àti ìmọ̀ ẹ̀rọ, agbẹ́dẹ àtọ̀run tí ó ṣí ọ̀nà fún ọlaju. Ó jẹ́ alábòójútó òtítọ́ àti ìbúra.",
        "diaspora": {
            "santeria": "St. Peter",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 25, "y": 50}
    },
    "oshun": {
        "name": "Ọ̀ṣun",
        "yoruba_name": "Ọ̀ṣun",
        "domains": ["Rivers", "Love", "Beauty", "Fertility", "Wealth", "Diplomacy"],
        "colors": ["Yellow", "Gold"],
        "symbols": ["River", "Honey", "Mirror", "Peacock Feathers"],
        "sacred_number": 5,
        "story": "The beautiful river goddess, the sweetness of life and the power of love. She saved humanity when the male Òrìṣà tried to govern without the feminine principle.",
        "yoruba_story": "Òrìṣà odò tí ó lẹ́wà, adùn ayé àti agbára ìfẹ́. Ó gba ẹ̀dá là nígbà tí àwọn Òrìṣà ọkùnrin fẹ́ ṣàkóso láì sí obìnrin.",
        "diaspora": {
            "santeria": "Our Lady of Charity",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 80, "y": 60}
    },
    "yemoja": {
        "name": "Yemọja",
        "yoruba_name": "Yemọja",
        "domains": ["Ocean", "Motherhood", "Water", "Health", "Wealth"],
        "colors": ["Blue", "White"],
        "symbols": ["Ocean Waves", "Cowrie Shells", "Fan"],
        "sacred_number": 7,
        "story": "The great mother of waters, the nurturing ocean goddess who is the mother of all Òrìṣà. She represents the primal waters from which all life emerges.",
        "yoruba_story": "Ìyá àgbà omi, òrìṣà òkun tí ó jẹ́ ìyá gbogbo Òrìṣà. Ó dúró fún àwọn omi àkọ́kọ́ tí gbogbo ẹ̀mí ti wá.",
        "diaspora": {
            "santeria": "Our Lady of Regla",
            "location": "Cuba, Brazil, Uruguay"
        },
        "constellation_position": {"x": 20, "y": 80}
    },
    "esu": {
        "name": "Eṣu",
        "yoruba_name": "Eṣu",
        "domains": ["Crossroads", "Messenger", "Trickster", "Chaos", "Travelers"],
        "colors": ["Red", "Black"],
        "symbols": ["Key", "Hooked Staff", "Crossroads"],
        "sacred_number": 21,
        "story": "The divine messenger and guardian of crossroads. He tests humanity, carries sacrifices to the heavens, and maintains cosmic balance through necessary chaos.",
        "yoruba_story": "Ìránṣẹ́ àtọ̀run àti alábòójútó ibi tí ọ̀nà pàdé. Ó dán ẹ̀dá wò, ó gbé ẹbọ lọ sí ọ̀run, ó sì ṣe ìdọ́gbà ayé.",
        "diaspora": {
            "santeria": "St. Anthony of Padua",
            "location": "Cuba, Brazil, Trinidad"
        },
        "constellation_position": {"x": 40, "y": 70}
    },
    "orunmila": {
        "name": "Ọ̀rúnmìlà",
        "yoruba_name": "Ọ̀rúnmìlà",
        "domains": ["Wisdom", "Divination", "Knowledge", "Fate", "Prophecy"],
        "colors": ["Green", "Yellow", "Brown"],
        "symbols": ["Divination Tray (Opón Ifá)", "Palm Nuts (Ikin)"],
        "sacred_number": 16,
        "story": "The wise witness of creation, the master of Ifá divination. He knows the destiny of all things and guides humanity through the wisdom of the oracle.",
        "yoruba_story": "Ẹlẹ́rìí ìdá ayé, ológbon Ifá. Ó mọ ìpín ohun gbogbo, ó sì tọ́ ẹ̀dá sọ́nà nípasẹ̀ ọgbọ́n àfọ̀ṣẹ.",
        "diaspora": {
            "santeria": "St. Francis of Assisi",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 60, "y": 85}
    },
    "oya": {
        "name": "Oya",
        "yoruba_name": "Oya",
        "domains": ["Winds", "Storms", "Lightning", "Change", "Guardian of the Cemetery"],
        "colors": ["Maroon", "Nine Colors"],
        "symbols": ["Buffalo Horns", "Machete", "Whirlwind"],
        "sacred_number": 9,
        "story": "The fierce goddess of winds and storms, the guardian of the gates of death. She brings change and transformation, clearing the way for new beginnings.",
        "yoruba_story": "Òrìṣà ìjì àti àrá, alábòójútó ẹnu-ọ̀nà ikú. Ó mú ìyípadà àti ìtúnṣe, ó sì ṣí ọ̀nà fún ìbẹ̀rẹ̀ tuntun.",
        "diaspora": {
            "santeria": "Our Lady of Candelaria",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 85, "y": 40}
    },
    "babalu_aye": {
        "name": "Babalu-Aye",
        "yoruba_name": "Babalu-Aye",
        "domains": ["Disease", "Healing", "Earth", "Miracles", "Epidemics"],
        "colors": ["White", "Black", "Red"],
        "symbols": ["Crutches", "Jute Cloth", "Dogs"],
        "sacred_number": 17,
        "story": "The compassionate healer who governs disease and healing. Once cast out for his pride, he learned humility and became the great physician of the Òrìṣà.",
        "yoruba_story": "Onísègùn àánú tí ó ṣàkóso àrùn àti ìwòsàn. Ó kọ́ ìrẹ̀lẹ̀ lẹ́yìn tí a ti lé lọ nítorí ìgbéraga, ó sì di dókítà àgbà àwọn Òrìṣà.",
        "diaspora": {
            "santeria": "St. Lazarus",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 15, "y": 45}
    },
    "oko": {
        "name": "Òkò",
        "yoruba_name": "Òkò",
        "domains": ["Agriculture", "Fertility", "Harvest", "Food", "Farming"],
        "colors": ["Blue", "White", "Pink"],
        "symbols": ["Yam", "Plow", "Harvest Tools"],
        "sacred_number": 7,
        "story": "The divine farmer who taught humanity agriculture. He ensures the fertility of the earth and the abundance of harvests for all communities.",
        "yoruba_story": "Àgbẹ̀ àtọ̀run tí ó kọ́ ẹ̀dá nípa ìṣẹ̀ àgbẹ̀. Ó ṣe ìdánilójú ọ̀rọ̀ ilẹ̀ àti ọ̀pọ̀ ìkórè fún gbogbo àgbègbè.",
        "diaspora": {
            "santeria": "St. Isidore",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 30, "y": 15}
    },
    "osanyin": {
        "name": "Ọ̀ṣányìn",
        "yoruba_name": "Ọ̀ṣányìn",
        "domains": ["Herbs", "Medicine", "Forest", "Healing", "Plants"],
        "colors": ["Green", "Brown"],
        "symbols": ["Mortar and Pestle", "Medicinal Plants", "Iron Staff"],
        "sacred_number": 7,
        "story": "The master of herbs and forest medicines. He holds the secrets of plant healing and works closely with all other Òrìṣà to provide natural remedies.",
        "yoruba_story": "Ológun ewébẹ̀ àti oògùn àgbò. Ó ni àṣírí ìwòsàn ewéko, ó sì ṣiṣẹ́ pọ̀ pẹ̀lú gbogbo Òrìṣà míràn láti pèsè oògùn àdáyébá.",
        "diaspora": {
            "santeria": "St. Joseph",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 70, "y": 15}
    },
    "oba": {
        "name": "Ọbà",
        "yoruba_name": "Ọbà",
        "domains": ["River", "Marriage", "Domestic Affairs", "Loyalty", "Sacrifice"],
        "colors": ["Pink", "Yellow"],
        "symbols": ["Ear", "River Current", "Marriage Cloth"],
        "sacred_number": 8,
        "story": "The loyal river goddess and third wife of Ṣàngó. Her story teaches about sacrifice, loyalty, and the complexities of love and marriage.",
        "yoruba_story": "Òrìṣà odò olóòtítọ́ àti aya kẹta Ṣàngó. Ìtàn rẹ̀ kọ́ni nípa ẹbọ, òtítọ́, àti ìdiju ìfẹ́ àti ìgbéyàwó.",
        "diaspora": {
            "santeria": "St. Catherine",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 90, "y": 70}
    },
    "osun": {
        "name": "Ọ̀ṣun",
        "yoruba_name": "Ọ̀ṣun",
        "domains": ["Sacred Grove", "Traditions", "Customs", "Ancestral Wisdom"],
        "colors": ["White", "Green"],
        "symbols": ["Sacred Grove", "Ancient Trees", "Ritual Objects"],
        "sacred_number": 4,
        "story": "The guardian of sacred traditions and ancestral customs. Different from the river Ọ̀ṣun, this deity preserves the ancient ways and ritual practices.",
        "yoruba_story": "Alábòójútó àṣà mímọ́ àti ìṣẹ̀ àwọn baba. Ó yàtọ̀ sí Ọ̀ṣun odò, òrìṣà yìí tọ́jú àwọn ọ̀nà àtijọ́ àti ìṣẹ̀ ìsìn.",
        "diaspora": {
            "santeria": "St. Norbert",
            "location": "Cuba"
        },
        "constellation_position": {"x": 10, "y": 25}
    },
    "nana": {
        "name": "Nana Bùkúù",
        "yoruba_name": "Nana Bùkúù",
        "domains": ["Swamp", "Mud", "Ancient Wisdom", "Life and Death", "Primordial Waters"],
        "colors": ["Purple", "White", "Blue"],
        "symbols": ["Ibiri (Curved Staff)", "Mud", "Swamp Plants"],
        "sacred_number": 9,
        "story": "The ancient mother of waters, older than Yemọja. She represents the primordial mud from which life first emerged and to which it returns.",
        "yoruba_story": "Ìyá àgbà omi, àgbà ju Yemọja lọ. Ó dúró fún àmí àkọ́kọ́ tí ẹ̀mí ti kọ́kọ́ jáde sí àti èyí tí ó máa padà sí.",
        "diaspora": {
            "santeria": "St. Anne",
            "location": "Brazil, Cuba"
        },
        "constellation_position": {"x": 5, "y": 60}
    },
    "osumare": {
        "name": "Ọ̀ṣùmàrè",
        "yoruba_name": "Ọ̀ṣùmàrè",
        "domains": ["Rainbow", "Serpent", "Transformation", "Renewal", "Cycles"],
        "colors": ["All Colors", "Rainbow"],
        "symbols": ["Rainbow", "Serpent", "Circle"],
        "sacred_number": 7,
        "story": "The rainbow serpent who connects heaven and earth. Represents transformation, renewal, and the eternal cycles of life and nature.",
        "yoruba_story": "Ejò òṣùmàrè tí ó so ọ̀run àti ayé pọ̀. Ó dúró fún ìyípadà, ìmúdọ̀gbà, àti àyíká àìnípẹ̀kun ayé àti ìṣẹ̀dá.",
        "diaspora": {
            "santeria": "St. Bartholomew",
            "location": "Brazil, Cuba"
        },
        "constellation_position": {"x": 90, "y": 20}
    },
    "ibeji": {
        "name": "Ìbejì",
        "yoruba_name": "Ìbejì",
        "domains": ["Twins", "Children", "Joy", "Playfulness", "Duality"],
        "colors": ["Blue", "Red", "White"],
        "symbols": ["Twin Dolls", "Children's Toys", "Double Symbols"],
        "sacred_number": 2,
        "story": "The divine twins who bring joy and blessings to families. They represent the sacred nature of twins and the importance of children in Yoruba culture.",
        "yoruba_story": "Ìbejì àtọ̀run tí ó mú ayọ̀ àti ìbùkún wá sí ìdílé. Wọ́n dúró fún ẹ̀mí mímọ́ ìbejì àti pàtàkì àwọn ọmọ nínú àṣà Yorùbá.",
        "diaspora": {
            "santeria": "St. Cosmas and Damian",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 95, "y": 50}
    },
    "aganju": {
        "name": "Aganjú",
        "yoruba_name": "Aganjú",
        "domains": ["Volcanoes", "Desert", "Fire", "Strength", "Deserts"],
        "colors": ["Red", "Brown", "Orange"],
        "symbols": ["Volcano", "Desert Sand", "Fire"],
        "sacred_number": 9,
        "story": "The fierce deity of volcanoes and deserts. Father of Ṣàngó, he represents the primal force of fire and the strength of the earth itself.",
        "yoruba_story": "Òrìṣà líle àwọn òkè iná àti àginjù. Baba Ṣàngó, ó dúró fún agbára àkọ́kọ́ iná àti okun ilẹ̀ fúnra rẹ̀.",
        "diaspora": {
            "santeria": "St. Christopher",
            "location": "Cuba, Brazil"
        },
        "constellation_position": {"x": 65, "y": 45}
    },
    "oke": {
        "name": "Òkè",
        "yoruba_name": "Òkè",
        "domains": ["Mountains", "Heights", "Peaks", "Elevation", "Boundaries"],
        "colors": ["Brown", "Green", "White"],
        "symbols": ["Mountain Peak", "High Places", "Boundaries"],
        "sacred_number": 8,
        "story": "The deity of mountains and high places. He guards the boundaries between realms and watches over all elevated places of power and worship.",
        "yoruba_story": "Òrìṣà àwọn òkè àti ibi gíga. Ó ṣọ́ àwọn ààlà láàrin àwọn agbègbè ó sì ṣọ́ gbogbo àwọn ibi gíga agbára àti ìsìn.",
        "diaspora": {
            "santeria": "St. Manuel",
            "location": "Cuba"
        },
        "constellation_position": {"x": 35, "y": 35}
    }
}

# Proverb database organized by categories
PROVERB_CATEGORIES = {
    "wisdom": {
        "name": "Ìmọ̀ (Wisdom)",
        "name_yoruba": "Ìmọ̀",
        "proverbs": [
            {
                "yoruba": "Ọgbọ́n ọlọ́gbọ́n ni a fi ń sọgbọ́n, afi ọgbọ́n ẹni nìkan dá, á ṣì gbọ́n ni.",
                "literal": "It is with the wisdom of others that one becomes wise; he who relies on his own wisdom alone remains foolish.",
                "meaning": "No one is an island; one should seek counsel from others to gain true wisdom.",
                "context": "Used to encourage collaboration and learning from others' experiences."
            },
            {
                "yoruba": "Ọ̀rọ̀ ọlọ́gbọ́n là ń gbọ́, kì í ṣe ọ̀rọ̀ aláígbọ́n.",
                "literal": "It is the words of the wise that we listen to, not the words of the foolish.",
                "meaning": "Wisdom comes from listening to those who have knowledge and experience.",
                "context": "Used to emphasize the importance of choosing good advisors and mentors."
            }
        ]
    },
    "patience": {
        "name": "Sùúrù (Patience)",
        "name_yoruba": "Sùúrù",
        "proverbs": [
            {
                "yoruba": "Sùúrù ni baba ìwà.",
                "literal": "Patience is the father of character.",
                "meaning": "Patience is the foundation of good character and moral behavior.",
                "context": "Used to encourage someone to be patient in difficult situations."
            },
            {
                "yoruba": "Àìsùúrù ò jẹ́ kí onílùú jẹ oúnjẹ.",
                "literal": "Impatience prevents the owner of palms from enjoying his palm wine.",
                "meaning": "Impatience can prevent us from enjoying the fruits of our labor.",
                "context": "Used to warn against rushing things that require time to develop properly."
            }
        ]
    },
    "hard_work": {
        "name": "Ìṣẹ́ (Hard Work)",
        "name_yoruba": "Ìṣẹ́",
        "proverbs": [
            {
                "yoruba": "Ìṣẹ́ l'oògùn ìṣẹ́.",
                "literal": "Work is the medicine for poverty.",
                "meaning": "Hard work is the cure for poverty and lack.",
                "context": "Used to motivate people to work hard and not be lazy."
            },
            {
                "yoruba": "A kì í fi ẹnu ṣoké, a fi ọwọ́ ṣoké.",
                "literal": "One does not farm with the mouth, one farms with the hands.",
                "meaning": "Talk without action accomplishes nothing; success requires actual work.",
                "context": "Used to criticize those who talk big but do little work."
            }
        ]
    },
    "respect": {
        "name": "Ọ̀wọ̀ (Respect)",
        "name_yoruba": "Ọ̀wọ̀",
        "proverbs": [
            {
                "yoruba": "Ọ̀wọ̀ kọ́ni dáni.",
                "literal": "Respect does not diminish a person.",
                "meaning": "Showing respect to others does not make you less of a person.",
                "context": "Used to encourage respectful behavior towards others."
            },
            {
                "yoruba": "Ọmọ tí ó bá bú baba rẹ̀, àgbà rẹ̀ kò ní pẹ́.",
                "literal": "A child who insults his father, his old age will not last long.",
                "meaning": "Disrespecting elders brings negative consequences.",
                "context": "Used to warn against disrespecting parents and elders."
            }
        ]
    },
    "unity": {
        "name": "Ìṣọ̀kan (Unity)",
        "name_yoruba": "Ìṣọ̀kan",
        "proverbs": [
            {
                "yoruba": "Ìgbá ọwọ́ la fi ń mu omi.",
                "literal": "It is with cupped hands that we drink water.",
                "meaning": "Unity and cooperation are necessary for success.",
                "context": "Used to emphasize the importance of working together."
            },
            {
                "yoruba": "Ọ̀pọ̀ ọwọ́ ni ó ń mú ẹrù dórí.",
                "literal": "It is many hands that carry the load to the head.",
                "meaning": "Many people working together can accomplish great things.",
                "context": "Used to encourage teamwork and collective effort."
            }
        ]
    }
}

# Ijapa (Tortoise) folktales
IJAPA_STORIES = {
    "how_tortoise_got_cracked_shell": {
        "title": "How Ìjàpá Got His Cracked Shell",
        "title_yoruba": "Bí Ìjàpá Ṣe Ní Ikarahun Títẹ́",
        "summary": "A tale of how Ìjàpá's greed led to his shell being cracked when he fell from the sky during a heavenly feast.",
        "full_story": "Long ago, when there was a great famine on earth, the birds decided to fly to heaven for a feast. Ìjàpá, being clever but unable to fly, convinced the birds to each give him a feather so he could join them. He told them his name was 'All of You' so that when the heavenly hosts said the feast was for 'All of You,' he could claim it was all for him. His greed was exposed when his wife called his real name from earth. In anger, the birds took back their feathers, and Ìjàpá fell from the sky, cracking his shell forever.",
        "moral": "Greed and deception lead to one's downfall. Truth always prevails in the end.",
        "characters": ["Ìjàpá (Tortoise)", "Various Birds", "Yannibo (Tortoise's Wife)"]
    },
    "tortoise_and_feast_in_sky": {
        "title": "Ìjàpá and the Feast in the Sky",
        "title_yoruba": "Ìjàpá àti Àríyá Ní Ọ̀run",
        "summary": "The classic tale of Ìjàpá's cunning attempt to attend a heavenly feast, which leads to his ultimate comeuppance.",
        "full_story": "During a time of great hunger, all the birds received an invitation to a feast in the sky. Ìjàpá, who was also hungry but could not fly, begged the birds to help him. Each bird gave him a feather, and soon he could fly like them. Before they left, Ìjàpá suggested they all take new names for the occasion. He called himself 'All of You.' When they arrived in heaven, the hosts said, 'This feast is prepared for All of You.' Ìjàpá quickly claimed the entire feast was for him alone. The birds, realizing they had been tricked, took back their feathers one by one, leaving Ìjàpá stranded in the sky.",
        "moral": "Cleverness without wisdom leads to trouble. Selfishness ultimately brings isolation.",
        "characters": ["Ìjàpá (Tortoise)", "Birds", "Heavenly Hosts"]
    },
    "tortoise_gourd_of_wisdom": {
        "title": "Ìjàpá's Gourd of Wisdom",
        "title_yoruba": "Ìgbá Ọgbọ́n Ìjàpá",
        "summary": "How Ìjàpá tried to hoard all the wisdom in the world for himself, only to learn that wisdom belongs to everyone.",
        "full_story": "Ìjàpá once decided that he would collect all the wisdom in the world and keep it for himself. He gathered wisdom from every corner of the earth and put it all in a large gourd. Then he decided to hide the gourd at the top of a tall palm tree where no one could reach it. As he climbed the tree with the gourd tied to his belly, his young son called from below: 'Father, wouldn't it be easier to tie the gourd to your back instead of your belly?' Ìjàpá realized that even his small son had wisdom that he had not collected. In frustration, he threw the gourd down, and it broke, scattering wisdom to all corners of the world once again.",
        "moral": "Wisdom cannot be hoarded. It is meant to be shared and belongs to all humanity.",
        "characters": ["Ìjàpá (Tortoise)", "Ìjàpá's Son"]
    },
    "tortoise_and_monkey_prayer": {
        "title": "Ìjàpá and the Monkey's Prayer",
        "title_yoruba": "Ìjàpá àti Àdúrà Ọ̀bọ",
        "summary": "A story about Ìjàpá's attempt to copy Monkey's successful prayer, leading to unexpected consequences.",
        "full_story": "Ìjàpá noticed that whenever Monkey prayed, he always received what he asked for. Curious about this success, Ìjàpá decided to spy on Monkey during his prayers. He discovered that Monkey always ended his prayers by saying, 'If you cannot grant my request, then let me die.' Ìjàpá thought this was the secret to successful prayer. The next day, Ìjàpá went to pray and ended with the same words. However, when he said, 'If you cannot grant my request, then let me die,' the spirits responded, 'So be it!' Ìjàpá quickly realized that Monkey's prayers were successful because of his sincere faith, not because of specific words. He hastily apologized and learned to pray with genuine heart.",
        "moral": "Sincerity and faith are more important than copying others' methods. True devotion comes from the heart.",
        "characters": ["Ìjàpá (Tortoise)", "Ọ̀bọ (Monkey)", "Spirits"]
    }
}

# Define Models
class OrishaProfile(BaseModel):
    id: str
    name: str
    yoruba_name: str
    domains: List[str]
    colors: List[str]
    symbols: List[str]
    sacred_number: int
    story: str
    yoruba_story: str
    diaspora: Dict[str, str]
    constellation_position: Dict[str, int]

class ProverbCategory(BaseModel):
    category: str
    name: str
    name_yoruba: str
    proverbs: List[Dict[str, str]]

class ProverbSearchResult(BaseModel):
    category: str
    proverb: Dict[str, str]

class FolktaleStory(BaseModel):
    id: str
    title: str
    title_yoruba: str
    summary: str
    full_story: str
    moral: str
    characters: List[str]

class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    language: str

class CulturalContentRequest(BaseModel):
    orisha_name: str
    content_type: str

# Routes
@api_router.get("/")
async def root():
    return {"message": "Kábíyèsí! Welcome to The Living Ìtàn"}

@api_router.get("/orisha", response_model=List[OrishaProfile])
async def get_all_orisha():
    """Get all Òrìṣà profiles"""
    profiles = []
    for orisha_id, data in ORISHA_DATA.items():
        profile = OrishaProfile(
            id=orisha_id,
            **data
        )
        profiles.append(profile)
    return profiles

@api_router.get("/orisha/{orisha_id}", response_model=OrishaProfile)
async def get_orisha_profile(orisha_id: str):
    """Get specific Òrìṣà profile"""
    if orisha_id not in ORISHA_DATA:
        raise HTTPException(status_code=404, detail="Òrìṣà not found")
    
    data = ORISHA_DATA[orisha_id]
    return OrishaProfile(
        id=orisha_id,
        **data
    )

@api_router.get("/proverbs/categories")
async def get_proverb_categories():
    """Get all proverb categories"""
    categories = []
    for category_id, data in PROVERB_CATEGORIES.items():
        categories.append({
            "id": category_id,
            "name": data["name"],
            "name_yoruba": data["name_yoruba"],
            "count": len(data["proverbs"])
        })
    return categories

@api_router.get("/proverbs/category/{category_id}")
async def get_proverbs_by_category(category_id: str):
    """Get proverbs by category"""
    if category_id not in PROVERB_CATEGORIES:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return PROVERB_CATEGORIES[category_id]

@api_router.get("/proverbs/search")
async def search_proverbs(q: str = Query(..., description="Search query")):
    """Search proverbs by keyword"""
    results = []
    search_term = q.lower()
    
    for category_id, category_data in PROVERB_CATEGORIES.items():
        for proverb in category_data["proverbs"]:
            # Search in all fields
            if (search_term in proverb["yoruba"].lower() or 
                search_term in proverb["literal"].lower() or
                search_term in proverb["meaning"].lower() or
                search_term in proverb["context"].lower()):
                
                results.append({
                    "category": category_id,
                    "category_name": category_data["name"],
                    "proverb": proverb
                })
    
    return results

@api_router.get("/proverbs/daily")
async def get_daily_proverb():
    """Get daily Yoruba proverb"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Provide a traditional Yoruba proverb (òwe) with proper formatting:
        
        Response format (provide ONLY the JSON, no markdown):
        {
            "yoruba": "Proverb in Yoruba with proper diacritics",
            "literal_translation": "Word-for-word English translation",
            "meaning": "Deep cultural meaning and wisdom",
            "usage_context": "When and how this proverb would be used"
        }
        
        Make sure the response is valid JSON without any markdown formatting.
        """
        
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Clean the response - remove markdown formatting if present
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        try:
            proverb_data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback to a predefined proverb if JSON parsing fails
            proverb_data = {
                "yoruba": "Ọgbọ́n ọlọ́gbọ́n ni a fi ń sọgbọ́n, afi ọgbọ́n ẹni nìkan dá, á ṣì gbọ́n ni.",
                "literal_translation": "It is with the wisdom of others that one becomes wise; he who relies on his own wisdom alone remains foolish.",
                "meaning": "No one is an island; one should seek counsel from others to gain true wisdom.",
                "usage_context": "Used to encourage collaboration and learning from others' experiences."
            }
        
        return {
            "proverb": proverb_data,
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }
    
    except Exception as e:
        # Fallback proverb in case of any error
        return {
            "proverb": {
                "yoruba": "Ìṣẹ́ l'oògùn ìṣẹ́.",
                "literal_translation": "Work is the medicine for poverty.",
                "meaning": "Hard work is the cure for poverty and lack.",
                "usage_context": "Used to motivate people to work hard and not be lazy."
            },
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }

@api_router.get("/folktales")
async def get_folktales():
    """Get all Ìjàpá folktales"""
    tales = []
    for story_id, data in IJAPA_STORIES.items():
        tales.append({
            "id": story_id,
            **data
        })
    return tales

@api_router.get("/folktales/{story_id}")
async def get_folktale(story_id: str):
    """Get specific folktale"""
    if story_id not in IJAPA_STORIES:
        raise HTTPException(status_code=404, detail="Folktale not found")
    
    return {
        "id": story_id,
        **IJAPA_STORIES[story_id]
    }

@api_router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text between Yoruba and English using Gemini"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if request.target_language.lower() == "yoruba":
            prompt = f"""
            Translate the following English text to Yoruba with proper diacritics and cultural context.
            Make sure to preserve the cultural and spiritual meaning.
            
            Text: {request.text}
            
            Please provide only the Yoruba translation with proper tone marks and diacritics.
            """
        else:
            prompt = f"""
            Translate the following Yoruba text to English while preserving the cultural and spiritual meaning.
            
            Text: {request.text}
            
            Please provide only the English translation that captures the cultural context.
            """
        
        response = model.generate_content(prompt)
        translated_text = response.text.strip()
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            language=request.target_language
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@api_router.post("/cultural-content", response_model=Dict[str, Any])
async def generate_cultural_content(request: CulturalContentRequest):
    """Generate culturally appropriate content using Gemini"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        orisha_name = request.orisha_name
        content_type = request.content_type
        
        if content_type == "story":
            prompt = f"""
            Generate a traditional Yoruba story about {orisha_name} that would be appropriate for 
            a cultural education app. The story should be:
            - Culturally authentic and respectful
            - Suitable for all ages
            - Include moral lessons
            - Written in engaging narrative style
            
            Provide both English and Yoruba versions.
            """
        elif content_type == "praise":
            prompt = f"""
            Generate traditional Yoruba praise poetry (oríkì) for {orisha_name}.
            Include proper diacritics and cultural context.
            Provide both Yoruba and English translations.
            """
        else:
            prompt = f"""
            Generate historical and cultural information about {orisha_name} including:
            - Historical significance
            - Cultural practices
            - Regional variations
            - Modern relevance
            
            Make it educational and respectful.
            """
        
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        return {
            "orisha_name": orisha_name,
            "content_type": content_type,
            "content": content,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation error: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()