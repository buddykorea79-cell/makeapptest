import streamlit as st
import pandas as pd
import random
import time
import io
from datetime import datetime

st.set_page_config(
    page_title="🎁 경품 추첨",
    page_icon="🎁",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700;800;900&display=swap');

/* ── 전체 배경 (흰색) ── */
[data-testid="stAppViewContainer"] {
    background: #f5f6fa;
    min-height: 100vh;
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="block-container"] { padding-top: 2rem; max-width: 1200px; }

/* ── 타이틀 영역 ── */
.title-wrap {
    background: #ffffff;
    border-radius: 24px;
    padding: 36px 32px 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    text-align: center;
    border: 1px solid #eaecf4;
    position: relative;
    overflow: hidden;
}
.title-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, #f7c948, #ffd700, #f7c948);
    background-size: 200% auto;
    animation: shimmer-bar 3s linear infinite;
}
@keyframes shimmer-bar {
    0%   { background-position: 0% center; }
    100% { background-position: 200% center; }
}
.main-title {
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: 4px;
    margin-bottom: 6px;
}
.main-title .title-emoji {
    -webkit-text-fill-color: initial;
    background: none;
}
.main-title .title-text {
    background: linear-gradient(135deg, #b8860b 0%, #ffd700 45%, #b8860b 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
}
@keyframes shimmer {
    0%   { background-position: 0% center; }
    100% { background-position: 200% center; }
}
.main-subtitle {
    color: #b0b8cc;
    font-size: 0.75rem;
    letter-spacing: 10px;
    text-transform: uppercase;
    font-weight: 600;
}

/* ── 구분선 ── */
.fancy-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #e0e4f0, transparent);
    margin: 20px 0;
}
.draw-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,215,0,0.35), transparent);
    margin: 20px 0;
}

/* ── 흰 카드 래퍼 ── */
.white-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 24px 28px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    border: 1px solid #eaecf4;
    margin-bottom: 16px;
}

/* ── 통계 카드 (밝은 버전) ── */
.stat-card {
    background: #ffffff;
    border: 1px solid #eaecf4;
    border-radius: 18px;
    padding: 22px 10px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #ffd700, #f7c948);
    border-radius: 18px 18px 0 0;
}
.stat-card .s-label {
    color: #a0a8c0;
    font-size: 0.72rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
}
.stat-card .s-value {
    color: #1a2040;
    font-size: 2.2rem;
    font-weight: 900;
    margin-top: 6px;
    line-height: 1;
}

/* ── 메인 버튼 ── */
.stButton > button {
    background: #ffffff !important;
    color: #2a3060 !important;
    border: 1.5px solid #d8dcee !important;
    border-radius: 14px !important;
    padding: 14px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    transition: all 0.22s ease !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
.stButton > button:hover:not([disabled]) {
    background: linear-gradient(135deg, #fffbea, #fff8d0) !important;
    border-color: #ffd700 !important;
    box-shadow: 0 4px 20px rgba(255,215,0,0.2), 0 2px 8px rgba(0,0,0,0.06) !important;
    transform: translateY(-2px) !important;
    color: #8b6c00 !important;
}
.stButton > button[disabled] {
    opacity: 0.35 !important;
    cursor: not-allowed !important;
}

/* ── 1등 당첨 박스 - 강조 (최근) ── */
.winner-highlight {
    background: linear-gradient(145deg, #07071a, #0f0f28);
    border: 2px solid rgba(255,215,0,0.55);
    border-radius: 28px;
    padding: 80px 40px 70px;
    text-align: center;
    margin: 10px 0 6px;
    min-height: 440px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 0 80px rgba(255,215,0,0.10),
        0 24px 60px rgba(0,0,0,0.25),
        inset 0 1px 0 rgba(255,215,0,0.15);
    position: relative;
    overflow: hidden;
}
.winner-highlight::before {
    content: '';
    position: absolute;
    top: -60%; left: -60%;
    width: 220%; height: 220%;
    background: radial-gradient(ellipse at center, rgba(255,215,0,0.045) 0%, transparent 65%);
    pointer-events: none;
}
.winner-highlight::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,215,0,0.6), transparent);
}

/* ── 1등 당첨 박스 - 이전 ── */
.winner-prev {
    background: linear-gradient(145deg, #060614, #0a0a20);
    border: 1px solid rgba(40,40,80,0.9);
    border-radius: 24px;
    padding: 50px 24px 40px;
    text-align: center;
    margin: 10px 0 6px;
    min-height: 340px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.15);
}

