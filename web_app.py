"""Local Streamlit UI for Bazi Trading Agents."""

import os
import re
import tempfile
from datetime import date, datetime, time
from html import escape
from typing import Dict, List
from urllib.parse import urlparse

import streamlit as st

from bazi_graph import BaziAnalysisGraph
from env_loader import load_env_file
from utils.auth import authenticate_user, is_admin, register_user, user_count
from utils.exporter import build_export_filename, export_report_bytes, normalize_export_format
from utils.time_utils import current_analysis_date, current_analysis_datetime
from utils.visualization import build_visualization_data
from utils.public_access import PROVIDERS, analysis_slot, validate_request, MAX_QUESTION
from utils.web_support import (
    build_birth_info,
    build_dual_view,
    build_focus_notes,
    build_report_overview,
    extract_action_plan,
    extract_intermediate_reports,
    get_runtime_settings,
    load_analysis_history,
    sanitize_error,
    save_feedback,
)


CURRENT_RESULT_KEY = "current_analysis_result"
PAGE_KEY = "guanji_page"
FORM_KEY = "guanji_form"
TOPICS_KEY = "guanji_topics"
CUSTOM_QUESTION_KEY = "guanji_custom_question"
ALLOW_RECORD_KEY = "guanji_allow_record"
FEEDBACK_KEY = "guanji_feedback"
AUTH_USER_KEY = "guanji_auth_user"

TOPICS = [
    "性格与优势",
    "职业与发展",
    "情绪与压力",
    "人际与亲密关系",
    "当前阶段变化",
    "自定义问题",
]

PROGRESS_STEPS = [
    "正在计算基础结构",
    "正在分析性格倾向",
    "正在整理传统文化视角",
    "正在生成心理学视角",
    "正在进行交叉校验",
    "正在生成综合报告",
]

FEEDBACK_OPTIONS = [
    "符合我的情况",
    "部分准确",
    "内容过于笼统",
    "表述过于绝对",
    "建议不适用",
    "基础信息有误",
]

PAGE_FLOW = [
    ("welcome", "开始", "工具入口"),
    ("form", "出生信息", "建立分析基础"),
    ("topic", "关注主题", "确定洞察方向"),
    ("confirm", "确认提交", "检查输入内容"),
    ("report", "报告概览", "查看核心结论"),
    ("dual", "双视角", "传统与心理对照"),
    ("action", "行动反馈", "建议与结果反馈"),
]

RESULT_PAGES = {"report", "dual", "action"}


def main():
    load_env_file()
    st.set_page_config(page_title="观己", layout="wide")
    public_url = getattr(getattr(st, "context", None), "url", "") or ""
    parsed_url = urlparse(public_url)
    local_host = parsed_url.hostname in {"localhost", "127.0.0.1", "::1"}
    if (public_url and parsed_url.scheme != "https" and not local_host) or (
        os.environ.get("PUBLIC_MODE") == "1" and parsed_url.scheme != "https"
    ):
        st.error("公开访问必须使用 HTTPS。请配置 HTTPS 反向代理后再访问。")
        st.stop()
    init_session_state()
    apply_theme()

    if not get_current_user():
        render_auth_page()
        return

    render_sidebar_tools()

    page = st.session_state.get(PAGE_KEY, "welcome")
    if page == "welcome":
        render_welcome_page()
    elif page == "form":
        render_form_page()
    elif page == "topic":
        render_topic_page()
    elif page == "confirm":
        render_confirm_page()
    elif page == "report":
        render_report_page()
    elif page == "dual":
        render_dual_page()
    elif page == "action":
        render_action_page()
    else:
        st.session_state[PAGE_KEY] = "welcome"
        rerun_app()


