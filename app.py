import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from datetime import time as dt_time
from streamlit_calendar import calendar
import plotly.express as px
import itertools
import calendar as cal_module
from dateutil.relativedelta import relativedelta
from urllib.parse import quote

# ==========================================
# 設定
# ==========================================

APP_VERSION = "1.0.0-demo"

SPORT_TYPE      = "テニス"
SPORT_EMOJI     = "🎾"
COURT_TYPE_LABEL = "コート種類"
COURT_TYPES     = ["オムニ", "クレー", "ハード", "インドア", "不明"]
SPORT_COLOR_MAP = {
    "不明":    "#808080",
    "オムニ":  "#00AA00",
    "クレー":  "#FF8800",
    "ハード":  "#0066FF",
    "インドア":"#9900CC",
}

LONG_PRESS_DELAY_MS = 1200

# ==========================================
# デモ用固定データ
# ==========================================

FACILITIES = {
    "駒沢オリンピック公園テニスコート": {
        "address": "東京都世田谷区駒沢1-1",
        "url": "https://www.tef.or.jp/kopgp/tennis/",
    },
    "光が丘公園テニスコート": {
        "address": "東京都練馬区光が丘4-1-1",
        "url": "https://www.tokyo-park.or.jp/park/hikarigaoka/index.html",
    },
    "野川公園テニスコート": {
        "address": "東京都三鷹市大沢6-4-1",
        "url": "https://www.city.mitaka.lg.jp/c_service/017/017503.html",
    },
    "舎人公園テニスコート": {
        "address": "東京都足立区舎人1-1",
        "url": "https://www.tokyo-park.or.jp/park/toneri/facility/index.html",
    },
    "府中の森公園テニスコート": {
        "address": "東京都府中市浅間町1-3-1",
        "url": "https://www.tokyo-park.or.jp/park/fuchunomori/index.html",
    },
}

LOTTERY_SETTINGS = [
    {"id": 1, "title": "○○テニスコート抽選", "frequency": "monthly",
     "start_day": 1,  "end_day": 10, "messages": "抽選期間(毎月1〜10日)",  "enabled": True},
    {"id": 2, "title": "△△施設抽選",         "frequency": "monthly",
     "start_day": 15, "end_day": 18, "messages": "抽選期間(毎月15〜18日)", "enabled": True},
]


def make_sample_df() -> pd.DataFrame:
    """デモ用サンプルデータを生成する（セッション初期化時に1回だけ呼ぶ）"""
    today = (datetime.utcnow() + timedelta(hours=9)).date()
    rows = []

    # ---- 過去データ（実績グラフ用）----
    past = [
        (-175, "駒沢オリンピック公園テニスコート", "オムニ",  10, 12, ["メンバーA","メンバーB","メンバーC","メンバーD"], 4),
        (-160, "光が丘公園テニスコート",          "ハード",  14, 16, ["メンバーA","メンバーC","メンバーE"],             6),
        (-145, "駒沢オリンピック公園テニスコート", "オムニ",  10, 12, ["メンバーA","メンバーB","メンバーD","メンバーE","メンバーF"], 6),
        (-130, "野川公園テニスコート",            "クレー",   9, 11, ["メンバーA","メンバーB","メンバーC"],             6),
        (-115, "駒沢オリンピック公園テニスコート", "オムニ",  21, 22, ["メンバーA","メンバーC","メンバーD"],             4),
        (-100, "光が丘公園テニスコート",          "ハード",  14, 16, ["メンバーA","メンバーB","メンバーC","メンバーD","メンバーE","メンバーF"], 6),
        (-85,  "駒沢オリンピック公園テニスコート", "オムニ",  10, 12, ["メンバーA","メンバーB","メンバーD"],             4),
        (-70,  "駒沢オリンピック公園テニスコート", "オムニ",  21, 22, ["メンバーA","メンバーC","メンバーE","メンバーF"], 4),
        (-55,  "野川公園テニスコート",            "クレー",   9, 11, ["メンバーA","メンバーB","メンバーC","メンバーD"], 6),
        (-40,  "駒沢オリンピック公園テニスコート", "オムニ",  10, 12, ["メンバーA","メンバーB","メンバーE"],             4),
        (-25,  "光が丘公園テニスコート",          "ハード",  14, 16, ["メンバーA","メンバーC","メンバーD","メンバーF"], 6),
        (-10,  "駒沢オリンピック公園テニスコート", "オムニ",  21, 22, ["メンバーA","メンバーB","メンバーC","メンバーD"], 4),
    ]
    for offset, fac, ct, sh, eh, members, cap in past:
        rows.append({
            "date": today + timedelta(days=offset),
            "facility": fac, "court_type": ct,
            "status": "完了",
            "start_hour": sh, "start_minute": 0,
            "end_hour":   eh, "end_minute":   0,
            "participants": members[:],
            "absent": [], "consider": [],
            "message": "幹事確保。",
            "capacity": cap,
        })

    # ---- 今後の予定 ----
    future = [
        ( 6,  "駒沢オリンピック公園テニスコート", "オムニ",  10, 12,
          ["メンバーA","メンバーB","メンバーC"], ["メンバーE"], 6, "募集中", "幹事確保。参加者募集中です。"),
        (13,  "光が丘公園テニスコート",          "ハード",  14, 16,
          ["メンバーA","メンバーB","メンバーC","メンバーD","メンバーE","メンバーF"], [], 6, "締切", "定員に達しました。"),
        (20,  "野川公園テニスコート",            "クレー",   9, 11,
          [], [], 6, "抽選中", "抽選申込み済。結果待ちです。"),
        (27,  "駒沢オリンピック公園テニスコート", "オムニ",  21, 22,
          ["メンバーA"], [], 4, "募集中", "幹事確保。参加者募集中です。"),
    ]
    for offset, fac, ct, sh, eh, parts, consider, cap, status, msg in future:
        rows.append({
            "date": today + timedelta(days=offset),
            "facility": fac, "court_type": ct,
            "status": status,
            "start_hour": sh, "start_minute": 0,
            "end_hour":   eh, "end_minute":   0,
            "participants": parts[:],
            "absent": [], "consider": consider[:],
            "message": msg,
            "capacity": cap,
        })

    return pd.DataFrame(rows)