/* ── 애니메이션 박스 ── */
.winner-anim {
    background: linear-gradient(145deg, #07071a, #10102c);
    border: 2px solid rgba(255,215,0,0.6);
    border-radius: 28px;
    padding: 80px 40px;
    text-align: center;
    margin: 12px 0;
    min-height: 440px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 100px rgba(255,215,0,0.13), 0 24px 60px rgba(0,0,0,0.25);
}

/* ── 번호 텍스트 ── */
.num-xl {
    font-size: 7rem;
    font-weight: 900;
    background: linear-gradient(180deg, #fff8e0 0%, #ffd700 50%, #a07010 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: 'Courier New', monospace;
    letter-spacing: 12px;
    filter: drop-shadow(0 0 40px rgba(255,215,0,0.55));
    line-height: 1.1;
}
.num-lg {
    font-size: 3.5rem;
    font-weight: 800;
    color: #404870;
    font-family: 'Courier New', monospace;
    letter-spacing: 8px;
    line-height: 1.2;
}
.name-xl { font-size: 2.2rem; color: #4dd4bc; margin-top: 30px; font-weight: 700; letter-spacing: 6px; }
.name-lg { font-size: 1.5rem; color: #303858; margin-top: 16px; letter-spacing: 3px; }
.round-xl { color: #5a6490; font-size: 1.2rem; margin-bottom: 28px; letter-spacing: 8px; font-weight: 700; text-transform: uppercase; }
.round-lg { color: #303858; font-size: 1rem; margin-bottom: 18px; letter-spacing: 4px; }

/* ── 2등 그리드 ── */
.second-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
    margin-top: 6px;
}
.phone-chip {
    background: linear-gradient(145deg, #08082a, #0e0e38);
    border: 1px solid rgba(40,40,90,0.9);
    border-radius: 10px;
    padding: 12px 8px;
    text-align: center;
    font-family: 'Courier New', monospace;
    font-weight: 700;
    font-size: 1.45rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    transition: all 0.2s;
    white-space: nowrap;
}
.phone-chip:hover {
    border-color: rgba(255,215,0,0.3);
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(255,215,0,0.08);
}
.chip-name { color: #4dd4bc; }
.chip-phone { color: #6070a0; letter-spacing: 3px; }
.phone-chip:hover .chip-name { color: #6ee8d0; }
.phone-chip:hover .chip-phone { color: #8090c0; }

/* ── 다운로드 버튼 ── */
[data-testid="stDownloadButton"] > button {
    background: #ffffff !important;
    color: #1a8a50 !important;
    border: 1.5px solid #b8e8cc !important;
    border-radius: 14px !important;
    padding: 14px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    transition: all 0.22s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #f0faf5 !important;
    border-color: #4caf80 !important;
    box-shadow: 0 4px 18px rgba(76,175,80,0.15) !important;
    transform: translateY(-2px) !important;
}

/* ── 업로드 영역 ── */
[data-testid="stFileUploader"] {
    background: #fafbff !important;
    border: 1.5px dashed #d0d4e8 !important;
    border-radius: 14px !important;
}

/* ── 섹션 제목 ── */
.section-title {
    font-size: 1rem;
    font-weight: 800;
    letter-spacing: 3px;
    margin: 0 0 12px 0;
    padding-bottom: 10px;
    border-bottom: 1.5px solid #eaecf4;
    text-transform: uppercase;
}
.section-title-gold {
    background: linear-gradient(90deg, #b8860b, #ffd700, #b8860b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.section-title-silver { color: #8090b0; }

/* ── 업로드 카드 영역 ── */
.upload-card-label {
    color: #2a3060;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.upload-card-hint {
    color: #9098b8;
    font-size: 0.8rem;
    margin-bottom: 10px;
}

/* ── 참가자 로드 카드 ── */
.loaded-card {
    background: linear-gradient(145deg, #f0fff6, #e8f9f0);
    border: 1.5px solid #b8e8cc;
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    margin-top: 4px;
    box-shadow: 0 2px 12px rgba(76,175,80,0.08);
}

/* ── 재추첨 버튼 래퍼 ── */
.redraw-wrap .stButton > button {
    background: #fff8f8 !important;
    color: #c05050 !important;
    border: 1.5px solid #f0c8c8 !important;
    font-size: 0.82rem !important;
    padding: 8px !important;
    letter-spacing: 1px !important;
    margin-top: 6px !important;
    box-shadow: none !important;
}
.redraw-wrap .stButton > button:hover:not([disabled]) {
    background: #fff0f0 !important;
    border-color: #e08080 !important;
    box-shadow: 0 2px 12px rgba(200,80,80,0.1) !important;
    color: #a03030 !important;
}

/* ── 추첨 영역 구분 래퍼 ── */
.draw-section {
    background: linear-gradient(160deg, #07071a 0%, #0c0c24 100%);
    border-radius: 24px;
    padding: 28px 24px 24px;
    margin: 16px 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.03);
    border: 1px solid rgba(255,215,0,0.08);
}
</style>
""", unsafe_allow_html=True)


# ─── 유틸 함수 ───────────────────────────────────────────────────
def parse_phone(phone: str) -> str:
    return ''.join(c for c in str(phone) if c.isdigit())

def format_phone8(phone: str) -> str:
    d = parse_phone(phone)
    last8 = d[-8:] if len(d) >= 8 else d
    if len(last8) < 8:
        return phone
    return f"{last8[0]}***-{last8[4]}*{last8[6]}{last8[7]}"

def format_phone4(phone: str) -> str:
    return parse_phone(phone)[-4:]

def format_name_last(name: str) -> str:
    return f"**{name[-1]}" if name else ""

def format_phone_full(phone: str) -> str:
    d = parse_phone(phone)
    if len(d) == 10 and d[0] != '0':
        d = '0' + d
    if len(d) == 11:
        return f"{d[:3]}-{d[3:7]}-{d[7:]}"
    if len(d) == 10:
        return f"{d[:3]}-{d[3:6]}-{d[6:]}"
    return phone

def random_phone8() -> str:
    r = lambda: random.randint(0, 9)
    return f"{r()}***-{r()}*{r()}{r()}"

def build_second_grid(winners: list) -> str:
    chips = ""
    for w in winners:
        chips += (
            f"<div class='phone-chip'>"
            f"<span class='chip-name'>{format_name_last(w['name'])}</span>"
            f"&nbsp;"
            f"<span class='chip-phone'>{format_phone4(w['phone'])}</span>"
            f"</div>"
        )
    return f"<div class='second-grid'>{chips}</div>"


# ─── 세션 초기화 ─────────────────────────────────────────────────
defaults = {
    'participants': [],
    'first_winners': [],
    'second_winners': [],
    'excluded_phones': [],
    'loaded': False,
    'latest_round': None,
    'file_key': '',
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── 제목 ────────────────────────────────────────────────────────
st.markdown(
    "<div class='title-wrap'>"
    "<div class='main-title'><span class='title-emoji'>🎁</span> <span class='title-text'>경품 추첨</span></div>"
    "<div class='main-subtitle'>P R I Z E &nbsp;&nbsp; D R A W</div>"
    "</div>",
    unsafe_allow_html=True,
)


# ─── CSV 업로드 ──────────────────────────────────────────────────
left_col, right_col = st.columns([2, 1])
with left_col:
    st.markdown(
        "<div class='white-card'>"
        "<div class='upload-card-label'>📋 참가자 CSV 업로드</div>"
        "<div class='upload-card-hint'>필수 열: <b>성명</b> (또는 이름/name) &nbsp;|&nbsp; <b>전화번호</b> (또는 연락처/핸드폰/phone)</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader("CSV 파일 선택", type=["csv"], label_visibility="collapsed")

with right_col:
    if st.session_state.loaded:
        p_count = len(st.session_state.participants)
        st.markdown(
            f"<div class='loaded-card'>"
            f"<div style='color:#1a8a50;font-size:0.72rem;letter-spacing:3px;font-weight:700;text-transform:uppercase;'>참가자 로드 완료</div>"
            f"<div style='color:#1a2040;font-size:2.8rem;font-weight:900;margin:8px 0 4px;'>{p_count}</div>"
            f"<div style='color:#70a888;font-size:0.78rem;letter-spacing:2px;font-weight:600;'>명</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

if uploaded is not None:
    file_key = f"{uploaded.name}_{uploaded.size}"
    if file_key != st.session_state.file_key:
        try:
            raw = uploaded.read()
            df = None
            for enc in ["utf-8-sig", "utf-8", "cp949", "euc-kr"]:
                try:
                    df = pd.read_csv(io.BytesIO(raw), encoding=enc)
                    break
                except Exception:
                    continue
            if df is None:
                st.error("파일 인코딩을 읽을 수 없습니다.")
            else:
                name_col = next(
                    (c for c in df.columns if any(k in c for k in ["성명", "이름", "name", "Name"])), None
                )
                phone_col = next(
                    (c for c in df.columns if any(k in c for k in ["전화", "연락", "핸드폰", "phone", "Phone"])), None
                )
                if name_col is None or phone_col is None:
                    st.error(f"열을 찾을 수 없습니다. 헤더: {list(df.columns)}")
                else:
                    data = []
                    for _, row in df.iterrows():
                        name = str(row[name_col]).strip()
                        phone = parse_phone(str(row[phone_col]))
                        if name and name != "nan" and len(phone) >= 8:
                            data.append({"name": name, "phone": phone})
                    if data:
                        st.session_state.participants = data
                        st.session_state.first_winners = []
                        st.session_state.second_winners = []
                        st.session_state.excluded_phones = []
                        st.session_state.latest_round = None
                        st.session_state.loaded = True
                        st.session_state.file_key = file_key
                        st.rerun()
                    else:
                        st.error("유효한 참가자 데이터가 없습니다.")
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")


# ─── 추첨 메인 영역 ──────────────────────────────────────────────
if st.session_state.loaded and st.session_state.participants:
    p  = st.session_state.participants
    fw = st.session_state.first_winners
    sw = st.session_state.second_winners
    ex = set(st.session_state.excluded_phones)

    excluded  = {w["phone"] for w in fw + sw} | ex
    remaining = [x for x in p if x["phone"] not in excluded]

    st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)

    # ── 통계 카드 ────────────────────────────────────────────────
    s1, s2, s3, s4 = st.columns(4)
    for col, label, val in [
        (s1, "전 체", len(p)),
        (s2, "1등 당첨", len(fw)),
        (s3, "2등 당첨", len(sw)),
        (s4, "잔 여", len(remaining)),
    ]:
        col.markdown(
            f"<div class='stat-card'>"
            f"<div class='s-label'>{label}</div>"
            f"<div class='s-value'>{val}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)

    # ── 추첨 버튼 ────────────────────────────────────────────────
    bc1, bc2 = st.columns(2)
    with bc1:
        btn_1st = st.button(
            "🥇 1등 추첨",
            disabled=(len(fw) >= 2),
            use_container_width=True,
        )
    with bc2:
        btn_2nd = st.button(
            "🥈 2등 추첨 (50명)",
            disabled=(len(fw) < 2 or len(sw) > 0),
            use_container_width=True,
        )

    # ══════════════════════════════════════════════════════════════
    # 1등 추첨 애니메이션
    # ══════════════════════════════════════════════════════════════
    if btn_1st and len(fw) < 2:
        pool = [x for x in p if x["phone"] not in ({w["phone"] for w in fw + sw} | ex)]
        if pool:
            winner = random.choice(pool)
            round_no = len(fw) + 1

            anim = st.empty()
            delays = [0.04] * 25 + [0.07] * 20 + [0.15] * 15
            for delay in delays:
                anim.markdown(
                    f"<div class='winner-anim'>"
                    f"<div class='round-xl'>🥇 &nbsp; {round_no}번째 추첨 중...</div>"
                    f"<div class='num-xl'>{random_phone8()}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                time.sleep(delay)

            anim.markdown(
                f"<div class='winner-anim'>"
                f"<div class='round-xl'>🥇 &nbsp; {round_no}번째 당첨번호</div>"
                f"<div class='num-xl'>{format_phone8(winner['phone'])}</div>"
                f"<div class='name-xl'>🎉 &nbsp; {winner['name']} 님 당첨! &nbsp; 🎉</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            time.sleep(2.0)

            st.session_state.first_winners.append(winner)
            st.session_state.latest_round = len(st.session_state.first_winners)
            st.rerun()
        else:
            if len(fw) == 0:
                for k in ("participants", "first_winners", "second_winners", "excluded_phones"):
                    st.session_state[k] = []
                st.session_state.latest_round = None
                st.session_state.loaded = False
                st.session_state.file_key = ''
                st.warning("추첨 가능한 참가자가 없습니다. 처음부터 다시 시작합니다.")
                st.rerun()
            else:
                st.warning("추첨 가능한 참가자가 없습니다. 1번째 당첨자는 그대로 유지됩니다.")

    # ══════════════════════════════════════════════════════════════
    # 2등 추첨 - 한 명씩 천천히 출력
    # ══════════════════════════════════════════════════════════════
    if btn_2nd and len(fw) >= 2 and len(sw) == 0:
        pool = [x for x in p if x["phone"] not in ({w["phone"] for w in fw} | ex)]
        random.shuffle(pool)
        winners_50 = pool[:min(50, len(pool))]

        st.markdown(
            f"<div class='draw-section'>"
            f"<div class='section-title section-title-silver'>🥈 &nbsp; 2등 당첨자 {len(winners_50)}명 — 이름 끝자리 / 뒷 4자리</div>",
            unsafe_allow_html=True,
        )

        grid_placeholder = st.empty()
        revealed = []

        for w in winners_50:
            revealed.append(w)
            grid_placeholder.markdown(build_second_grid(revealed), unsafe_allow_html=True)
            time.sleep(0.5)

        st.markdown("</div>", unsafe_allow_html=True)

        time.sleep(0.8)
        st.session_state.second_winners = winners_50
        st.session_state.latest_round = None
        st.rerun()

    # ══════════════════════════════════════════════════════════════
    # 누적 결과 표시 (rerun 이후 영구 렌더링)
    # ══════════════════════════════════════════════════════════════

    # ── 1등 결과 ─────────────────────────────────────────────────
    if fw:
        st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-title section-title-gold'>🥇 &nbsp; 1등 당첨자</div>",
            unsafe_allow_html=True,
        )
        latest = st.session_state.latest_round

        cols_1st = st.columns(len(fw)) if len(fw) > 1 else [st.container()]
        for i, (col, w) in enumerate(zip(cols_1st, fw)):
            round_no = i + 1
            with col:
                if latest == round_no:
                    st.markdown(
                        f"<div class='winner-highlight'>"
                        f"<div class='round-xl'>🥇 &nbsp; {round_no}번째 당첨번호</div>"
                        f"<div class='num-xl'>{format_phone8(w['phone'])}</div>"
                        f"<div class='name-xl'>🎉 &nbsp; {w['name']} 님 &nbsp; 🎉</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<div class='winner-prev'>"
                        f"<div class='round-lg'>🥇 &nbsp; {round_no}번째 당첨번호</div>"
                        f"<div class='num-lg'>{format_phone8(w['phone'])}</div>"
                        f"<div class='name-lg'>( &nbsp; {w['name']} 님 &nbsp; )</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                if not sw:
                    st.markdown("<div class='redraw-wrap'>", unsafe_allow_html=True)
                    if st.button(
                        f"🔄 부재자 재추첨",
                        key=f"redraw_{i}_{w['phone']}",
                        use_container_width=True,
                    ):
                        st.session_state.excluded_phones.append(w["phone"])
                        st.session_state.first_winners.pop(i)
                        st.session_state.latest_round = None
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # ── 2등 결과 ─────────────────────────────────────────────────
    if sw:
        st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='draw-section'>"
            f"<div class='section-title section-title-silver'>🥈 &nbsp; 2등 당첨자 {len(sw)}명 — 이름 끝자리 / 뒷 4자리</div>",
            unsafe_allow_html=True,
        )
        st.markdown(build_second_grid(sw), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 다운로드 & 초기화 ─────────────────────────────────────────
    if fw or sw:
        st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
        total = len(fw) + len(sw)

        rows = []
        for i, w in enumerate(fw):
            rows.append({"등수": f"1등 ({i+1}번째)", "성명": w["name"], "전화번호": f"'{format_phone_full(w['phone'])}"})
        for i, w in enumerate(sw):
            rows.append({"등수": f"2등 ({i+1}번)", "성명": w["name"], "전화번호": f"'{format_phone_full(w['phone'])}"})

        csv_bytes = (
            pd.DataFrame(rows)
            .to_csv(index=False, encoding="utf-8-sig")
            .encode("utf-8-sig")
        )
        today = datetime.now().strftime("%Y%m%d")

        dl_col, reset_col = st.columns(2)
        with dl_col:
            st.download_button(
                label=f"⬇️  당첨자 {total}명 전체 CSV 다운로드",
                data=csv_bytes,
                file_name=f"경품당첨자_{today}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with reset_col:
            if st.button("🔄  전체 초기화", use_container_width=True):
                for k in ("participants", "first_winners", "second_winners", "excluded_phones"):
                    st.session_state[k] = []
                st.session_state.latest_round = None
                st.session_state.loaded = False
                st.session_state.file_key = ''
                st.rerun()
