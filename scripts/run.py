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
    # 以后你只需要在这里继续添加 ICS 链接
]
OUTPUT_FILE = "calendarIOS.ics"
FILTER_KEYWORD = "SOLO选边"
EVENT_URL = "bilibili://live/6"
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


def main():
    merged_cal = Calendar()
    merged_cal.add('prodid', '-//Merged ICS Calendar//')
    merged_cal.add('version', '2.0')

    all_events = []

    for url in ICS_URLS:
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
        event['URL'] = EVENT_URL
        merged_cal.add_component(event)

    # 写回文件
    try:
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(merged_cal.to_ical())
        print(f"✅ 已合并并保存：{OUTPUT_FILE}")
    except Exception as e:
        print(f"ERROR: 无法写入文件 → {e}")


if __name__ == '__main__':
    main()
