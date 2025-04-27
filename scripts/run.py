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
ICS_URL = "https://cdn.jsdelivr.net/gh/TankNee/LOL_Game_Subscription/2025_lpl/2025_lpl.ics"
OUTPUT_FILE = "calendar.ics"
# 过滤所有包含 “SOLO选边” 的事件
FILTER_KEYWORD = "SOLO选边"
# 事件 URL 统一替换为 B 站直播协议
EVENT_URL = "bilibili://live/6"
# =================


def main():
    # 下载 ICS
    try:
        resp = requests.get(ICS_URL, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"ERROR: 无法拉取 ICS → {e}")
        return

    # 解析为 Calendar 对象
    cal = Calendar.from_ical(resp.content)

    # 收集并过滤 VEVENT
    events = []
    for comp in list(cal.subcomponents):
        if getattr(comp, 'name', None) == 'VEVENT':
            desc = str(comp.get('DESCRIPTION', ''))
            if FILTER_KEYWORD in desc:
                cal.subcomponents.remove(comp)
            else:
                events.append(comp)

    # 按 DTSTART 排序
    events.sort(key=lambda e: e.get('DTSTART').dt)

    # 调整时长，避免重叠，可让结束时间等于下一个开始时间
    for curr, nxt in zip(events, events[1:]):
        end_curr = curr.get('DTEND').dt
        start_next = nxt.get('DTSTART').dt
        if end_curr > start_next:
            curr['DTEND'].dt = start_next

    # 替换所有事件的 URL
    for comp in cal.subcomponents:
        if getattr(comp, 'name', None) == 'VEVENT':
            comp['URL'] = EVENT_URL

    # 写回新的 ICS
    try:
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(cal.to_ical())
        print(f"✅ 已生成并保存：{OUTPUT_FILE}")
    except Exception as e:
        print(f"ERROR: 无法写入文件 → {e}")


if __name__ == '__main__':
    main()
