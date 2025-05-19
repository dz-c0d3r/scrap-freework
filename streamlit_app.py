import requests
from bs4 import BeautifulSoup
import json
import time
import streamlit as st
from datetime import datetime


BASE_URL = "https://www.free-work.com"
LIST_URL = f"{BASE_URL}/fr/tech-it/jobs?contracts=contractor"
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7,tr;q=0.6",
    "cookie": "locale=fr; cc_cookie=%7B%22categories%22%3A%5B%22analytics%22%2C%22ads%22%5D%2C%22revision%22%3A0%2C%22data%22%3Anull%2C%22consentTimestamp%22%3A%222025-01-20T11%3A06%3A35.050Z%22%2C%22consentId%22%3A%220e238adb-d154-42c0-94f2-2abd20e7ec86%22%2C%22services%22%3A%7B%22analytics%22%3A%5B%22google_analytics%22%2C%22hotjar%22%2C%22posthog%22%2C%22microsoft%22%5D%2C%22ads%22%3A%5B%22facebook_pixel%22%2C%22linkedin%22%5D%7D%2C%22lastConsentTimestamp%22%3A%222025-01-20T11%3A06%3A35.050Z%22%2C%22expirationTime%22%3A1753095995051%7D; ph_phc_xEwl3WE7C2GlVRi9SkKi0tnzwSIcTVWYX231StJwvw1_posthog=%7B%22%24user_state%22%3A%22anonymous%22%2C%22distinct_id%22%3A%2239ebdbff-32b4-4e57-83ed-bd1364d010ef%22%2C%22%24device_id%22%3A%2239ebdbff-32b4-4e57-83ed-bd1364d010ef%22%2C%22%24flag_call_reported%22%3A%7B%22jobs_search_page_mobile_experiment%22%3A%5B%22undefined%22%5D%7D%2C%22%24initial_campaign_params%22%3A%7B%7D%2C%22%24initial_referrer_info%22%3A%7B%22%24referrer%22%3A%22%24direct%22%2C%22%24referring_domain%22%3A%22%24direct%22%7D%2C%22%24sesid%22%3A%5B1747676737181%2C%220196e9a6-ae9d-7795-ae14-1477e090d934%22%2C1747676737181%5D%2C%22%24client_session_props%22%3A%7B%22sessionId%22%3A%220196e9a6-ae9d-7795-ae14-1477e090d934%22%2C%22props%22%3A%7B%22initialPathName%22%3A%22%2Ffr%2Ftech-it%2Fjobs%22%2C%22referringDomain%22%3A%22%24direct%22%7D%7D%2C%22%24active_feature_flags%22%3A%5B%5D%2C%22%24enabled_feature_flags%22%3A%7B%7D%2C%22%24feature_flag_payloads%22%3A%7B%7D%7D; AWSALB=yoq2dnnI/VvMf38ZOCZNkOpowKB0FGKWN/1EP3nQ/fVECXxWjr8BFcLg0ixrk3bLhvZf0Ibn6Ly3e386DL0Zn8EGLteB+OzN0Hb1Y0zXclLNZ/JV5dXD7D7/enU3; AWSALBCORS=yoq2dnnI/VvMf38ZOCZNkOpowKB0FGKWN/1EP3nQ/fVECXxWjr8BFcLg0ixrk3bLhvZf0Ibn6Ly3e386DL0Zn8EGLteB+OzN0Hb1Y0zXclLNZ/JV5dXD7D7/enU3",
    "if-none-match": "\"5f8a5-ohth7OTKHntIzksiGSaPFj1FMkQ\"",
    "priority": "u=0, i",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}

