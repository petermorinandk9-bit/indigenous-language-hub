import io
import os
import re
import sqlite3

import pandas as pd
import qrcode
import streamlit as st

st.set_page_config(page_title="Indigenous Language Hub", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,650&family=Source+Sans+3:wght@400;600;700&display=swap');

    .stApp {
        background:
            radial-gradient(1200px 500px at 10% -10%, rgba(196, 149, 90, 0.12), transparent 50%),
            radial-gradient(900px 400px at 100% 0%, rgba(72, 112, 92, 0.10), transparent 45%);
    }
    html, body, [class*="stApp"] {
        font-family: "Source Sans 3", "Segoe UI", sans-serif;
        font-size: 18px;
    }
    h1, h2, h3 { font-family: "Source Serif 4", Georgia, serif; }
    h1 { font-size: 2.2rem !important; margin-bottom: 0.35rem !important; }
    h2 { font-size: 1.65rem !important; }
    h3 { font-size: 1.3rem !important; }
    section[data-testid="stSidebar"] {
        background: rgba(28, 32, 30, 0.55);
        border-right: 1px solid rgba(210, 190, 150, 0.18);
    }
    .hero-kicker {
        letter-spacing: 0.14em; text-transform: uppercase;
        font-size: 0.78rem; opacity: 0.72; margin-bottom: 0.15rem;
    }
    .blurb-box, .mission-box {
        font-size: 1.16rem; line-height: 1.7; padding: 1.15rem 1.35rem;
        border-radius: 0.85rem; background: rgba(18, 22, 20, 0.35);
        border: 1px solid rgba(210, 184, 140, 0.28);
        box-shadow: 0 10px 30px rgba(0,0,0,0.18); margin: 0.55rem 0 0.9rem 0;
    }
    .mission-box p { margin: 0 0 0.85rem 0; }
    .mission-box p:last-child { margin-bottom: 0; }
    .hear-box { display: flex; flex-wrap: wrap; gap: 0.55rem; align-items: center; margin: 0 0 1.15rem 0; font-size: 1.05rem; }
    .hear-label { opacity: 0.8; margin-right: 0.2rem; }
    .chip {
        display: inline-block; padding: 0.38rem 0.75rem; border-radius: 999px;
        background: rgba(196, 149, 90, 0.18); border: 1px solid rgba(196, 149, 90, 0.45);
        text-decoration: none !important; font-weight: 650; color: inherit !important;
    }
    .chip:hover { background: rgba(196, 149, 90, 0.32); }
    .quiet { opacity: 0.75; font-size: 1.02rem; margin-bottom: 1rem; }
    .sources-box { font-size: 0.92rem; line-height: 1.5; opacity: 0.92; }
    label, .stTextInput label, .stCheckbox label { font-size: 1.05rem !important; }
    div[data-testid="stCaption"] { font-size: 1rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="hero-kicker">Public-domain and community lexicons</div>', unsafe_allow_html=True)
st.title("Indigenous Language Hub")

region_map = {
    "Anishinaabemowin (Ojibwe)": {
        "db": "ojibwe_dictionary.db",
        "col": "ojibwe_word",
        "short": "Anishinaabemowin",
        "audio_sites": [("Ojibwe People's Dictionary", "https://ojibwe.lib.umn.edu/")],
        "blurb": (
            "Anishinaabemowin is the language of the Anishinaabe — Ojibwe, Odawa, "
            "and Potawatomi peoples — across the Great Lakes from Ontario and Manitoba "
            "through Minnesota, Wisconsin, and Michigan. It is an Algonquian language, "
            "closely related to Cree and more distantly to Powhatan and Massachusett. "
            "Speakers call the land and water into the grammar itself: nouns are living "
            "or non-living, and verbs carry who did what to whom. Communities still use "
            "it in homes, ceremony, and schools; dialects shift from the Border Lakes "
            "to the Ottawa Valley, but the shared spine is one language."
        ),
    },
    "Anishinaabemowin (Baraga 1878)": {
        "db": "baraga_dictionary.db",
        "col": "ojibwe_word",
        "short": "Otchipwe (Baraga)",
        "audio_sites": [("Ojibwe People's Dictionary (modern audio)", "https://ojibwe.lib.umn.edu/")],
        "blurb": (
            "This is Bishop Baraga’s 1878 Otchipwe lexicon — the same Anishinaabemowin "
            "as the modern module, written in a 19th-century missionary spelling. "
            "It covers Chippewa, Ottawa, and Potawatomi country around the Great Lakes. "
            "It is here to be used as a historical shelf next to the living Ojibwe People's Dictionary; "
            "We do not treat the two orthographies as one list."
        ),
    },
    "Powhatan (Mid-Atlantic)": {
        "db": "powhatan_dictionary.db",
        "col": "powhatan_word",
        "short": "Powhatan",
        "audio_sites": [],
        "blurb": (
            "Powhatan — Virginia Algonquian — was the language of Tsenacomoco, the "
            "tidewater confederacy under Wahunsenacawh that met the English at "
            "Jamestown in 1607. It was spoken along the James, York, and Rappahannock, "
            "from the Fall Line to the Chesapeake. Sister tongues ran north into "
            "Nanticoke and Lenape country and south toward Carolina Algonquian. "
            "Everyday words from this coast entered English early: moccasin, tomahawk, "
            "opossum, raccoon, persimmon, chinquapin. The spoken language receded in "
            "the eighteenth century; what survives on the page is the voice of that "
            "river world as colonists first heard it. No historical speaker recordings "
            "exist; living Virginia tribes keep new teaching audio in their own programs."
        ),
    },
    "Skarù·ręʔ (Tuscarora)": {
        "db": "tuscarora_dictionary.db",
        "col": "tuscarora_word",
        "short": "Tuscarora",
        "audio_sites": [],
        "blurb": (
            "Skarù·ręʔ is an Iroquoian language — kin to Mohawk, Oneida, Onondaga, "
            "Cayuga, and Seneca, not to Ojibwe or Powhatan. Its homeland was the "
            "rivers of eastern North Carolina. After the Tuscarora War many families "
            "walked north and became the sixth nation of the Haudenosaunee, in what "
            "is now New York and Ontario. This module is William Chew’s 1846 "
            "vocabulary printed by Schoolcraft: a short historical list, not Blair "
            "Rudes’s modern dictionary and not a classroom standard of the Nation."
        ),
    },
    "Chahta (Choctaw)": {
        "db": "choctaw_dictionary.db",
        "col": "choctaw_word",
        "short": "Chahta",
        "audio_sites": [
            ("Mississippi Band talking dictionary", "https://dictionary.choctaw.org/"),
            ("Choctaw Nation dictionary", "https://dictionary.choctawnation.com/"),
        ],
        "blurb": (
            "Chahta is a Muskogean language of the Mississippi valley — kin to "
            "Chickasaw, and more distantly to Creek, Seminole, and Alabama-Koasati. "
            "It was spoken across the rich bottomlands of central Mississippi before "
            "removal carried most families west to Indian Territory, today's Oklahoma. "
            "Mississippi Chahta and Oklahoma Chahta remain living communities. The "
            "language is verb-heavy, built from compact roots that stack direction, "
            "number, and aspect. Place-names and foodways still carry it: bogue, "
            "bayou borrowings, hominy-country speech along the Pearl and the Yazoo."
        ),
    },
    "Mvskoke (Creek)": {
        "db": "creek_dictionary.db",
        "col": "creek_word",
        "short": "Mvskoke",
        "audio_sites": [],
        "blurb": (
            "Mvskoke — Muskogee, Creek — is a Muskogean language of the river towns "
            "that ran from the Chattahoochee and Coosa into what became Alabama and "
            "Georgia, then west to Indian Territory after removal. It is the close "
            "sister of Seminole and a cousin of Chahta and Chickasaw. Town names, "
            "hymns, and the old mission press at Tullahassee kept it on the page. "
            "This module is Loughridge and Hodge’s 1890 lexicon, not a modern classroom "
            "standard of the Muscogee (Creek) Nation."
        ),
    },
    "Massachusett / Natick": {
        "db": "natick_dictionary.db",
        "col": "natick_word",
        "short": "Massachusett",
        "audio_sites": [("Wôpanâak Language Reclamation Project", "https://www.wlrp.org/")],
        "blurb": (
            "Massachusett — Natick in the mission records — was the Algonquian language "
            "of the people around Massachusetts Bay, the Charles, and the islands south "
            "to Wampanoag country. It is a close cousin of Narragansett and a more "
            "distant cousin of Powhatan and Anishinaabemowin. John Eliot’s 1663 Bible "
            "was printed in this tongue at Cambridge; praying towns at Natick and "
            "Punkapoag kept it on the page. The spoken language later receded; Wôpanâak "
            "reclamation now works from that same written spine. This module is the "
            "historical Natick lexicon, not a modern classroom standard."
        ),
    },
    "Lenape (Delaware)": {
        "db": "lenape_dictionary.db",
        "col": "lenape_word",
        "short": "Lenape",
        "audio_sites": [("Lenape Talking Dictionary (Delaware Tribe)", "https://www.talk-lenape.org/")],
        "blurb": (
            "Lenape is the Algonquian language of the Delaware people — Unami in the "
            "south, Munsee in the north — from the lower Hudson and the Delaware River "
            "to the Jersey shore and eastern Pennsylvania. It is a close kin of "
            "Mahican and a more distant kin of Massachusett and Powhatan. Towns, "
            "rivers, and the word Delaware itself sit on this coast. Communities in "
            "Oklahoma, Wisconsin, and Ontario still carry it. This module is the 1888 "
            "Moravian / Brinton historical lexicon, not modern spoken Unami or Munsee."
        ),
    },
}

SOURCES = [
    ("Anishinaabemowin (modern)", "Ojibwe People's Dictionary, University of Minnesota. Living lexicon and speaker audio. We link to their site; we do not copy their sound files."),
    ("Anishinaabemowin (historical)", "Frederic Baraga, A Dictionary of the Otchipwe Language (1878). Public domain."),
    ("Powhatan", "Captain John Smith (1612/1624) and William Strachey, A Dictionarie of the Indian Language (1612, pub. 1849). Public domain colonial records."),
    ("Tuscarora", "William Chew vocabulary, written out by Rev. Gilbert Rockwood, in Henry R. Schoolcraft, Notes on the Iroquois (1846). Public domain. Not the copyrighted Rudes 1999 dictionary."),
    ("Chahta", "Cyrus Byington, A Dictionary of the Choctaw Language, ed. Swanton & Halbert, BAE Bulletin 46 (1915). Public domain. Living audio belongs to the Mississippi Band of Choctaw Indians and the Choctaw Nation of Oklahoma."),
    ("Mvskoke", "R. M. Loughridge and David M. Hodge, English and Muskokee Dictionary (1890). Public domain."),
    ("Massachusett / Natick", "James Hammond Trumbull, Natick Dictionary, BAE Bulletin 25 (1903), drawn from John Eliot’s 1663 Bible. Public domain. Living reclamation: Wôpanâak Language Reclamation Project."),
    ("Lenape", "Daniel G. Brinton and Albert Seqaqkind Anthony, A Lenâpé-English Dictionary (1888). Public domain. Living audio: Lenape Talking Dictionary, Delaware Tribe of Indians."),
    ("Scans", "Internet Archive and Smithsonian / BAE reprints of the public-domain books above."),
]

ENGLISH_HEADS = {
    "building", "man", "woman", "water", "oil", "the", "and", "from", "with",
    "this", "that", "edited", "morton", "eliot", "survey",
}

PLACEHOLDER = "Select a language…"

st.sidebar.header("Module Selection")
selected_region = st.sidebar.selectbox(
    "Active Language Region",
    [PLACEHOLDER] + list(region_map.keys()),
    index=0,
)


def render_sources(expanded=False):
    with st.expander("Sources and credit", expanded=expanded):
        st.markdown('<div class="sources-box">', unsafe_allow_html=True)
        st.write(
            "The Hub only keeps public-domain print lexicons on this server. "
            "Living talking dictionaries stay on the nations’ own sites."
        )
        for name, credit in SOURCES:
            st.markdown(f"- **{name}** — {credit}")
        st.caption("Built by Divergent Engines / Peter Morin. The app is free and stays free.")
        st.markdown("</div>", unsafe_allow_html=True)


if selected_region == PLACEHOLDER:
    st.markdown(
        """
        <div class="mission-box">
          <p>The language hub was built by Divergent Engines, a technical solutions company founded by Peter Morin, A software Engineer born and raised in Baraga, Michigan. This hub was made in the hopes of preserving the languages of our people.
          Too much has already been lost or taken, we must preserve our language.
          What can still be gathered from public-domain records and community-verified lexicons you will find here. </p>
          <p>This app is free. It will stay free. No subscription. No lock on the words. No paywall ever.</p>
          <p>Choose a language in the sidebar to open its lexicon, you will also find links to the living speakers, and a complete glossary for every language. It is downloadable as an app under the mobile access tab, simply select download as an app and it will function just like any other app. </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_sources(expanded=False)
    st.stop()

info = region_map[selected_region]
language_name = info.get("short", selected_region.split(" ")[0])
db_path = info["db"]
native_col = info["col"]
audio_sites = info.get("audio_sites") or []

st.markdown(f"## {selected_region}")
st.markdown(f'<div class="blurb-box">{info["blurb"]}</div>', unsafe_allow_html=True)

if audio_sites:
    chips = " ".join(
        f'<a class="chip" href="{url}" target="_blank">{label}</a>'
        for label, url in audio_sites
    )
    st.markdown(
        f'<div class="hear-box"><span class="hear-label">Hear speakers</span>{chips}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="quiet">No public historical speaker recordings for this lexicon.</div>',
        unsafe_allow_html=True,
    )


def get_columns(conn):
    return {row[1] for row in conn.execute("PRAGMA table_info(dictionary)")}


def load_lexicon(conn, native_col, like=None):
    cols = get_columns(conn)
    select_bits = [f"{native_col} AS native_word", "english_translation"]
    for extra in ("word_class", "source", "license", "orthography", "notes", "audio_url"):
        if extra in cols:
            select_bits.append(extra)
    sql = f"SELECT {', '.join(select_bits)} FROM dictionary"
    params = []
    if like:
        sql += f" WHERE {native_col} LIKE ? OR english_translation LIKE ?"
        params = [f"%{like}%", f"%{like}%"]
    sql += f" ORDER BY {native_col} COLLATE NOCASE"
    return pd.read_sql_query(sql, conn, params=params)


def is_verb_sense(gloss, term):
    g = (gloss or "").lower()
    t = term.lower()
    if re.search(rf"\b(to|he|she|it|they)\s+{re.escape(t)}s?\b", g):
        return True
    if re.search(rf"\b{re.escape(t)}s?\s+(or\s+carries|fruit|witness|testimony)\b", g):
        return True
    return False


def rank_hits(df, term, include_verbs=False):
    t = (term or "").strip().lower()
    if df.empty or not t:
        return df
    word_pat = re.compile(rf"\b{re.escape(t)}\b", re.I)
    noun_pat = re.compile(
        rf"(?:\b(?:a|an|the|young|male|female)\s+)?\b{re.escape(t)}\b",
        re.I,
    )

    def keep_row(row):
        word = str(row.get("native_word") or "")
        gloss = str(row.get("english_translation") or "")
        lead = gloss[:90]
        if word.lower() in ENGLISH_HEADS:
            return False
        if not (word_pat.search(word) or word_pat.search(lead)):
            return False
        if not include_verbs and is_verb_sense(lead, t):
            return False
        return True

    rows = df[df.apply(keep_row, axis=1)]

    def score(row):
        word = str(row.get("native_word") or "").lower()
        lead = str(row.get("english_translation") or "")[:90].lower()
        klass = str(row.get("word_class") or "").lower()
        if word == t or lead == t:
            return 0
        if noun_pat.search(lead):
            return 1 if klass.startswith("n") else 2
        if word_pat.search(word):
            return 3
        return 4

    out = rows.copy()
    if out.empty:
        return out
    out["_s"] = out.apply(score, axis=1)
    out = out.sort_values(["_s", "native_word"], kind="stable").drop(columns=["_s"])
    return out.reset_index(drop=True)


def display_frame(df):
    view = df.copy()
    drop = []
    for col in ("notes", "audio_url"):
        if col in view.columns:
            emptied = view[col].fillna("").astype(str).isin(["", "None", "nan"])
            if emptied.all():
                drop.append(col)
    if drop:
        view = view.drop(columns=drop)
    return view


def qr_png_bytes(url: str) -> bytes:
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2C2C2C", back_color="#F9F8F4")
    if hasattr(img, "get_image"):
        img = img.get_image()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


search_tab, glossary_tab, mobile_tab, sources_tab = st.tabs(
    ["Search", "Glossary", "Mobile Access", "Sources"]
)

with search_tab:
    st.subheader(f"Search the {language_name} lexicon")
    search_term = st.text_input(f"Enter a word (English or {language_name}):")
    include_verbs = st.checkbox(
        "Show English verb senses (to bear fruit, to bear witness)", value=False
    )
    if search_term:
        if not os.path.exists(db_path):
            st.error(f"Could not locate {db_path}")
        else:
            conn = sqlite3.connect(db_path)
            try:
                df = load_lexicon(conn, native_col, like=search_term)
            finally:
                conn.close()
            df = rank_hits(df, search_term, include_verbs=include_verbs)
            if df.empty:
                st.warning(f"No results for '{search_term}'")
            else:
                st.caption(f"{len(df)} matches")
                st.dataframe(display_frame(df), use_container_width=True, hide_index=True)
                played = 0
                if "audio_url" in df.columns:
                    for _, row in df.iterrows():
                        url = row.get("audio_url") or ""
                        if isinstance(url, str) and url.startswith("http") and played < 8:
                            st.caption(row["native_word"])
                            st.audio(url)
                            played += 1
                if audio_sites:
                    st.markdown("**Look up this word on the official talking dictionary:**")
                    for label, url in audio_sites:
                        st.markdown(f"- [{label}]({url})")

with glossary_tab:
    st.subheader(f"{language_name} glossary")
    if audio_sites:
        for label, url in audio_sites:
            st.markdown(f"Spoken audio lives on [{label}]({url}).")
    if not os.path.exists(db_path):
        st.error(f"Could not locate {db_path}")
    else:
        conn = sqlite3.connect(db_path)
        try:
            df = load_lexicon(conn, native_col)
        finally:
            conn.close()
        st.caption(f"{len(df)} entries in {db_path}")
        filter_term = st.text_input("Filter glossary", key="glossary_filter")
        view = df
        if filter_term:
            mask = view["native_word"].fillna("").str.contains(
                filter_term, case=False, na=False
            ) | view["english_translation"].fillna("").str.contains(
                filter_term, case=False, na=False
            )
            view = view[mask]
        st.dataframe(display_frame(view), use_container_width=True, hide_index=True)
        csv = view.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download this view as CSV",
            data=csv,
            file_name=f"{language_name.lower()}_glossary.csv",
            mime="text/csv",
        )

with mobile_tab:
    st.subheader("Mobile Access")
    st.write(
        "Scan the QR code, or open the URL on your phone. "
        "In the mobile browser choose Add to Home Screen if you want an icon."
    )
    deployment_url = os.environ.get(
        "HUB_PUBLIC_URL",
        "https://divergent-engines-language-translator.streamlit.app",
    )
    st.code(deployment_url)
    st.image(qr_png_bytes(deployment_url), caption="Scan to open the Hub", width=250)

with sources_tab:
    render_sources(expanded=True)