import streamlit as st
import pandas as pd
import random
import time
import io
from datetime import datetime

st.set_page_config(page_title="🎁 경품 추첨", page_icon="🎁", layout="centered")

# ─── 스타일 ──────────────────────────────────────────────────────
st.markdown("""
<style>
.stat-box {
    background: #1a1a3a;
    border: 1px solid #3a3a6a;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}
.stat-box .label { color: #9ca3af; font-size: 0.85rem; }
.stat-box .value { color: #e5e7eb; font-size: 1.6rem; font-weight: 700; }

.winner-box {
    background: #0d0d22;
    border: 2px solid #ffd700;
    border-radius: 16px;
    padding: 28px 20px;
    text-align: center;
    margin: 10px 0;
}
.winner-number {
    font-size: 3.4rem;
    font-weight: 900;
    color: #ffd700;
    font-family: 'Courier New', monospace;
    letter-spacing: 5px;
    text-shadow: 0 0 30px rgba(255,215,0,0.7);
}
.winner-name {
    font-size: 1.1rem;
    color: #6ee7b7;
    margin-top: 10px;
}
.prev-winner-box {
    background: #111122;
    border: 1px solid #3a3a6a;
    border-radius: 10px;
    padding: 14px 20px;
    margin: 6px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.prev-winner-label { color: #9ca3af; font-size: 0.85rem; }
.prev-winner-number {
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffd700;
    font-family: 'Courier New', monospace;
    letter-spacing: 2px;
}
.prev-winner-name { color: #6ee7b7; font-size: 0.9rem; margin-top: 2px; }
.phone-chip {
    display: inline-block;
    background: #1a1a3a;
    border: 1px solid #3a3a6a;
    border-radius: 8px;
    padding: 8px 6px;
    text-align: center;
    font-size: 1rem;
    font-family: 'Courier New', monospace;
    color: #d1d5db;
    font-weight: 600;
    width: 100%;
    margin: 2px 0;
}
.stButton > button { font-weight: 600; }
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

# ─── 세션 초기화 ─────────────────────────────────────────────────
for key, default in [
    ('participants', []),
    ('first_winners', []),
    ('second_winners', []),
    ('loaded', False),
    ('saved_winner', None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─── 제목 ────────────────────────────────────────────────────────
st.title("🎁 경품 추첨")
st.caption("CSV 파일을 업로드하고 1등 → 2등 순서로 추첨하세요")
st.markdown("---")

# ─── CSV 업로드 ──────────────────────────────────────────────────
st.subheader("📋 참가자 CSV 업로드")
st.caption("필수 열: **성명** (또는 이름/name), **전화번호** (또는 연락처/핸드폰/phone)")

uploaded = st.file_uploader("CSV 파일 선택", type=["csv"], label_visibility="collapsed")

if uploaded:
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
                    st.session_state.saved_winner = None
                    st.session_state.loaded = True
                    st.success(f"✅ **{len(data)}명** 로드 완료")
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

    st.markdown("---")

    # ── 통계 ─────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in [
        (c1, "전체", len(p)),
        (c2, "1등 당첨", len(fw)),
        (c3, "2등 당첨", len(sw)),
        (c4, "잔여", len(remaining)),
    ]:
        col.markdown(
            f"<div class='stat-box'><div class='label'>{label}</div>"
            f"<div class='value'>{val}명</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── 버튼 ─────────────────────────────────────────────────────
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        btn_1st = st.button("🥇 1등 추첨", disabled=(len(fw) >= 2), use_container_width=True)
    with btn_col2:
        btn_2nd = st.button("🥈 2등 추첨 (50명)", disabled=(len(fw) < 2 or len(sw) > 0), use_container_width=True)

    # ── 저장된 1번째 당첨자 표시 (rerun 후에도 유지) ──────────────
    if st.session_state.saved_winner and len(fw) == 1 and not btn_1st:
        w = st.session_state.saved_winner
        st.markdown(
            f"<div class='prev-winner-box'>"
            f"<div><div class='prev-winner-label'>✅ 저장된 1번째 당첨자</div>"
            f"<div class='prev-winner-number'>{format_phone8(w['phone'])}</div>"
            f"<div class='prev-winner-name'>( {w['name']} 님 )</div></div>"
            f"<div style='color:#ffd700;font-size:1.8rem;'>🥇</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── 1등 추첨 처리 ─────────────────────────────────────────────
    if btn_1st:
        excl = {w["phone"] for w in fw + sw}
        pool = [x for x in p if x["phone"] not in excl]
        if pool:
            if st.session_state.saved_winner:
                w = st.session_state.saved_winner
                st.markdown(
                    f"<div class='prev-winner-box'>"
                    f"<div><div class='prev-winner-label'>✅ 저장된 1번째 당첨자</div>"
                    f"<div class='prev-winner-number'>{format_phone8(w['phone'])}</div>"
                    f"<div class='prev-winner-name'>( {w['name']} 님 )</div></div>"
                    f"<div style='color:#ffd700;font-size:1.8rem;'>🥇</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            winner = random.choice(pool)
            st.session_state.first_winners.append(winner)
            round_no = len(st.session_state.first_winners)

            if round_no == 1:
                st.session_state.saved_winner = winner

            st.markdown(f"### 🥇 {round_no}번째 추첨 중...")
            anim = st.empty()

            # 점진적 감속: 빠름(1.0s) → 중간(1.6s) → 느림(2.2s), 총 ~4.8초
            delays = [0.04] * 25 + [0.08] * 20 + [0.18] * 12
            for delay in delays:
                anim.markdown(
                    f"<div class='winner-box'>"
                    f"<div class='winner-number'>{random_phone8()}</div></div>",
                    unsafe_allow_html=True,
                )
                time.sleep(delay)

            anim.markdown(
                f"<div class='winner-box'>"
                f"<div style='color:#aaa;font-size:0.9rem;margin-bottom:8px;'>🥇 {round_no}번째 당첨번호</div>"
                f"<div class='winner-number'>{format_phone8(winner['phone'])}</div>"
                f"<div class='winner-name'>🎉 {winner['name']} 님 당첨! 🎉</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── 2등 추첨 처리 ─────────────────────────────────────────────
    if btn_2nd:
        excl = {w["phone"] for w in st.session_state.first_winners}
        pool = [x for x in p if x["phone"] not in excl]
        shuffled = pool.copy()
        random.shuffle(shuffled)
        st.session_state.second_winners = shuffled[: min(50, len(shuffled))]
        st.rerun()

    # ── 1등 결과 기록 표시 ────────────────────────────────────────
    if fw and not btn_1st:
        st.markdown("---")
        st.subheader("🥇 1등 당첨자")
        for i, w in enumerate(fw):
            st.markdown(
                f"<div class='winner-box'>"
                f"<div style='color:#aaa;font-size:0.9rem;margin-bottom:8px;'>{i+1}번째 당첨번호</div>"
                f"<div class='winner-number'>{format_phone8(w['phone'])}</div>"
                f"<div class='winner-name'>( {w['name']} 님 )</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ── 2등 결과 표시 ─────────────────────────────────────────────
    if sw:
        st.markdown("---")
        st.subheader(f"🥈 2등 당첨자 ({len(sw)}명) — 전화번호 뒷 4자리")
        cols_per_row = 5
        for i in range(0, len(sw), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, w in enumerate(sw[i: i + cols_per_row]):
                cols[j].markdown(
                    f"<div class='phone-chip'>{format_phone4(w['phone'])}</div>",
                    unsafe_allow_html=True,
                )

    # ── 다운로드 & 초기화 ─────────────────────────────────────────
    if fw or sw:
        st.markdown("---")
        rows = []
        for i, w in enumerate(fw):
            rows.append({"등수": f"1등 ({i+1}번째)", "성명": w["name"], "전화번호": format_phone_full(w["phone"])})
        for i, w in enumerate(sw):
            rows.append({"등수": f"2등 ({i+1}번)", "성명": w["name"], "전화번호": format_phone_full(w["phone"])})

        csv_bytes = pd.DataFrame(rows).to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        today = datetime.now().strftime("%Y%m%d")

        dl_col, reset_col = st.columns(2)
        with dl_col:
            st.download_button(
                label="⬇️ 결과 CSV 다운로드",
                data=csv_bytes,
                file_name=f"경품당첨자_{today}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with reset_col:
            if st.button("🔄 전체 초기화", use_container_width=True):
                for key in ("participants", "first_winners", "second_winners"):
                    st.session_state[key] = []
                st.session_state.saved_winner = None
                st.session_state.loaded = False
                st.rerun()