@st.cache_data(show_spinner=False)
def get_offer_links():
    st.info("🔗 Chargement de la page de liste des offres...")
    try:
        res = requests.get(LIST_URL, headers=HEADERS)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        cards = soup.select("div.mb-4.relative.flex.flex-col")

        st.success(f"✅ {len(cards)} offres détectées sur la page.")
        
        links = []
        for idx, card in enumerate(cards):
            a_tag = card.find("a", href=True)
            if a_tag:
                href = a_tag['href']
                if href.startswith("/fr/tech-it/"):
                    full_url = BASE_URL + href
                    links.append(full_url)
                    st.write(f"🔗 Lien {idx+1}: {full_url}")
                else:
                    st.warning(f"⛔️ Lien ignoré : {href}")
            else:
                st.warning(f"❌ Aucun lien trouvé dans le bloc d'offre {idx+1}")
        
        return links
    except Exception as e:
        st.error(f"❌ Erreur lors de la récupération des liens d'offres : {e}")
        return []
 

def improved_parse_offer_from_html(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Bloc principal : <aside> contient les infos clés
    aside = soup.find("aside")

    # Titre du poste
    title_el = aside.select_one("span.hidden.md\\:block")
    title = title_el.get_text(strip=True) if title_el else None

    # Type de contrat (Freelance, CDI, etc.)
    contract_type = [tag.get_text(strip=True) for tag in aside.select("div.tags span.bg-contractor, div.tags span.bg-worker")]

    # Liste ordonnée des infos (disponibilité, durée, TJM, expérience, remote, localisation)
    info_blocks = aside.select("div.grid > div.flex.items-center")

    def extract_field(index):
        try:
            return info_blocks[index].select_one("span.text-sm").get_text(strip=True)
        except (IndexError, AttributeError):
            return None

    disponibilite = extract_field(0)
    duree = extract_field(1)
    tjm = extract_field(2)
    experience = extract_field(3)
    remote = extract_field(4)
    localisation = extract_field(5)

    # Date du jour (par défaut)
    date = datetime.now().strftime("%d/%m/%Y")

    # Bloc de description/contenu principal
    content_block = soup.select_one("div.html-renderer.prose-content")
    content = content_block.get_text(separator="\n", strip=True) if content_block else None

    # Profils & environnement technique
    text_blocks = soup.select("div.shadow.bg-white.rounded-lg")
    profil = text_blocks[1].get_text(separator="\n", strip=True) if len(text_blocks) > 1 else ""
    env = text_blocks[2].get_text(separator="\n", strip=True) if len(text_blocks) > 2 else ""

    return {
        "url": url,
        "title": title,
        "contract_type": contract_type,
        "disponibilite": disponibilite,
        "duree": duree,
        "tjm": tjm,
        "experience": experience,
        "remote": remote,
        "localisation": localisation,
        "date": date,
        "content": content,
        "profil": profil,
        "env": env
    }


def parse_offer(url):
    st.write(f"🔍 Traitement de l’offre : {url}")
    try:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        html = res.text

        # DEBUG — vérifier que <aside> est bien là
        if "<aside" not in html:
            st.error("❌ Le bloc <aside> est absent du HTML retourné.")
            st.code(html[:3000], language="html")
            return None

        soup = BeautifulSoup(html, "html.parser")
        aside = soup.find("aside")
        if not aside:
            st.error("❌ Le bloc <aside> n’a pas été trouvé après parsing.")
            st.code(html[:3000], language="html")
            return None

        return improved_parse_offer_from_html(html, url)
    except Exception as e:
        st.warning(f"⚠️ Erreur lors du parsing de l’offre : {e}")
        return None

def generate_structured_message(offer: dict) -> str:
    tjm = offer.get("tjm")
    experience = offer.get("experience")
    remote = offer.get("remote")
    localisation = offer.get("localisation")
    contract_type = offer.get("contract_type")[0] if offer.get("contract_type") else "Contrat à définir"
    duree = offer.get("duree", "Durée non précisée")

    # 🛠 Corriger les décalages logiques
    if tjm and "expérien" in tjm.lower():
        experience, tjm = tjm, None
    if experience and "télétravail" in experience.lower():
        remote, experience = experience, None
    if remote and ("france" in remote.lower() or "boulogne" in remote.lower()):
        localisation, remote = remote, None

    # 🧹 Nettoyage du contenu
    content = offer.get("content", "").strip()
    if content.lower().startswith("description"):
        content = content[11:].strip(": \n")

    profil = offer.get("profil", "").strip()
    env = offer.get("env", "").strip()

    return f"""Hello 👋

Je recherche un profil *{offer.get('title', 'Expert IT')}* pour un client final.

🎯 *Contexte de la mission* :  
{content}

🧠 *Le profil idéal* :  
{profil}

🏗️ *Environnement de travail* :  
{env}

📍 Lieu : {localisation or 'Non précisé'}  
📅 Démarrage : {offer.get('disponibilite') or 'À convenir'}  
💸 TJM : {tjm or 'À négocier'}  
🏡 Remote : {remote or 'À confirmer'}  
📄 Contrat : {contract_type}  
⏳ Durée : {duree}

👉 Intéressé(e) ou une reco ? MP moi !  
🔗 [Voir l’offre]({offer.get('url')})
"""


def scrape_all_offers(progress_callback=None):
    st.write("🚀 Démarrage du scraping...")
    offers = []
    links = get_offer_links()
    
    if not links:
        st.error("❌ Aucun lien d'offre récupéré.")
        return []

    for i, link in enumerate(links):
        if progress_callback:
            progress_callback(i / len(links))
        st.info(f"📄 Offre {i+1}/{len(links)}")
        data = parse_offer(link)
        if data:
            offers.append(data)
        else:
            st.warning(f"⛔️ Offre ignorée : parsing échoué.")
        time.sleep(1)

    st.success("✅ Scraping terminé.")
    return offers

# ---- STREAMLIT UI ----
st.title("🕷️ Scraper Free-Work.com – Offres Freelance")

# Init session_state
if "auto_scraped" not in st.session_state:
    st.session_state.auto_scraped = False
if "offers" not in st.session_state:
    st.session_state.offers = []

# ⚙️ Auto-exécution une seule fois
if not st.session_state.auto_scraped:
    with st.spinner("⏳ Scraping automatique au démarrage..."):
        progress_bar = st.progress(0)
        st.session_state.offers = scrape_all_offers(progress_callback=progress_bar.progress)
        st.session_state.auto_scraped = True

# 👆 Bouton manuel (une seule fois)
if st.button("Lancer le scraping"):
    with st.spinner("⏳ Scraping manuel..."):
        progress_bar = st.progress(0)
        st.session_state.offers = scrape_all_offers(progress_callback=progress_bar.progress)

# Récupération
offers = st.session_state.offers

# 🔽 Affichage
if offers:
    json_data = json.dumps(offers, ensure_ascii=False, indent=2)
    st.success(f"🎉 {len(offers)} offres récupérées avec succès.")
    st.download_button("📥 Télécharger le JSON", data=json_data, file_name="freework_offres.json", mime="application/json")
    
    st.subheader("🧾 Aperçu des premières offres")
    st.subheader("📢 Messages WhatsApp générés automatiquement")

    for i, offer in enumerate(offers):
        message = generate_structured_message(offer)
        st.markdown(f"#### ✉️ Offre {i+1}")
        st.code(message)
        st.subheader(offer["title"])
        st.write(f"🧾 Contrat : {', '.join(offer['contract_type'])}")
        st.write(f"📍 Localisation : {offer['localisation']}")
        st.write(f"📅 Disponibilité : {offer['disponibilite']}")
        st.write(f"📈 Expérience : {offer['experience']}")
        st.write(f"💻 Télétravail : {offer['remote']}")
        st.write(f"🔗 [Voir l’offre]({offer['url']})")
        st.markdown("---")
else:
    st.error("❌ Aucune offre n’a pu être extraite.")
