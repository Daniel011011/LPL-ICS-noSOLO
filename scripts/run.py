#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_and_process_ics.py

直接运行：
    python fetch_and_process_ics.py

依赖：
    pip install requests icalendar
"""

import requests
from icalendar import Calendar
from datetime import datetime

# === 配置区域 ===
ICS_URLS = [
    "https://raw.githubusercontent.com/TankNee/LOL_Game_Subscription/refs/heads/master/2025_lpl/2025_lpl.ics",
    "https://raw.githubusercontent.com/TankNee/LOL_Game_Subscription/refs/heads/master/2025_msi/2025_msi.ics",
    "https://raw.githubusercontent.com/TankNee/LOL_Game_Subscription/refs/heads/master/2025_lpl/2026_lpl.ics",
    # 以后你只需要在这里继续添加 ICS 链接
]
LCK_ICS_URL = "https://raw.githubusercontent.com/ChengLuffy/lpl.ics/refs/heads/master/LCK2025.ics"
OUTPUT_FILE = "calendarIOS.ics"
LCK_OUTPUT_FILE = "calendarIOS-LCK.ics"
FILTER_KEYWORD = "SOLO选边"
EVENT_URL = "bilibili://live/6"
LCK_EVENT_URL = "bilibili://live/6"
# =================


def fetch_ics(url):
    """下载并返回 Calendar 对象"""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return Calendar.from_ical(resp.content)
    except Exception as e:
        print(f"ERROR: 无法拉取 {url} → {e}")
        return None


def process_calendar(urls, output_file, event_url):
    """处理日历并保存到指定文件"""
    merged_cal = Calendar()
    merged_cal.add('prodid', '-//Merged ICS Calendar//')
    merged_cal.add('version', '2.0')

    all_events = []

    for url in urls:
        cal = fetch_ics(url)
        if cal is None:
            continue

        # 收集 VEVENT 并过滤
        for comp in list(cal.subcomponents):
            if getattr(comp, 'name', None) == 'VEVENT':
                desc = str(comp.get('DESCRIPTION', ''))
                if FILTER_KEYWORD in desc:
                    continue
                all_events.append(comp)

    # 按开始时间排序
    all_events.sort(key=lambda e: e.get('DTSTART').dt)

    # 调整时长避免重叠
    for curr, nxt in zip(all_events, all_events[1:]):
        end_curr = curr.get('DTEND').dt
        start_next = nxt.get('DTSTART').dt
        if end_curr > start_next:
            curr['DTEND'].dt = start_next

    # 统一替换事件 URL，并加入到合并日历
    for event in all_events:
        event['URL'] = event_url
        merged_cal.add_component(event)

    # 写回文件
    try:
        with open(output_file, 'wb') as f:
            f.write(merged_cal.to_ical())
        print(f"✅ 已合并并保存：{output_file}")
    except Exception as e:
        print(f"ERROR: 无法写入文件 → {e}")

def main():
    # 处理 LPL 日历
    process_calendar(ICS_URLS, OUTPUT_FILE, EVENT_URL)
    
    # 处理 LCK 日历
    lck_cal = fetch_ics(LCK_ICS_URL)
    if lck_cal is not None:
        merged_lck_cal = Calendar()
        merged_lck_cal.add('prodid', '-//Merged ICS Calendar//')
        merged_lck_cal.add('version', '2.0')
        
        # 收集 LCK VEVENT
        for comp in list(lck_cal.subcomponents):
            if getattr(comp, 'name', None) == 'VEVENT':
                # LCK 日历不需要过滤 SOLO 选边
                merged_lck_cal.add_component(comp)
        
        # 写回 LCK 文件
        try:
            with open(LCK_OUTPUT_FILE, 'wb') as f:
                f.write(merged_lck_cal.to_ical())
            print(f"✅ 已合并并保存：{LCK_OUTPUT_FILE}")
        except Exception as e:
            print(f"ERROR: 无法写入文件 → {e}")


if __name__ == '__main__':
    main()
