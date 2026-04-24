import streamlit as st
import pandas as pd
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartFishing Med",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
}
h1, h2, h3 {
    font-family: 'Playfair Display', serif;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a2342 0%, #1a4a6e 100%);
}
[data-testid="stSidebar"] * {
    color: #e8f4f8 !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 1.05rem;
    padding: 6px 0;
}
.stRadio [data-testid="stMarkdownContainer"] p {
    color: #b0d4e8 !important;
    font-size: 0.85rem;
    font-weight: 300;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    color: #0a2342;
    line-height: 1.2;
    margin-bottom: 0.25rem;
}
.hero-sub {
    color: #4a7a9b;
    font-size: 1.1rem;
    font-weight: 300;
    margin-bottom: 2rem;
}
.card {
    background: #f0f7fc;
    border-left: 4px solid #1a7dc4;
    border-radius: 8px;
    padding: 1.1rem 1.4rem;
    margin: 0.7rem 0;
}
.card-title {
    font-weight: 600;
    color: #0a2342;
    margin-bottom: 0.3rem;
}
.tag {
    display: inline-block;
    background: #1a7dc4;
    color: white;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    margin: 2px 3px;
}
.tag-red   { background: #c0392b; }
.tag-orange{ background: #d35400; }
.tag-green { background: #27ae60; }
.tag-grey  { background: #7f8c8d; }
.divider { border-top: 2px solid #d5e8f5; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Dataset ───────────────────────────────────────────────────────────────────

AREAS = [
    "Calanques National Park (Marseille)",
    "Gulf of Lion (Open Sea)",
    "Côte Bleue Marine Park",
    "Port-Cros National Park",
    "Étang de Berre (Lagoon)",
    "Camargue Coast",
    "Nice / Côte d'Azur",
    "Corsica Coast",
]

FISHING_TYPES = ["Shore fishing", "Boat fishing", "Spearfishing", "Fly fishing", "Kayak fishing"]

MONTHS = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December",
]

MONTH_SEASON = {
    "January": "winter", "February": "winter", "March": "spring",
    "April": "spring", "May": "spring", "June": "summer",
    "July": "summer", "August": "summer", "September": "autumn",
    "October": "autumn", "November": "autumn", "December": "winter",
}

# species dataset
SPECIES = {
    "European Sea Bass (Loup)": {
        "fr_name": "Bar / Loup",
        "status": "restricted",
        "min_size_cm": 42,
        "bag_limit": 3,
        "seasons_ok": ["spring", "summer", "autumn"],
        "seasons_closed": ["winter"],
        "areas_banned": ["Port-Cros National Park"],
        "spearfishing_ok": True,
        "notes": "Minimum landing size strictly enforced. Stock under pressure — keep only what you need.",
        "sustainability": "medium",
    },
    "Gilt-head Bream (Daurade)": {
        "fr_name": "Daurade royale",
        "status": "restricted",
        "min_size_cm": 25,
        "bag_limit": 5,
        "seasons_ok": ["spring", "summer", "autumn"],
        "seasons_closed": ["winter"],
        "areas_banned": ["Côte Bleue Marine Park", "Port-Cros National Park"],
        "spearfishing_ok": True,
        "notes": "Protected inside marine reserves. Good recovery outside reserves.",
        "sustainability": "medium",
    },
    "Red Mullet (Rouget)": {
        "fr_name": "Rouget de roche",
        "status": "allowed",
        "min_size_cm": 15,
        "bag_limit": 10,
        "seasons_ok": ["spring", "summer", "autumn", "winter"],
        "seasons_closed": [],
        "areas_banned": [],
        "spearfishing_ok": True,
        "notes": "Widely abundant in rocky Mediterranean areas. Good choice for sustainability.",
        "sustainability": "good",
    },
    "Common Octopus (Poulpe)": {
        "fr_name": "Pieuvre / Poulpe",
        "status": "allowed",
        "min_size_cm": 60,  # mantle + arms
        "bag_limit": 3,
        "seasons_ok": ["spring", "summer", "autumn"],
        "seasons_closed": ["winter"],
        "areas_banned": [],
        "spearfishing_ok": True,
        "notes": "Bag limit of 3 per person per day. Measure total length including arms.",
        "sustainability": "good",
    },
    "European Conger (Congre)": {
        "fr_name": "Congre",
        "status": "allowed",
        "min_size_cm": 58,
        "bag_limit": 5,
        "seasons_ok": ["spring", "summer", "autumn", "winter"],
        "seasons_closed": [],
        "areas_banned": [],
        "spearfishing_ok": True,
        "notes": "Popular with spearfishers. Prefers rocky caves and wrecks.",
        "sustainability": "good",
    },
    "Greater Amberjack (Sériole)": {
        "fr_name": "Sériole",
        "status": "restricted",
        "min_size_cm": 70,
        "bag_limit": 3,
        "seasons_ok": ["summer", "autumn"],
        "seasons_closed": ["winter", "spring"],
        "areas_banned": [],
        "spearfishing_ok": True,
        "notes": "Migratory pelagic species. Best in warmer months. Size limit strictly enforced.",
        "sustainability": "medium",
    },
    "Atlantic Bluefin Tuna": {
        "fr_name": "Thon rouge",
        "status": "protected",
        "min_size_cm": 115,
        "bag_limit": 0,
        "seasons_ok": [],
        "seasons_closed": ["winter", "spring", "summer", "autumn"],
        "areas_banned": AREAS,
        "spearfishing_ok": False,
        "notes": "⛔ Strictly prohibited for recreational anglers in French Mediterranean waters. Report any accidental catch and release immediately.",
        "sustainability": "critical",
    },
    "European Eel (Anguille)": {
        "fr_name": "Anguille européenne",
        "status": "protected",
        "min_size_cm": None,
        "bag_limit": 0,
        "seasons_ok": [],
        "seasons_closed": ["winter", "spring", "summer", "autumn"],
        "areas_banned": AREAS,
        "spearfishing_ok": False,
        "notes": "⛔ Critically endangered. Catch-and-release only if caught accidentally. Fishing actively banned.",
        "sustainability": "critical",
    },
    "Dusky Grouper (Mérou)": {
        "fr_name": "Mérou brun",
        "status": "protected",
        "min_size_cm": None,
        "bag_limit": 0,
        "seasons_ok": [],
        "seasons_closed": ["winter", "spring", "summer", "autumn"],
        "areas_banned": AREAS,
        "spearfishing_ok": False,
        "notes": "⛔ Fully protected in French waters. Catch-and-release only. Major spearfishing penalties apply.",
        "sustainability": "critical",
    },
    "Dentex (Denté)": {
        "fr_name": "Denté commun",
        "status": "restricted",
        "min_size_cm": 25,
        "bag_limit": 5,
        "seasons_ok": ["spring", "summer"],
        "seasons_closed": ["autumn", "winter"],
        "areas_banned": ["Port-Cros National Park", "Côte Bleue Marine Park"],
        "spearfishing_ok": True,
        "notes": "Prized Mediterranean species. Best season is late spring to summer.",
        "sustainability": "medium",
    },
    "Sarago (White Seabream)": {
        "fr_name": "Sarago commun",
        "status": "allowed",
        "min_size_cm": 20,
        "bag_limit": 10,
        "seasons_ok": ["spring", "summer", "autumn", "winter"],
        "seasons_closed": [],
        "areas_banned": [],
        "spearfishing_ok": True,
        "notes": "Very common in rocky shallow waters. Beginner-friendly target species.",
        "sustainability": "good",
    },
}

AREA_NOTES = {
    "Calanques National Park (Marseille)": {
        "type": "National Park",
        "restrictions": [
            "No boat fishing within 300m of shore in core zones.",
            "Spearfishing banned in all National Park waters.",
            "No fishing in Zones de Non-Prélèvement (ZNP).",
            "Seasonal restrictions apply from April to September (nesting/spawning).",
        ],
        "allowed_types": ["Shore fishing"],
        "best_spots": "Côte bleue side, outside core protection zones.",
    },
    "Gulf of Lion (Open Sea)": {
        "type": "Open Sea",
        "restrictions": [
            "Standard French Mediterranean recreational fishing rules apply.",
            "Bag limits per species must be respected.",
            "No trawling equipment allowed for recreational vessels.",
        ],
        "allowed_types": ["Shore fishing", "Boat fishing", "Spearfishing", "Kayak fishing"],
        "best_spots": "Canyon edges and underwater banks attract pelagic species.",
    },
    "Côte Bleue Marine Park": {
        "type": "Marine Park",
        "restrictions": [
            "Fishing restricted in core reserve zones.",
            "Some species (Gilt-head Bream) have additional protections here.",
            "Boats must not anchor on Posidonia seagrass beds.",
            "No spearfishing inside reserve zones.",
        ],
        "allowed_types": ["Shore fishing", "Boat fishing (outside reserve zones)"],
        "best_spots": "Buffer zones on eastern and western edges of the park.",
    },
    "Port-Cros National Park": {
        "type": "National Park (Strict)",
        "restrictions": [
            "Fishing is almost entirely prohibited throughout the park.",
            "No recreational fishing of any kind in core zones.",
            "No spearfishing.",
            "Entry requires park authorization for any water activity.",
        ],
        "allowed_types": ["None (park waters)", "Shore fishing (peripheral areas only)"],
        "best_spots": "Fish outside park boundaries — Hyères area nearby.",
    },
    "Étang de Berre (Lagoon)": {
        "type": "Lagoon / Estuary",
        "restrictions": [
            "Lagoon has specific freshwater/brackish species rules.",
            "Industrial pollution history — check health advisories before consuming catch.",
            "Net fishing prohibited for recreational anglers.",
        ],
        "allowed_types": ["Shore fishing", "Fly fishing"],
        "best_spots": "Eastern banks near Berre town for mullet and bass.",
    },
    "Camargue Coast": {
        "type": "Natural Reserve",
        "restrictions": [
            "Large sections of Camargue delta are Natura 2000 zones.",
            "Waterfowl disturbance rules may restrict access to some zones.",
            "Freshwater rules apply in river delta sections.",
        ],
        "allowed_types": ["Shore fishing", "Kayak fishing", "Fly fishing"],
        "best_spots": "Grau du Roi and beach areas outside protected zones.",
    },
    "Nice / Côte d'Azur": {
        "type": "Open Coast",
        "restrictions": [
            "Standard French Mediterranean rules apply.",
            "Some local municipal pier restrictions.",
            "Monaco EEZ has additional rules near the border.",
        ],
        "allowed_types": ["Shore fishing", "Boat fishing", "Spearfishing", "Kayak fishing"],
        "best_spots": "Rocky headlands and submerged reefs offshore.",
    },
    "Corsica Coast": {
        "type": "Regional Park / Open Coast",
        "restrictions": [
            "Réserve naturelle de Scandola strictly prohibits all fishing.",
            "Regional parks have additional species protections.",
            "Spearfishing banned in all reserves.",
        ],
        "allowed_types": ["Shore fishing", "Boat fishing (outside reserves)", "Spearfishing (open coast)"],
        "best_spots": "Southern cap areas and eastern coast outside reserve zones.",
    },
}

BEST_TARGETS_BY_SEASON = {
    "winter":  ["Red Mullet (Rouget)", "European Conger (Congre)", "Sarago (White Seabream)"],
    "spring":  ["European Sea Bass (Loup)", "Gilt-head Bream (Daurade)", "Dentex (Denté)", "Sarago (White Seabream)"],
    "summer":  ["Greater Amberjack (Sériole)", "Common Octopus (Poulpe)", "European Sea Bass (Loup)", "Dentex (Denté)"],
    "autumn":  ["European Sea Bass (Loup)", "Gilt-head Bream (Daurade)", "Common Octopus (Poulpe)", "Red Mullet (Rouget)"],
}

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐟 SmartFishing Med")
    st.markdown("*Sustainable fishing planner for the Mediterranean*")
    st.divider()
    page = st.radio(
        "Navigation",
        ["🗓️ Trip Planner", "📋 Species & Rules Checker", "💡 Project Overview"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("""
    <div style='font-size:0.8rem; color:#7fbfdf; line-height:1.6'>
    ⚠️ <b>Disclaimer</b><br>
    This app provides educational guidance only.
    Always verify current regulations with
    <a href='https://www.legifrance.gouv.fr' style='color:#7fbfdf'>French official sources</a>
    before fishing.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — TRIP PLANNER
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🗓️ Trip Planner":
    st.markdown('<div class="hero-title">🗓️ Fishing Trip Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Plan a legal, sustainable fishing trip in the Mediterranean</div>', unsafe_allow_html=True)

    with st.form("trip_form"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.selectbox("📍 Fishing Area", AREAS)
            month = st.selectbox("📅 Month", MONTHS, index=datetime.now().month - 1)
            fishing_type = st.selectbox("🎣 Fishing Method", FISHING_TYPES)
        with col2:
            target_species = st.multiselect(
                "🐠 Target Species (select up to 3)",
                list(SPECIES.keys()),
                max_selections=3,
                help="Pick the species you'd like to catch.",
            )
            experience = st.select_slider(
                "Your experience level",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Intermediate",
            )
        submitted = st.form_submit_button("🔍 Get My Trip Recommendation", use_container_width=True)

    if submitted:
        season = MONTH_SEASON[month]
        area_info = AREA_NOTES[area]
        good_targets = BEST_TARGETS_BY_SEASON[season]

        st.markdown("---")
        st.subheader(f"📊 Trip Summary — {area} in {month}")

        # ── Area legal check
        st.markdown("### 📍 Area Regulations")
        st.markdown(f'<div class="card"><div class="card-title">{area} — {area_info["type"]}</div>', unsafe_allow_html=True)
        for r in area_info["restrictions"]:
            st.markdown(f"• {r}")
        allowed = area_info["allowed_types"]
        if fishing_type.split(" ")[0] in " ".join(allowed) or any(fishing_type in a for a in allowed):
            st.success(f"✅ **{fishing_type}** is permitted in this area.")
        else:
            if "None" in " ".join(allowed):
                st.error(f"⛔ Fishing is essentially **prohibited** in {area}. Choose a different location.")
            else:
                st.warning(f"⚠️ **{fishing_type}** may be restricted here. Allowed methods: {', '.join(allowed)}")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Species checks
        st.markdown("### 🐠 Species Checks")
        if not target_species:
            st.info("ℹ️ You didn't select any target species. See seasonal recommendations below.")
        else:
            for sp_name in target_species:
                sp = SPECIES[sp_name]
                in_season = season in sp["seasons_ok"]
                area_banned = area in sp.get("areas_banned", [])
                spear_ok = sp["spearfishing_ok"] or fishing_type != "Spearfishing"
                fully_protected = sp["status"] == "protected"

                cols = st.columns([3, 1])
                with cols[0]:
                    if fully_protected or area_banned or not in_season or not spear_ok:
                        st.error(f"⛔ **{sp_name}** ({sp['fr_name']})")
                    elif sp["sustainability"] == "medium":
                        st.warning(f"⚠️ **{sp_name}** ({sp['fr_name']})")
                    else:
                        st.success(f"✅ **{sp_name}** ({sp['fr_name']})")

                    if fully_protected:
                        st.markdown(f"🚫 **FULLY PROTECTED** — Do not target this species. {sp['notes']}")
                    else:
                        if not in_season:
                            closed = ", ".join(sp["seasons_closed"]) or "none"
                            st.markdown(f"🗓️ **Out of season** in {month} (closed: {closed.title()})")
                        if area_banned:
                            st.markdown(f"📍 **Not allowed** in {area}")
                        if not spear_ok:
                            st.markdown("🤿 **Spearfishing banned** for this species")
                        if sp["min_size_cm"]:
                            st.markdown(f"📏 Minimum size: **{sp['min_size_cm']} cm**")
                        if sp["bag_limit"] and sp["bag_limit"] > 0:
                            st.markdown(f"🎒 Bag limit: **{sp['bag_limit']} per person/day**")
                        st.markdown(f"💬 {sp['notes']}")
                with cols[1]:
                    sust = sp["sustainability"]
                    color = {"good": "🟢", "medium": "🟡", "critical": "🔴"}.get(sust, "⚪")
                    st.metric("Sustainability", f"{color} {sust.title()}")

        # ── Seasonal recommendations
        st.markdown("### 🌊 Best Targets This Season")
        st.markdown(f"In **{season.title()}**, these species are in season and sustainable:")
        rec_cols = st.columns(len(good_targets))
        for i, sp_name in enumerate(good_targets):
            with rec_cols[i]:
                sp = SPECIES.get(sp_name, {})
                sust = sp.get("sustainability", "good")
                icon = "🟢" if sust == "good" else "🟡"
                st.markdown(f"<div class='card'><b>{icon} {sp_name}</b><br><small>{sp.get('fr_name','')}</small><br>Min size: {sp.get('min_size_cm','—')} cm<br>Bag limit: {sp.get('bag_limit','—')}</div>", unsafe_allow_html=True)

        # ── General tips
        st.markdown("### 💡 General Tips for This Trip")
        tips = [
            "Always carry your fishing licence (Permis de pêche en mer).",
            "Keep a measuring tape to check minimum fish sizes before keeping.",
            "Use barbless hooks when possible to improve catch-and-release survival.",
            f"Best tides and light in {month}: early morning (1h before sunrise) and evening (1h before sunset).",
            "Photograph rare or uncertain species before release — helps track biodiversity.",
        ]
        if experience == "Beginner":
            tips.append("🔰 Beginner tip: Shore fishing with light tackle is safest and requires no boat licence.")
        for t in tips:
            st.markdown(f"• {t}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SPECIES & RULES CHECKER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Species & Rules Checker":
    st.markdown('<div class="hero-title">📋 Species & Rules Checker</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Look up rules, protections, and seasons for Mediterranean species and areas</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🐠 Species Lookup", "📍 Area Rules"])

    with tab1:
        selected_sp = st.selectbox("Select a species", list(SPECIES.keys()))
        sp = SPECIES[selected_sp]

        # Status badge
        status_colors = {"allowed": "🟢 ALLOWED", "restricted": "🟡 RESTRICTED", "protected": "🔴 FULLY PROTECTED"}
        sust_colors   = {"good": "🟢 Good", "medium": "🟡 Medium concern", "critical": "🔴 Critical"}
        st.markdown(f"## {selected_sp}")
        st.markdown(f"**French name:** {sp['fr_name']}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Legal Status", status_colors.get(sp["status"], sp["status"]))
        c2.metric("Sustainability", sust_colors.get(sp["sustainability"], sp["sustainability"]))
        c3.metric("Bag Limit / day", sp["bag_limit"] if sp["bag_limit"] > 0 else "❌ BANNED")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📏 Minimum landing size**")
            if sp["min_size_cm"]:
                st.markdown(f"### {sp['min_size_cm']} cm")
            else:
                st.markdown("❌ Not applicable (catch banned)")

            st.markdown("**🗓️ Open seasons**")
            if sp["seasons_ok"]:
                for s in sp["seasons_ok"]:
                    st.markdown(f"✅ {s.title()}")
            else:
                st.markdown("❌ No open season — fully protected")

            st.markdown("**🚫 Closed seasons**")
            if sp["seasons_closed"]:
                for s in sp["seasons_closed"]:
                    st.markdown(f"🔴 {s.title()}")
            else:
                st.markdown("None")

        with col2:
            st.markdown("**🤿 Spearfishing allowed?**")
            st.markdown("✅ Yes" if sp["spearfishing_ok"] else "❌ No")

            st.markdown("**📍 Areas with additional bans**")
            if sp.get("areas_banned"):
                for a in sp["areas_banned"]:
                    st.markdown(f"⛔ {a}")
            else:
                st.markdown("No area-specific bans (standard rules apply)")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        if sp["status"] == "protected":
            st.error(f"⛔ {sp['notes']}")
        elif sp["sustainability"] == "critical":
            st.error(f"⚠️ {sp['notes']}")
        elif sp["sustainability"] == "medium":
            st.warning(f"⚠️ {sp['notes']}")
        else:
            st.success(f"✅ {sp['notes']}")

        # Full species table
        st.markdown("---")
        st.markdown("### 📊 All Species at a Glance")
        rows = []
        for name, s in SPECIES.items():
            rows.append({
                "Species": name,
                "French Name": s["fr_name"],
                "Status": s["status"].upper(),
                "Min Size (cm)": s["min_size_cm"] or "BANNED",
                "Bag Limit": s["bag_limit"] if s["bag_limit"] > 0 else "BANNED",
                "Open Seasons": ", ".join(s["seasons_ok"]).title() if s["seasons_ok"] else "NONE",
                "Sustainability": s["sustainability"].title(),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        selected_area = st.selectbox("Select an area", AREAS)
        ar = AREA_NOTES[selected_area]

        st.markdown(f"## {selected_area}")
        st.markdown(f"**Zone type:** {ar['type']}")

        st.markdown("### 🚫 Restrictions")
        for r in ar["restrictions"]:
            if any(w in r for w in ["prohibited", "banned", "ban", "No fishing", "strictly"]):
                st.error(f"⛔ {r}")
            elif "restricted" in r.lower() or "additional" in r.lower():
                st.warning(f"⚠️ {r}")
            else:
                st.info(f"ℹ️ {r}")

        st.markdown("### ✅ Permitted Fishing Methods")
        for m in ar["allowed_types"]:
            if "None" in m:
                st.error(f"⛔ {m}")
            else:
                st.success(f"✅ {m}")

        st.markdown("### 📌 Best Spots Nearby")
        st.info(f"🗺️ {ar['best_spots']}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — PROJECT OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💡 Project Overview":
    st.markdown('<div class="hero-title">💡 SmartFishing AI — Project Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Academic presentation — Concept, positioning & value proposition</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Concept", "👤 Target Segment", "📊 Competitor Positioning", "💎 Value Proposition"])

    with tab1:
        st.markdown("## What is SmartFishing AI?")
        st.markdown("""
SmartFishing AI is a **decision-support tool for recreational marine fishers** in the Mediterranean.
It combines a localised regulation database with sustainability guidance to help anglers fish legally,
responsibly, and more successfully.

The core insight is simple: **most recreational fishing rule violations are accidental**.
Fishers often don't know which species are protected, what the minimum sizes are, or where restrictions apply.
SmartFishing AI removes this information gap.
        """)

        col1, col2, col3 = st.columns(3)
        col1.markdown('<div class="card"><div class="card-title">🎣 The Problem</div>Recreational fishers lack easy access to local, up-to-date rules. Violations happen by accident, causing ecosystem harm and legal risk.</div>', unsafe_allow_html=True)
        col2.markdown('<div class="card"><div class="card-title">💡 The Solution</div>A simple app that checks species legality, seasonal closures, and area restrictions — and suggests sustainable alternatives.</div>', unsafe_allow_html=True)
        col3.markdown('<div class="card"><div class="card-title">🌊 The Impact</div>Fewer illegal catches. Better fish stock recovery. More confident, informed anglers who fish sustainably.</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("## Target Segment")

        st.markdown("""
**Primary users:** Recreational marine fishers aged 25–60, based in or visiting the French Mediterranean coast (Marseille, Toulon, Nice, Corsica).

**Profile characteristics:**
- Fishes 1–4 times per month, mostly from shore or small boats
- Cares about following rules but finds regulations complex and hard to find
- Increasingly conscious of marine conservation
- Uses a smartphone before and during fishing trips
- Belongs to local fishing clubs or online communities (forums, Facebook groups)

**Size of opportunity:** France counts approximately **1.5 million saltwater recreational fishers**.
The Mediterranean coast accounts for an estimated 300,000–400,000 of these.
        """)

        col1, col2 = st.columns(2)
        col1.markdown("### 🧭 User Needs")
        col1.markdown("""
- Know **what** is legal to catch, **where** and **when**
- Avoid accidental fines or ecological damage
- Plan trips efficiently with confidence
- Get simple, actionable guidance — not legal text
        """)
        col2.markdown("### 😤 Current Frustrations")
        col2.markdown("""
- Regulations scattered across government websites
- Rules change seasonally and differ by zone
- No single mobile-friendly resource
- Peer advice online is often outdated or wrong
        """)

    with tab3:
        st.markdown("## Competitor Positioning")

        data = {
            "Product": [
                "SmartFishing AI",
                "FishBrain",
                "iAngler",
                "Légifrance (official)",
                "Local fishing club advice",
            ],
            "Legal Rules": ["✅ Full", "❌ None", "⚠️ Partial (US-focused)", "✅ Full (raw text)", "⚠️ Informal"],
            "Mediterranean Focus": ["✅ Yes", "⚠️ Generic", "❌ No", "✅ Yes", "✅ Yes"],
            "Sustainability Guidance": ["✅ Yes", "❌ No", "❌ No", "❌ No", "⚠️ Varies"],
            "Trip Planning": ["✅ Yes", "✅ Yes", "✅ Yes", "❌ No", "❌ No"],
            "Ease of Use": ["✅ High", "✅ High", "✅ High", "❌ Low", "⚠️ Medium"],
            "Free": ["✅ Yes", "⚠️ Freemium", "⚠️ Freemium", "✅ Yes", "✅ Yes"],
        }
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

        st.markdown("""
**Key insight:** No existing product combines **Mediterranean-specific regulations + sustainability guidance + trip planning** in a single, easy-to-use free tool.
FishBrain leads on social features but has zero legal compliance tools.
Official government sources have the data but are inaccessible to ordinary users.

SmartFishing AI fills the **"Legal + Local + Simple"** gap.
        """)

    with tab4:
        st.markdown("## Value Proposition")

        st.success("**For the angler:** Fish with confidence. Know the rules before you go. Protect yourself from fines and help protect the sea.")
        st.info("**For the ecosystem:** Fewer accidental catches of protected or undersized fish. Better enforcement culture through education.")
        st.warning("**For regulators & NGOs:** A scalable, low-cost tool to communicate conservation rules to thousands of fishers.")

        st.markdown("---")
        st.markdown("### 📈 Business Model (Future)")

        col1, col2, col3 = st.columns(3)
        col1.markdown('<div class="card"><div class="card-title">🆓 Free Core</div>Species checker and basic trip planner always free — drives adoption and serves conservation mission.</div>', unsafe_allow_html=True)
        col2.markdown('<div class="card"><div class="card-title">⭐ Premium</div>Real-time regulation alerts, offline mode, weather & tide integration, personalised catch log. €3.99/month.</div>', unsafe_allow_html=True)
        col3.markdown('<div class="card"><div class="card-title">🤝 B2B2C</div>White-label for fishing clubs, marine parks, or regional tourism authorities. Licensing model.</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🛣️ Roadmap")
        roadmap = {
            "Phase": ["MVP (Now)", "Phase 2 (6 mo)", "Phase 3 (12 mo)"],
            "Focus": ["Rules database + trip planner (this app)", "Real-time tide/weather + offline mode", "Community catch log + ranger partnership"],
            "Goal": ["Validate product-market fit", "Grow to 5,000 active users", "Monetise and scale regionally"],
        }
        st.dataframe(pd.DataFrame(roadmap), use_container_width=True, hide_index=True)

        st.markdown("""
---
*SmartFishing AI — developed as part of an entrepreneurship academic project. Data based on French Mediterranean recreational fishing regulations (DPMA / Légifrance). Always verify with official sources.*
        """)
