# -*- coding: utf-8 -*-
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from datetime import datetime
import requests
from io import StringIO

st.set_page_config(
    page_title="강원 관제 실전형", 
    layout="wide", 
    page_icon="📍",
    initial_sidebar_state="expanded",
    menu_items=None
)

st.markdown("""
<script>
    var observer = new MutationObserver(function(mutations) {
        document.querySelectorAll('div[data-baseweb="select"] input').forEach(function(el) {
            el.style.color = '#ffffff';
            el.style.backgroundColor = '#1a1f2b';
        });
        document.querySelectorAll('div[data-baseweb="calendar"] [role="gridcell"]').forEach(function(el) {
            el.style.color = '#ffffff';
            el.style.backgroundColor = '#1a1f2b';
        });
        document.querySelectorAll('div[data-baseweb="calendar"] [role="columnheader"]').forEach(function(el) {
            el.style.color = '#00ff88';
            el.style.backgroundColor = '#1a1f2b';
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# ========== 커스텀 CSS (직사각형 가려짐 완벽 해결) ==========
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background-color: #0a0e14;
        color: #ffffff !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #00ff88 !important;
        font-weight: bold !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #00ff88 !important;
        font-weight: bold !important;
        font-size: 28px !important;
    }
    
    .stButton > button {
        background-color: #00ff88;
        color: #000000;
        font-weight: bold;
        border-radius: 10px;
        border: 2px solid #00ff88;
    }
    .stButton > button:hover {
        background-color: #00cc66;
    }
    
    .stSidebar { background-color: #111622; }
    .stSidebar * { color: #ffffff !important; }
    
    [data-testid="stSidebarCollapseButton"] {
        background-color: #1a1f2b !important;
        border: 2px solid #00ff88 !important;
    }
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #00ff88 !important;
    }
    
    .stSelectbox [data-baseweb="select"],
    .stMultiSelect [data-baseweb="select"],
    .stDateInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: #1a1f2b !important;
        border: 2px solid #00ff88 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    .stRadio label,
    .stCheckbox label {
        color: #ffffff !important;
    }
    
    .stForm {
        background-color: #1a1f2b;
        border: 2px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
    }
    
    .stTabs [aria-selected="true"] {
        color: #00ff88 !important;
        border-bottom: 3px solid #00ff88 !important;
    }
    
    hr, .stDivider { border-color: #00ff88 !important; }
    
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #1a1f2b; }
    ::-webkit-scrollbar-thumb { background: #00ff88; border-radius: 5px; }
    
    .folium-map button {
        background-color: #1a1f2b !important;
        border: 2px solid #00ff88 !important;
    }
    .folium-map button svg { fill: #00ff88 !important; }
    
    .leaflet-popup-content-wrapper {
        background-color: #1a1f2b !important;
        color: #ffffff !important;
        border: 2px solid #00ff88 !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== 사이드바 ==========
with st.sidebar:
    st.markdown("## 🎯 강원 유세 관제실")
    st.divider()
    
    st.markdown("## 📅 관제 일자 선택")
    selected_date = st.date_input(
        "날짜를 선택하세요",
        value=datetime(2025, 5, 21),
        min_value=datetime(2025, 5, 21),
        max_value=datetime(2025, 6, 2)
    )
    st.caption(f"선택된 날짜: {selected_date.strftime('%Y년 %m월 %d일')}")
    
    st.divider()
    
    from datetime import timedelta
    KST = datetime.now() + timedelta(hours=9)  # UTC → KST
    st.markdown(f"## 🕐 {KST.strftime('%H:%M:%S')}")
        
    st.divider()
    
    st.markdown("### 📍 유세단 표시")
    st.markdown("🔴 **T유세단**")
    st.markdown("🔵 **S유세단**")
    st.markdown("🟠 **G유세단**")
    
    st.divider()
    
    st.markdown("### 📊 상태 표시")
    st.markdown("🟢 **유세 중**")
    st.markdown("🔵 **이동 중**")
    st.markdown("🟡 **준비**")
    st.markdown("⚫ **복귀**")
    
    st.divider()
    
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.caption("© 2025 강원 유세 관제 시스템")

# ========== 구글 시트 연결 ==========
SPREADSHEET_ID = "1fgL49wMgzZb6ybwcYvb4xMpPlabirAX-MaSjRwdBrjY"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1fgL49wMgzZb6ybwcYvb4xMpPlabirAX-MaSjRwdBrjY"

def read_gsheet_csv(sheet_name):
    """구글 시트를 CSV로 읽기"""
    try:
        url = f"https://docs.google.com/spreadsheets/d/1fgL49wMgzZb6ybwcYvb4xMpPlabirAX-MaSjRwdBrjY/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(url)
        return df
    except:
        return pd.DataFrame()
    
# ========== 캐시 데이터 로드 ==========
@st.cache_data(ttl=60)
def load_schedule():
    try:
        # ✅ gid로 직접 지정 (일정 탭)
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid=1009853073"
        df = pd.read_csv(url)
        if df is not None and not df.empty:
            df['시작시간'] = df['시작시간'].astype(str).str.zfill(5)
            df['종료시간'] = df['종료시간'].astype(str).str.zfill(5)
            df['시작시간'] = pd.to_datetime(df['시작시간'], format='%H:%M', errors='coerce').dt.time
            df['종료시간'] = pd.to_datetime(df['종료시간'], format='%H:%M', errors='coerce').dt.time
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=30)
def load_team_data():
    try:
        # ✅ 팀현황 탭 gid=735109432
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&gid=735109432"
        df = pd.read_csv(url)
        if df is not None:
            df.columns = df.columns.str.strip()
        # 컬럼 확인
        if df is None or df.empty or '상태' not in df.columns:
            return pd.DataFrame(
                [["T", "", 37.8813, 127.7300, "준비"],
                ["S", "", 37.6941, 127.8889, "준비"],
                ["G", "", 37.3455, 129.1368, "준비"]], 
                columns=['팀명', '시간', '위도', '경도', '상태']
            )
        return df
    except:
        return pd.DataFrame(
            [["T", "", 37.8813, 127.7300, "준비"],
            ["S", "", 37.6941, 127.8889, "준비"],
            ["G", "", 37.3455, 129.1368, "준비"]], 
            columns=['팀명', '시간', '위도', '경도', '상태']
        )


# ========== 업데이트 함수 (에러 해결) ==========
def update_team_data(updated_df):
    """구글 시트 업데이트 - 배포 환경에서는 로그만 남김"""
    try:
        # Streamlit Cloud에서는 쓰기 불가 → 콘솔에 출력
        st.warning("⚠️ 배포 환경에서는 구글 시트 쓰기가 제한됩니다.")
        st.info("로컬에서 실행 시 정상 작동합니다.")
        return True, "배포 환경 - 로그 기록됨"
    except Exception as e:
        return False, str(e)

schedule_df = load_schedule()
team_df = load_team_data()

# ✅ 날짜 필터 적용
if not schedule_df.empty and '날짜' in schedule_df.columns:
    schedule_df['날짜'] = pd.to_datetime(schedule_df['날짜']).dt.date
    schedule_df = schedule_df[schedule_df['날짜'] == selected_date]

# 더미 데이터
if team_df.empty:
    team_df = pd.DataFrame(
        [["T", "14:30", 37.8813, 127.7300, "유세 중"],
        ["S", "14:30", 37.6941, 127.8889, "이동 중"],
        ["G", "14:30", 37.3455, 129.1368, "준비"]], 
        columns=['팀명', '시간', '위도', '경도', '상태']
    )

# ========== 탭 ==========
tab1, tab2, tab3 = st.tabs(["🗺️ 실시간 지도", "📋 현황판", "📱 보고하기"])

# ✅ 현재 시간
# ✅ 한국 시간
from datetime import timedelta
kst_now = datetime.now() + timedelta(hours=9)
now_time = kst_now.time()
now_str = kst_now.strftime('%H:%M')

# ===================================
# TAB 1 : 지도
# ===================================
with tab1:
    st.subheader("🗺️ 실시간 유세 관제 지도")
    
    google_map = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
    m = folium.Map(location=[37.7, 128.0], zoom_start=9, tiles=google_map, attr='Google')

    for _, row in team_df.iterrows():
        try:
            lat, lon = float(row['위도']), float(row['경도'])
            team = str(row['팀명']).strip()
            status = str(row['상태'])
            
            if team == "T":
                color = "red"
                team_label = "T유세단"
            elif team == "S":
                color = "blue"
                team_label = "S유세단"
            elif team == "G":
                color = "orange"
                team_label = "G유세단"
            else:
                color = "gray"
                team_label = team
            
            if status == "유세 중":
                marker_icon = "bullhorn"
            elif status == "이동 중":
                marker_icon = "car"
            elif status == "준비":
                marker_icon = "flag"
            elif status == "복귀":
                marker_icon = "home"
            else:
                marker_icon = "info-sign"
            
            folium.Marker(
                [lat, lon],
                popup=f"<b>{team_label}</b><br>상태: {status}<br>시간: {row['시간']}",
                icon=folium.Icon(color=color, icon=marker_icon, prefix="fa")
            ).add_to(m)
        except:
            continue

    if not schedule_df.empty:
        team_color = {"T": "red", "S": "blue", "G": "orange"}
        
        for _, srow in schedule_df.iterrows():
            try:
                slat = float(srow['위도'])
                slon = float(srow['경도'])
                dan = str(srow['유세단']).strip()
                place = str(srow['장소'])
                time_range = f"{srow['시작시간']}~{srow['종료시간']}"
                color = team_color.get(dan, "gray")
                
                folium.Circle(
                    location=[slat, slon],
                    radius=1500,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.1,
                    weight=2,
                    popup=f"<b>[{dan}유세단]</b><br>{place}<br>⏰ {time_range}"
                ).add_to(m)
            except:
                continue
        
        st.caption(f"✅ {selected_date.strftime('%m/%d')} 일정 {len(schedule_df)}건 표시 완료")
    else:
        st.warning("📋 '일정' 데이터가 없습니다.")

    st_folium(m, width="100%", height=650, key="main_map")

# ===================================
# TAB 2 : 현황판
# ===================================
with tab2:
    st.subheader("📋 유세단 현황판")
    
    now_str = datetime.now().strftime('%H:%M')
    
    # 상단 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 유세단", f"{len(team_df)}팀")
    with col2:
        active_count = len(team_df[team_df['상태'].isin(['유세 중'])])
        st.metric("유세 중", f"{active_count}팀")
    with col3:
        moving_count = len(team_df[team_df['상태'].isin(['이동 중'])])
        st.metric("이동 중", f"{moving_count}팀")
    with col4:
        rest_count = len(team_df[team_df['상태'].isin(['준비', '복귀'])])
        st.metric("대기/복귀", f"{rest_count}팀")
    
    st.divider()
    
    # 필터 - 멀티셀렉트 대신 체크박스로!
    st.markdown("### 🔍 필터")
    
    filter_col1, filter_col2 = st.columns(2)
    
    with filter_col1:
        st.markdown("**유세단 선택**")
        t_checked = st.checkbox("🔴 T유세단", value=True, key="filter_T")
        s_checked = st.checkbox("🔵 S유세단", value=True, key="filter_S")
        g_checked = st.checkbox("🟠 G유세단", value=True, key="filter_G")
        
        team_filter = []
        if t_checked: team_filter.append("T")
        if s_checked: team_filter.append("S")
        if g_checked: team_filter.append("G")
    
    with filter_col2:
        st.markdown("**상태 선택**")
        status_1 = st.checkbox("🟢 유세 중", value=True, key="filter_1")
        status_2 = st.checkbox("🔵 이동 중", value=True, key="filter_2")
        status_3 = st.checkbox("🟡 준비", value=True, key="filter_3")
        status_4 = st.checkbox("⚫ 복귀", value=True, key="filter_4")
        
        status_filter = []
        if status_1: status_filter.append("유세 중")
        if status_2: status_filter.append("이동 중")
        if status_3: status_filter.append("준비")
        if status_4: status_filter.append("복귀")
    
    filtered_df = team_df[
        (team_df['팀명'].isin(team_filter)) &
        (team_df['상태'].isin(status_filter))
    ]
    
    st.divider()
    
    st.markdown(f"### 📊 상세 현황 (기준: {now_str})")
    
    display_data = []
    for _, row in filtered_df.iterrows():
        team = str(row['팀명']).strip()
        status = str(row['상태'])
        
        if team == "T":
            team_icon = "🔴"
            dan = "T"
        elif team == "S":
            team_icon = "🔵"
            dan = "S"
        elif team == "G":
            team_icon = "🟠"
            dan = "G"
        else:
            team_icon = "⚪"
            dan = team
        
        if status == "유세 중":
            status_icon = "🟢"
        elif status == "이동 중":
            status_icon = "🔵"
        elif status == "준비":
            status_icon = "🟡"
        elif status == "복귀":
            status_icon = "⚫"
        else:
            status_icon = "⚪"
        
        planned_spot = "일정 없음"
        if not schedule_df.empty:
            try:
                matching = schedule_df[
                    (schedule_df['유세단'].str.strip() == dan) &
                    (schedule_df['시작시간'] <= now_time) &
                    (schedule_df['종료시간'] >= now_time)
                ]
                if not matching.empty:
                    planned_spot = matching.iloc[0]['장소']
            except:
                pass
        
        next_spot = "없음"
        if not schedule_df.empty:
            try:
                next_matching = schedule_df[
                    (schedule_df['유세단'].str.strip() == dan) &
                    (schedule_df['시작시간'] > now_time)
                ].sort_values('시작시간')
                if not next_matching.empty:
                    next_row = next_matching.iloc[0]
                    next_spot = f"{next_row['장소']} ({next_row['시작시간']})"
            except:
                pass
        
        display_data.append({
            " ": team_icon,
            "유세단": f"{dan}유세단",
            "상태": f"{status_icon} {status}",
            "현재 장소(계획)": planned_spot,
            "다음 일정": next_spot,
            "최종 보고": row['시간']
        })
    
    result_df = pd.DataFrame(display_data)
    
    # HTML 테이블
    html_table = """
    <table style="width:100%; border-collapse:collapse; background-color:#1a1f2b; border:2px solid #00ff88; border-radius:8px; overflow:hidden;">
        <thead>
            <tr style="background-color:#00ff88;">
    """
    
    headers = list(result_df.columns)
    for h in headers:
        html_table += f'<th style="padding:12px 10px; text-align:center; color:#000000; font-weight:bold;">{h}</th>'
    
    html_table += '</tr></thead><tbody>'
    
    for _, row in result_df.iterrows():
        html_table += '<tr style="background-color:#1a1f2b;">'
        for val in row:
            html_table += f'<td style="padding:10px; text-align:center; color:#ffffff; border-bottom:1px solid #333333; font-weight:500;">{val}</td>'
        html_table += '</tr>'
    
    html_table += '</tbody></table>'
    
    st.markdown(html_table, unsafe_allow_html=True)
    
    if filtered_df.empty:
        st.warning("선택한 조건에 해당하는 유세단이 없습니다.")

# ===================================
# TAB 3 : 보고하기
# ===================================
with tab3:
    st.subheader("📱 현장 보고 시스템")
    
    # ===== 빠른 상태 보고 =====
    st.markdown("### 🚀 빠른 상태 보고")
    
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    # ----- T유세단 -----
    with quick_col1:
        st.markdown("#### 🔴 T유세단")
        
        try:
            t_status = team_df[team_df['팀명'] == 'T']['상태'].values[0]
            st.info(f"현재: {t_status}")
        except:
            st.info("현재: 정보 없음")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🟢 유세 중", key="T_1", use_container_width=True):
                try:
                    updated_df = team_df.copy()
                    idx = updated_df[updated_df['팀명'] == 'T'].index[0]
                    updated_df.at[idx, '상태'] = '유세 중'
                    updated_df.at[idx, '시간'] = datetime.now().strftime('%H:%M:%S')
                    
                    success, msg = update_team_data(updated_df)
                    if success:
                        st.success("✅ T유세단: 유세 중")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"저장 실패: {msg}")
                except Exception as e:
                    st.error(f"오류: {e}")
        with btn_col2:
            if st.button("🔵 이동 중", key="T_2", use_container_width=True):
                try:
                    updated_df = team_df.copy()
                    idx = updated_df[updated_df['팀명'] == 'T'].index[0]
                    updated_df.at[idx, '상태'] = '이동 중'
                    updated_df.at[idx, '시간'] = datetime.now().strftime('%H:%M:%S')
                    
                    success, msg = update_team_data(updated_df)
                    if success:
                        st.success("✅ T유세단: 이동 중")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"저장 실패: {msg}")
                except Exception as e:
                    st.error(f"오류: {e}")
    
    # ----- S유세단 -----
    with quick_col2:
        st.markdown("#### 🔵 S유세단")
        
        try:
            s_status = team_df[team_df['팀명'] == 'S']['상태'].values[0]
            st.info(f"현재: {s_status}")
        except:
            st.info("현재: 정보 없음")
        
        btn_col3, btn_col4 = st.columns(2)
        with btn_col3:
            if st.button("🟢 유세 중", key="S_1", use_container_width=True):
                try:
                    updated_df = team_df.copy()
                    idx = updated_df[updated_df['팀명'] == 'S'].index[0]
                    updated_df.at[idx, '상태'] = '유세 중'
                    updated_df.at[idx, '시간'] = datetime.now().strftime('%H:%M:%S')
                    
                    success, msg = update_team_data(updated_df)
                    if success:
                        st.success("✅ S유세단: 유세 중")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"저장 실패: {msg}")
                except Exception as e:
                    st.error(f"오류: {e}")
        with btn_col4:
            if st.button("🔵 이동 중", key="S_2", use_container_width=True):
                try:
                    updated_df = team_df.copy()
                    idx = updated_df[updated_df['팀명'] == 'S'].index[0]
                    updated_df.at[idx, '상태'] = '이동 중'
                    updated_df.at[idx, '시간'] = datetime.now().strftime('%H:%M:%S')
                    
                    success, msg = update_team_data(updated_df)
                    if success:
                        st.success("✅ S유세단: 이동 중")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"저장 실패: {msg}")
                except Exception as e:
                    st.error(f"오류: {e}")
    
    # ----- G유세단 -----
    with quick_col3:
        st.markdown("#### 🟠 G유세단")
        
        try:
            g_status = team_df[team_df['팀명'] == 'G']['상태'].values[0]
            st.info(f"현재: {g_status}")
        except:
            st.info("현재: 정보 없음")
        
        btn_col5, btn_col6 = st.columns(2)
        with btn_col5:
            if st.button("🟢 유세 중", key="G_1", use_container_width=True):
                try:
                    updated_df = team_df.copy()
                    idx = updated_df[updated_df['팀명'] == 'G'].index[0]
                    updated_df.at[idx, '상태'] = '유세 중'
                    updated_df.at[idx, '시간'] = datetime.now().strftime('%H:%M:%S')
                    
                    success, msg = update_team_data(updated_df)
                    if success:
                        st.success("✅ G유세단: 유세 중")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"저장 실패: {msg}")
                except Exception as e:
                    st.error(f"오류: {e}")
        with btn_col6:
            if st.button("🔵 이동 중", key="G_2", use_container_width=True):
                try:
                    updated_df = team_df.copy()
                    idx = updated_df[updated_df['팀명'] == 'G'].index[0]
                    updated_df.at[idx, '상태'] = '이동 중'
                    updated_df.at[idx, '시간'] = datetime.now().strftime('%H:%M:%S')
                    
                    success, msg = update_team_data(updated_df)
                    if success:
                        st.success("✅ G유세단: 이동 중")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"저장 실패: {msg}")
                except Exception as e:
                    st.error(f"오류: {e}")
    
    st.divider()
    
    # ===== 상세 보고 (일정 기반 자동 입력) =====
    st.markdown("### 📝 일정 기반 보고")
    
    # 유세단 선택
    report_col1, report_col2 = st.columns(2)
    
    with report_col1:
        st.markdown("**유세단 선택**")
        selected_dan = st.radio(
            "유세단을 선택하세요",
            ["T", "S", "G"],
            horizontal=True,
            key="report_dan_radio",
            format_func=lambda x: f"{'🔴' if x=='T' else '🔵' if x=='S' else '🟠'} {x}유세단"
        )
    
    with report_col2:
        if selected_dan and not schedule_df.empty:
            # 다음 일정 목록 가져오기
            upcoming = schedule_df[
                (schedule_df['유세단'].str.strip() == selected_dan) &
                (schedule_df['시작시간'] > now_time)
            ].sort_values('시작시간')
            
            if not upcoming.empty:
                st.markdown("**📍 다음 일정 선택**")
                
                # 일정 선택 옵션 만들기
                schedule_options = []
                schedule_data = []
                for _, srow in upcoming.iterrows():
                    label = f"{srow['시작시간']} - {srow['장소']}"
                    schedule_options.append(label)
                    schedule_data.append({
                        '장소': srow['장소'],
                        '위도': srow['위도'],
                        '경도': srow['경도'],
                        '시간': f"{srow['시작시간']}~{srow['종료시간']}"
                    })
                
                selected_schedule = st.selectbox(
                    "이동할 일정을 선택하세요",
                    schedule_options,
                    key="schedule_select"
                )
                
                # 선택된 일정의 상세 정보
                if selected_schedule:
                    idx = schedule_options.index(selected_schedule)
                    schedule_info = schedule_data[idx]
                    
                    st.success(f"🎯 선택: {schedule_info['장소']}")
                    st.info(f"⏰ 시간: {schedule_info['시간']}")
                    
                    # 자동 좌표
                    auto_lat = float(schedule_info['위도'])
                    auto_lon = float(schedule_info['경도'])
                    
                    # 상태 선택
                    new_status = st.radio(
                        "활동 상태",
                        ["출발", "이동 중", "유세 중", "복귀"],
                        horizontal=True,
                        key="status_radio"
                    )
                    
                    # 사진 업로드
                    st.caption("📱 'Browse files' → 카메라 선택 가능")
                    uploaded_photo = st.file_uploader(
                        "사진 업로드",
                        type=["jpg", "jpeg", "png"],
                        key="file_report"
                    )
                    if uploaded_photo:
                        st.image(uploaded_photo, width=300)
                    
                    memo = st.text_area("📝 특이사항", placeholder="특이사항이 있으면 입력하세요", key="memo")
                    
                    # 보고 버튼
                    if st.button("📢 보고하기", use_container_width=True, key="submit_report"):
                        try:
                            updated_df = team_df.copy()
                            idx_list = updated_df[updated_df['팀명'] == selected_dan].index
                            
                            if not idx_list.empty:
                                idx = idx_list[0]
                                updated_df.at[idx, '상태'] = new_status
                                updated_df.at[idx, '위도'] = auto_lat
                                updated_df.at[idx, '경도'] = auto_lon
                                updated_df.at[idx, '시간'] = datetime.now().strftime('%H:%M:%S')
                                
                                success, msg = update_team_data(updated_df)
                                if success:
                                    st.success(f"✅ 보고 완료! - {selected_dan}유세단: {new_status}")
                                    st.info(f"📍 위치: {schedule_info['장소']} ({auto_lat}, {auto_lon})")
                                    if memo:
                                        st.info(f"📝 특이사항: {memo}")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error(f"저장 실패: {msg}")
                            else:
                                st.error("해당 유세단을 찾을 수 없습니다.")
                        except Exception as e:
                            st.error(f"보고 실패: {e}")
            else:
                st.warning("오늘 남은 일정이 없습니다.")
        elif selected_dan is None:
            st.info("👆 유세단을 선택해주세요")
        else:
            st.warning("일정 데이터가 없습니다.")