# ==========================================
# ユーティリティ
# ==========================================

def safe_int(val, default=0):
    try:
        if pd.isna(val) or val == "":
            return default
        return int(float(val))
    except Exception:
        return default


def to_jst_date(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return (dt + timedelta(hours=9)).date()
    except Exception:
        if isinstance(iso_str, date):
            return iso_str
        return datetime.strptime(str(iso_str)[:10], "%Y-%m-%d").date()


def generate_google_calendar_url(r):
    title    = f"{SPORT_EMOJI}{SPORT_TYPE}_{r['facility']}"
    ct       = r.get("court_type")
    if ct and ct != "不明":
        title += f" ({ct})"
    res_date = r["date"]
    s_h = int(safe_int(r.get("start_hour"), 9))
    s_m = int(safe_int(r.get("start_minute"), 0))
    e_h = int(safe_int(r.get("end_hour"),   11))
    e_m = int(safe_int(r.get("end_minute"),  0))
    start_dt = datetime.combine(res_date, dt_time(s_h, s_m))
    end_dt   = datetime.combine(res_date, dt_time(e_h, e_m))
    params = [
        "action=TEMPLATE",
        f"text={quote(title)}",
        f"dates={start_dt.strftime('%Y%m%dT%H%M%S')}/{end_dt.strftime('%Y%m%dT%H%M%S')}",
        "ctz=Asia/Tokyo",
    ]
    return f"https://calendar.google.com/calendar/render?{'&'.join(params)}"


# ==========================================
# データ読み書き（セッションメモリ）
# ==========================================

def _init_data():
    """セッション初回のみサンプルデータを投入"""
    if "demo_df" not in st.session_state:
        st.session_state["demo_df"] = make_sample_df()


def load_reservations() -> pd.DataFrame:
    _init_data()
    return st.session_state["demo_df"].copy()


def save_reservations(df: pd.DataFrame):
    st.session_state["demo_df"] = df.reset_index(drop=True)
    # load_reservations のキャッシュはないのでそのまま反映


def load_facilities_data() -> dict:
    return FACILITIES


def add_facility_if_not_exists(facility_name: str):
    """デモ版ではセッション中の一時追加のみ（再起動でリセット）"""
    if facility_name not in st.session_state.get("extra_facilities", {}):
        if "extra_facilities" not in st.session_state:
            st.session_state["extra_facilities"] = {}
        st.session_state["extra_facilities"][facility_name] = {"address": "", "url": ""}


def load_facilities_with_extra() -> dict:
    fac = dict(FACILITIES)
    fac.update(st.session_state.get("extra_facilities", {}))
    return fac


def check_and_show_reminders() -> list[str]:
    today = (datetime.utcnow() + timedelta(hours=9)).date()
    messages = []
    for item in LOTTERY_SETTINGS:
        if not item["enabled"]:
            continue
        d = today.day
        if item["start_day"] <= d <= item["end_day"]:
            messages.append(item["messages"])
    return messages


# ==========================================
# 自動完了（前日イベントを完了に）
# ==========================================

def auto_complete_yesterday_events():
    today     = (datetime.utcnow() + timedelta(hours=9)).date()
    yesterday = today - timedelta(days=1)
    if st.session_state.get("auto_completed_for_date") == str(yesterday):
        return
    df = load_reservations()
    if df.empty:
        st.session_state["auto_completed_for_date"] = str(yesterday)
        return
    mask = (df["date"] == yesterday) & (~df["status"].isin(["完了", "中止"]))
    if mask.sum() > 0:
        df.loc[mask, "status"] = "完了"
        save_reservations(df)
    st.session_state["auto_completed_for_date"] = str(yesterday)


# ==========================================
# 画面描画
# ==========================================

st.markdown(f"<h3>{SPORT_EMOJI} {SPORT_TYPE}予約管理（デモ）</h3>", unsafe_allow_html=True)
st.markdown(f"<div style='font-size:0.6em; text-align:right;'>v{APP_VERSION}</div>", unsafe_allow_html=True)

st.markdown("""
<script>
    const observer = new MutationObserver(() => {
        const dialog = parent.document.querySelector('div[data-testid="stDialog"]');
        if (dialog) dialog.scrollTop = 0;
    });
    observer.observe(parent.document.body, { childList: true, subtree: true });
</script>
<style>
div[data-testid="stDialog"] {
    align-items: flex-start !important;
    padding-top: 10px !important;
    overflow-y: auto !important;
}
div[data-testid="stDialog"] > div[role="dialog"] {
    margin-top: 0 !important;
    margin-bottom: 50px !important;
}
div[data-testid="stDialog"] button[aria-label="Close"] { display: none !important; }
.stAppViewContainer { margin-top: 0 !important; }
.stApp { padding-top: 0 !important; }
.block-container { padding-top: 4.0rem !important; }
</style>
""", unsafe_allow_html=True)

# デモバナー
st.info("🎾 これはデモ版です。データはブラウザを閉じるとリセットされます。", icon=None)

# お知らせ
reminder_messages = check_and_show_reminders()
if reminder_messages:
    with st.expander("📢 お知らせ", expanded=False):
        for m in reminder_messages:
            st.info(m)

# 成功トースト
if st.session_state.get("show_success_message"):
    st.toast(st.session_state["show_success_message"], icon="✅")
    st.session_state["show_success_message"] = None

# データ読み込み
auto_complete_yesterday_events()
df_res = load_reservations()

# リストリセットカウンター
if "list_reset_counter" not in st.session_state:
    st.session_state["list_reset_counter"] = 0

status_color = {
    "募集中": {"bg": "#90ee90", "text": "black"},
    "締切":   {"bg": "#90ee90", "text": "black"},
    "抽選中": {"bg": "#ffd966", "text": "black"},
    "中止":   {"bg": "#d3d3d3", "text": "black"},
    "完了":   {"bg": "#d3d3d3", "text": "black"},
}

events = []
for idx, r in df_res.iterrows():
    raw_date = r.get("date")
    if pd.isna(raw_date) or raw_date == "":
        continue
    curr_date = raw_date if isinstance(raw_date, date) else datetime.strptime(str(raw_date)[:10], "%Y-%m-%d").date()
    s_h = safe_int(r.get("start_hour"), 9)
    s_m = safe_int(r.get("start_minute"), 0)
    e_h = safe_int(r.get("end_hour"),   11)
    e_m = safe_int(r.get("end_minute"),  0)
    try:
        start_dt = datetime.combine(curr_date, dt_time(s_h, s_m))
        end_dt   = datetime.combine(curr_date, dt_time(e_h, e_m))
    except Exception:
        continue
    color = status_color.get(r["status"], {"bg": "#FFFFFF", "text": "black"})
    ct_val = r.get("court_type")
    title_str = (f"{r['status']} {r['facility']} ({ct_val})"
                 if ct_val and ct_val != "不明"
                 else f"{r['status']} {r['facility']}")
    events.append({
        "id": idx,
        "title": title_str,
        "start": start_dt.isoformat(),
        "end":   end_dt.isoformat(),
        "backgroundColor": color["bg"],
        "borderColor":     color["bg"],
        "textColor":       color["text"],
    })


# ==========================================
# 表示モード切り替え
# ==========================================

if "prev_view_mode" not in st.session_state:
    st.session_state["prev_view_mode"] = None

view_mode = st.radio(
    "表示モード",
    ["予定", "一覧", "実績"],
    horizontal=True,
    label_visibility="collapsed",
    key="view_mode_selector",
)

if (st.session_state["prev_view_mode"] is not None
        and st.session_state["prev_view_mode"] != view_mode):
    st.session_state["is_popup_open"]        = False
    st.session_state["last_click_signature"] = None
    st.session_state["active_event_idx"]     = None
    st.session_state["list_reset_counter"]  += 1
st.session_state["prev_view_mode"] = view_mode


# === モード1: カレンダー ===
if view_mode == "予定":
    initial_date = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.get("clicked_date"):
        initial_date = st.session_state["clicked_date"]
    cal_key = str(initial_date)[:7]
    cal_state = calendar(
        events=events,
        options={
            "initialView":    "dayGridMonth",
            "initialDate":    initial_date,
            "selectable":     True,
            "headerToolbar":  {"left": "prev,next today", "center": "title", "right": ""},
            "eventDisplay":   "block",
            "displayEventTime": False,
            "height":         "auto",
            "contentHeight":  "auto",
            "aspectRatio":    1.2,
            "titleFormat":    {"year": "numeric", "month": "2-digit"},
            "longPressDelay": LONG_PRESS_DELAY_MS,
        },
        key=f"calendar_{cal_key}",
    )

# === モード2: 一覧 ===
elif view_mode == "一覧":
    cal_state = None
    show_past = st.checkbox("過去の予約も表示する", value=False, key="filter_show_past")
    df_list   = df_res.copy()

# === モード3: 実績 ===
elif view_mode == "実績":
    cal_state = None

    if df_res.empty:
        st.info("予約データがありません")
    else:
        df_stats = df_res.copy()

        def compute_duration(row):
            try:
                s = datetime.combine(row["date"], dt_time(safe_int(row["start_hour"]), safe_int(row["start_minute"])))
                e = datetime.combine(row["date"], dt_time(safe_int(row["end_hour"]),   safe_int(row["end_minute"])))
                return (e - s).total_seconds() / 3600.0
            except Exception:
                return 0.0

        df_stats["duration_hours"] = df_stats.apply(compute_duration, axis=1)
        df_stats["year_month"]     = df_stats["date"].apply(lambda d: d.strftime("%Y/%m"))

        today_jst        = (datetime.utcnow() + timedelta(hours=9)).date()
        last_day         = cal_module.monthrange(today_jst.year, today_jst.month)[1]
        default_end_date = date(today_jst.year, today_jst.month, last_day)

        all_participants = set()
        for _, row in df_stats.iterrows():
            p = row.get("participants", [])
            if isinstance(p, list):
                all_participants.update(p)

        selected_person = st.selectbox(
            "表示対象",
            ["全体"] + sorted(list(all_participants)),
            key="stats_person_select",
        )

        use_date_range = st.checkbox("期間を指定する", value=False, key="stats_use_date_range")
        if use_date_range:
            col1, col2 = st.columns(2)
            min_date   = df_stats["date"].min()
            with col1:
                start_date = st.date_input("開始日", value=min_date, min_value=min_date, max_value=default_end_date, key="stats_start_date")
            with col2:
                end_date = st.date_input("終了日", value=default_end_date, min_value=min_date, max_value=default_end_date, key="stats_end_date")
        else:
            start_date = df_stats["date"].min()
            end_date   = default_end_date

        df_f = df_stats[df_stats["status"] == "完了"].copy()
        if selected_person != "全体":
            df_f = df_f[df_f["participants"].apply(lambda x: selected_person in x if isinstance(x, list) else False)]
        df_f = df_f[(df_f["date"] >= start_date) & (df_f["date"] <= end_date)]

        all_months = []
        cur = start_date.replace(day=1)
        while cur <= end_date.replace(day=1):
            all_months.append(cur.strftime("%Y/%m"))
            cur += relativedelta(months=1)

        all_court_types = sorted(df_f["court_type"].dropna().unique())

        if df_f.empty:
            st.warning("選択条件に該当するデータがありません")
        else:
            summary = df_f.groupby(["year_month", "court_type"]).agg(
                events_count=("date", "count"),
                total_hours=("duration_hours", "sum"),
            ).reset_index()
            summary["total_hours"] = summary["total_hours"].round(2)

            base = pd.DataFrame(
                list(itertools.product(all_months, all_court_types)),
                columns=["year_month", "court_type"],
            )
            summary = base.merge(summary, on=["year_month", "court_type"], how="left")
            summary["events_count"] = summary["events_count"].fillna(0).astype(int)
            summary["total_hours"]  = summary["total_hours"].fillna(0).round(2)
            summary = summary.sort_values("year_month")

            st.markdown("---")
            fig_count = px.bar(
                summary, x="year_month", y="events_count", color="court_type",
                title=f"月別練習回数 - {selected_person}",
                labels={"year_month": "", "events_count": "練習回数（回）", "court_type": COURT_TYPE_LABEL},
                text="events_count", barmode="stack", color_discrete_map=SPORT_COLOR_MAP,
            )
            fig_count.update_traces(textposition="inside", texttemplate="%{text:.0f}", textangle=0, textfont=dict(color="white", size=14))
            fig_count.update_layout(
                yaxis_title="練習回数（回）", xaxis_tickangle=90, height=500,
                margin=dict(b=120, l=80, r=80, t=100), hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text=""),
            )
            st.plotly_chart(fig_count, use_container_width=True, config={"staticPlot": True})

            fig_hours = px.bar(
                summary, x="year_month", y="total_hours", color="court_type",
                title=f"月別練習時間 - {selected_person}",
                labels={"year_month": "", "total_hours": "練習時間（時間）", "court_type": COURT_TYPE_LABEL},
                text="total_hours", barmode="stack", color_discrete_map=SPORT_COLOR_MAP,
            )
            fig_hours.update_traces(textposition="inside", texttemplate="%{text:.0f}", textangle=0, textfont=dict(color="white", size=14))
            fig_hours.update_layout(
                yaxis_title="練習時間（時間）", xaxis_tickangle=90, height=500,
                margin=dict(b=120, l=80, r=80, t=100), hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, title_text=""),
            )
            st.plotly_chart(fig_hours, use_container_width=True, config={"staticPlot": True})


