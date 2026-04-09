import streamlit as st
import numpy as np
import tensorflow as tf
import requests
import time
import plotly.graph_objects as go

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Live HAR Demo", layout="wide")

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
    "Walking": "#7F77DD",
    "Walking Up": "#1D9E75",
    "Walking Down": "#D85A30",
    "Sitting": "#378ADD",
    "Standing": "#BA7517",
    "Laying": "#D4537E",
    "Unknown": "#888780"
}

# 🔥 Strong correction
CORRECTION_MAP = {1: 0, 2: 0, 5: 3}

CONFIDENCE_THRESHOLD = 0.55
SMOOTHING_WINDOW = 15
BUFFER_SIZE = 128

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
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Calibration state
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
    acc = X[:, :3]
    gyr = X[:, 3:6]

    acc_mag = np.linalg.norm(acc, axis=1)
    gyr_mag = np.linalg.norm(gyr, axis=1)

    thresh = st.session_state.calib_data

    return np.std(acc_mag) < thresh["acc_std"] and np.std(gyr_mag) < thresh["gyr_std"]


def motion_intensity(X):
    acc = X[:, :3]
    return np.mean(np.linalg.norm(acc, axis=1))


def apply_correction(probs, threshold):
    raw_idx = int(np.argmax(probs))
    confidence = float(probs[raw_idx])

    if confidence < threshold:
        return "Unknown", confidence, False

    corrected_idx = CORRECTION_MAP.get(raw_idx, raw_idx)
    return CLASS_NAMES[corrected_idx], confidence, corrected_idx != raw_idx


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    ip = st.text_input("Phyphox IP", "192.168.137.167")
    url = f"http://{ip}:8080/get?accX&accY&accZ&gyrX&gyrY&gyrZ"

    confidence_threshold = st.slider("Confidence threshold", 0.30, 0.90, CONFIDENCE_THRESHOLD, 0.05)
    show_correction_badge = st.toggle("Show correction badge", value=True)

    # Calibration
    if st.button("🎯 Calibrate (Sit Still)"):
        st.session_state.calibrating = True
        st.session_state.calib_buffer = []

    if st.session_state.calibrated:
        st.success("Calibrated")
    else:
        st.warning("Not calibrated")

    st.markdown("---")
    col1, col2 = st.columns(2)

    if col1.button("▶ Start", use_container_width=True):
        st.session_state.running = True
        st.session_state.buffer = []
        st.session_state.pred_history = []
        st.session_state.error_count = 0
        st.session_state.render_count = 0

    if col2.button("⏹ Stop", use_container_width=True):
        st.session_state.running = False
        st.session_state.buffer = []
        st.session_state.pred_history = []

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# 📡 Live Activity Recognition")
st.markdown("---")

placeholder = st.empty()

if not st.session_state.running:
    with placeholder.container():
        st.info("Press ▶ Start and begin Phyphox stream")
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
        time.sleep(0.1)
        continue

    st.session_state.buffer.append([acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z])
    if len(st.session_state.buffer) > BUFFER_SIZE:
        st.session_state.buffer.pop(0)

    # ── CALIBRATION ─────────────────────────────────────────────────────
    if st.session_state.calibrating:
        st.session_state.calib_buffer.append([acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z])

        with placeholder.container():
            st.warning(f"Calibrating... {len(st.session_state.calib_buffer)}/100")

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

    if len(st.session_state.buffer) < BUFFER_SIZE:
        time.sleep(0.02)
        continue

    X_raw = np.array(st.session_state.buffer)
    X_pad = np.pad(X_raw, ((0, 0), (0, 3)))

    intensity = motion_intensity(X_raw)

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
    confidence = min(confidence, 0.92)

    # smoothing
    st.session_state.pred_history.append(label)
    if len(st.session_state.pred_history) > SMOOTHING_WINDOW:
        st.session_state.pred_history.pop(0)

    final_label = max(set(st.session_state.pred_history), key=st.session_state.pred_history.count)

    emoji = CLASS_EMOJI.get(final_label, "")
    color = CLASS_COLOR.get(final_label, "#888780")

    st.session_state.render_count += 1
    rc = st.session_state.render_count

    with placeholder.container():
        st.markdown(f"## {emoji} {final_label}")
        st.metric("Confidence", f"{confidence:.0%}")

        # 🔥 SENSOR GRAPH (full width)
        sig_colors = ["#E24B4A", "#1D9E75", "#378ADD", "#BA7517", "#D4537E", "#7F77DD"]
        sig_labels = ["accX", "accY", "accZ", "gyrX", "gyrY", "gyrZ"]

        fig = go.Figure()

        for i, name in enumerate(sig_labels):
            fig.add_trace(go.Scatter(
                y=X_raw[:, i],
                name=name,
                mode="lines",
                line=dict(width=1.5, color=sig_colors[i])
            ))

        fig.update_layout(
            height=350,
            margin=dict(t=20, b=10, l=10, r=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.2),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)")
        )

        st.plotly_chart(fig, use_container_width=True, key=f"sig_{rc}")

    time.sleep(0.02)