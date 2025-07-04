from fastapi import FastAPI, APIRouter, HTTPException
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

# Orisha data structure
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

class TranslationRequest(BaseModel):
    text: str
    target_language: str  # "yoruba" or "english"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    language: str

class CulturalContentRequest(BaseModel):
    orisha_name: str
    content_type: str  # "story", "praise", "historical"

# Add your routes to the router instead of directly to app
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

@api_router.get("/proverbs/daily")
async def get_daily_proverb():
    """Get daily Yoruba proverb"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Provide a traditional Yoruba proverb (òwe) with:
        1. The proverb in Yoruba with proper diacritics
        2. Literal English translation
        3. Cultural meaning and context
        4. When it would be appropriately used
        
        Format as JSON with keys: yoruba, literal_translation, meaning, usage_context
        """
        
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Try to parse as JSON, fallback to raw text
        try:
            proverb_data = json.loads(content)
        except:
            proverb_data = {"content": content}
        
        return {
            "proverb": proverb_data,
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proverb generation error: {str(e)}")

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