# === 一覧表示（続き）===
if view_mode == "一覧" and not df_list.empty:
    if not show_past:
        today_jst = (datetime.utcnow() + timedelta(hours=9)).date()
        df_list   = df_list[df_list["date"] >= today_jst]

    def fmt_time(r):
        return f"{safe_int(r.get('start_hour')):02}:{safe_int(r.get('start_minute')):02} - {safe_int(r.get('end_hour')):02}:{safe_int(r.get('end_minute')):02}"

    def fmt_participants_consider(row):
        parts     = row["participants"] if isinstance(row["participants"], list) else []
        consider  = row["consider"]     if isinstance(row["consider"], list)     else []
        result    = ", ".join(parts)
        if consider:
            result += f" (保留 {', '.join(consider)})"
        return result

    def fmt_date_wd(d):
        if not isinstance(d, (date, datetime)):
            return str(d)
        wd = ["(月)","(火)","(水)","(木)","(金)","(土)","(日)"][d.weekday()]
        return f"{d.strftime('%Y-%m-%d')} {wd}"

    df_list["日時"]       = df_list["date"].apply(fmt_date_wd) + " " + df_list.apply(fmt_time, axis=1)
    df_list["施設名"]     = df_list["facility"]
    df_list["コート種類"] = df_list["court_type"].fillna("")
    df_list["ステータス"] = df_list["status"]
    df_list["定員"]       = df_list["capacity"].apply(
        lambda x: "指定なし" if (x is None or x == "" or pd.isna(x)) else f"{int(x)}名"
    )
    df_list["参加者"]     = df_list.apply(fmt_participants_consider, axis=1)
    df_list["メモ"]       = df_list["message"].apply(lambda x: str(x).replace("<br>", " ") if pd.notna(x) else "")

    display_cols = ["日時", "施設名", "コート種類", "ステータス", "定員", "参加者", "メモ"]
    df_display   = df_list[display_cols].sort_values("日時", ascending=True)

    table_key    = f"reservation_list_table_{st.session_state['list_reset_counter']}"
    event_selection = st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=table_key,
        column_config={
            "日時":       st.column_config.TextColumn("日時",       width="medium"),
            "施設名":     st.column_config.TextColumn("施設名",     width="medium"),
            "コート種類": st.column_config.TextColumn("コート種類", width="small"),
            "ステータス": st.column_config.TextColumn("ステータス", width="small"),
            "定員":       st.column_config.TextColumn("定員",       width="small"),
            "参加者":     st.column_config.TextColumn("参加者",     width="large"),
            "メモ":       st.column_config.TextColumn("メモ",       width="large"),
        },
    )

    if len(event_selection.selection.rows) > 0:
        sel_row    = event_selection.selection.rows[0]
        actual_idx = df_display.index[sel_row]
        if st.session_state.get("active_event_idx") != actual_idx:
            st.session_state["active_event_idx"]     = actual_idx
            st.session_state["clicked_date"]         = str(df_res.loc[actual_idx]["date"])
            st.session_state["is_popup_open"]        = True
            st.session_state["popup_mode"]           = "edit"
            st.rerun()
