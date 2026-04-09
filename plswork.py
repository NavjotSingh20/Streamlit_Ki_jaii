import streamlit as st
import numpy as np
import tensorflow as tf
import requests
import time
import plotly.graph_objects as go

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Motion Sense",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"Get help": None, "Report a bug": None, "About": None}
)

# ── CUSTOM CSS (from Codeset 1) ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

    :root {
        --bg: #020307;
        --surface: #090d16;
        --surface-soft: #0e1524;
        --surface-raise: #121d33;
        --text-strong: #f7fbff;
        --text-muted: #a5b3ca;
        --accent: #3b82f6;
        --accent-strong: #1d4ed8;
        --success: #22c55e;
        --border: #1d2b45;
        --border-strong: #2b4062;
        --radius-lg: 18px;
        --radius-md: 12px;
        --space-sm: 0.78rem;
        --space-md: 1.15rem;
        --space-lg: 1.55rem;
        --space-xl: 2.1rem;
        --shadow-card: 0 16px 34px rgba(0,0,0,0.5);
        --shadow-card-hover: 0 22px 42px rgba(0,0,0,0.62);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 8% -14%, rgba(59,130,246,0.16), transparent 34%),
            radial-gradient(circle at 100% -25%, rgba(29,78,216,0.14), transparent 28%),
            linear-gradient(180deg, #020307 0%, #050a14 100%);
        color: var(--text-strong);
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(2,3,7,0.9) !important;
        border-bottom: 1px solid var(--border) !important;
        backdrop-filter: blur(10px);
    }

    [data-testid="stMainBlockContainer"] {
        padding: 1.15rem 1.15rem 2rem;
        max-width: 1300px;
        margin: 0 auto;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #050b17 0%, #0a1222 100%) !important;
        border-right: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stMarkdown {
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
        color: var(--text-strong) !important;
        font-weight: 700 !important;
    }

    h1, h2, h3 {
        color: var(--text-strong);
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', sans-serif;
        font-weight: 900;
        letter-spacing: -0.02em;
    }

    p, label {
        color: var(--text-muted);
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        line-height: 1.55;
    }

    [data-testid="stButton"] button {
        background: linear-gradient(120deg, var(--accent) 0%, var(--accent-strong) 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: 0.01em !important;
        font-size: 1.12rem !important;
        padding: 0.9rem 1.2rem !important;
        box-shadow: 0 10px 20px rgba(40,111,255,0.35) !important;
        transition: all 0.2s ease !important;
        position: relative !important;
        overflow: hidden !important;
        isolation: isolate !important;
    }

    [data-testid="stButton"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 14px 25px rgba(40,111,255,0.46) !important;
    }

    [data-testid="stButton"] button:active {
        transform: translateY(0) !important;
    }

    [data-testid="stTextInput"] input {
        background: var(--surface-soft) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-strong) !important;
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', 'Segoe UI', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.22) !important;
        background: #111b2f !important;
    }

    hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.1rem 0 !important; }

    .status-strip {
        display: flex; gap: 0.7rem; flex-wrap: wrap;
        justify-content: center; margin: 0.2rem auto 1rem; max-width: 980px;
    }

    .status-pill {
        padding: 0.5rem 0.85rem; border-radius: 999px;
        border: 1px solid var(--border);
        background: linear-gradient(160deg, #0f1729 0%, #0b1220 100%);
        color: var(--text-strong);
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', sans-serif;
        font-size: 0.82rem; font-weight: 700; letter-spacing: 0.04em;
        box-shadow: 0 6px 16px rgba(0,0,0,0.35);
    }

    .status-pill b { color: #f3f8ff; font-weight: 800; }
    .pill-good    { border-color: rgba(34,197,94,0.55);  box-shadow: 0 0 0 1px rgba(34,197,94,0.25) inset; }
    .pill-warn    { border-color: rgba(251,191,36,0.55); box-shadow: 0 0 0 1px rgba(251,191,36,0.2) inset; }
    .pill-neutral { border-color: rgba(165,179,202,0.42); }

    .page-hero { text-align: center; margin-bottom: var(--space-xl); padding: 0.55rem 0 0.3rem; }

    .page-title {
        font-size: clamp(3.1rem, 5.8vw, 4.8rem);
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', sans-serif;
        font-weight: 900; line-height: 1; margin-bottom: 0.55rem; color: #f7fbff;
    }

    .subtitle {
        color: #83adff;
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', sans-serif;
        font-size: 1.05rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase;
    }

    .status-ready    { color: var(--success); font-weight: 700; font-size: 0.96rem; }
    .status-notready { color: #a5b3ca; font-weight: 600; }

    .state-card {
        background: linear-gradient(170deg, #0c111d 0%, #080d17 100%);
        border: 1px solid var(--border); border-radius: var(--radius-lg);
        padding: 1.95rem 1.3rem; text-align: center;
        box-shadow: var(--shadow-card); max-width: 960px; margin: 0 auto;
        min-height: 186px; display: flex; flex-direction: column;
        justify-content: center; gap: 0.18rem; position: relative; overflow: hidden;
    }

    .state-card::before {
        content: ""; position: absolute; inset: 1px;
        border-radius: inherit; border: 1px solid rgba(255,255,255,0.045); pointer-events: none;
    }

    .is-loading::after {
        content: ""; position: absolute; inset: -10%; opacity: 1 !important;
        animation: shimmerSweep 1.8s linear infinite;
        background: linear-gradient(110deg, rgba(59,130,246,0.0) 20%, rgba(59,130,246,0.18) 45%, rgba(59,130,246,0.0) 70%);
    }

    .skeleton-line { height: 10px; border-radius: 999px; background: rgba(165,179,202,0.24); margin: 0.3rem auto; }
    .skeleton-line.w-60 { width: 60%; }
    .skeleton-line.w-42 { width: 42%; }
    .skeleton-line.w-35 { width: 35%; }

    .state-title {
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', sans-serif;
        font-size: 2.1rem; font-weight: 800; color: #f5f9ff; margin-bottom: 0.48rem;
    }

    .state-copy {
        color: var(--text-muted);
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', sans-serif;
        font-size: 1.12rem; font-weight: 600;
    }

    .accent { color: #8eb6ff; font-weight: 800; }

    .glass-container {
        background: linear-gradient(170deg, #0d1526 0%, #090f1b 100%);
        border: 1px solid var(--border); border-radius: var(--radius-lg);
        padding: var(--space-lg); box-shadow: var(--shadow-card);
        transition: all 0.25s ease; position: relative; overflow: hidden;
    }

    .glass-container:hover {
        border-color: var(--border-strong);
        box-shadow: var(--shadow-card-hover);
        transform: translateY(-2px);
    }

    .section-title {
        margin-bottom: 0.8rem; color: #e8efff;
        font-family: 'Bricolage Grotesque', 'Plus Jakarta Sans', sans-serif;
        font-weight: 800; font-size: 1.35rem;
    }

    .prob-top {
        margin-bottom: 0.9rem; border-radius: 14px;
        border: 1px solid var(--border-strong);
        background: linear-gradient(165deg, #12203a 0%, #0e182b 100%);
        padding: 0.95rem 1rem;
        display: flex; justify-content: space-between; align-items: center; gap: 0.8rem;
    }
    .prob-top .name  { font-family: 'Bricolage Grotesque','Plus Jakarta Sans',sans-serif; font-size: 1.1rem;  font-weight: 800; color: #f5f9ff; }
    .prob-top .score { font-family: 'Bricolage Grotesque','Plus Jakarta Sans',sans-serif; font-size: 1.35rem; font-weight: 800; color: #f5f9ff; }

    .prob-list { display: grid; gap: 0.6rem; }

    .prob-row {
        display: grid;
        grid-template-columns: minmax(100px,120px) 1fr minmax(86px,100px);
        align-items: center; gap: 0.65rem;
    }
    .prob-row .name { color: #c2d3ec; font-size: 0.86rem; font-weight: 700; letter-spacing: 0.02em; }
    .prob-track { height: 10px; border-radius: 999px; background: #1a263f; overflow: hidden; border: 1px solid #273a5a; }
    .prob-fill  { height: 100%; border-radius: 999px; transition: width 0.35s ease; }
    .prob-meta  { text-align: right; color: #d9e5fb; font-size: 0.86rem; font-weight: 700; }
    .delta-up   { color: #22c55e; }
    .delta-down { color: #f97316; }

    @keyframes shimmerSweep {
        0%   { transform: translateX(-120%); }
        100% { transform: translateX(120%); }
    }

    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] { padding: 0.92rem 0.6rem 1.25rem; }
        .glass-container { padding: 0.9rem; }
        .state-card { padding: 1.35rem 0.85rem; min-height: 156px; }
        .page-title { font-size: clamp(1.95rem,8vw,2.55rem); }
        .subtitle   { letter-spacing: 0.08em; font-size: 0.76rem; }
    }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
CLASS_NAMES = [
    "Walking", "Walking Up", "Walking Down",
    "Sitting", "Standing", "Laying"
]

CLASS_EMOJI = {
    "Walking": "🚶",
    "Walking Up": "🔼",
    "Walking Down": "🔽",
    "Sitting": "🪑",
    "Standing": "🧍",
    "Laying": "🛌",
    "Unknown": "❓"
}

CLASS_COLOR = {
    "Walking":      "#FF6B6B",
    "Walking Up":   "#0066FF",
    "Walking Down": "#FFB800",
    "Sitting":      "#FF006B",
    "Standing":     "#6B5BFF",
    "Laying":       "#00C9A7",
    "Unknown":      "#999999"
}

CLASS_GRADIENT = {
    "Walking":      "linear-gradient(135deg, #FF6B6B 0%, #FF4444 100%)",
    "Walking Up":   "linear-gradient(135deg, #0066FF 0%, #0044CC 100%)",
    "Walking Down": "linear-gradient(135deg, #FFB800 0%, #FF9500 100%)",
    "Sitting":      "linear-gradient(135deg, #FF006B 0%, #DD0055 100%)",
    "Standing":     "linear-gradient(135deg, #6B5BFF 0%, #5533EE 100%)",
    "Laying":       "linear-gradient(135deg, #00C9A7 0%, #009988 100%)",
    "Unknown":      "linear-gradient(135deg, #999999 0%, #777777 100%)"
}

# 🔥 Strong correction
CORRECTION_MAP = {1: 0, 2: 0, 5: 3}

CONFIDENCE_THRESHOLD = 0.55
SMOOTHING_WINDOW = 15
BUFFER_SIZE = 128
CONFIDENCE_DISPLAY_MAX = 0.92

# ── MODEL ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("model.h5")

model = load_model()

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for key, default in [
    ("buffer", []),
    ("running", False),
    ("pred_history", []),
    ("error_count", 0),
    ("render_count", 0),
    ("prev_probs", [0.0] * len(CLASS_NAMES)),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "calibrated" not in st.session_state:
    st.session_state.calibrated = False

if "calibrating" not in st.session_state:
    st.session_state.calibrating = False

if "calib_buffer" not in st.session_state:
    st.session_state.calib_buffer = []

if "calib_data" not in st.session_state:
    st.session_state.calib_data = {
        "acc_std": 0.12,
        "gyr_std": 0.04,
        "intensity": 0.75
    }

# ── HELPERS ───────────────────────────────────────────────────────────────────
def detect_stationary(X):
    acc = X[:, :3].astype(np.float32)
    gyr = X[:, 3:6].astype(np.float32)
    acc_mag = np.linalg.norm(acc, axis=1)
    gyr_mag = np.linalg.norm(gyr, axis=1)
    thresh = st.session_state.calib_data
    return np.std(acc_mag) < thresh["acc_std"] and np.std(gyr_mag) < thresh["gyr_std"]


def motion_intensity(X):
    acc = X[:, :3].astype(np.float32)
    return np.mean(np.linalg.norm(acc, axis=1))


def apply_correction(probs, threshold):
    raw_idx = int(np.argmax(probs))
    confidence = float(probs[raw_idx])
    if confidence < threshold:
        return "Unknown", confidence, False
    corrected_idx = CORRECTION_MAP.get(raw_idx, raw_idx)
    return CLASS_NAMES[corrected_idx], confidence, corrected_idx != raw_idx


# ── UI HELPERS (from Codeset 1) ───────────────────────────────────────────────
def activity_html(label, gradient):
    return f"""<div style="
        padding:2.55rem 1.75rem;text-align:center;border-radius:18px;
        margin-bottom:1.05rem;box-shadow:0 18px 34px rgba(0,0,0,0.52);
        background:{gradient};">
        <h2 style="color:#fff;margin:0 0 0.2rem 0;
            font-size:clamp(2.4rem,4.3vw,3.45rem);
            font-family:'Bricolage Grotesque','Plus Jakarta Sans',sans-serif;
            font-weight:800;letter-spacing:-0.03em;">{label}</h2>
        <p style="color:rgba(255,255,255,0.92);font-size:1.02rem;font-weight:600;margin:0;
            font-family:'Bricolage Grotesque','Plus Jakarta Sans',sans-serif;">Detected Activity</p>
    </div>"""


def confidence_html(confidence, color):
    d = min(confidence, CONFIDENCE_DISPLAY_MAX)
    pct = d * 100
    return f"""<div style="
        background:linear-gradient(170deg,#0d1526 0%,#090f1b 100%);
        border:1px solid #1d2b45;border-radius:18px;padding:1.55rem;
        box-shadow:0 16px 34px rgba(0,0,0,0.5);text-align:center;margin-bottom:1rem;">
        <p style="color:#a5b3ca;font-size:0.92rem;margin-bottom:0.76rem;
            text-transform:uppercase;font-weight:800;letter-spacing:0.12em;
            font-family:'Bricolage Grotesque','Plus Jakarta Sans',sans-serif;">Confidence</p>
        <div style="font-family:'Bricolage Grotesque','Plus Jakarta Sans',sans-serif;
            font-size:clamp(2.6rem,4.2vw,3.6rem);font-weight:800;
            margin-bottom:0.7rem;letter-spacing:-0.03em;color:{color};">{d:.0%}</div>
        <div style="background:#1a263f;border-radius:999px;height:8px;overflow:hidden;">
            <div style="height:100%;border-radius:999px;width:{pct:.1f}%;
                background:{color};transition:width 0.25s ease;"></div>
        </div>
    </div>"""


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Settings")
    st.divider()
    ip = st.text_input("Device IP", "192.168.137.167")
    url = f"http://{ip}:8080/get?accX&accY&accZ&gyrX&gyrY&gyrZ"

    confidence_threshold = st.slider("Confidence threshold", 0.30, 0.90, CONFIDENCE_THRESHOLD, 0.05)
    show_correction_badge = st.toggle("Show correction badge", value=True)

    st.divider()
    st.markdown("### Calibration")
    c1, c2 = st.columns(2)
    if c1.button("Calibrate", use_container_width=True, key="calib_btn"):
        st.session_state.calibrating = True
        st.session_state.calib_buffer = []

    if st.session_state.calibrated:
        c2.markdown("<span class='status-ready'>&#10003; Ready</span>", unsafe_allow_html=True)
    else:
        c2.markdown("<span class='status-notready'>- Not set</span>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### Controls")
    d1, d2 = st.columns(2)
    if d1.button("Start", use_container_width=True, key="start_btn"):
        st.session_state.running = True
        st.session_state.buffer = []
        st.session_state.pred_history = []
        st.session_state.error_count = 0
        st.session_state.render_count = 0
        st.session_state.prev_probs = [0.0] * len(CLASS_NAMES)

    if d2.button("Stop", use_container_width=True, key="stop_btn"):
        st.session_state.running = False
        st.session_state.buffer = []
        st.session_state.pred_history = []

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
    <h1 class="page-title">Motion Sense</h1>
    <p class="subtitle">Real-time Activity Recognition</p>
</div>
""", unsafe_allow_html=True)

# ── STATUS STRIP ──────────────────────────────────────────────────────────────
status_ph = st.empty()

if st.session_state.running and st.session_state.error_count == 0:
    conn_lbl, conn_cls = "Connected",    "pill-good"
elif st.session_state.error_count > 0:
    conn_lbl, conn_cls = "Reconnecting", "pill-warn"
else:
    conn_lbl, conn_cls = "Idle",         "pill-neutral"

mode_txt = ("Calibrating" if st.session_state.calibrating
            else ("Live" if st.session_state.running else "Standby"))

with status_ph.container():
    st.markdown(f"""
    <div class="status-strip">
        <span class="status-pill {conn_cls}">Device <b>{conn_lbl}</b></span>
        <span class="status-pill pill-neutral">Mode <b>{mode_txt}</b></span>
        <span class="status-pill pill-good">Model <b>Ready</b></span>
    </div>""", unsafe_allow_html=True)

placeholder = st.empty()

# ── IDLE STATE ────────────────────────────────────────────────────────────────
if not st.session_state.running:
    with placeholder.container():
        st.markdown("""
        <div class="state-card">
            <h2 class="state-title">Ready to Start</h2>
            <p class="state-copy">Configure your device in the sidebar, then press
                <span class="accent"> Start </span> to begin monitoring.</p>
        </div>""", unsafe_allow_html=True)
    st.stop()

# ── LIVE LOOP ─────────────────────────────────────────────────────────────────
while st.session_state.running:

    try:
        response = requests.get(url, timeout=1).json()

        acc_x = response['buffer']['accX']['buffer'][0]
        acc_y = response['buffer']['accY']['buffer'][0]
        acc_z = response['buffer']['accZ']['buffer'][0]
        gyr_x = response['buffer']['gyrX']['buffer'][0]
        gyr_y = response['buffer']['gyrY']['buffer'][0]
        gyr_z = response['buffer']['gyrZ']['buffer'][0]

        st.session_state.error_count = 0

    except Exception:
        st.session_state.error_count += 1

        with placeholder.container():
            st.markdown(f"""
            <div class="state-card is-loading">
                <h2 class="state-title">Waiting For Device</h2>
                <p class="state-copy">Retrying ({st.session_state.error_count})...</p>
                <div class="skeleton-line w-60"></div>
                <div class="skeleton-line w-35"></div>
            </div>""", unsafe_allow_html=True)

        time.sleep(0.1)
        continue

    # Sanitize: skip frame if any value is None or non-finite
    frame = [acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z]
    try:
        frame = [float(v) for v in frame]
        if not all(np.isfinite(frame)):
            raise ValueError("Non-finite sensor value")
    except (TypeError, ValueError):
        time.sleep(0.02)
        continue

    st.session_state.buffer.append(frame)
    if len(st.session_state.buffer) > BUFFER_SIZE:
        st.session_state.buffer.pop(0)

    # ── CALIBRATION ──────────────────────────────────────────────────────
    if st.session_state.calibrating:
        st.session_state.calib_buffer.append(frame)
        pct = min(int(len(st.session_state.calib_buffer) / 100 * 100), 100)

        with placeholder.container():
            st.markdown(f"""
            <div class="state-card is-loading">
                <h2 class="state-title">Calibrating Device</h2>
                <p class="state-copy">Please sit still while we establish baseline...</p>
                <div class="skeleton-line w-42"></div>
                <div style="font-family:'Bricolage Grotesque',sans-serif;font-size:2.5rem;
                            font-weight:800;color:#3b82f6;margin-top:1rem;">{pct}%</div>
                <div style="background:#1a263f;border-radius:999px;height:8px;
                            max-width:420px;margin:0.5rem auto 0;overflow:hidden;">
                    <div style="height:100%;border-radius:999px;width:{pct}%;
                                background:linear-gradient(90deg,#1f6fff,#17b891);"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        if len(st.session_state.calib_buffer) >= 100:
            calib = np.array(st.session_state.calib_buffer)
            acc = calib[:, :3]
            gyr = calib[:, 3:6]
            acc_mag = np.linalg.norm(acc, axis=1)
            gyr_mag = np.linalg.norm(gyr, axis=1)

            st.session_state.calib_data = {
                "acc_std": np.std(acc_mag) * 2.5,
                "gyr_std": np.std(gyr_mag) * 2.5,
                "intensity": np.mean(acc_mag) * 1.2
            }

            st.session_state.calibrated = True
            st.session_state.calibrating = False

        time.sleep(0.02)
        continue

    # ── WARMUP ───────────────────────────────────────────────────────────
    if len(st.session_state.buffer) < BUFFER_SIZE:
        pct = int(len(st.session_state.buffer) / BUFFER_SIZE * 100)
        with placeholder.container():
            st.markdown(f"""
            <div class="state-card is-loading">
                <h2 class="state-title">Collecting Sensor Window</h2>
                <p class="state-copy">Preparing inference buffer... {pct}%</p>
                <div class="skeleton-line w-60"></div>
                <div class="skeleton-line w-42"></div>
            </div>""", unsafe_allow_html=True)
        time.sleep(0.02)
        continue

    X_raw = np.array(st.session_state.buffer, dtype=np.float32)
    X_pad = np.pad(X_raw, ((0, 0), (0, 3)))

    intensity = motion_intensity(X_raw)

    # ── INFERENCE (Codeset 2 logic, unchanged) ────────────────────────────
    if detect_stationary(X_raw):
        label = "Sitting"
        confidence = 0.9
        was_corrected = True
        probs = np.zeros(6)
        probs[3] = 1.0

    elif intensity < st.session_state.calib_data["intensity"]:
        label = "Standing"
        confidence = 0.85
        was_corrected = True
        probs = np.zeros(6)
        probs[4] = 1.0

    else:
        probs = model(X_pad[np.newaxis, ...]).numpy()[0]
        label, confidence, was_corrected = apply_correction(probs, confidence_threshold)

    # 🔥 clamp confidence
    confidence = min(confidence, CONFIDENCE_DISPLAY_MAX)

    # smoothing
    st.session_state.pred_history.append(label)
    if len(st.session_state.pred_history) > SMOOTHING_WINDOW:
        st.session_state.pred_history.pop(0)

    final_label = max(set(st.session_state.pred_history), key=st.session_state.pred_history.count)

    color    = CLASS_COLOR.get(final_label, "#999999")
    gradient = CLASS_GRADIENT.get(final_label, CLASS_GRADIENT["Unknown"])

    # delta probs
    prev_probs  = np.asarray(st.session_state.prev_probs, dtype=np.float32)
    delta_probs = probs - (prev_probs if prev_probs.shape == probs.shape else np.zeros_like(probs))

    st.session_state.render_count += 1
    rc = st.session_state.render_count

    # ── RENDER ────────────────────────────────────────────────────────────
    with placeholder.container():
        st.markdown(activity_html(final_label, gradient), unsafe_allow_html=True)
        st.markdown(confidence_html(confidence, color),   unsafe_allow_html=True)
        st.markdown("")

        # Sensor streams
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Sensor Streams</h3>', unsafe_allow_html=True)

        sig_colors = ["#FF6B6B", "#0066FF", "#FFB800", "#FF006B", "#6B5BFF", "#00C9A7"]
        sig_labels = ["Accel X", "Accel Y", "Accel Z", "Gyro X", "Gyro Y", "Gyro Z"]

        fig = go.Figure()
        for i, name in enumerate(sig_labels):
            fig.add_trace(go.Scatter(
                y=X_raw[:, i],
                name=name,
                mode="lines",
                line=dict(width=2.5, color=sig_colors[i])
            ))

        fig.update_layout(
            height=340, margin=dict(t=6, b=8, l=10, r=10),
            plot_bgcolor="#0b1220", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                        bgcolor="rgba(12,18,32,0.92)", bordercolor="#2b4062", borderwidth=1),
            xaxis=dict(showgrid=True, gridcolor="rgba(165,179,202,0.2)", zeroline=False, color="#a5b3ca"),
            yaxis=dict(showgrid=True, gridcolor="rgba(165,179,202,0.2)", zeroline=False, color="#a5b3ca"),
            hovermode="x unified", font=dict(color="#e4edff", size=11, family="Plus Jakarta Sans"),
        )

        st.plotly_chart(fig, use_container_width=True, key=f"sig_{rc}")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

        # Activity Probabilities
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">Activity Probabilities</h3>', unsafe_allow_html=True)

        sorted_idx = np.argsort(probs)[::-1]
        li = int(sorted_idx[0])
        ln = CLASS_NAMES[li]
        lp = min(float(probs[li]), CONFIDENCE_DISPLAY_MAX)
        ld = float(delta_probs[li] * 100.0)
        ls = "+" if ld >= 0 else ""
        lc = "delta-up" if ld >= 0 else "delta-down"
        lcolor = CLASS_COLOR.get(ln, "#999999")

        st.markdown(f"""
        <div class="prob-top" style="border-color:{lcolor};">
            <div class="name">Top: {ln}</div>
            <div class="score">{lp:.0%}
                <span class="{lc}" style="font-size:0.78rem;">({ls}{ld:.1f}%)</span>
            </div>
        </div>
        <div class="prob-list">""", unsafe_allow_html=True)

        for idx in sorted_idx[1:]:
            idx  = int(idx)
            cn   = CLASS_NAMES[idx]
            cc   = CLASS_COLOR.get(cn, "#999999")
            cp   = float(probs[idx])
            cd   = float(delta_probs[idx] * 100.0)
            cs   = "+" if cd >= 0 else ""
            ccls = "delta-up" if cd >= 0 else "delta-down"
            cw   = max(0.0, min(100.0, cp * 100.0))
            st.markdown(f"""
            <div class="prob-row">
                <div class="name">{cn}</div>
                <div class="prob-track"><div class="prob-fill" style="width:{cw:.2f}%;background:{cc};"></div></div>
                <div class="prob-meta">{cp:.0%} <span class="{ccls}">{cs}{cd:.1f}%</span></div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    st.session_state.prev_probs = probs.tolist()

    time.sleep(0.02)
