import streamlit as st
from datetime import datetime, timedelta, date
import uuid
import holidays

st.set_page_config(layout="wide") 

kr_holidays = holidays.KR(years=range(2024, 2030))

MOCK_EXAMS = {
    "2026-03-26": "3월 모의평가",
    "2026-06-04": "6월 모의평가",
    "2026-09-02": "9월 모의평가",
    "2026-10-20": "10월 전국연합학력평가",
    "2026-11-19": "대학수학능력시험" 
}

# --- 3단계(글로벌 ↔ 학교 ↔ 개별일정) 양방향 동기화 콜백 함수 ---
def toggle_high_schools():
    val = st.session_state.show_high
    for ev in st.session_state.events:
        if ev['name'].endswith('고'):
            st.session_state[f"chk_{ev['id']}"] = val
            st.session_state[f"master_{ev['name']}"] = val

def toggle_mid_schools():
    val = st.session_state.show_mid
    for ev in st.session_state.events:
        if ev['name'].endswith('중'):
            st.session_state[f"chk_{ev['id']}"] = val
            st.session_state[f"master_{ev['name']}"] = val

def toggle_school(s_name, is_high):
    val = st.session_state[f"master_{s_name}"]
    for ev in st.session_state.events:
        if ev['name'] == s_name:
            st.session_state[f"chk_{ev['id']}"] = val
    
    all_global = True
    for ev in st.session_state.events:
        if (is_high and ev['name'].endswith('고')) or (not is_high and ev['name'].endswith('중')):
            if not st.session_state.get(f"chk_{ev['id']}", True):
                all_global = False
                break
    if is_high: st.session_state.show_high = all_global
    else: st.session_state.show_mid = all_global

def toggle_individual(s_name, is_high):
    all_school = True
    for ev in st.session_state.events:
        if ev['name'] == s_name:
            if not st.session_state.get(f"chk_{ev['id']}", True):
                all_school = False
                break
    st.session_state[f"master_{s_name}"] = all_school
    
    all_global = True
    for ev in st.session_state.events:
        if (is_high and ev['name'].endswith('고')) or (not is_high and ev['name'].endswith('중')):
            if not st.session_state.get(f"chk_{ev['id']}", True):
                all_global = False
                break
    if is_high: st.session_state.show_high = all_global
    else: st.session_state.show_mid = all_global

# --- 상태 및 기본 데이터 초기화 ---
if 'show_high' not in st.session_state: st.session_state.show_high = True
if 'show_mid' not in st.session_state: st.session_state.show_mid = True
if 'show_mocks' not in st.session_state: st.session_state.show_mocks = True

if 'cal_start_val' not in st.session_state: st.session_state.cal_start_val = date(2026, 9, 21)

