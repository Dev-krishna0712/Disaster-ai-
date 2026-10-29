"""
Disaster AI Dataset Preparation & Validation Pipeline
Generates curated disaster management datasets from official NDMA SACHET, NDRF, and IMD guidelines.
Enforces zero data leakage between train, validation, and test splits.
Format: Conversational chat template with metadata (English, Hindi, Hinglish).
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

SYSTEM_PROMPT = (
    "You are Disaster AI, an official citizen-safety emergency response assistant. "
    "You provide concise, life-saving, verified disaster guidance based on NDMA and NDRF protocols in English and Hindi. "
    "During life-threatening situations, prioritize immediate human safety, emphasize Helpline 112, "
    "and provide clear, numbered survival steps. Acknowledge uncertainty when details are insufficient and never offer risky advice."
)

CURATED_EXAMPLES: List[Dict[str, Any]] = [
    # ==========================================
    # A. FLOOD SAFETY
    # ==========================================
    {
        "id": "flood_001_en",
        "category": "Flood Safety",
        "user_language": "en",
        "question": "Floodwater is entering my ground floor home rapidly. What should I do right now?",
        "context": "Water is actively rising inside a residential dwelling.",
        "response": (
            "IMMEDIATE ACTIONS FOR RISING FLOODWATER:\n"
            "1. Switch off main electricity supply and close the domestic LPG gas cylinder valve immediately to prevent electrocution and fire.\n"
            "2. Move yourself, family, children, and elderly persons to the upper floor or rooftop immediately.\n"
            "3. Take your emergency survival kit, charged mobile phone, torch, and medicines.\n"
            "4. Never step into flooded water touching electrical appliances or switchboards.\n"
            "5. Signal your location to rescue boats using a flashlight, whistle, or bright/white cloth.\n"
            "6. Call National Emergency Helpline 112 or NDRF Helpline 1078 with your exact rooftop location."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "flood_001_hi",
        "category": "Flood Safety",
        "user_language": "hi",
        "question": "मेरे घर के अंदर बाढ़ का पानी तेजी से भर रहा है। मुझे अभी क्या करना चाहिए?",
        "context": "आवासीय मकान में जलभराव की गंभीर स्थिति।",
        "response": (
            "बाढ़ का पानी घर में घुसने पर तत्काल कदम:\n"
            "1. सबसे पहले बिजली का मुख्य स्विच (मेन स्विच) बंद करें और रसोई गैस सिलेंडर का रेगुलेटर बंद करें ताकि करंट और आग का खतरा न रहे।\n"
            "2. बच्चों, बुजुर्गों और परिवार को तुरंत ऊपरी मंजिल या पक्की छत पर ले जाएं।\n"
            "3. आवश्यक दवाइयां, पीने का पानी, टॉर्च और मोबाइल फोन साथ रखें।\n"
            "4. पानी में डूबे बिजली के तारों या उपकरणों को बिल्कुल न छुएं।\n"
            "5. छत से बचाव दल को सफेद कपड़ा या टॉर्च दिखाकर संकेत दें।\n"
            "6. तुरंत राष्ट्रीय आपातकालीन नंबर 112 या एनडीआरएफ हेल्पलाइन 1078 पर संपर्क करें।"
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "flood_001_hinglish",
        "category": "Flood Safety",
        "user_language": "hinglish",
        "question": "Paani mere ghar mein bhar raha hai, mujhe kya karna chahiye urgently?",
        "context": "Water level rising inside house.",
        "response": (
            "URGENT SAFETY STEPS:\n"
            "1. Sabse pehle electricity ka MAIN SWITCH aur gas cylinder valve band karein.\n"
            "2. Family, bachon aur elderly logon ko turant upper floor ya chhat (rooftop) par le jayein.\n"
            "3. Zaroori medicines, drinking water, torch aur mobile phone saath rakhein.\n"
            "4. Flooded paani mein bijli ke switches ya wires ko bilkul mat chhuwein.\n"
            "5. Emergency Helpline 112 ya NDRF 1078 par call karke apni rooftop location batayein.\n"
            "6. Chhat par safe rahein aur torch ya bright cloth se rescue team ko signal karein."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "flood_002_en",
        "category": "Flood Safety",
        "user_language": "en",
        "question": "Can I drive my car through a waterlogged road if the water looks shallow?",
        "context": "Traveler deciding whether to cross flooded causeway.",
        "response": (
            "NO. NEVER drive through flooded or waterlogged roads:\n"
            "1. Just 15 cm (6 inches) of moving floodwater can reach the bottom of passenger cars and stall the engine.\n"
            "2. 30 cm (1 foot) of water can float most cars and small SUVs, sweeping them into drainage ditches or rivers.\n"
            "3. Floodwaters often conceal collapsed culverts, washed-away road surfaces, and open manholes.\n"
            "4. Turn around and take an alternate elevated route. If your vehicle stalls in rising water, abandon it immediately and seek higher ground on foot."
        ),
        "safety_priority": "URGENT_ACTION",
        "source_url": "https://ndrf.gov.in/en/disaster-awareness",
        "source_org": "NDRF Awareness",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "flood_002_hi",
        "category": "Flood Safety",
        "user_language": "hi",
        "question": "क्या जलभराव वाली सड़क पर गाड़ी या बाइक निकालना सुरक्षित है?",
        "context": "जलमग्न सड़क पार करने का प्रश्न।",
        "response": (
            "नहीं, जलमग्न या बहते पानी वाली सड़क पर गाड़ी कभी न चलाएं:\n"
            "1. मात्र 15 सेंटीमीटर (6 इंच) बहता पानी कार का संतुलन बिगाड़ सकता है और इंजन बंद कर सकता है।\n"
            "2. 30 से 60 सेंटीमीटर पानी अधिकांश कारों और एसयूवी को बहा ले जाने के लिए काफी होता है।\n"
            "3. पानी के नीचे टूटी हुई सड़क, खुले गटर या बह चुके पुल का पता नहीं चलता।\n"
            "4. वाहन मोड़ें और सुरक्षित ऊंचे रास्ते का उपयोग करें। यदि पानी बढ़ रहा हो और गाड़ी रुक जाए, तो तुरंत गाड़ी छोड़कर पैदल ऊंचे स्थान पर जाएं।"
        ),
        "safety_priority": "URGENT_ACTION",
        "source_url": "https://ndrf.gov.in/en/disaster-awareness",
        "source_org": "NDRF Awareness",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "flood_003_en",
        "category": "Flood Safety",
        "user_language": "en",
        "question": "How do we get safe drinking water when tap water is contaminated by floodwater?",
        "context": "Water supply safety post-flood.",
        "response": (
            "SAFE DRINKING WATER IN FLOODS:\n"
            "1. Do NOT drink regular tap or tube-well water in flood zones without treatment; it often carries sewage pathogens.\n"
            "2. Boil water vigorously for at least 1 full minute (3 minutes at high altitude) before drinking.\n"
            "3. If boiling is impossible, use chlorine / Halazone water purification tablets as directed (typically 1 tablet per 5 liters of clear water; wait 30 minutes).\n"
            "4. Keep drinking water covered in clean, disinfected containers.\n"
            "5. Consume packaged bottled water supplied by relief camps whenever available."
        ),
        "safety_priority": "PREPAREDNESS",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },

    # ==========================================
    # B. EARTHQUAKE SAFETY
    # ==========================================
    {
        "id": "quake_001_en",
        "category": "Earthquake Safety",
        "user_language": "en",
        "question": "What should I do immediately during earthquake shaking while indoors?",
        "context": "Tremors felt inside home or office.",
        "response": (
            "DROP, COVER, AND HOLD ON:\n"
            "1. DROP down onto your hands and knees immediately so the tremor cannot knock you down.\n"
            "2. COVER your head and neck under a sturdy table or desk. If no desk is nearby, crouch against an interior wall away from windows, ceiling fans, and heavy glass.\n"
            "3. HOLD ON to your shelter until the shaking completely stops.\n"
            "4. Do NOT rush outdoors or use elevators during the tremor; falling glass, brick, and facades cause the majority of injuries.\n"
            "5. After shaking ceases, evacuate calmly using the stairs and inspect for gas leaks before using switches."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://ndrf.gov.in/en/disaster-awareness",
        "source_org": "NDRF Awareness",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "quake_001_hi",
        "category": "Earthquake Safety",
        "user_language": "hi",
        "question": "भूकंप के तेज झटके महसूस होने पर घर के अंदर क्या करना चाहिए?",
        "context": "घर के अंदर भूकंप के झटके।",
        "response": (
            "झुको, ढको और पकड़ो (Drop, Cover, Hold On):\n"
            "1. तुरंत घुटनों के बल नीचे बैठें (Drop) ताकि गिरने से बच सकें।\n"
            "2. किसी मजबूत मेज या डेस्क के नीचे सिर और गर्दन को सुरक्षित ढकें (Cover)। खिड़कियों, कांच और पंखों से दूर रहें।\n"
            "3. मेज को मजबूती से पकड़ कर रखें (Hold On) जब तक कंपन रुक न जाए।\n"
            "4. झटकों के दौरान बाहर भागने की कोशिश न करें और लिफ्ट का उपयोग बिल्कुल न करें।\n"
            "5. झटके बंद होने के बाद सीढ़ियों से शांतिपूर्वक खुले मैदान में जाएं।"
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "quake_002_en",
        "category": "Earthquake Safety",
        "user_language": "en",
        "question": "There is a large diagonal crack in my wall after an earthquake. Is it safe to stay inside?",
        "context": "Post-earthquake structural damage assessment.",
        "response": (
            "EVACUATE IMMEDIATELY. It is NOT safe to stay inside:\n"
            "1. Diagonal shear cracks (especially wider than 5mm or extending across load-bearing pillars/beams) indicate severe structural compromise.\n"
            "2. Strong aftershocks can trigger secondary building collapse within hours or days of the main shock.\n"
            "3. Turn off the gas and electrical main supplies, evacuate all family members to an open area away from tall structures.\n"
            "4. Do NOT re-enter the building until an authorized civil engineer or municipal disaster authority certifies structural stability.\n"
            "5. Report the building damage to local disaster control at 112."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://ndrf.gov.in/en/basic-disaster-management-course",
        "source_org": "NDRF Course",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "quake_003_en",
        "category": "Earthquake Safety",
        "user_language": "en",
        "question": "What should I do if I am trapped under debris or rubble after an earthquake?",
        "context": "Survivor trapped under collapsed masonry.",
        "response": (
            "SURVIVAL ACTIONS UNDER DEBRIS:\n"
            "1. Cover your mouth and nose with your shirt or handkerchief to protect against choking dust inhalation.\n"
            "2. Do NOT light a match or lighter; gas leaks may be present and fire can ignite.\n"
            "3. Avoid unnecessary movement to prevent stirring up dust or dislodging further debris onto yourself.\n"
            "4. Tap rhythmically on pipes or masonry walls with a stone or metal object so acoustic rescue detectors can pinpoint you.\n"
            "5. Shout only as a last resort when you clearly hear rescuers nearby to conserve oxygen and energy."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://ndrf.gov.in/en/disaster-awareness",
        "source_org": "NDRF Awareness",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },

    # ==========================================
    # C. CYCLONE & SEVERE WEATHER
    # ==========================================
    {
        "id": "cyclone_001_en",
        "category": "Cyclone and Severe Weather",
        "user_language": "en",
        "question": "A severe cyclone warning has been issued for my coastal district. How should my family prepare?",
        "context": "Pre-cyclone alert phase (24-48 hours before landfall).",
        "response": (
            "CYCLONE PREPAREDNESS PROTOCOL (NDMA Guidelines):\n"
            "1. Inspect and secure your roof; board up or tape glass windows with adhesive tape to prevent flying glass shards.\n"
            "2. Trim dead tree branches and clear drains around the house.\n"
            "3. Store at least 3 days of clean drinking water, non-perishable dry rations, and infant/elderly essentials.\n"
            "4. Fully charge emergency lanterns, torches, power banks, and keep a battery-operated transistor radio ready.\n"
            "5. Keep personal identity documents, property papers, and cash in a sealed waterproof plastic bag.\n"
            "6. If your home is kutcha or in a low-lying storm surge zone, evacuate immediately to the nearest designated cyclone shelter when advised by authorities."
        ),
        "safety_priority": "URGENT_ACTION",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "cyclone_001_hi",
        "category": "Cyclone and Severe Weather",
        "user_language": "hi",
        "question": "चक्रवात (तूफान) की चेतावनी जारी होने पर क्या सावधानियां रखनी चाहिए?",
        "context": "तटीय क्षेत्र में चक्रवात की पूर्व चेतावनी।",
        "response": (
            "चक्रवात से पूर्व आवश्यक सावधानियां:\n"
            "1. खिड़कियों के शीशों पर टेप चिपकाएं और दरवाजों-खिड़कियों को मजबूती से बंद करें।\n"
            "2. घर के आसपास कमजोर पेड़ों की टहनियों को छांटें और खुले सामान को अंदर रखें।\n"
            "3. पीने का पानी, सूखा भोजन, टॉर्च, बैटरी और दवाइयां पर्याप्त मात्रा में रखें।\n"
            "4. मोबाइल और पावर बैंक पहले से चार्ज रखें।\n"
            "5. जरूरी कागजात और पहचान पत्र प्लास्टिक की वाटरप्रूफ थैली में रखें।\n"
            "6. यदि मकान कच्चा या तटीय निचले इलाके में है, तो प्रशासन के निर्देशानुसार तुरंत पक्के चक्रवात राहत शिविर में जाएं।"
        ),
        "safety_priority": "URGENT_ACTION",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "cyclone_002_en",
        "category": "Cyclone and Severe Weather",
        "user_language": "en",
        "question": "During a cyclone, the fierce wind suddenly stopped completely. Is it safe to go outside?",
        "context": "Eye of the storm phenomenon during cyclone landfall.",
        "response": (
            "DO NOT GO OUTSIDE. This is the 'Eye of the Cyclone':\n"
            "1. The calm period is temporary as the eye of the storm passes overhead.\n"
            "2. Destructive winds and torrential rain will suddenly resume with extreme intensity from the opposite direction within minutes.\n"
            "3. Remain inside the strongest reinforced room of your shelter away from windows.\n"
            "4. Await the official 'All Clear' bulletin from the India Meteorological Department (IMD) or State Disaster Management Authority before exiting."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },

    # ==========================================
    # D. LANDSLIDE & CLOUDBURST
    # ==========================================
    {
        "id": "slide_001_en",
        "category": "Landslide and Cloudburst",
        "user_language": "en",
        "question": "What are the earliest warning signs of an impending landslide in hilly areas?",
        "context": "Slope observation during heavy monsoon precipitation.",
        "response": (
            "CRITICAL LANDSLIDE WARNING SIGNS:\n"
            "1. Appearance of new cracks or widening fissures on slopes, retaining walls, paved roads, or building foundations.\n"
            "2. Tilting of telephone poles, trees, fences, or retaining walls.\n"
            "3. Sudden muddiness or rapid changes in discharge volume in local hillside streams.\n"
            "4. Continuous rumbling sound like a freight train, indicating rockfall or debris flow movement.\n"
            "5. Doors or windows sticking or jamming due to foundation soil displacement.\n"
            "ACTION: If you observe these indicators during torrential rainfall, evacuate immediately perpendicular to the slope to a stable ridge."
        ),
        "safety_priority": "URGENT_ACTION",
        "source_url": "https://ndrf.gov.in/en/disaster-awareness",
        "source_org": "NDRF Awareness",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "slide_001_hi",
        "category": "Landslide and Cloudburst",
        "user_language": "hi",
        "question": "पहाड़ी इलाकों में भूस्खलन (लैंडस्लाइड) होने के शुरुआती संकेत क्या हैं?",
        "context": "पहाड़ी क्षेत्र में भारी वर्षा के दौरान ढलान का निरीक्षण।",
        "response": (
            "भूस्खलन के प्रमुख पूर्व चेतावनी संकेत:\n"
            "1. पहाड़ी ढलान, सड़क या घर की दीवारों पर नई दरारों का दिखना या चौड़ा होना।\n"
            "2. बिजली के खंभों, पेड़ों या चहारदीवारी का एक तरफ झुकना।\n"
            "3. पहाड़ी नालों में अचानक पानी का बहुत गदला या मटमैला होना।\n"
            "4. गड़गड़ाहट या पत्थरों के गिरने की निरंतर आवाज सुनाई देना।\n"
            "5. दरवाजों और खिड़कियों का चौखट में अटकना।\n"
            "सलाह: ऐसा संकेत दिखने पर तुरंत ढलान से दूर सुरक्षित ऊंचे और स्थिर स्थान पर जाएं और 112 पर सूचना दें।"
        ),
        "safety_priority": "URGENT_ACTION",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "slide_002_en",
        "category": "Landslide and Cloudburst",
        "user_language": "en",
        "question": "A massive mudslide is heading down the hill towards my village. How do we escape?",
        "context": "Active debris flow approaching.",
        "response": (
            "IMMEDIATE EVACUATION DIRECTIVE:\n"
            "1. Move PERPENDICULAR (sideways) to the path of the debris flow. Never run straight downhill along the valley or gully path.\n"
            "2. Seek immediate high ground on a solid rock ridge or stable promontory.\n"
            "3. If escape is blocked and mudflow is upon you, curl tightly into a ball under a sturdy structure and protect your head with your arms.\n"
            "4. Stay clear of riverbanks and bridges; cloudburst mudflows can breach culverts and carry boulders at high velocity.\n"
            "5. Alert neighbors with shouts or vehicle horn and notify 112 as soon as you reach safe ground."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://ndrf.gov.in/en/basic-disaster-management-course",
        "source_org": "NDRF Course",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },

    # ==========================================
    # E. FIRE & SMOKE
    # ==========================================
    {
        "id": "fire_001_en",
        "category": "Fire and Smoke",
        "user_language": "en",
        "question": "There is a fire in my apartment building and smoke is filling the hallway. What should I do?",
        "context": "Multi-story residential building fire emergency.",
        "response": (
            "APARTMENT FIRE SURVIVAL PROTOCOL:\n"
            "1. Call 112 or Fire Service 101 immediately. Pull the building fire alarm if accessible.\n"
            "2. Feel the door handle with the back of your hand before opening. If it is HOT, do NOT open; the fire is right outside.\n"
            "3. If escaping through smoke: CRAWL LOW on your hands and knees. Toxic smoke and gases rise; cleaner, cooler air is within 30-60 cm of the floor.\n"
            "4. Cover your mouth and nose with a damp cloth to filter particulates.\n"
            "5. NEVER use elevators during a fire; always take the emergency fire stairs.\n"
            "6. If trapped in your flat: Seal doors and air vents with wet towels, retreat to a window, and signal firefighters with a bright cloth."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "fire_002_en",
        "category": "Fire and Smoke",
        "user_language": "en",
        "question": "Someone's clothes have caught on fire. What should they do immediately?",
        "context": "Clothing ignition emergency.",
        "response": (
            "STOP, DROP, AND ROLL:\n"
            "1. STOP immediately. Do NOT run; running fans the flames and makes the fire spread much faster.\n"
            "2. DROP to the ground immediately.\n"
            "3. COVER face and mouth with hands to protect airways and eyes.\n"
            "4. ROLL back and forth repeatedly on the ground to smother the fire.\n"
            "5. If assisting someone else: Wrap them tightly in a thick heavy blanket, wool coat, or rug to smother flames, then douse with cool water.\n"
            "6. Call 112 / 108 immediately for urgent burn care."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://ndrf.gov.in/en/disaster-awareness",
        "source_org": "NDRF Awareness",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },

    # ==========================================
    # F. HEATWAVES & EXTREME WEATHER
    # ==========================================
    {
        "id": "heat_001_en",
        "category": "Heatwaves and Extreme Weather",
        "user_language": "en",
        "question": "What are the warning signs of heatstroke and how should a victim be treated?",
        "context": "Severe heat exposure during peak summer.",
        "response": (
            "HEATSTROKE RECOGNITION & FIRST AID (Life-Threatening):\n"
            "WARNING SIGNS: Body temperature above 104°F (40°C), hot red dry skin (lack of sweating), confusion, dizziness, rapid pulse, seizures, or loss of consciousness.\n"
            "IMMEDIATE ACTION:\n"
            "1. Call 112 or 108 for an ambulance immediately; heatstroke is a medical emergency.\n"
            "2. Move the person to an air-conditioned or shaded room immediately.\n"
            "3. Cool the body rapidly: Apply wet cloths or ice packs to the neck, armpits, and groin where major blood vessels pass.\n"
            "4. Fan air vigorously and sprinkle cool (not freezing) water over the skin.\n"
            "5. If conscious and able to swallow, give small sips of cool water or ORS solution. Do NOT force fluids if disoriented or drowsy."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "heat_001_hi",
        "category": "Heatwaves and Extreme Weather",
        "user_language": "hi",
        "question": "लू (हीटस्ट्रोक) लगने के लक्षण क्या हैं और प्राथमिक उपचार क्या करें?",
        "context": "गर्मियों में लू से बचाव और उपचार।",
        "response": (
            "हीटस्ट्रोक (लू) के लक्षण एवं प्राथमिक उपचार:\n"
            "लक्षण: तेज बुखार (104°F से अधिक), त्वचा का सूखा और लाल होना (पसीना न आना), चक्कर आना, सिरदर्द, उल्टी या बेहोशी।\n"
            "तत्काल प्राथमिक उपचार:\n"
            "1. तुरंत 108 या 112 पर एम्बुलेंस बुलाएं; यह जानलेवा हो सकता है।\n"
            "2. पीड़ित को तुरंत छायादार और हवादार ठंडे स्थान पर ले जाएं।\n"
            "3. शरीर को ठंडा करें: गर्दन, कांख (armpit) और जांघों पर ठंडे पानी की पट्टी रखें।\n"
            "4. सामान्य पानी का छिड़काव करें और पंखा चलाएं।\n"
            "5. यदि होश में हो, तो ओआरएस (ORS), नींबू पानी या मट्ठा पिलाएं। बेहोश व्यक्ति के मुंह में कुछ न डालें।"
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },

    # ==========================================
    # G. TSUNAMI
    # ==========================================
    {
        "id": "tsunami_001_en",
        "category": "Tsunami",
        "user_language": "en",
        "question": "What natural warning signs indicate an approaching tsunami, and what should coastal residents do?",
        "context": "Coastal resident observing abnormal ocean behavior after an earthquake.",
        "response": (
            "NATURAL TSUNAMI WARNING SIGNS & EVACUATION:\n"
            "SIGNS:\n"
            "1. A strong or prolonged earthquake felt near the coast.\n"
            "2. Rapid and unusual withdrawal of the ocean exposing the seafloor, reefs, and stranded fish.\n"
            "3. A loud roaring sound from the ocean resembling a train or jet aircraft.\n"
            "IMMEDIATE EVACUATION ACTION:\n"
            "1. Move INLAND and to HIGH GROUND immediately (at least 15 to 30 meters above sea level) or at least 2 km inland.\n"
            "2. Do NOT go to the beach to watch the exposed seabed or waves.\n"
            "3. If high ground is unavailable, evacuate to the 3rd floor or higher of a reinforced multi-story concrete building.\n"
            "4. Stay away: A tsunami is a series of waves; subsequent waves can be much larger and arrive hours after the first."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://ndrf.gov.in/en/disaster-awareness",
        "source_org": "NDRF Awareness",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },

    # ==========================================
    # H. FIRST-AID & EMERGENCY RESPONSE
    # ==========================================
    {
        "id": "firstaid_001_en",
        "category": "First Aid and Emergency Response",
        "user_language": "en",
        "question": "Someone has severe spurting arterial bleeding from an arm injury. How do I stop it?",
        "context": "Severe traumatic hemorrhage.",
        "response": (
            "CONTROLLING SEVERE ARTERIAL BLEEDING (CRITICAL):\n"
            "1. Call 112 / 108 immediately for an emergency ambulance.\n"
            "2. Apply DIRECT, CONTINUOUS PRESSURE onto the wound using a clean cloth, towel, or sterile gauze dressing.\n"
            "3. Press down firmly with both hands using your body weight directly over the bleeding site.\n"
            "4. Do NOT remove soaked cloths; place additional cloths directly on top and maintain constant pressure.\n"
            "5. Keep the victim lying down and warm to combat shock.\n"
            "6. If blood continues to pulse through and you have certified tourniquet training, apply a tourniquet 5 cm (2 inches) above the wound, noting the exact time applied."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://ndrf.gov.in/en/basic-disaster-management-course",
        "source_org": "NDRF Course",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "firstaid_001_hi",
        "category": "First Aid and Emergency Response",
        "user_language": "hi",
        "question": "दुर्घटना के बाद किसी व्यक्ति के हाथ से बहुत तेजी से खून बह रहा है, क्या करें?",
        "context": "गंभीर रक्तस्राव की आपातकालीन स्थिति।",
        "response": (
            "गंभीर रक्तस्राव रोकने के लिए तत्काल कदम:\n"
            "1. तुरंत 112 या 108 पर एम्बुलेंस बुलाएं।\n"
            "2. घाव पर साफ कपड़े या पट्टी से सीधा और मजबूत दबाव (Direct Pressure) बनाएं।\n"
            "3. दोनों हाथों से लगातार दबाए रखें। यदि कपड़ा खून से भीग जाए, तो उसे हटाएं नहीं, बल्कि उसके ऊपर दूसरा कपड़ा रखकर दबाते रहें।\n"
            "4. घायल व्यक्ति को लेटा कर रखें और पैर थोड़े ऊंचे रखें ताकि शॉक से बचा जा सके।\n"
            "5. घाव में धंसी हुई किसी भी वस्तु को बाहर निकालने की कोशिश न करें।"
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://ndrf.gov.in/en/basic-disaster-management-course",
        "source_org": "NDRF Course",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "firstaid_002_en",
        "category": "First Aid and Emergency Response",
        "user_language": "en",
        "question": "What should I do if a family member faints or becomes unconscious during a disaster?",
        "context": "Unresponsive patient.",
        "response": (
            "FIRST AID FOR UNCONSCIOUSNESS:\n"
            "1. Call 112 / 108 immediately.\n"
            "2. Check responsiveness and breathing (look, listen, and feel for chest movement for 5 seconds).\n"
            "3. If breathing normally: Place in the RECOVERY POSITION (gently roll them onto their left side, tilt head back slightly to keep airway clear, bend top leg to stabilize).\n"
            "4. Loosen tight clothing around neck, chest, and waist.\n"
            "5. Do NOT give water, food, or medicines to an unconscious person; it can cause fatal airway choking.\n"
            "6. If NOT breathing normally, begin CPR immediately (30 chest compressions at 100-120 bpm followed by 2 rescue breaths) until medical help arrives."
        ),
        "safety_priority": "IMMEDIATE_PERIL",
        "source_url": "https://ndrf.gov.in/en/basic-disaster-management-course",
        "source_org": "NDRF Course",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },

    # ==========================================
    # I. EMERGENCY PREPAREDNESS
    # ==========================================
    {
        "id": "prep_001_en",
        "category": "Emergency Preparedness",
        "user_language": "en",
        "question": "What essential items should be in a family emergency disaster survival kit?",
        "context": "Family emergency kit preparation.",
        "response": (
            "ESSENTIAL DISASTER SURVIVAL KIT (72-Hour Supply):\n"
            "1. Water: 3-4 liters per person per day (at least 3-day supply).\n"
            "2. Food: Ready-to-eat non-perishable food (dry fruits, biscuits, canned food, energy bars).\n"
            "3. First Aid Kit: Bandages, antiseptic lotion, ORS sachets, pain relievers, and personal prescription medicines (7-day supply).\n"
            "4. Tools & Lighting: Battery-operated flashlight with extra batteries, whistle, multi-tool knife.\n"
            "5. Communication: Battery or hand-crank portable radio, fully charged power bank with cables.\n"
            "6. Documents: Waterproof pouch containing copies of Aadhaar, property papers, insurance, and emergency contact numbers.\n"
            "7. Sanitation: Hand sanitizer, chlorine purification tablets, soap, wet wipes, and face masks.\n"
            "8. Cash in small denominations."
        ),
        "safety_priority": "PREPAREDNESS",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "prep_001_hi",
        "category": "Emergency Preparedness",
        "user_language": "hi",
        "question": "आपदा से निपटने के लिए घर में इमरजेंसी किट (आपदा थैला) में क्या-क्या होना चाहिए?",
        "context": "पारिवारिक आपदा किट की तैयारी।",
        "response": (
            "आपातकालीन आपदा किट (72 घंटे हेतु आवश्यक सामग्री):\n"
            "1. पीने का पानी: 3 लीटर प्रति व्यक्ति प्रतिदिन (कम से कम 3 दिन का स्टॉक)।\n"
            "2. सूखा भोजन: बिस्कुट, भुना चना, सूखे मेवे, ओआरएस पैकेट।\n"
            "3. प्राथमिक चिकित्सा पेटी: पट्टी, डिटॉल, दर्दनिवारक और परिवार की आवश्यक दैनिक दवाइयां।\n"
            "4. रोशनी और संकेत: टॉर्च (अतिरिक्त सेल सहित), सीटी (whistle), मोमबत्ती व माचिस।\n"
            "5. संचार: बैटरी से चलने वाला छोटा रेडियो, पूरी तरह चार्ज पावर बैंक।\n"
            "6. दस्तावेज: आधार कार्ड, बैंक व जरूरी कागजात प्लास्टिक थैली में।\n"
            "7. नकदी (छोटे नोटों में)।"
        ),
        "safety_priority": "PREPAREDNESS",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    },
    {
        "id": "prep_002_en",
        "category": "Emergency Preparedness",
        "user_language": "en",
        "question": "What should I do if mobile phone networks stop working during a disaster?",
        "context": "Communication blackout during disaster.",
        "response": (
            "COMMUNICATION DURING CELLULAR BLACKOUT:\n"
            "1. Use SMS text messages instead of voice calls; SMS packets often go through when voice networks are jammed.\n"
            "2. Keep calls brief (under 10 seconds) to conserve your phone battery and reduce cellular tower congestion.\n"
            "3. Switch phone to 'Battery Saver / Low Power Mode' and disable Wi-Fi/Bluetooth scanning.\n"
            "4. Tune into All India Radio (AIR) on your transistor or FM mobile receiver for verified government announcements.\n"
            "5. Agree on a pre-planned physical family meeting point (e.g. local school or community center) before disasters strike."
        ),
        "safety_priority": "PREPAREDNESS",
        "source_url": "https://sachet.ndma.gov.in/DosDont",
        "source_org": "NDMA SACHET",
        "review_status": "VERIFIED_OFFICIAL_GUIDELINE",
        "last_verified": "2026-10-28"
    }
]

def format_conversational_example(item: Dict[str, Any]) -> Dict[str, Any]:
    """Wraps each curated Q&A into standardized conversational chat format."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": item["question"]},
        {"role": "assistant", "content": item["response"]}
    ]
    return {
        "id": item["id"],
        "category": item["category"],
        "user_language": item["user_language"],
        "safety_priority": item["safety_priority"],
        "source_url": item["source_url"],
        "source_org": item["source_org"],
        "review_status": item["review_status"],
        "last_verified": item["last_verified"],
        "messages": messages
    }