def init_session_state():
    st.session_state.setdefault(PAGE_KEY, "welcome")
    st.session_state.setdefault(
        FORM_KEY,
        {
            "birth_date": "",
            "birth_time": "",
            "birth_place": "",
            "display_name": "",
            "gender": "",
            "calendar_type": "公历",
            "notes": "",
            "debug": False,
            "show_dev_info": False,
        },
    )
    st.session_state.setdefault(TOPICS_KEY, [])
    st.session_state.setdefault(CUSTOM_QUESTION_KEY, "")
    st.session_state.setdefault(ALLOW_RECORD_KEY, False)
    st.session_state.setdefault(FEEDBACK_KEY, "")
    st.session_state.setdefault(AUTH_USER_KEY, None)


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --bg: #F6F2EA;
            --panel: #FFFFFF;
            --panel-soft: #FBF9F5;
            --paper: #F7F3EA;
            --paper-deep: #EDE6D9;
            --ink: #26312C;
            --muted: #74766F;
            --line: #E3DED3;
            --green: #29483E;
            --green-hover: #203A32;
            --green-soft: #E8EFEA;
            --blue: #5D7483;
            --gold: #B68B45;
            --cinnabar: #9C4A3D;
            --danger: #A45A4E;
            --shadow: 0 16px 42px rgba(50, 44, 35, 0.08);
        }
        .stApp {
            background:
                repeating-linear-gradient(90deg, rgba(157,132,91,0.028) 0 1px, transparent 1px 34px),
                repeating-linear-gradient(0deg, rgba(157,132,91,0.02) 0 1px, transparent 1px 36px),
                radial-gradient(circle at top left, rgba(232,239,234,0.7), transparent 34rem),
                linear-gradient(180deg, #F8F5EF 0%, #F3F5F0 100%);
            color: var(--ink);
            font-family: "Inter", "Microsoft YaHei", "PingFang SC", sans-serif;
        }
        header[data-testid="stHeader"] {
            background: linear-gradient(180deg, #EFE8DC 0%, #E7E1D5 100%);
            border-bottom: 1px solid #D9CFBE;
            border-bottom-left-radius: 18px;
            border-bottom-right-radius: 18px;
            box-shadow: 0 10px 26px rgba(60, 48, 35, 0.08);
            overflow: hidden;
        }
        header[data-testid="stHeader"]::before {
            content: "";
            position: absolute;
            inset: 0;
            pointer-events: none;
            border-bottom-left-radius: 18px;
            border-bottom-right-radius: 18px;
            background:
                linear-gradient(90deg, rgba(41,72,62,0.08), transparent 18%, transparent 82%, rgba(182,139,69,0.08)),
                repeating-linear-gradient(90deg, rgba(157,132,91,0.08) 0 1px, transparent 1px 26px);
        }
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        h1, h2, h3 {
            color: var(--ink);
            letter-spacing: 0;
        }
        p, li {
            line-height: 1.75;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #FCFAF6 0%, #F1F4EE 100%);
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] > div:first-child {
            padding: 1.25rem 1rem 2rem;
        }
        [data-testid="stSidebar"] .stButton > button {
            min-height: 2.65rem;
            justify-content: flex-start;
            transition: all 120ms ease;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            transform: translateY(-1px);
        }
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background:
                linear-gradient(90deg, rgba(230,215,170,0.18), transparent 18%, transparent 82%, rgba(230,215,170,0.14)),
                repeating-linear-gradient(90deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 18px),
                linear-gradient(180deg, var(--green) 0%, #233F36 100%) !important;
            color: #FFFFFF !important;
            border-color: rgba(214,190,130,0.62) !important;
        }
        [data-testid="stSidebar"] .stTextInput input {
            border-radius: 8px;
            border-color: #DCD6CA;
            background: #FFFFFF;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255,255,255,0.62);
            box-shadow: none;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] details {
            border: 0;
        }
        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button,
        .stButton button[data-testid^="stBaseButton"],
        .stDownloadButton button[data-testid^="stBaseButton"],
        .stFormSubmitButton button[data-testid^="stBaseButton"] {
            position: relative;
            overflow: hidden;
            border-radius: 8px !important;
            border: 1px solid rgba(214,190,130,0.62) !important;
            background:
                linear-gradient(90deg, rgba(230,215,170,0.18), transparent 18%, transparent 82%, rgba(230,215,170,0.14)),
                repeating-linear-gradient(90deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 18px),
                linear-gradient(180deg, var(--green) 0%, #233F36 100%) !important;
            color: #FFFFFF !important;
            font-weight: 650 !important;
            letter-spacing: 0 !important;
            box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.12),
                inset 0 -1px 0 rgba(0,0,0,0.18),
                0 10px 22px rgba(41,72,62,0.18) !important;
            transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease !important;
        }
        .stFormSubmitButton {
            margin-top: 0.85rem;
        }
        .stButton > button::after,
        .stDownloadButton > button::after,
        .stFormSubmitButton > button::after {
            content: "";
            position: absolute;
            left: 0.65rem;
            right: 0.65rem;
            top: 0.34rem;
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent 0 7%,
                rgba(238,221,170,0.68) 7% 11%,
                transparent 11% 16%,
                rgba(238,221,170,0.76) 16% 84%,
                transparent 84% 89%,
                rgba(238,221,170,0.68) 89% 93%,
                transparent 93% 100%
            );
            pointer-events: none;
        }
        .stButton > button::before,
        .stDownloadButton > button::before,
        .stFormSubmitButton > button::before {
            content: "";
            position: absolute;
            left: 0.65rem;
            right: 0.65rem;
            bottom: 0.34rem;
            height: 1px;
            background: linear-gradient(
                90deg,
                transparent 0 7%,
                rgba(238,221,170,0.56) 7% 11%,
                transparent 11% 16%,
                rgba(238,221,170,0.64) 16% 84%,
                transparent 84% 89%,
                rgba(238,221,170,0.56) 89% 93%,
                transparent 93% 100%
            );
            pointer-events: none;
        }
        .stButton > button p,
        .stDownloadButton > button p,
        .stFormSubmitButton > button p {
            color: #FFFFFF !important;
        }
        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"],
        .stButton button[data-testid="stBaseButton-primary"],
        .stButton button[data-testid="stBaseButton-secondary"],
        .stDownloadButton button[data-testid="stBaseButton-primary"],
        .stDownloadButton button[data-testid="stBaseButton-secondary"],
        .stFormSubmitButton button[data-testid="stBaseButton-primary"],
        .stFormSubmitButton button[data-testid="stBaseButton-secondary"] {
            background:
                linear-gradient(90deg, rgba(230,215,170,0.18), transparent 18%, transparent 82%, rgba(230,215,170,0.14)),
                repeating-linear-gradient(90deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 18px),
                linear-gradient(180deg, var(--green) 0%, #233F36 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(214,190,130,0.62) !important;
            box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.12),
                inset 0 -1px 0 rgba(0,0,0,0.18),
                0 10px 22px rgba(41,72,62,0.18) !important;
        }
        .stButton > button[kind="primary"]:hover,
        .stFormSubmitButton > button[kind="primary"]:hover,
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover,
        .stButton button[data-testid="stBaseButton-primary"]:hover,
        .stButton button[data-testid="stBaseButton-secondary"]:hover,
        .stDownloadButton button[data-testid="stBaseButton-primary"]:hover,
        .stDownloadButton button[data-testid="stBaseButton-secondary"]:hover,
        .stFormSubmitButton button[data-testid="stBaseButton-primary"]:hover,
        .stFormSubmitButton button[data-testid="stBaseButton-secondary"]:hover {
            background:
                linear-gradient(90deg, rgba(230,215,170,0.22), transparent 18%, transparent 82%, rgba(230,215,170,0.18)),
                repeating-linear-gradient(90deg, rgba(255,255,255,0.045) 0 1px, transparent 1px 18px),
                linear-gradient(180deg, var(--green-hover) 0%, #1D342D 100%) !important;
            border-color: var(--green-hover) !important;
            color: #FFFFFF !important;
            transform: translateY(-1px);
            box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.14),
                inset 0 -1px 0 rgba(0,0,0,0.2),
                0 14px 26px rgba(41,72,62,0.22) !important;
        }
        .stButton > button[kind="primary"]:focus,
        .stFormSubmitButton > button[kind="primary"]:focus,
        .stButton > button:focus,
        .stDownloadButton > button:focus,
        .stFormSubmitButton > button:focus,
        .stButton button[data-testid="stBaseButton-primary"]:focus,
        .stButton button[data-testid="stBaseButton-secondary"]:focus,
        .stDownloadButton button[data-testid="stBaseButton-primary"]:focus,
        .stDownloadButton button[data-testid="stBaseButton-secondary"]:focus,
        .stFormSubmitButton button[data-testid="stBaseButton-primary"]:focus,
        .stFormSubmitButton button[data-testid="stBaseButton-secondary"]:focus {
            box-shadow: 0 0 0 0.18rem rgba(41,72,62,0.22) !important;
            color: #FFFFFF !important;
        }
        .stButton > button:disabled,
        .stDownloadButton > button:disabled,
        .stFormSubmitButton > button:disabled {
            background:
                repeating-linear-gradient(90deg, rgba(255,255,255,0.025) 0 1px, transparent 1px 18px),
                linear-gradient(180deg, #607168 0%, #53645C 100%) !important;
            color: rgba(255,255,255,0.72) !important;
            border-color: rgba(214,190,130,0.28) !important;
            box-shadow: none !important;
            transform: none !important;
        }
        [data-testid="stSidebar"] .stButton > button:not([kind="primary"]):not(:disabled),
        [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-secondary"]:not(:disabled) {
            background:
                linear-gradient(180deg, rgba(255,255,255,0.84), rgba(250,247,241,0.78)) !important;
            color: var(--ink) !important;
            border: 1px solid #E1DCD0 !important;
            box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.5),
                0 4px 10px rgba(50,44,35,0.04) !important;
            transform: none !important;
        }
        [data-testid="stSidebar"] .stButton > button:not([kind="primary"]):not(:disabled) p,
        [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-secondary"]:not(:disabled) p {
            color: var(--ink) !important;
        }
        [data-testid="stSidebar"] .stButton > button:not([kind="primary"]):not(:disabled)::after {
            background: linear-gradient(90deg, transparent, rgba(182,139,69,0.22), transparent);
        }
        [data-testid="stSidebar"] .stButton > button:not([kind="primary"]):not(:disabled):hover,
        [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-secondary"]:not(:disabled):hover {
            background:
                linear-gradient(180deg, rgba(244,249,246,0.92), rgba(235,242,237,0.88)) !important;
            color: var(--green) !important;
            border-color: rgba(41,72,62,0.38) !important;
            box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.55),
                0 6px 14px rgba(41,72,62,0.08) !important;
        }
        [data-testid="stSidebar"] .stButton > button:not([kind="primary"]):not(:disabled):hover p,
        [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-secondary"]:not(:disabled):hover p {
            color: var(--green) !important;
        }
        [data-testid="stSidebar"] .stButton > button[kind="primary"],
        [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] {
            background:
                linear-gradient(90deg, rgba(230,215,170,0.18), transparent 18%, transparent 82%, rgba(230,215,170,0.14)),
                repeating-linear-gradient(90deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 18px),
                linear-gradient(180deg, var(--green) 0%, #233F36 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(214,190,130,0.62) !important;
            box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.12),
                inset 0 -1px 0 rgba(0,0,0,0.18),
                0 10px 22px rgba(41,72,62,0.18) !important;
        }
        [data-testid="stSidebar"] .stButton > button[kind="primary"] p,
        [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] p {
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] .stButton > button:disabled {
            background:
                linear-gradient(180deg, rgba(246,243,236,0.72), rgba(237,232,222,0.68)) !important;
            color: rgba(116,118,111,0.62) !important;
            border-color: rgba(225,220,208,0.78) !important;
            box-shadow: none !important;
        }
        [data-testid="stSidebar"] .stButton > button:disabled p {
            color: rgba(116,118,111,0.72) !important;
        }
        .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
            border-radius: 8px;
        }
        .stAlert {
            border-radius: 8px;
        }
        .page-shell {
            max-width: 900px;
            margin: 0 auto;
            padding: 0;
            display: none;
        }
        .center-shell {
            max-width: 680px;
            margin: 0 auto;
            text-align: center;
        }
        .welcome-hero {
            max-width: 680px;
            margin: clamp(1rem, 5vh, 3rem) auto 1.1rem;
            text-align: center;
            padding: 0.5rem 0 0.2rem;
            position: relative;
        }
        .welcome-hero::before {
            content: "观\\A己";
            white-space: pre;
            position: absolute;
            right: -1.4rem;
            top: 0.65rem;
            width: 2.1rem;
            height: 3.2rem;
            border: 1px solid rgba(156,74,61,0.52);
            color: var(--cinnabar);
            background: rgba(255,253,248,0.68);
            border-radius: 7px;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1.2;
            font-family: "Noto Serif SC", "STSong", serif;
            font-size: 0.82rem;
            font-weight: 700;
            transform: rotate(-3deg);
        }
        .welcome-hero::after {
            content: "";
            display: block;
            width: 128px;
            height: 1px;
            margin: 1.05rem auto 0;
            background: linear-gradient(90deg, transparent, rgba(182,139,69,0.72), transparent);
        }
        .welcome-caption {
            text-align: center;
            color: var(--muted);
            font-size: 0.82rem;
            margin-top: 0.8rem;
        }
        .auth-shell {
            max-width: 520px;
            margin: clamp(2rem, 10vh, 5rem) auto 1rem;
            padding: 1.35rem 1.45rem;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.9), rgba(252,249,243,0.92)),
                repeating-linear-gradient(90deg, rgba(182,139,69,0.03) 0 1px, transparent 1px 18px);
            border: 1px solid var(--line);
            border-left: 4px solid var(--green);
            border-radius: 8px;
            box-shadow: var(--shadow);
        }
        .auth-shell h1 {
            margin: 0 0 0.35rem;
            font-family: "Noto Serif SC", "STSong", serif;
            font-size: 2rem;
        }
        .auth-shell p {
            color: var(--muted);
            margin: 0;
            font-size: 0.9rem;
        }
        .logo-mark {
            width: 72px;
            height: 72px;
            margin: 0 auto 1.5rem;
            border-radius: 8px;
            background: linear-gradient(145deg, #E7EFEA, #FFFFFF);
            color: var(--green);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            font-weight: 700;
            font-family: "Noto Serif SC", "STSong", serif;
            border: 1px solid #DDE7E0;
            box-shadow: 0 12px 28px rgba(41,72,62,0.12);
        }
        .serif-title {
            font-family: "Noto Serif SC", "STSong", serif;
            font-weight: 700;
            letter-spacing: 0;
        }
        .muted {
            color: var(--muted);
            font-size: 0.92rem;
        }
        .notice {
            background:
                linear-gradient(180deg, rgba(255,255,255,0.82), rgba(252,249,243,0.86)),
                repeating-linear-gradient(90deg, rgba(182,139,69,0.035) 0 1px, transparent 1px 18px);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.9rem 1.2rem;
            color: #706C65;
            font-size: 0.82rem;
            line-height: 1.7;
            box-shadow: 0 8px 20px rgba(50,44,35,0.05);
            margin-bottom: 1.25rem;
        }
        .step-text {
            color: var(--muted);
            font-size: 0.85rem;
            margin-top: -0.5rem;
            margin-bottom: 1.2rem;
        }
        .tag {
            display: inline-block;
            padding: 0.25rem 0.85rem;
            border-radius: 8px;
            margin: 0.15rem;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .tag-primary {
            background: var(--green);
            color: #FFFFFF;
        }
        .tag-secondary {
            background: #EEF1EE;
            color: #4E5650;
        }
        .soft-card {
            background: #FFFFFF;
            border-radius: 8px;
            padding: 1.15rem 1.25rem;
            border: 1px solid #E7E1D6;
            border-left: 4px solid var(--green);
            box-shadow: var(--shadow);
            margin-bottom: 0.9rem;
        }
        .soft-card p,
        .view-block p,
        .report-text,
        .action-card li {
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            word-break: break-word;
        }
        .soft-card h3 {
            font-size: 1.05rem;
            margin: 0 0 0.5rem;
        }
        .soft-card.gold {
            border-left-color: var(--gold);
            background: #FFFDF8;
        }
        .view-block {
            background: #FFFFFF;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.85rem;
            border: 1px solid #E7E1D6;
            border-left: 4px solid #E8E4DF;
            box-shadow: 0 10px 26px rgba(50,44,35,0.06);
        }
        .view-block.traditional {
            border-left-color: var(--green);
        }
        .view-block.psychology {
            border-left-color: var(--blue);
        }
        .view-block.shared {
            border-left-color: var(--gold);
            background: #FFFDF8;
        }
        .action-card {
            background: #FFFFFF;
            border: 1px solid #E7E1D6;
            border-left: 4px solid var(--gold);
            border-radius: 8px;
            padding: 1.05rem 1.2rem;
            margin: 0.9rem 0 1rem;
            box-shadow: 0 10px 26px rgba(50,44,35,0.06);
        }
        .action-card h3 {
            font-size: 1.08rem;
            margin: 0 0 0.65rem;
        }
        .action-card ul {
            margin: 0;
            padding-left: 1.25rem;
        }
        .action-list {
            margin: 0.15rem 0 0;
            padding-left: 1.25rem;
        }
        .action-card li {
            margin: 0.42rem 0;
            line-height: 1.75;
        }
        .action-list li {
            margin: 0.42rem 0;
            line-height: 1.75;
            white-space: normal;
            overflow-wrap: anywhere;
            word-break: break-word;
        }
        .nav-row {
            display: flex;
            gap: 0.6rem;
            justify-content: center;
            margin-top: 1.4rem;
            padding-top: 1rem;
            border-top: 1px solid var(--line);
        }
        .sidebar-brand {
            padding: 0.35rem 0.15rem 1rem;
            border-bottom: 1px solid var(--line);
            margin-bottom: 1rem;
        }
        .brand-row {
            display: flex;
            gap: 0.72rem;
            align-items: center;
        }
        .brand-mark {
            width: 44px;
            height: 44px;
            border-radius: 8px;
            background: var(--green);
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: "Noto Serif SC", "STSong", serif;
            font-weight: 700;
            font-size: 1.2rem;
            box-shadow: 0 10px 24px rgba(41,72,62,0.2);
        }
        .brand-title {
            font-family: "Noto Serif SC", "STSong", serif;
            font-weight: 700;
            font-size: 1.25rem;
            color: var(--ink);
            line-height: 1.1;
        }
        .brand-subtitle {
            color: var(--muted);
            font-size: 0.78rem;
            margin-top: 0.12rem;
        }
        .sidebar-section-title {
            color: #596158;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin: 1.05rem 0 0.45rem;
            text-transform: uppercase;
        }
        .sidebar-note {
            color: var(--muted);
            font-size: 0.78rem;
            line-height: 1.6;
            margin: 0.15rem 0 0.65rem;
        }
        .sidebar-mini-card {
            background: rgba(255,255,255,0.68);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.72rem 0.78rem;
            margin-bottom: 0.55rem;
        }
        .sidebar-mini-card strong {
            display: block;
            color: var(--ink);
            font-size: 0.82rem;
            margin-bottom: 0.2rem;
        }
        .sidebar-mini-card span {
            color: var(--muted);
            font-size: 0.78rem;
            line-height: 1.55;
        }
        .sidebar-chip {
            display: inline-block;
            margin: 0.12rem 0.12rem 0.12rem 0;
            padding: 0.18rem 0.48rem;
            border-radius: 8px;
            background: var(--green-soft);
            color: var(--green);
            font-size: 0.74rem;
            font-weight: 600;
        }
        .setting-row {
            display: flex;
            justify-content: space-between;
            gap: 0.6rem;
            padding: 0.34rem 0;
            border-bottom: 1px solid rgba(227,222,211,0.7);
            font-size: 0.78rem;
        }
        .setting-row:last-child {
            border-bottom: 0;
        }
        .setting-key {
            color: var(--muted);
        }
        .setting-value {
            color: var(--ink);
            font-weight: 600;
            text-align: right;
            overflow-wrap: anywhere;
        }
        .quality-pill {
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 8px;
            background: #EEF3F5;
            color: var(--blue);
            font-size: 0.74rem;
            font-weight: 700;
        }
        .mini-divider {
            height: 1px;
            background: var(--line);
            margin: 0.9rem 0 0.75rem;
        }
        @media (max-width: 760px) {
            .welcome-hero::before {
                display: none;
            }
            header[data-testid="stHeader"] {
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_page():
    st.markdown(
        """
        <div class="welcome-hero">
            <div class="logo-mark">观</div>
            <h1 class="serif-title" style="font-size:3rem;margin-bottom:0.25rem;text-align:center;">观己</h1>
            <p class="muted" style="text-align:center;margin-bottom:1.1rem;">从传统文化与心理学两个视角，重新理解自己</p>
            <div class="notice">内容仅供文化解读与自我观察参考，不构成心理诊断、医疗建议或重大决策依据。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 1.3, 1])
    with center:
        if st.button("开始分析", type="primary", use_container_width=True):
            switch_page("form")

    spacer, col1, col2, spacer2 = st.columns([1, 0.65, 0.65, 1])
    with col1:
        if st.button("使用说明", use_container_width=True):
            st.session_state["info_panel"] = "usage"
    with col2:
        if st.button("隐私说明", use_container_width=True):
            st.session_state["info_panel"] = "privacy"
    render_info_panel()
    st.markdown('<div class="welcome-caption">个人洞察工具 v1.0</div>', unsafe_allow_html=True)


def render_auth_page():
    st.markdown(
        """
        <div class="auth-shell">
            <h1>观己</h1>
            <p>请登录后继续。每个账号只能查看自己的分析记录。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["登录", "注册"])
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("用户名", key="login_username")
            password = st.text_input("密码", type="password", key="login_password")
            submitted = st.form_submit_button("登录", type="primary")
        if submitted:
            try:
                st.session_state[AUTH_USER_KEY] = authenticate_user(username, password)
                switch_page("welcome")
            except Exception as exc:
                st.error(sanitize_error(exc))

    with register_tab:
        with st.form("register_form"):
            username = st.text_input("用户名", key="register_username", help="2-32 位中文、字母、数字、下划线或短横线")
            password = st.text_input("密码", type="password", key="register_password")
            confirm_password = st.text_input("确认密码", type="password", key="register_password_confirm")
            admin_token = (
                st.text_input("管理员邀请码（普通用户留空）", type="password")
                if user_count() == 0 and os.environ.get("INITIAL_ADMIN_TOKEN") else ""
            )
            submitted = st.form_submit_button("注册并登录", type="primary")
        if submitted:
            if password != confirm_password:
                st.error("两次输入的密码不一致")
            else:
                try:
                    st.session_state[AUTH_USER_KEY] = register_user(username, password, admin_token=admin_token)
                    switch_page("welcome")
                except Exception as exc:
                    st.error(sanitize_error(exc))


def render_info_panel():
    panel = st.session_state.get("info_panel")
    if panel == "usage":
        st.info(
            "1. 提供出生信息，建立基础分析框架。\n\n"
            "2. 选择关注主题，系统从传统文化与心理学双视角进行交叉分析。\n\n"
            "3. 分析结果仅供自我观察参考，不构成任何重大决策依据。"
        )
    elif panel == "privacy":
        st.info(
            "API Key 会经由本站服务器发送到所选模型服务商；本站不保存 Key，也不将其写入分析记录或日志。"
            "分析记录默认关闭。出生资料和分析内容仍会发送给所选服务商以生成报告。"
        )


def render_form_page():
    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    st.markdown('<h2 class="serif-title">填写出生信息</h2>', unsafe_allow_html=True)
    st.markdown('<div class="step-text">Step 1 of 3</div>', unsafe_allow_html=True)
    form_state = st.session_state[FORM_KEY]

    with st.form("birth_info_form"):
        col1, col2 = st.columns(2)
        with col1:
            birth_date_value = st.date_input(
                "出生日期",
                value=_parse_date(form_state.get("birth_date", "")),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
            )
        with col2:
            birth_time_value = st.time_input(
                "出生时间",
                value=_parse_time(form_state.get("birth_time", "")),
                step=300,
            )
        birth_place = st.text_input("出生地点", value=form_state.get("birth_place", ""), placeholder="省/市/县", max_chars=100)
        display_name = st.text_input("称谓", value=form_state.get("display_name", ""), placeholder="如：昵称、名字", max_chars=50)
        col3, col4 = st.columns(2)
        with col3:
            gender = st.selectbox("性别", ["", "男", "女", "其他/不提供"], index=_select_index(["", "男", "女", "其他/不提供"], form_state.get("gender", "")))
        with col4:
            calendar_type = st.selectbox("历法", ["公历", "农历", "不确定"], index=_select_index(["公历", "农历", "不确定"], form_state.get("calendar_type", "公历")))
        notes = st.text_input("补充说明", value=form_state.get("notes", ""), placeholder="可补充时辰不确定、城市时区等信息", max_chars=250)
        if current_user_is_admin():
            debug = st.checkbox("开启调试信息", value=bool(form_state.get("debug", False)))
            show_dev_info = st.checkbox("显示开发信息", value=bool(form_state.get("show_dev_info", False)))
        else:
            debug = False
            show_dev_info = False

        submitted = st.form_submit_button("下一步", type="primary")

    if submitted:
        st.session_state[FORM_KEY] = {
            "birth_date": birth_date_value.isoformat(),
            "birth_time": birth_time_value.strftime("%H:%M"),
            "birth_place": birth_place.strip(),
            "display_name": display_name.strip(),
            "gender": gender,
            "calendar_type": calendar_type,
            "notes": notes.strip(),
            "debug": debug,
            "show_dev_info": show_dev_info,
        }
        switch_page("topic")

    st.markdown("</div>", unsafe_allow_html=True)


def render_topic_page():
    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    st.markdown('<h2 class="serif-title">选择你关注的主题</h2>', unsafe_allow_html=True)
    st.markdown('<div class="step-text">Step 2 of 3（可多选）</div>', unsafe_allow_html=True)

    selected = set(st.session_state.get(TOPICS_KEY, []))
    cols = st.columns(3)
    for index, topic in enumerate(TOPICS):
        with cols[index % 3]:
            checked = st.checkbox(topic, value=topic in selected, key=f"topic_{topic}")
            if checked:
                selected.add(topic)
            else:
                selected.discard(topic)
    st.session_state[TOPICS_KEY] = [topic for topic in TOPICS if topic in selected]

    if "自定义问题" in selected:
        st.session_state[CUSTOM_QUESTION_KEY] = st.text_area(
            "自定义问题",
            value=st.session_state.get(CUSTOM_QUESTION_KEY, ""),
            placeholder="写下你最想理解的问题",
            height=90,
            max_chars=MAX_QUESTION,
        )

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("返回修改", use_container_width=True):
            switch_page("form")
    with col2:
        if st.button("下一步", type="primary", disabled=not bool(selected), use_container_width=True):
            switch_page("confirm")
    st.markdown("</div>", unsafe_allow_html=True)


def render_confirm_page():
    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    st.markdown('<h2 class="serif-title">确认你的信息</h2>', unsafe_allow_html=True)
    st.markdown('<div class="step-text">Step 3 of 3</div>', unsafe_allow_html=True)

    form_state = st.session_state[FORM_KEY]
    focus_topics = st.session_state.get(TOPICS_KEY, [])
    notes = build_focus_notes(focus_topics, st.session_state.get(CUSTOM_QUESTION_KEY, ""))
    birth_info = build_birth_info(
        birth_date=form_state.get("birth_date", ""),
        birth_time=form_state.get("birth_time", ""),
        gender=form_state.get("gender", ""),
        birth_place=form_state.get("birth_place", ""),
        calendar_type=form_state.get("calendar_type", ""),
        notes="；".join(part for part in [form_state.get("notes", ""), notes] if part),
        display_name=form_state.get("display_name", ""),
    )

    with st.container():
        st.write(f"**出生日期**：{form_state.get('birth_date') or '未填写'}")
        st.write(f"**出生时间**：{form_state.get('birth_time') or '未填写'}")
        st.write(f"**出生地点**：{form_state.get('birth_place') or '未填写'}")
        st.write(f"**称谓**：{form_state.get('display_name') or '未填写'}")
        st.write(f"**关注主题**：{'、'.join(focus_topics) if focus_topics else '未选择'}")

    st.session_state[ALLOW_RECORD_KEY] = st.checkbox(
        "允许记录本次分析结果",
        value=bool(st.session_state.get(ALLOW_RECORD_KEY, False)),
    )
    provider = st.selectbox(
        "模型服务商",
        list(PROVIDERS),
        format_func=lambda name: f"{PROVIDERS[name][0]} · {PROVIDERS[name][1]}",
    )
    api_key = st.text_input("你的 API Key", type="password", max_chars=512)
    st.caption("Key 会通过本站服务器发送到所选模型服务商，仅用于本次分析；本站不保存 Key，也不写入日志或分析记录。出生资料也会发送给该服务商。")
    st.markdown(
        '<div class="notice">分析结果基于传统文化与心理学视角生成，仅供自我观察参考。请勿将其作为医疗、法律、投资或重大人生决策依据。</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("返回修改", use_container_width=True):
            switch_page("topic")
    with col2:
        if st.button("开始分析", type="primary", use_container_width=True):
            if not birth_info.strip():
                st.warning("请至少填写一项出生信息。")
            else:
                try:
                    validate_request(provider, api_key, birth_info, st.session_state.get(CUSTOM_QUESTION_KEY, ""))
                except ValueError as exc:
                    st.warning(str(exc))
                else:
                    run_real_analysis(birth_info, focus_topics, provider, api_key)
    st.markdown("</div>", unsafe_allow_html=True)


def run_real_analysis(birth_info: str, focus_topics: List[str], provider: str, api_key: str):
    st.session_state[PAGE_KEY] = "progress"
    render_progress_header()

    progress_bar = st.progress(0)
    status_box = st.empty()
    steps_box = st.empty()
    progress_events: List[Dict[str, str]] = []

    def progress_callback(stage, message, _state):
        progress_events.append({"stage": stage, "message": message})
        progress_value = min(len(progress_events), len(PROGRESS_STEPS)) / len(PROGRESS_STEPS)
        progress_bar.progress(progress_value)
        status_box.info(f"{stage}：{message}")
        steps_box.markdown(_progress_markdown(len(progress_events)))

    try:
        progress_bar.progress(0.05)
        status_box.info(PROGRESS_STEPS[0])
        steps_box.markdown(_progress_markdown(0))

        form_state = st.session_state[FORM_KEY]
        analysis_datetime = current_analysis_datetime()
        analysis_date = analysis_datetime.split("T", 1)[0] or current_analysis_date()
        user_id = get_current_user().get("user_id", "")
        # The existing chart calculator also calls an LLM. It cannot make a
        # reliable four-pillar chart without a key, so no fake free chart is shown.
        with analysis_slot(user_id), tempfile.TemporaryDirectory() as tmpdir:
            settings = get_runtime_settings()
            results_dir = settings["results_dir"] if st.session_state.get(ALLOW_RECORD_KEY, False) else tmpdir
            config = _temporary_graph_config(results_dir)
            config["memory_dir"] = os.path.join(tmpdir, "memory")
            config["embedding_enabled"] = False
            config["quality_rewrite_enabled"] = False
            config["quality_llm_judge_enabled"] = False
            _, model, base_url = PROVIDERS[provider]
            graph = BaziAnalysisGraph(
                debug=False, config=config, llm_provider=provider,
                llm_model=model, base_url=base_url, api_key=api_key,
            )
            try:
                final_state, final_analysis = graph.analyze(
                    birth_info,
                    analysis_date=analysis_date,
                    analysis_datetime=analysis_datetime,
                    progress_callback=progress_callback,
                    case_metadata=_analysis_case_metadata(focus_topics),
                )
            finally:
                # Do not retain a client that holds the visitor's key.
                del graph

        final_state["focus_topics"] = focus_topics
        final_state["display_name"] = form_state.get("display_name", "")
        final_state["allow_record"] = bool(st.session_state.get(ALLOW_RECORD_KEY, False))
        final_state["user_id"] = get_current_user().get("user_id", "")
        final_state["username"] = get_current_user().get("username", "")
        progress_bar.progress(1.0)
        status_box.success("综合报告生成完成")
        steps_box.markdown(_progress_markdown(len(PROGRESS_STEPS)))

        st.session_state[CURRENT_RESULT_KEY] = {
            "final_state": final_state,
            "final_analysis": final_analysis,
            "focus_topics": focus_topics,
            "birth_info": birth_info,
            "show_dev_info": bool(form_state.get("show_dev_info", False)),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        st.session_state[PAGE_KEY] = "report"
        rerun_app()
    except Exception as exc:
        status_box.error("分析失败")
        # Provider exception strings can contain arbitrary request data or keys.
        st.error("分析失败。请检查 API Key、服务商余额和网络连接后重试。")
        if st.button("返回确认页"):
            switch_page("confirm")


def render_progress_header():
    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    st.markdown('<h2 class="serif-title">正在为你生成分析报告</h2>', unsafe_allow_html=True)
    st.caption("请保持页面打开，系统会根据真实分析阶段更新进度。")
    st.markdown("</div>", unsafe_allow_html=True)


def render_report_page():
    result = get_current_result()
    if not result:
        switch_page("welcome")
        return

    final_state = result["final_state"]
    final_analysis = result["final_analysis"]
    focus_topics = result.get("focus_topics", [])
    display_state = final_state if current_user_is_admin() else public_final_state(final_state)
    overview = build_report_overview(display_state, final_analysis, focus_topics)

    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    st.markdown('<h2 class="serif-title">你的洞察报告</h2>', unsafe_allow_html=True)
    for index, tag in enumerate(overview["tags"]):
        cls = "tag-primary" if index == 0 else "tag-secondary"
        st.markdown(f'<span class="tag {cls}">{tag}</span>', unsafe_allow_html=True)

    st.write("")
    for card in overview["cards"]:
        render_text_card(card["title"], card["content"])

    render_action_summary_card(overview["top_actions"])

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("双视角分析", use_container_width=True):
            switch_page("dual")
    with col2:
        if st.button("行动与反馈", use_container_width=True):
            switch_page("action")
    with col3:
        with st.expander("完整报告", expanded=False):
            st.markdown(final_analysis)
            render_export_controls(display_state, key_prefix="current_analysis")
    render_result_nav("report")
    render_developer_info(final_state, result)
    st.markdown("</div>", unsafe_allow_html=True)


def render_dual_page():
    result = get_current_result()
    if not result:
        switch_page("welcome")
        return

    dual = build_dual_view(
        result["final_state"] if current_user_is_admin() else public_final_state(result["final_state"]),
        result["final_analysis"],
        result.get("focus_topics", []),
    )
    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    st.markdown('<h2 class="serif-title">双视角分析</h2>', unsafe_allow_html=True)
    st.caption("以下从传统文化与心理学两个维度交叉分析，帮助你更全面地理解自己。")
    st.markdown(f"### {dual['title']}")
    render_view_block("traditional", "传统文化视角", dual["traditional"])
    render_view_block("psychology", "心理学视角", dual["psychology"])
    render_view_block("shared", "共享观察", dual["shared"])
    st.info("差异说明：" + dual["difference"])
    st.warning("反思：" + dual["reflection"])
    render_result_nav("dual")
    st.markdown("</div>", unsafe_allow_html=True)


def render_action_page():
    result = get_current_result()
    if not result:
        switch_page("welcome")
        return

    actions = extract_action_plan(result["final_analysis"])
    st.markdown('<div class="page-shell">', unsafe_allow_html=True)
    st.markdown('<h2 class="serif-title">行动建议与反馈</h2>', unsafe_allow_html=True)
    render_action_group("今天可以尝试", actions["today"])
    render_action_group("一周内可以观察", actions["week"])
    render_action_group("长期可以记录", actions["long_term"])

    st.divider()
    st.subheader("这份分析是否符合你的情况？")
    feedback_choice = st.selectbox("选择反馈", ["请选择"] + FEEDBACK_OPTIONS)
    feedback = "" if feedback_choice == "请选择" else feedback_choice
    if st.button("提交反馈", type="primary", disabled=not feedback):
        feedback_path = submit_feedback(feedback, result)
        if feedback_path:
            st.success(f"感谢你的反馈，已记录到：{feedback_path}")
        else:
            st.success("感谢你的反馈。本次设置为不记录分析结果，反馈仅保存在当前会话。")
    render_result_nav("action")
    st.markdown("</div>", unsafe_allow_html=True)


def render_text_card(title: str, content: str, class_name: str = "soft-card"):
    st.markdown(
        f"""
        <div class="{escape(class_name)}">
            <h3>{escape(title)}</h3>
            <p class="report-text">{_html_text(content)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_summary_card(items: List[str]):
    st.markdown(
        f"""
        <div class="soft-card gold">
            <h3>三条行动建议</h3>
            <ul class="action-list">{_html_list(items)}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_view_block(kind: str, title: str, content: str):
    safe_kind = kind if kind in {"traditional", "psychology", "shared"} else "shared"
    st.markdown(
        f"""
        <div class="view-block {safe_kind}">
            <b>{escape(title)}</b>
            <p class="report-text">{_html_text(content)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_action_group(title: str, items: List[str]):
    st.markdown(
        f"""
        <div class="action-card">
            <h3>{escape(title)}</h3>
            <ul>{_html_list(items)}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def submit_feedback(feedback: str, result: Dict[str, object]) -> str:
    st.session_state[FEEDBACK_KEY] = feedback
    final_state = result.get("final_state") or {}
    allow_record = bool(final_state.get("allow_record", True))
    if not allow_record:
        return ""

    settings = get_runtime_settings()
    payload = {
        "case_id": result.get("created_at", "").replace(":", "").replace("-", ""),
        "feedback": feedback,
        "focus_topics": result.get("focus_topics", []),
        "birth_info": result.get("birth_info", ""),
        "analysis_date": final_state.get("analysis_date", ""),
        "quality_score": (final_state.get("quality_report") or {}).get("overall_score"),
    }
    return save_feedback(settings["results_dir"], payload)


def render_result_nav(active: str):
    st.markdown('<div class="nav-row">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("报告概览", disabled=active == "report", use_container_width=True, on_click=lambda: set_page("report"))
    with col2:
        st.button("双视角", disabled=active == "dual", use_container_width=True, on_click=lambda: set_page("dual"))
    with col3:
        st.button("行动计划", disabled=active == "action", use_container_width=True, on_click=lambda: set_page("action"))
    st.markdown("</div>", unsafe_allow_html=True)


def render_export_controls(final_state, key_prefix="export"):
    admin = current_user_is_admin()
    if admin:
        mode = st.radio(
            "导出模式",
            ["simple", "professional"],
            format_func=lambda item: "简版" if item == "simple" else "专业版",
            horizontal=True,
            key=f"{key_prefix}_export_mode",
        )
        formats = ["markdown", "json", "word", "pdf"]
        export_state = final_state
    else:
        mode = "simple"
        formats = ["markdown", "word", "pdf"]
        export_state = public_final_state(final_state)
        st.caption("普通用户仅支持简版导出，不包含中间分析、质量评分或原始 JSON。")
    labels = {
        "markdown": "下载 Markdown",
        "json": "下载 JSON",
        "word": "下载 Word",
        "pdf": "下载 PDF",
    }
    mimes = {
        "markdown": "text/markdown",
        "json": "application/json",
        "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
    }
    cols = st.columns(len(formats))
    for col, export_format in zip(cols, formats):
        with col:
            try:
                _canonical, ext = normalize_export_format(export_format)
                data = export_report_bytes(export_state, export_format, mode=mode)
                st.download_button(
                    labels[export_format],
                    data=data,
                    file_name=build_export_filename(export_state, ext=ext, mode=mode),
                    mime=mimes[export_format],
                    key=f"{key_prefix}_download_{export_format}",
                )
            except Exception as exc:
                st.caption(f"{labels[export_format]}: {sanitize_error(exc)}")


def render_developer_info(final_state: Dict[str, object], result: Dict[str, object]):
    if not current_user_is_admin() or not result.get("show_dev_info"):
        return
    with st.expander("开发信息", expanded=False):
        st.json(
            {
                "focus_topics": result.get("focus_topics", []),
                "quality_report": final_state.get("quality_report"),
                "visualization_data": final_state.get("visualization_data") or build_visualization_data(final_state),
            }
        )
        reports = extract_intermediate_reports(final_state)
        for report in reports:
            with st.expander(report["title"], expanded=False):
                st.markdown(report["content"])


def render_sidebar_brand():
    user = get_current_user() or {}
    role_label = "管理员" if current_user_is_admin() else "普通用户"
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="brand-row">
                <div class="brand-mark">观</div>
                <div>
                    <div class="brand-title">观己</div>
                    <div class="brand-subtitle">{escape(user.get("username", ""))} · {role_label}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_nav():
    current_page = st.session_state.get(PAGE_KEY, "welcome")
    has_result = bool(get_current_result())

    st.markdown('<div class="sidebar-section-title">流程导航</div>', unsafe_allow_html=True)
    for page, title, description in PAGE_FLOW:
        disabled = page in RESULT_PAGES and not has_result
        prefix = "当前" if current_page == page else ("未生成" if disabled else "进入")
        button_type = "primary" if current_page == page else "secondary"
        label = f"{prefix} · {title}｜{description}"
        if st.button(
            label,
            key=f"sidebar_nav_{page}",
            disabled=disabled,
            type=button_type,
            use_container_width=True,
        ):
            switch_page(page)


def render_sidebar_session():
    result = get_current_result()
    form_state = st.session_state.get(FORM_KEY, {})
    birth_summary = _compact_text(_build_form_summary(form_state), 68) or "尚未填写出生信息"
    topics = st.session_state.get(TOPICS_KEY, [])
    allow_record = "会保存结果" if st.session_state.get(ALLOW_RECORD_KEY, False) else "仅本次会话"

    st.markdown('<div class="sidebar-section-title">当前会话</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="sidebar-mini-card">
            <strong>输入状态</strong>
            <span>{escape(birth_summary)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if topics:
        chips = "".join(f'<span class="sidebar-chip">{escape(topic)}</span>' for topic in topics)
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-note">还没有选择关注主题。</div>', unsafe_allow_html=True)

    if result:
        final_state = result.get("final_state") or {}
        quality_report = final_state.get("quality_report") or {}
        score = _format_quality_score(quality_report.get("overall_score"))
        analysis_date = final_state.get("analysis_date") or result.get("created_at", "")
        score_html = f'<span class="quality-pill">质量评分 {escape(score)}</span>' if current_user_is_admin() else ""
        st.markdown(
            f"""
            <div class="sidebar-mini-card">
                <strong>报告状态</strong>
                <span>已生成 · {escape(str(analysis_date) or "未记录日期")}</span><br>
                {score_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="sidebar-mini-card">
                <strong>报告状态</strong>
                <span>尚未生成 · {escape(allow_record)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar_history():
    settings = get_runtime_settings()
    with st.expander("最近记录", expanded=False):
        query = st.text_input("搜索记录", "", placeholder="日期、出生信息或模型", key="sidebar_history_query")
        records = load_visible_history(settings["results_dir"], query=query, limit=8)
        if not records:
            st.caption("暂无匹配记录")
            return

        for index, record in enumerate(records):
            date_text = record.get("analysis_date") or "未知日期"
            birth_text = _compact_text(record.get("birth_info") or record.get("file_name"), 34)
            button_label = f"{date_text} · {birth_text}"
            if st.button(button_label, key=f"history_{index}_{record['file_name']}", use_container_width=True):
                payload = record.get("payload", {})
                st.session_state[CURRENT_RESULT_KEY] = {
                    "final_state": payload,
                    "final_analysis": payload.get("final_analysis", ""),
                    "focus_topics": payload.get("focus_topics", []),
                    "birth_info": payload.get("birth_info", ""),
                    "show_dev_info": current_user_is_admin(),
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                }
                switch_page("report")

            meta = []
            if record.get("quality_score") is not None:
                meta.append(f"质量 {record['quality_score']}")
            if record.get("llm_model"):
                meta.append(str(record["llm_model"]))
            if meta:
                st.caption(" | ".join(meta))


def render_sidebar_settings():
    settings = get_runtime_settings()
    rows = [
        ("模型", "由本次分析选择"),
        ("API Key", "由用户本次提供，不保存"),
        ("记忆目录", settings["memory_dir"]),
        ("结果目录", settings["results_dir"]),
    ]

    with st.expander("运行设置", expanded=False):
        rows_html = []
        for key, value in rows:
            rows_html.append(
                f"""
                <div class="setting-row">
                    <span class="setting-key">{escape(str(key))}</span>
                    <span class="setting-value">{escape(_compact_text(value, 42))}</span>
                </div>
                """
            )
        st.markdown(
            f'<div class="sidebar-mini-card">{"".join(rows_html)}</div>',
            unsafe_allow_html=True,
        )
        st.caption("API Key 仅用于当前分析，不显示或保存。")


def render_sidebar_tools():
    with st.sidebar:
        render_sidebar_brand()
        render_sidebar_nav()
        render_sidebar_session()
        if st.button("重新开始", key="sidebar_reset", use_container_width=True):
            reset_current_flow()
        if st.button("退出登录", key="sidebar_logout", use_container_width=True):
            logout_current_user()
        st.markdown('<div class="mini-divider"></div>', unsafe_allow_html=True)
        render_sidebar_history()
        render_sidebar_settings()


def _build_form_summary(form_state: Dict[str, object]) -> str:
    parts = [
        form_state.get("display_name"),
        form_state.get("birth_date"),
        form_state.get("birth_time"),
        form_state.get("birth_place"),
    ]
    return " · ".join(str(part).strip() for part in parts if str(part or "").strip())


def _compact_text(value: object, limit: int = 48) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _format_quality_score(score: object) -> str:
    if score is None:
        return "未生成"
    try:
        return f"{float(score):.1f}"
    except (TypeError, ValueError):
        return str(score)


def _format_api_status(api_keys: Dict[str, object]) -> str:
    configured = [key.replace("_API_KEY", "") for key, enabled in api_keys.items() if enabled]
    if not configured:
        return "未配置"
    return "已配置 " + "、".join(configured)


def get_current_user() -> Dict[str, object]:
    return st.session_state.get(AUTH_USER_KEY) or {}


def current_user_is_admin() -> bool:
    return is_admin(get_current_user())


def logout_current_user():
    for key in (CURRENT_RESULT_KEY, FEEDBACK_KEY, "info_panel"):
        st.session_state.pop(key, None)
    st.session_state[AUTH_USER_KEY] = None
    st.session_state[PAGE_KEY] = "welcome"
    rerun_app()


def _analysis_case_metadata(focus_topics: List[str]) -> Dict[str, object]:
    user = get_current_user()
    form_state = st.session_state.get(FORM_KEY, {})
    return {
        "user_id": user.get("user_id", ""),
        "username": user.get("username", ""),
        "focus_topics": focus_topics,
        "display_name": form_state.get("display_name", ""),
        "allow_record": bool(st.session_state.get(ALLOW_RECORD_KEY, False)),
    }


def load_visible_history(results_dir: str, query: str = "", limit: int = 8) -> List[Dict[str, object]]:
    user = get_current_user()
    user_id = str(user.get("user_id") or "")
    return load_analysis_history(results_dir, query=query, limit=limit, user_id=user_id)


def public_final_state(final_state: Dict[str, object]) -> Dict[str, object]:
    return {
        "birth_info": final_state.get("birth_info", ""),
        "analysis_date": final_state.get("analysis_date", ""),
        "analysis_datetime": final_state.get("analysis_datetime", ""),
        "final_analysis": final_state.get("final_analysis", ""),
        "focus_topics": final_state.get("focus_topics", []),
        "display_name": final_state.get("display_name", ""),
        "user_id": final_state.get("user_id", ""),
        "username": final_state.get("username", ""),
    }


def _parse_date(value: object) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception:
        return date(1995, 6, 15)


def _parse_time(value: object) -> time:
    if isinstance(value, time):
        return value
    for pattern in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(str(value), pattern).time()
        except Exception:
            continue
    return time(10, 30)


def _html_text(value: object) -> str:
    text = str(value or "").strip()
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = text.replace("**", "").replace("__", "").replace("`", "")
    text = re.sub(r"(?m)^[-*•]\s+", "· ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if not text:
        return "暂无内容。"
    return "<br>".join(escape(line) for line in text.splitlines())


def _html_list(items: List[str]) -> str:
    cleaned_items = []
    for item in items or []:
        text = str(item or "").strip()
        text = re.sub(r"^[-*•\d.、\s]+", "", text)
        text = text.replace("**", "").replace("__", "").replace("`", "")
        if text:
            cleaned_items.append(f"<li>{escape(text)}</li>")
    if not cleaned_items:
        cleaned_items.append("<li>暂无明确建议，请查看完整报告。</li>")
    return "".join(cleaned_items)


def get_current_result():
    return st.session_state.get(CURRENT_RESULT_KEY)


def switch_page(page: str):
    st.session_state[PAGE_KEY] = page
    rerun_app()


def set_page(page: str):
    st.session_state[PAGE_KEY] = page


def reset_current_flow():
    for key in (CURRENT_RESULT_KEY, FEEDBACK_KEY, "info_panel"):
        st.session_state.pop(key, None)
    st.session_state[TOPICS_KEY] = []
    st.session_state[CUSTOM_QUESTION_KEY] = ""
    st.session_state[ALLOW_RECORD_KEY] = False
    st.session_state[PAGE_KEY] = "welcome"
    rerun_app()


def rerun_app():
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun is not None:
        rerun()


def _progress_markdown(done_count: int) -> str:
    lines = []
    for index, step in enumerate(PROGRESS_STEPS, 1):
        if index <= done_count:
            status = "已完成"
        elif index == done_count + 1:
            status = "进行中"
        else:
            status = "待开始"
        lines.append(f"{index}. {status} - {step}")
    return "\n\n".join(lines)


def _temporary_graph_config(results_dir: str) -> Dict[str, object]:
    settings = get_runtime_settings()
    return {
        "memory_dir": settings["memory_dir"],
        "results_dir": results_dir,
        "max_debate_rounds": int(os.environ.get("MAX_DEBATE_ROUNDS", "3")),
        "prompt_version": os.environ.get("PROMPT_VERSION", "phase2-prompt-v1"),
        "quality_min_score": float(os.environ.get("QUALITY_MIN_SCORE", "70")),
        "quality_rewrite_enabled": os.environ.get("QUALITY_REWRITE_ENABLED", "false"),
        "quality_llm_judge_enabled": os.environ.get("QUALITY_LLM_JUDGE_ENABLED", "false"),
    }


def _select_index(options: List[str], value: str) -> int:
    try:
        return options.index(value)
    except ValueError:
        return 0


if __name__ == "__main__":
    main()