if 'events' not in st.session_state:
    st.session_state.events = [
        {"id": str(uuid.uuid4()), "name": "경산고", "color": "#E2D0F9", "type": "중간고사", "start_date": date(2026, 9, 30), "end_date": date(2026, 10, 2)},
        {"id": str(uuid.uuid4()), "name": "경산고", "color": "#E2D0F9", "type": "기말고사", "start_date": date(2026, 12, 1), "end_date": date(2026, 12, 4)},
        {"id": str(uuid.uuid4()), "name": "경산여고", "color": "#FFF2CC", "type": "중간고사", "start_date": date(2026, 9, 28), "end_date": date(2026, 10, 1)},
        {"id": str(uuid.uuid4()), "name": "경산여고", "color": "#FFF2CC", "type": "기말고사", "start_date": date(2026, 12, 1), "end_date": date(2026, 12, 4)},
        {"id": str(uuid.uuid4()), "name": "문명고", "color": "#F9CB9C", "type": "중간고사", "start_date": date(2026, 10, 12), "end_date": date(2026, 10, 15)},
        {"id": str(uuid.uuid4()), "name": "문명고", "color": "#F9CB9C", "type": "기말고사", "start_date": date(2026, 12, 10), "end_date": date(2026, 12, 15)},
        {"id": str(uuid.uuid4()), "name": "사동고", "color": "#B6D7A8", "type": "중간고사", "start_date": date(2026, 10, 12), "end_date": date(2026, 10, 15)},
        {"id": str(uuid.uuid4()), "name": "사동고", "color": "#B6D7A8", "type": "기말고사", "start_date": date(2026, 12, 10), "end_date": date(2026, 12, 15)},
        {"id": str(uuid.uuid4()), "name": "선화여고", "color": "#F4CCCC", "type": "중간고사", "start_date": date(2026, 10, 19), "end_date": date(2026, 10, 23)},
        {"id": str(uuid.uuid4()), "name": "선화여고", "color": "#F4CCCC", "type": "기말고사", "start_date": date(2026, 12, 15), "end_date": date(2026, 12, 18)},
        {"id": str(uuid.uuid4()), "name": "청도고", "color": "#C9DAF8", "type": "중간고사", "start_date": date(2026, 10, 2), "end_date": date(2026, 10, 8)},
        {"id": str(uuid.uuid4()), "name": "청도고", "color": "#C9DAF8", "type": "기말고사", "start_date": date(2026, 12, 15), "end_date": date(2026, 12, 18)},
        {"id": str(uuid.uuid4()), "name": "하양여고", "color": "#D9EAD3", "type": "중간고사", "start_date": date(2026, 10, 13), "end_date": date(2026, 10, 16)},
        {"id": str(uuid.uuid4()), "name": "하양여고", "color": "#D9EAD3", "type": "기말고사", "start_date": date(2026, 12, 3), "end_date": date(2026, 12, 8)},
        # 중학교
        {"id": str(uuid.uuid4()), "name": "경산중", "color": "#B6D7A8", "type": "중간고사", "start_date": date(2026, 9, 28), "end_date": date(2026, 9, 30)},
        {"id": str(uuid.uuid4()), "name": "경산중", "color": "#B6D7A8", "type": "기말고사(중3)", "start_date": date(2026, 11, 16), "end_date": date(2026, 11, 18)},
        {"id": str(uuid.uuid4()), "name": "경산중", "color": "#B6D7A8", "type": "기말고사(중1,2)", "start_date": date(2026, 12, 14), "end_date": date(2026, 12, 16)},
        {"id": str(uuid.uuid4()), "name": "경산여중", "color": "#FFF9E6", "type": "중간고사", "start_date": date(2026, 9, 29), "end_date": date(2026, 10, 1)},
        {"id": str(uuid.uuid4()), "name": "경산여중", "color": "#FFF9E6", "type": "기말고사(중3)", "start_date": date(2026, 11, 10), "end_date": date(2026, 11, 12)},
        {"id": str(uuid.uuid4()), "name": "경산여중", "color": "#FFF9E6", "type": "기말고사(중1,2)", "start_date": date(2026, 12, 2), "end_date": date(2026, 12, 4)},
        {"id": str(uuid.uuid4()), "name": "덕원중", "color": "#EFEFEF", "type": "중간고사", "start_date": date(2026, 9, 29), "end_date": date(2026, 9, 30)},
        {"id": str(uuid.uuid4()), "name": "덕원중", "color": "#EFEFEF", "type": "기말고사(중3)", "start_date": date(2026, 11, 2), "end_date": date(2026, 11, 4)},
        {"id": str(uuid.uuid4()), "name": "덕원중", "color": "#EFEFEF", "type": "기말고사(중1,2)", "start_date": date(2026, 12, 8), "end_date": date(2026, 12, 10)},
        {"id": str(uuid.uuid4()), "name": "문명중", "color": "#FCE5CD", "type": "중간고사", "start_date": date(2026, 10, 13), "end_date": date(2026, 10, 15)},
        {"id": str(uuid.uuid4()), "name": "문명중", "color": "#FCE5CD", "type": "기말고사(중3)", "start_date": date(2026, 11, 16), "end_date": date(2026, 11, 18)},
        {"id": str(uuid.uuid4()), "name": "문명중", "color": "#FCE5CD", "type": "기말고사(중1,2)", "start_date": date(2026, 12, 11), "end_date": date(2026, 12, 15)},
        {"id": str(uuid.uuid4()), "name": "사동중", "color": "#E2D0F9", "type": "중간고사", "start_date": date(2026, 9, 30), "end_date": date(2026, 10, 2)},
        {"id": str(uuid.uuid4()), "name": "사동중", "color": "#E2D0F9", "type": "기말고사(중3)", "start_date": date(2026, 11, 16), "end_date": date(2026, 11, 18)},
        {"id": str(uuid.uuid4()), "name": "사동중", "color": "#E2D0F9", "type": "기말고사(중1,2)", "start_date": date(2026, 12, 7), "end_date": date(2026, 12, 9)},
        {"id": str(uuid.uuid4()), "name": "삼성현중", "color": "#C9DAF8", "type": "중간고사", "start_date": date(2026, 9, 29), "end_date": date(2026, 10, 1)},
        {"id": str(uuid.uuid4()), "name": "삼성현중", "color": "#C9DAF8", "type": "기말고사(중3)", "start_date": date(2026, 11, 16), "end_date": date(2026, 11, 18)},
        {"id": str(uuid.uuid4()), "name": "삼성현중", "color": "#C9DAF8", "type": "기말고사(중1,2)", "start_date": date(2026, 12, 15), "end_date": date(2026, 12, 17)},
        {"id": str(uuid.uuid4()), "name": "시지중", "color": "#F4CCCC", "type": "중간고사", "start_date": date(2026, 10, 26), "end_date": date(2026, 10, 27)},
        {"id": str(uuid.uuid4()), "name": "시지중", "color": "#F4CCCC", "type": "기말고사(중3)", "start_date": date(2026, 10, 26), "end_date": date(2026, 10, 28)},
        {"id": str(uuid.uuid4()), "name": "시지중", "color": "#F4CCCC", "type": "기말고사(중1,2)", "start_date": date(2026, 12, 15), "end_date": date(2026, 12, 17)},
        {"id": str(uuid.uuid4()), "name": "장산중", "color": "#FFF2CC", "type": "중간고사", "start_date": date(2026, 9, 29), "end_date": date(2026, 10, 1)},
        {"id": str(uuid.uuid4()), "name": "장산중", "color": "#FFF2CC", "type": "기말고사(중3)", "start_date": date(2026, 11, 10), "end_date": date(2026, 11, 12)},
        {"id": str(uuid.uuid4()), "name": "장산중", "color": "#FFF2CC", "type": "기말고사(중1,2)", "start_date": date(2026, 12, 14), "end_date": date(2026, 12, 16)}
    ]