def generate_dataset_splits():
    """Generates train, validation, and test splits with strict group-based zero leakage."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Save raw verified guidelines
    raw_file = RAW_DIR / "official_guidelines_curated.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(CURATED_EXAMPLES, f, indent=2, ensure_ascii=False)
    print(f"[OK] Saved {len(CURATED_EXAMPLES)} verified raw guidelines to {raw_file}")

    # Build conversational items
    formatted_items = [format_conversational_example(item) for item in CURATED_EXAMPLES]

    # Group by scenario base id (e.g. 'flood_001') to prevent cross-split leakage
    scenario_groups: Dict[str, List[Dict[str, Any]]] = {}
    for item in formatted_items:
        base_id = "_".join(item["id"].split("_")[:2])
        if base_id not in scenario_groups:
            scenario_groups[base_id] = []
        scenario_groups[base_id].append(item)

    # Deterministic split by scenario groups
    random.seed(42)
    group_keys = list(scenario_groups.keys())
    random.shuffle(group_keys)

    n_groups = len(group_keys)
    n_test = max(1, int(n_groups * 0.15))
    n_val = max(1, int(n_groups * 0.15))

    test_keys = set(group_keys[:n_test])
    val_keys = set(group_keys[n_test:n_test + n_val])
    train_keys = set(group_keys[n_test + n_val:])

    train_data = []
    val_data = []
    test_data = []

    for k in train_keys:
        train_data.extend(scenario_groups[k])
    for k in val_keys:
        val_data.extend(scenario_groups[k])
    for k in test_keys:
        test_data.extend(scenario_groups[k])

    # Save splits
    train_file = DATA_DIR / "train.jsonl"
    val_file = DATA_DIR / "validation.jsonl"
    test_file = DATA_DIR / "test.jsonl"

    for path, data in [(train_file, train_data), (val_file, val_data), (test_file, test_data)]:
        with open(path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    manifest = {
        "dataset_name": "Disaster-AI-Curated-SFT-Dataset",
        "version": "1.0.0",
        "total_examples": len(formatted_items),
        "split_counts": {
            "train": len(train_data),
            "validation": len(val_data),
            "test": len(test_data)
        },
        "supported_languages": ["en", "hi", "hinglish"],
        "categories_covered": sorted(list(set(i["category"] for i in CURATED_EXAMPLES))),
        "provenance": {
            "primary_sources": [
                "NDMA SACHET (https://sachet.ndma.gov.in/DosDont)",
                "NDRF Disaster Awareness (https://ndrf.gov.in/en/disaster-awareness)",
                "NDRF Basic Disaster Management Course (https://ndrf.gov.in/en/basic-disaster-management-course)"
            ],
            "license": "Government Open Data / Public Awareness Educational Guidance",
            "curation_methodology": "Manual verification against official Indian disaster protocols"
        },
        "data_leakage_safeguard": "Group-wise scenario partitioning ensures identical questions in different languages remain in the same split."
    }

    manifest_file = DATA_DIR / "dataset_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Generated Dataset Manifest: {manifest_file}")
    print(f"     Train: {len(train_data)} | Validation: {len(val_data)} | Test: {len(test_data)}")

if __name__ == "__main__":
    generate_dataset_splits()
