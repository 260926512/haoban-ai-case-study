#!/usr/bin/env python3
"""轨道A：2384条App Store评论 主题聚类 + 痛点分布
方法：规则化关键词归类（多标签），对1-3星差评做主题占比统计；
另对核心AI健康App的好评做正向主题统计。
局限：关键词规则而非语义聚类，有少量误归；样本为近期评论，反映近期口碑。"""
import csv, json
from collections import defaultdict

rows = list(csv.DictReader(open("appstore_reviews.csv", encoding="utf-8-sig")))

# 差评主题（1-3星）—— 注意：用户方法论是看1-3星，不只≤2星
NEG_THEMES = {
  "工程质量(bug/卡/登录/闪退)": ["闪退","卡顿","卡死","卡住","死机","崩溃","登录","登陆","token","打不开","加载","用不了","输入不进","跳出","跳转到登录","转圈","bug","Bug","BUG","byg","修复","白屏","黑屏","进不去"],
  "付费纠纷(扣费/退款/套路)": ["收费","付费","扣费","扣款","续费","会员","退款","退钱","退费","骗钱","充值","太贵","很贵","好贵","白花","花了钱","自动续","乱收费","诱导"],
  "广告/营销/骚扰": ["广告","推销","营销","地推","拉人","拉新","邀请","弹窗","推广","骚扰","短信","诱导下载","骗下载","拦人"],
  "AI能力差(不准/幻觉/没用)": ["不准","不對","误诊","误判","错误","出错","搞错","幻觉","答非所问","人工智障","没用","没什么用","很笨","太笨","智障","乱说","瞎说","不如","虚构","编造","胡说","不专业","敷衍","模板","一样的回答"],
  "记忆/档案翻车": ["历史","记录没","记录全部","清空","记不住","忘","丢了","丢失","档案","重新填","记错"],
  "隐私/权限": ["隐私","权限","个人信息","实名","身份证","偷拍","信息安全","泄露"],
  "真人服务/客服差": ["客服","医生不回","没人理","联系不上","人工","回复慢","找不到人"],
  "功能臃肿/交互差": ["难用","复杂","臃肿","又臭又长","界面","啰嗦","问卷","繁琐","流程","操作","找不到","逻辑混乱","反人类"],
  "不敢下结论/导医院": ["建议就医","去医院","看医生","不敢","没有结论","让我自己","推给"],
}

POS_THEMES = {
  "准确/专业": ["准","专业","靠谱","详细","权威","精准","到位"],
  "方便/快捷/省时": ["方便","快","便捷","随时","省时","及时","秒"],
  "免费/实惠": ["免费","不要钱","实惠","便宜","划算"],
  "耐心/陪伴/温度": ["耐心","贴心","温暖","陪伴","像朋友","安心","暖","关心","细心"],
  "报告/体检解读有用": ["报告","解读","体检","化验","指标","看懂"],
  "记得我/懂我": ["记得","懂我","记住","了解我","档案"],
}

APPS = ["蚂蚁阿福","好伴AI","小荷AI医生","平安好医生","京东健康","丁香医生","薄荷健康","春雨医生"]
AI_CORE = ["蚂蚁阿福","好伴AI","小荷AI医生"]  # AI健康助手核心三家

def cluster(themes, apps, low, high):
    """low,high = 评分区间(含)；返回 {app:{theme:count}}, base{app:n}"""
    res = defaultdict(lambda: defaultdict(int)); base = defaultdict(int)
    for r in rows:
        if r["app"] not in apps: continue
        rt = int(r["rating"])
        if not (low <= rt <= high): continue
        base[r["app"]] += 1
        text = r["title"] + " " + r["content"]
        for theme, kws in themes.items():
            if any(k in text for k in kws):
                res[r["app"]][theme] += 1
    return res, base

neg_res, neg_base = cluster(NEG_THEMES, APPS, 1, 3)
pos_res, pos_base = cluster(POS_THEMES, AI_CORE, 4, 5)

# 评分概览
overview = {}
for app in APPS:
    rs = [int(r["rating"]) for r in rows if r["app"]==app]
    overview[app] = {
        "样本": len(rs),
        "近期均分": round(sum(rs)/len(rs),2),
        "差评率(1-3星)%": round(sum(1 for x in rs if x<=3)/len(rs)*100,1),
        "好评率(4-5星)%": round(sum(1 for x in rs if x>=4)/len(rs)*100,1),
    }

out = {"评分概览": overview, "差评主题(1-3星)": {}, "好评主题(4-5星)": {}, "差评样本量": dict(neg_base), "好评样本量": dict(pos_base)}

print("="*70); print("【评分概览】")
print(f"{'App':<10}{'样本':>6}{'近期均分':>10}{'差评率%':>10}{'好评率%':>10}")
for app,v in overview.items():
    print(f"{app:<10}{v['样本']:>6}{v['近期均分']:>10}{v['差评率(1-3星)%']:>9}%{v['好评率(4-5星)%']:>9}%")

print("\n"+"="*70); print("【差评主题分布】(占该app 1-3星差评数的%)")
hdr = f"{'主题':<24}"+"".join(f"{a[:4]:>8}" for a in APPS); print(hdr)
for theme in NEG_THEMES:
    line = f"{theme:<24}"
    for app in APPS:
        n=neg_base[app]; c=neg_res[app][theme]; pct=round(c/n*100,1) if n else 0
        line += f"{pct:>7}%"
        out["差评主题(1-3星)"].setdefault(app,{})[theme]={"count":c,"pct":pct}
    print(line)

print("\n"+"="*70); print("【好评主题分布】(AI核心三家，占4-5星好评数的%)")
hdr2 = f"{'主题':<22}"+"".join(f"{a[:5]:>9}" for a in AI_CORE); print(hdr2)
for theme in POS_THEMES:
    line=f"{theme:<22}"
    for app in AI_CORE:
        n=pos_base[app]; c=pos_res[app][theme]; pct=round(c/n*100,1) if n else 0
        line+=f"{pct:>8}%"
        out["好评主题(4-5星)"].setdefault(app,{})[theme]={"count":c,"pct":pct}
    print(line)

json.dump(out, open("review_clusters.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n已保存 → review_clusters.json")