for ev in st.session_state.events:
    if f"chk_{ev['id']}" not in st.session_state:
        st.session_state[f"chk_{ev['id']}"] = True
    if f"master_{ev['name']}" not in st.session_state:
        st.session_state[f"master_{ev['name']}"] = True

if 'selected_color' not in st.session_state:
    st.session_state.selected_color = "#FFF2CC"

def is_event_visible(ev):
    return st.session_state.get(f"chk_{ev['id']}", True)

COLORS = {
    "연노랑": "#FFF2CC", "연두": "#D9EAD3", "하늘": "#C9DAF8", 
    "분홍": "#F4CCCC", "주황": "#FCE5CD", "보라": "#E2D0F9", 
    "회색": "#EFEFEF", "살구": "#F9CB9C", "민트": "#B6D7A8", "베이지": "#FFF9E6"
}

# === 💡 [최종 완벽판] 팝오버 확인 사살 & 스크롤바 원천 차단 CSS ===
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; margin-top: 0rem !important; }
        header, [data-testid="stHeader"] { display: none !important; }
        
        @media print {
            /* 1. 기본 브라우저 여백 억제 */
            @page { margin-top: 10mm; margin-bottom: 10mm; }
            
            /* 2. 스크롤바 완전 숨김 및 창 크기 고정 */
            ::-webkit-scrollbar { display: none !important; }
            html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, .block-container {
                overflow: hidden !important;
                height: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* 3. 스트림릿 사이드바 완전 차단 */
            [data-testid="stSidebar"] { display: none !important; }
            
            /* 4. ★ 핵심: 팝오버(색상 팔레트), 구분선, 버튼 등 찌꺼기 UI들 명시적 킬(Kill)! */
            [data-testid="stPopover"], 
            [data-testid="stHorizontalBlock"],
            hr {
                display: none !important;
            }
            
            /* 5. 달력 외의 모든 컨테이너 숨김 처리 */
            .element-container { 
                display: none !important; 
            }
            
            /* 6. 오직 달력이 들어있는 컨테이너 단 1개만 부활시킴 */
            .element-container:has(#printable-calendar) {
                display: block !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# === [맨 위] 달력이 들어갈 자리 마련 ===
cal_container = st.empty() 

# =========================================================================
# === 아래 UI 영역 ===
st.markdown("<hr style='margin-top:20px; margin-bottom:20px; border-top: 2px dashed #aaa;'>", unsafe_allow_html=True)

st.subheader("⚙️ 달력 설정 및 일정 추가")
calendar_title = st.text_input("출력용 달력 제목을 입력하세요", "2026 2학기 학교별 시험 일정")

cal_col1, cal_col2 = st.columns([1, 1])
with cal_col1:
    cal_start = st.date_input("달력 시작 기준일을 선택하세요", key="cal_start_val")
with cal_col2:
    num_weeks = st.radio("달력 표시 기간", [4, 8, 12], format_func=lambda x: f"{x}주 보기", horizontal=True)

st.markdown("<br>", unsafe_allow_html=True)

add_col1, add_col2 = st.columns([1, 1])
with add_col1:
    school_name = st.text_input("새로운 학교 이름을 입력하세요", "사동고")
    exam_type = st.radio("시험 종류", ["중간고사", "기말고사", "기말고사(중3)", "기말고사(중1,2)"], horizontal=True)
    
    # 🔴 문제의 팝오버: 인쇄 시 이 녀석을 포함한 모든 팝오버가 사라집니다!
    with st.popover("🎨 색상 팔레트 열기 (클릭)"):
        st.write("▼ 아래 실제 색상을 확인하고 고르세요")
        palette_html = "<div style='display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap;'>"
        for name, hex_code in COLORS.items():
            palette_html += f"<div style='text-align: center;'><div title='{name}' style='width: 30px; height: 30px; background-color: {hex_code}; border-radius: 50%; border: 1px solid #aaa; margin: 0 auto; box-shadow: 1px 1px 3px rgba(0,0,0,0.2);'></div><span style='font-size: 10px;'>{name}</span></div>"
        palette_html += "</div>"
        st.markdown(palette_html, unsafe_allow_html=True)
        
        selected_name = st.radio("색상 선택", list(COLORS.keys()), horizontal=True, label_visibility="collapsed")
        st.session_state.selected_color = COLORS[selected_name]

    st.markdown(f"<div style='display: inline-block; width: 25px; height: 25px; background-color: {st.session_state.selected_color}; border-radius: 50%; border: 1px solid #bbb; margin-bottom: 10px; box-shadow: 1px 1px 2px rgba(0,0,0,0.1);'></div> <span style='vertical-align: top; font-weight: bold; margin-left: 8px;'>현재 선택됨</span>", unsafe_allow_html=True)

with add_col2:
    date_range = st.date_input("시험 기간 (시작일 ~ 종료일)", value=(date(2026, 12, 10), date(2026, 12, 15)))
    
    if st.button("달력에 추가하기", use_container_width=True):
        if len(date_range) == 2:
            start_date, end_date = date_range
            new_id = str(uuid.uuid4())
            st.session_state.events.append({
                "id": new_id, "name": school_name, "color": st.session_state.selected_color,
                "type": exam_type, "start_date": start_date, "end_date": end_date
            })
            st.session_state[f"chk_{new_id}"] = True
            st.session_state[f"master_{school_name}"] = True
            st.success(f"[{school_name}] 일정 추가 완료!")
        else:
            st.warning("시작일과 종료일을 모두 선택해 주세요.")

st.divider()

c_hdr, c_high, c_mid, c_mock = st.columns([3, 1.5, 1.5, 2])
with c_hdr:
    st.subheader("📋 전체 등록된 학교 시험 일정")
with c_high:
    st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
    st.checkbox("🏫 고등학교", key="show_high", on_change=toggle_high_schools)
    st.markdown("</div>", unsafe_allow_html=True)
with c_mid:
    st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
    st.checkbox("🎒 중학교", key="show_mid", on_change=toggle_mid_schools)
    st.markdown("</div>", unsafe_allow_html=True)
with c_mock:
    st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
    st.checkbox("📝 수능, 모의고사", key="show_mocks")
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.events:
    def get_weekday_kr(d):
        return ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]

    def format_date_str(ev):
        start_str = f"{ev['start_date'].strftime('%Y-%m-%d')}({get_weekday_kr(ev['start_date'])})"
        end_str = f"{ev['end_date'].strftime('%m-%d')}({get_weekday_kr(ev['end_date'])})"
        return f"{start_str} ~ {end_str}"

    schools = {}
    for ev in st.session_state.events:
        schools.setdefault(ev['name'], []).append(ev)
        
    high_schools = {k: v for k, v in schools.items() if k.endswith('고')}
    mid_schools = {k: v for k, v in schools.items() if k.endswith('중')}

    def render_school_row(s_name, ev_list, is_middle=False):
        if is_middle:
            cols = st.columns([0.3, 1.5, 0.5, 2.2, 0.4, 2.2, 0.4, 2.2, 0.3, 1.0])
        else:
            cols = st.columns([0.3, 1.5, 0.8, 2.5, 0.8, 2.5, 0.6, 1.0])
            
        with cols[0]:
            st.markdown("<div style='margin-top: 14px;'>", unsafe_allow_html=True)
            st.checkbox("", key=f"master_{s_name}", on_change=toggle_school, args=(s_name, not is_middle), label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with cols[1]:
            color = ev_list[0]['color']
            st.markdown(f"<div style='background-color:{color}; padding: 6px; border-radius: 4px; font-weight: bold; text-align: center; margin-top: 8px; color: black;'>{s_name}</div>", unsafe_allow_html=True)
        
        def draw_event_col(col_idx, ev_type_match):
            ev_match = next((e for e in ev_list if e['type'] == ev_type_match or (ev_type_match=='기말고사' and e['type'] in ['기말고사', '기말고사(중3)', '기말고사(중1,2)'] and not is_middle)), None)
            if ev_match:
                with cols[col_idx]:
                    st.markdown("<div style='margin-top: 6px;'>", unsafe_allow_html=True)
                    st.checkbox(format_date_str(ev_match), key=f"chk_{ev_match['id']}", on_change=toggle_individual, args=(s_name, not is_middle))
                    st.markdown("</div>", unsafe_allow_html=True)
        
        if is_middle:
            draw_event_col(3, '중간고사')
            draw_event_col(5, '기말고사(중3)')
            draw_event_col(7, '기말고사(중1,2)')
            del_col = 9
        else:
            draw_event_col(3, '중간고사')
            draw_event_col(5, '기말고사')
            del_col = 7
            
        with cols[del_col]:
            def delete_school_callback(name=s_name):
                st.session_state.events = [e for e in st.session_state.events if e['name'] != name]
            st.markdown("<div style='margin-top: 5px;'>", unsafe_allow_html=True)
            st.button("삭제", key=f"del_{s_name}", on_click=delete_school_callback)
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<hr style='margin: 8px 0; border: 0; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

    if high_schools:
        st.markdown("<br>", unsafe_allow_html=True)
        h_cols = st.columns([0.3, 1.5, 0.8, 2.5, 0.8, 2.5, 0.6, 1.0])
        h_cols[1].markdown("<div style='text-align: center; color: #555;'><b>고등학교</b></div>", unsafe_allow_html=True)
        h_cols[3].markdown("<div style='color: #555; padding-left: 28px;'><b>중간고사</b></div>", unsafe_allow_html=True)
        h_cols[5].markdown("<div style='color: #555; padding-left: 28px;'><b>기말고사</b></div>", unsafe_allow_html=True)
        h_cols[7].markdown("<div style='text-align: center; color: #555;'><b>삭제</b></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 2px solid #bbb;'>", unsafe_allow_html=True)
        
        for s_name, ev_list in high_schools.items():
            render_school_row(s_name, ev_list, is_middle=False)
            
    if mid_schools:
        st.markdown("<br>", unsafe_allow_html=True)
        m_cols = st.columns([0.3, 1.5, 0.5, 2.2, 0.4, 2.2, 0.4, 2.2, 0.3, 1.0])
        m_cols[1].markdown("<div style='text-align: center; color: #555;'><b>중학교</b></div>", unsafe_allow_html=True)
        m_cols[3].markdown("<div style='color: #555; padding-left: 28px;'><b>중간고사</b></div>", unsafe_allow_html=True)
        m_cols[5].markdown("<div style='color: #555; padding-left: 28px;'><b>기말고사(중3)</b></div>", unsafe_allow_html=True)
        m_cols[7].markdown("<div style='color: #555; padding-left: 28px;'><b>기말고사(중1,2)</b></div>", unsafe_allow_html=True)
        m_cols[9].markdown("<div style='text-align: center; color: #555;'><b>삭제</b></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 2px solid #bbb;'>", unsafe_allow_html=True)
        
        for s_name, ev_list in mid_schools.items():
            render_school_row(s_name, ev_list, is_middle=True)
else:
    st.info("등록된 학교 일정이 없습니다.")


# === 💡 달력 그리기 (ID: printable-calendar) ===
days_to_subtract = (st.session_state.cal_start_val.weekday() + 1) % 7
start_sunday = st.session_state.cal_start_val - timedelta(days=days_to_subtract)

cal_html = "<div id='printable-calendar'>"
cal_html += f"<h1 style='text-align: center; margin-bottom: 20px; margin-top: 0px; color: #333;'>{calendar_title}</h1>"
cal_html += """
<style>
    .cal-table { width: 100%; border-collapse: collapse; table-layout: fixed; background-color: white; }
    .cal-th { text-align: center; padding: 10px 0; border-bottom: 2px solid #ccc; font-weight: bold; font-size: 15px;}
    .cal-td { border: 1px solid #ddd; padding: 6px 4px; vertical-align: top; overflow: hidden; }
    .ev-container { display: flex; flex-wrap: wrap; gap: 2px; margin-top: 4px; }
    .ev-box { width: 48%; flex: 0 0 auto; padding: 3px 1px; border-radius: 4px; font-size: 11px; letter-spacing: -0.5px; color: black; font-weight: bold; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; box-shadow: 1px 1px 2px rgba(0,0,0,0.05); }
</style>
<table class='cal-table'>
<tr>
"""

week_days = ["일", "월", "화", "수", "목", "금", "토"]
for i, day_name in enumerate(week_days):
    color = "#e53935" if i == 0 else "#1e88e5" if i == 6 else "black"
    col_width = "9.5%" if (i == 0 or i == 6) else "16.2%"
    cal_html += f"<th class='cal-th' style='color: {color}; width: {col_width};'>{day_name}</th>"
cal_html += "</tr>"

for week in range(num_weeks):
    has_events = False
    for i in range(7):
        current_date = start_sunday + timedelta(days=week*7 + i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        if st.session_state.show_mocks and date_str in MOCK_EXAMS:
            has_events = True
            break
            
        if not (i == 0 or i == 6 or current_date in kr_holidays):
            for ev in st.session_state.events:
                if is_event_visible(ev) and ev["start_date"] <= current_date <= ev["end_date"]:
                    has_events = True
                    break
                    
    row_height = "65px" if has_events else "40px"
    cal_html += "<tr>"
    
    for i in range(7):
        current_date = start_sunday + timedelta(days=week*7 + i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        is_holiday = current_date in kr_holidays
        is_weekend = (i == 0 or i == 6)
        holiday_name = kr_holidays.get(current_date) if is_holiday else ""
        is_mock_day = st.session_state.show_mocks and (date_str in MOCK_EXAMS)
        
        valid_daily_events = []
        if not (is_weekend or is_holiday):
            for ev in st.session_state.events:
                if is_event_visible(ev) and ev["start_date"] <= current_date <= ev["end_date"]:
                    if is_mock_day and ev['name'].endswith('고'):
                        continue
                    valid_daily_events.append(ev)
        
        exam_types = set([ev.get('type', '') for ev in valid_daily_events])
        
        cell_bg = "white"
        if is_mock_day:
            cell_bg = "#E4FDA2"
        elif "중간고사" in exam_types:
            cell_bg = "#DFDEFC"
        elif any("기말고사" in t for t in exam_types):
            cell_bg = "#EFD0D0"
            
        day_color = "#e53935" if (i == 0 or is_holiday) else "#1e88e5" if i == 6 else "#555"
        
        cal_html += f"<td class='cal-td' style='height: {row_height}; background-color: {cell_bg};'>"
        
        cal_html += f"<div style='white-space: nowrap; margin-bottom: 2px;'>"
        cal_html += f"<b style='font-size: 13px; color: {day_color};'>{current_date.month}/{current_date.day}</b>"
        
        if is_mock_day:
            if MOCK_EXAMS[date_str] == "대학수학능력시험":
                cal_html += "<span style='font-size: 11px; font-weight: bold; color: #d32f2f; margin-left: 4px; letter-spacing: -0.5px;'>[수능]</span>"
            else:
                cal_html += "<span style='font-size: 11px; font-weight: bold; color: #d32f2f; margin-left: 4px; letter-spacing: -0.5px;'>[모의고사]</span>"
                
        if "중간고사" in exam_types:
            cal_html += "<span style='font-size: 11px; font-weight: bold; color: #444; margin-left: 4px; letter-spacing: -0.5px;'>[중간고사]</span>"
        if any("기말고사" in t for t in exam_types):
            cal_html += "<span style='font-size: 11px; font-weight: bold; color: #444; margin-left: 4px; letter-spacing: -0.5px;'>[기말고사]</span>"
            
        if is_holiday:
            cal_html += f"<span style='font-size: 11px; color: #e53935; margin-left: 4px; font-weight: bold;'>{holiday_name}</span>"
            
        cal_html += "</div>"
            
        if is_mock_day:
            cal_html += f"<div style='color: #d32f2f; font-weight: bold; font-size: 11px; margin-top: 2px; text-align: center;'>{MOCK_EXAMS[date_str]}</div>"
        
        if valid_daily_events:
            cal_html += "<div class='ev-container'>"
            for ev in valid_daily_events:
                cal_html += f"<div class='ev-box' style='background-color:{ev['color']};' title='{ev['name']}'>{ev['name']}</div>"
            cal_html += "</div>"
                
        cal_html += "</td>"
    cal_html += "</tr>"
    
cal_html += "</table></div>"

cal_container.markdown(cal_html, unsafe_allow_html=True)
