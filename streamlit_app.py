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
/* ── 전체 배경 ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #06061a 0%, #0d0d2b 50%, #06061a 100%);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="block-container"] { padding-top: 2rem; max-width: 1300px; }

/* ── 타이틀 ── */
.main-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #ffd700, #fff5cc, #ffd700);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 4px;
    margin-bottom: 4px;
}
.main-subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 1rem;
    letter-spacing: 2px;
    margin-bottom: 0;
}

/* ── 구분선 ── */
.fancy-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #ffd70055, transparent);
    margin: 24px 0;
}

/* ── 통계 카드 ── */
.stat-card {
    background: linear-gradient(135deg, #12122e, #1a1a3e);
    border: 1px solid #2a2a5a;
    border-radius: 16px;
    padding: 20px 10px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #ffd700, transparent);
}
.stat-card .s-label { color: #8892a4; font-size: 0.9rem; letter-spacing: 1px; }
.stat-card .s-value { color: #f1f5f9; font-size: 2.2rem; font-weight: 900; margin-top: 4px; }

/* ── 버튼 ── */
.stButton > button {
    background: linear-gradient(135deg, #1e1e4a, #2a2a6a) !important;
    color: #e5e7eb !important;
    border: 1px solid #4a4a8a !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover:not([disabled]) {
    background: linear-gradient(135deg, #2a2a6a, #3a3a9a) !important;
    border-color: #ffd700 !important;
    box-shadow: 0 0 18px rgba(255,215,0,0.2) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[disabled] {
    opacity: 0.35 !important;
    cursor: not-allowed !important;
}

/* ── 1등 당첨 박스 - 강조 (최근) ── */
.winner-highlight {
    background: linear-gradient(135deg, #0d0d22, #181830);
    border: 2px solid #ffd700;
    border-radius: 20px;
    padding: 36px 24px;
    text-align: center;
    margin: 12px 0;
    box-shadow: 0 0 40px rgba(255,215,0,0.15), inset 0 0 40px rgba(255,215,0,0.03);
    position: relative;
    overflow: hidden;
}
.winner-highlight::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at center, rgba(255,215,0,0.04) 0%, transparent 60%);
    pointer-events: none;
}
/* ── 1등 당첨 박스 - 이전 ── */
.winner-prev {
    background: linear-gradient(135deg, #0d0d1e, #121228);
    border: 1px solid #2a2a4a;
    border-radius: 16px;
    padding: 22px 20px;
    text-align: center;
    margin: 10px 0;
}

/* ── 애니메이션 박스 ── */
.winner-anim {
    background: linear-gradient(135deg, #0d0d22, #181830);
    border: 2px solid #ffd700;
    border-radius: 20px;
    padding: 36px 24px;
    text-align: center;
    margin: 12px 0;
    box-shadow: 0 0 40px rgba(255,215,0,0.2);
}

/* ── 번호 텍스트 ── */
.num-xl {
    font-size: 4rem;
    font-weight: 900;
    color: #ffd700;
    font-family: 'Courier New', monospace;
    letter-spacing: 8px;
    text-shadow: 0 0 40px rgba(255,215,0,0.8);
    line-height: 1.1;
}
.num-lg {
    font-size: 2.4rem;
    font-weight: 800;
    color: #8892a4;
    font-family: 'Courier New', monospace;
    letter-spacing: 5px;
    line-height: 1.2;
}
.name-xl { font-size: 1.3rem; color: #6ee7b7; margin-top: 14px; font-weight: 600; letter-spacing: 2px; }
.name-lg { font-size: 1rem; color: #4b5563; margin-top: 8px; letter-spacing: 1px; }
.round-xl { color: #aab0bd; font-size: 1rem; margin-bottom: 12px; letter-spacing: 3px; font-weight: 500; }
.round-lg { color: #4b5563; font-size: 0.85rem; margin-bottom: 8px; letter-spacing: 2px; }

/* ── 2등 그리드 ── */
.second-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-top: 8px;
}
.phone-chip {
    background: linear-gradient(135deg, #12122e, #1a1a40);
    border: 1px solid #2e2e5e;
    border-radius: 12px;
    padding: 16px 8px;
    text-align: center;
    font-size: 1.4rem;
    font-family: 'Courier New', monospace;
    color: #c8d0e0;
    font-weight: 700;
    letter-spacing: 3px;
    transition: all 0.2s;
}
.phone-chip:hover {
    border-color: #5a5a9a;
    background: linear-gradient(135deg, #1a1a3e, #22224e);
}

/* ── 다운로드 버튼 ── */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #1a3a1a, #1e4a1e) !important;
    color: #6ee7b7 !important;
    border: 1px solid #2a6a2a !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg, #1e4a1e, #266026) !important;
    box-shadow: 0 0 18px rgba(110,231,183,0.2) !important;
}

/* ── 업로드 영역 ── */
[data-testid="stFileUploader"] {
    background: #12122e !important;
    border: 1px dashed #3a3a6a !important;
    border-radius: 12px !important;
}

/* ── 성공 메시지 ── */
[data-testid="stAlert"] {
    background: #0d2010 !important;
    border: 1px solid #1a4a20 !important;
    border-radius: 10px !important;
}

/* ── 섹션 제목 ── */
.section-title {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: 3px;
    margin: 0 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #1e1e40;
}
.section-title-gold { color: #ffd700; }
.section-title-silver { color: #a8b5c8; }
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

def format_phone_full(phone: str) -> str:
    d = parse_phone(phone)
    if len(d) == 11:
        return f"{d[:3]}-{d[3:7]}-{d[7:]}"
    if len(d) == 10:
        return f"{d[:3]}-{d[3:6]}-{d[6:]}"
    return phone

def random_phone8() -> str:
    r = lambda: random.randint(0, 9)
    return f"{r()}***-{r()}*{r()}{r()}"

def build_second_grid(winners: list) -> str:
    """2등 그리드 HTML (CSS grid 5열)"""
    chips = ""
    for w in winners:
        chips += f"<div class='phone-chip'>{format_phone4(w['phone'])}</div>"
    return f"<div class='second-grid'>{chips}</div>"


# ─── 세션 초기화 ─────────────────────────────────────────────────
defaults = {
    'participants': [],
    'first_winners': [],
    'second_winners': [],
    'loaded': False,
    'latest_round': None,
    'file_key': '',
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── 제목 ────────────────────────────────────────────────────────
st.markdown("<div class='main-title'>🎁 경품 추첨</div>", unsafe_allow_html=True)
st.markdown("<div class='main-subtitle'>P R I Z E &nbsp; D R A W</div>", unsafe_allow_html=True)
st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)


# ─── CSV 업로드 ──────────────────────────────────────────────────
left_col, right_col = st.columns([2, 1])
with left_col:
    st.markdown("#### 📋 참가자 CSV 업로드")
    st.caption("필수 열: **성명** (또는 이름/name)&nbsp;&nbsp;|&nbsp;&nbsp;**전화번호** (또는 연락처/핸드폰/phone)")
    uploaded = st.file_uploader("CSV 파일 선택", type=["csv"], label_visibility="collapsed")

with right_col:
    if st.session_state.loaded:
        p_count = len(st.session_state.participants)
        st.markdown(
            f"<div style='background:linear-gradient(135deg,#0d2010,#122018);"
            f"border:1px solid #1a5020;border-radius:14px;padding:20px;text-align:center;"
            f"margin-top:28px;'>"
            f"<div style='color:#6ee7b7;font-size:0.85rem;letter-spacing:2px;'>참가자 로드 완료</div>"
            f"<div style='color:#f1f5f9;font-size:2.8rem;font-weight:900;'>{p_count}</div>"
            f"<div style='color:#4b5563;font-size:0.85rem;'>명</div>"
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

    excluded  = {w["phone"] for w in fw + sw}
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
        pool = [x for x in p if x["phone"] not in {w["phone"] for w in fw + sw}]
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

    # ══════════════════════════════════════════════════════════════
    # 2등 추첨 - 한 줄씩 천천히 출력
    # ══════════════════════════════════════════════════════════════
    if btn_2nd and len(fw) >= 2 and len(sw) == 0:
        pool = [x for x in p if x["phone"] not in {w["phone"] for w in fw}]
        random.shuffle(pool)
        winners_50 = pool[:min(50, len(pool))]

        st.markdown(
            f"<div class='section-title section-title-silver'>"
            f"🥈 &nbsp; 2등 당첨자 &nbsp; {len(winners_50)}명 &nbsp;— 전화번호 뒷 4자리"
            f"</div>",
            unsafe_allow_html=True,
        )

        grid_placeholder = st.empty()
        COLS = 5
        revealed = []

        for i in range(0, len(winners_50), COLS):
            row = winners_50[i: i + COLS]
            revealed.extend(row)
            grid_placeholder.markdown(build_second_grid(revealed), unsafe_allow_html=True)
            time.sleep(0.4)

        time.sleep(0.5)
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

    # ── 2등 결과 ─────────────────────────────────────────────────
    if sw:
        st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='section-title section-title-silver'>"
            f"🥈 &nbsp; 2등 당첨자 &nbsp; {len(sw)}명 &nbsp;— 전화번호 뒷 4자리"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(build_second_grid(sw), unsafe_allow_html=True)

    # ── 다운로드 & 초기화 ─────────────────────────────────────────
    if fw or sw:
        st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)
        total = len(fw) + len(sw)

        rows = []
        for i, w in enumerate(fw):
            rows.append({"등수": f"1등 ({i+1}번째)", "성명": w["name"], "전화번호": format_phone_full(w["phone"])})
        for i, w in enumerate(sw):
            rows.append({"등수": f"2등 ({i+1}번)", "성명": w["name"], "전화번호": format_phone_full(w["phone"])})

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
                for k in ("participants", "first_winners", "second_winners"):
                    st.session_state[k] = []
                st.session_state.latest_round = None
                st.session_state.loaded = False
                st.session_state.file_key = ''
                st.rerun()