elif view_mode == "一覧":
    st.info("表示できる予約データがありません。")


# ==========================================
# イベントハンドリング
# ==========================================

for key, default in [
    ("is_popup_open",        False),
    ("last_click_signature", None),
    ("popup_mode",           None),
    ("prev_cal_state",       None),
    ("active_event_idx",     None),
    ("skip_calendar_event",  False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if view_mode == "予定" and cal_state:
    if cal_state != st.session_state["prev_cal_state"]:
        st.session_state["prev_cal_state"] = cal_state

        if st.session_state["skip_calendar_event"]:
            st.session_state["skip_calendar_event"] = False
            current_view = cal_state.get("view", {})
            st.session_state["last_view_start"] = current_view.get("currentStart")
        else:
            current_view  = cal_state.get("view", {})
            current_start = current_view.get("currentStart")

            if "last_view_start" not in st.session_state:
                st.session_state["last_view_start"] = current_start

            if current_start != st.session_state["last_view_start"]:
                st.session_state["last_view_start"]      = current_start
                st.session_state["is_popup_open"]        = False
                st.session_state["active_event_idx"]     = None
                st.session_state["list_reset_counter"]  += 1
            else:
                callback          = cal_state.get("callback")
                current_signature = None
                if callback == "dateClick":
                    current_signature = f"date_{cal_state['dateClick']['date']}"
                elif callback == "eventClick":
                    current_signature = f"event_{cal_state['eventClick']['event']['id']}"

                if current_signature and current_signature != st.session_state["last_click_signature"]:
                    st.session_state["last_click_signature"] = current_signature
                    st.session_state["is_popup_open"]        = True

                    if callback == "dateClick":
                        st.session_state["clicked_date"]        = cal_state["dateClick"]["date"]
                        st.session_state["active_event_idx"]    = None
                        st.session_state["popup_mode"]          = "new"
                        st.session_state["list_reset_counter"] += 1
                    elif callback == "eventClick":
                        idx = int(cal_state["eventClick"]["event"]["id"])
                        st.session_state["active_event_idx"]    = idx
                        if idx in df_res.index:
                            st.session_state["clicked_date"] = str(df_res.loc[idx]["date"])
                        st.session_state["popup_mode"]          = "edit"
                        st.session_state["list_reset_counter"] += 1

                    st.rerun()


# ==========================================
# ポップアップ定義
# ==========================================

@st.dialog("予約内容の登録・編集")
def entry_form_dialog(mode, idx=None, date_str=None):

    def _close():
        st.session_state["is_popup_open"]        = False
        st.session_state["last_click_signature"] = None
        st.session_state["active_event_idx"]     = None
        st.session_state["list_reset_counter"]  += 1
        st.rerun()

    facilities_data = load_facilities_with_extra()

    # ---- 新規登録 ----
    if mode == "new":
        display_date = to_jst_date(date_str)
        st.write(f"📅 **日付:** {display_date}")

        past_facilities = df_res["facility"].dropna().unique().tolist() if "facility" in df_res.columns else []
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("開始時間", value=dt_time(9, 0),  step=timedelta(minutes=30))
        with col2:
            end_time   = st.time_input("終了時間", value=dt_time(11, 0), step=timedelta(minutes=30))

        fac_select = st.selectbox("施設名", ["(施設名を選択)"] + past_facilities + ["新規登録"], index=0)
        facility   = st.text_input("施設名を入力") if fac_select == "新規登録" else (fac_select if fac_select != "(施設名を選択)" else "")

        court_type = st.selectbox("コート種類", COURT_TYPES, index=0)

        cap_opts     = ["指定なし"] + [str(i) for i in range(1, 31)]
        cap_selected = st.selectbox("定員", cap_opts, index=0)
        capacity     = None if cap_selected == "指定なし" else int(cap_selected)

        status  = st.selectbox("ステータス", ["募集中", "抽選中"], index=0)
        message = st.text_area("メモ", placeholder="例：集合時間や持ち物など")

        st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)
        st.divider()
        col_reg, col_close = st.columns(2)
        with col_reg:
            if st.button("登録する", type="primary", use_container_width=True):
                if not facility:
                    st.error("⚠️ 施設名を選択してください")
                elif end_time <= start_time:
                    st.error("⚠️ 終了時間は開始時間より後にしてください")
                else:
                    add_facility_if_not_exists(facility)
                    new_row = {
                        "date": to_jst_date(date_str),
                        "facility": facility, "court_type": court_type,
                        "status": status,
                        "start_hour": start_time.hour, "start_minute": start_time.minute,
                        "end_hour":   end_time.hour,   "end_minute":   end_time.minute,
                        "participants": [], "absent": [], "consider": [],
                        "message": message.replace("\n", "<br>"),
                        "capacity": capacity,
                    }
                    current_df = load_reservations()
                    save_reservations(pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True))
                    st.session_state["show_success_message"] = "登録しました"
                    _close()
        with col_close:
            if st.button("閉じる", use_container_width=True):
                _close()

    # ---- 編集 ----
    elif mode == "edit" and idx is not None:
        if idx not in df_res.index:
            st.error("イベントが削除されました。")
            if st.button("閉じる"):
                _close()
            return

        r = df_res.loc[idx]
        fac_info   = facilities_data.get(r["facility"], {})
        fac_url    = fac_info.get("url", "")
        fac_addr   = fac_info.get("address", "")

        # --- 詳細表示 ---
        st.markdown(f"**日時:** {r['date']} {safe_int(r.get('start_hour')):02}:{safe_int(r.get('start_minute')):02} - {safe_int(r.get('end_hour')):02}:{safe_int(r.get('end_minute')):02}")
        cal_url = generate_google_calendar_url(r)
        st.markdown(f'<a href="{cal_url}" target="_blank" style="font-size:14px;color:#1f77b4;">カレンダーに追加</a>', unsafe_allow_html=True)

        if fac_url:
            st.markdown(f'**施設:** <a href="{fac_url}" target="_blank" style="color:#1f77b4;">{r["facility"]}</a>', unsafe_allow_html=True)
        else:
            st.markdown(f"**施設:** {r['facility']}")

        if fac_addr:
            map_url = f"https://www.google.com/maps/search/?api=1&query={quote(fac_addr)}"
            st.markdown(f'**住所:** <a href="{map_url}" target="_blank" style="color:#1f77b4;">{fac_addr}</a>', unsafe_allow_html=True)

        ct_val = r.get("court_type")
        if ct_val:
            st.markdown(f"**コート種類:** {ct_val}")

        cap = r.get("capacity")
        if cap is None or cap == "":
            cap_text = "指定なし"
        else:
            try:
                p_cnt    = len([p for p in r.get("participants", []) if p])
                cap_text = f"{int(cap)}名（参加者{p_cnt}名）"
            except Exception:
                cap_text = "指定なし"
        st.markdown(f"**定員:** {cap_text}")

        parts    = r.get("participants", []) if isinstance(r.get("participants"), list) else []
        consider = r.get("consider", [])     if isinstance(r.get("consider"), list)     else []
        p_text   = ", ".join(str(x) for x in parts if str(x).strip())
        if consider:
            p_text += f" (保留 {', '.join(str(x) for x in consider if str(x).strip())})"
        st.markdown(f"**参加者:** {p_text if p_text else 'なし'}")
        st.markdown(f"**ステータス:** {r['status']}")

        display_msg = str(r.get("message", "")).replace("<br>", "\n") or "（なし）"
        st.markdown(f"**メモ:**\n{display_msg}")

        st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)
        st.divider()
        st.subheader("参加表明")

        past_nicks = set()
        for col in ["participants", "absent", "consider"]:
            if col in df_res.columns:
                for lst in df_res[col]:
                    if isinstance(lst, list):
                        past_nicks.update(n for n in lst if n)
        past_nicks = sorted(past_nicks)

        col_nick, col_type = st.columns(2)
        with col_nick:
            nick_choice = st.selectbox("名前", ["(選択)"] + past_nicks + ["新規入力"], key="edit_nick")
            nick = st.text_input("名前を入力", key="edit_nick_input") if nick_choice == "新規入力" else (nick_choice if nick_choice != "(選択)" else "")
        with col_type:
            part_type = st.radio("区分", ["参加", "保留", "削除"], horizontal=True, key="edit_type")

        col_upd, col_close_main = st.columns(2)
        with col_upd:
            if st.button("反映する", type="primary", use_container_width=True):
                if not nick:
                    st.warning("名前を選択してください")
                else:
                    current_df   = load_reservations()
                    participants = list(current_df.at[idx, "participants"]) if isinstance(current_df.at[idx, "participants"], list) else []
                    absent       = list(current_df.at[idx, "absent"])       if isinstance(current_df.at[idx, "absent"], list)       else []
                    consider_lst = list(current_df.at[idx, "consider"])     if isinstance(current_df.at[idx, "consider"], list)     else []
                    capacity     = current_df.at[idx, "capacity"]
                    cur_status   = current_df.at[idx, "status"]

                    try:
                        capacity = int(capacity) if capacity not in (None, "") else None
                    except (ValueError, TypeError):
                        capacity = None

                    cap_error = False
                    if part_type != "削除" and capacity is not None:
                        temp = [p for p in participants if p != nick]
                        if part_type == "参加":
                            temp.append(nick)
                        if len(temp) > capacity:
                            st.error(f"⚠️ 定員に達しています（定員: {capacity}名）")
                            cap_error = True

                    if not cap_error:
                        for lst in [participants, absent, consider_lst]:
                            if nick in lst:
                                lst.remove(nick)
                        if part_type == "参加":
                            participants.append(nick)
                        elif part_type == "保留":
                            consider_lst.append(nick)

                        current_df.at[idx, "participants"] = participants
                        current_df.at[idx, "absent"]       = absent
                        current_df.at[idx, "consider"]     = consider_lst

                        p_cnt = len(participants)
                        if capacity is not None:
                            if p_cnt >= capacity and cur_status == "募集中":
                                current_df.at[idx, "status"] = "締切"
                            elif p_cnt < capacity and cur_status == "締切":
                                current_df.at[idx, "status"] = "募集中"

                        save_reservations(current_df)
                        st.success("反映しました")
                        st.rerun()
        with col_close_main:
            if st.button("閉じる", use_container_width=True):
                _close()

        with st.expander("イベント編集・削除"):
            edit_tab, delete_tab = st.tabs(["編集", "削除"])
            with edit_tab:
                new_msg   = st.text_area("メモの編集", value=str(r.get("message", "")).replace("<br>", "\n"))
                new_court = st.selectbox("コート種類", COURT_TYPES,
                                         index=COURT_TYPES.index(r.get("court_type")) if r.get("court_type") in COURT_TYPES else 0)

                cur_parts_count = len([p for p in r.get("participants", []) if p])
                cur_cap         = r.get("capacity")
                try:
                    cur_cap = int(cur_cap) if cur_cap not in (None, "") else None
                except Exception:
                    cur_cap = None

                status_opts = ["募集中", "締切", "抽選中", "中止", "完了"]
                if cur_cap is not None and cur_parts_count >= cur_cap and r["status"] != "募集中":
                    if "募集中" in status_opts:
                        status_opts.remove("募集中")

                new_status = st.selectbox("ステータスの変更", status_opts,
                                          index=status_opts.index(r["status"]) if r["status"] in status_opts else 0)

                cap_opts2   = ["指定なし"] + [str(i) for i in range(max(cur_parts_count, 1), 31)]
                cur_cap_idx = 0
                if cur_cap is not None and str(cur_cap) in cap_opts2:
                    cur_cap_idx = cap_opts2.index(str(cur_cap))
                cap_selected2 = st.selectbox("定員", cap_opts2, index=cur_cap_idx)
                new_cap       = None if cap_selected2 == "指定なし" else int(cap_selected2)

                if st.button("内容を更新", use_container_width=True):
                    if new_cap is not None and cur_parts_count > new_cap:
                        st.error(f"⚠️ 定員は現在の参加者数（{cur_parts_count}名）以上に設定してください")
                    else:
                        current_df = load_reservations()
                        current_df.at[idx, "message"]    = new_msg.replace("\n", "<br>")
                        current_df.at[idx, "status"]     = new_status
                        current_df.at[idx, "capacity"]   = new_cap
                        current_df.at[idx, "court_type"] = new_court
                        save_reservations(current_df)
                        st.success("更新しました")
                        st.rerun()

            with delete_tab:
                st.warning("本当に削除しますか？")
                if st.button("削除実行", type="primary", use_container_width=True):
                    current_df = load_reservations()
                    current_df = current_df.drop(idx).reset_index(drop=True)
                    save_reservations(current_df)
                    st.session_state["show_success_message"] = "削除しました"
                    _close()


# ==========================================
# ポップアップ表示制御
# ==========================================

if st.session_state["is_popup_open"]:
    if st.session_state["popup_mode"] == "new":
        entry_form_dialog("new", date_str=st.session_state.get("clicked_date", str(date.today())))
    elif st.session_state["popup_mode"] == "edit":
        e_idx = st.session_state.get("active_event_idx")
        if e_idx is not None:
            entry_form_dialog("edit", idx=e_idx)
