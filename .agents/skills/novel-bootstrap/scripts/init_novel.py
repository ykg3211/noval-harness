#!/usr/bin/env python3
"""Create a non-overwriting Markdown scaffold; story design is filled by the agent."""

import argparse
import json
from pathlib import Path
import re
import sys


def identifier(value):
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", value) or len(value) > 64:
        raise ValueError(f"非法标识：{value!r}，使用小写英文、数字及连字符，最长 64 字符")
    return value


def single_line(value):
    if not value.strip() or any(ord(c) < 32 for c in value):
        raise ValueError("标题和人物名称必须是非空单行文本")
    return value.strip()


def md(title, sections, **metadata):
    frontmatter = ""
    if metadata:
        fields = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}"
                           for key, value in metadata.items())
        frontmatter = f"---\n{fields}\n---\n\n"
    body = "\n\n".join(f"## {section}\n\n待定。" for section in sections)
    return f"{frontmatter}# {title}\n\n{body}\n"


def scaffold(slug, title, characters):
    files = {
        "novel.md": md(title, ["一句话故事", "题材与读者体验", "主题", "叙事视角与风格", "篇幅与节奏", "创作边界"],
                       id=slug, kind="novel", status="provisional", source="design.md"),
        "design.md": md("设计记录", ["已确定", "暂定方案与理由", "待定问题与影响", "故事时间约定"]),
        "story-assets/index.md": """# 长期叙事素材库

尚无登记条目。统一检索伏笔、彩蛋、专属梗、笑点与爽点；引用 outline/foreshadowing.md 和 outline/payoffs.md 中的原条目，不复制详情或重复发 ID。专属梗详情按需建在 motifs/。

| ID | 类型 | 摘要 | 人物 / 触发标签 | 状态摘要 | 详情链接 |
| --- | --- | --- | --- | --- | --- |

## 使用与更新

按工程 harness/storycraft/asset-library.md 执行：候选设计可先登记，草稿实际使用进入 changes.md，定稿后记录 occurrence ID、正文位置、变奏与后果，更新状态和索引。使用次数、首次和最近使用从有效历史推导。修订保留 superseded 记录并检查后续依赖，不虚构读者反馈。
""",
        "reader-promise.md": md("阅读期待", ["主要阅读体验与辅助体验", "主角为何值得在意", "开篇如何示范核心体验", "回报机制与作品差异", "压力、释放与余韵偏好", "避免重复的套路"],
                                kind="reader-promise", status="provisional", source="design.md"),
        "outline/overall.md": md("全书大纲", ["核心冲突", "结构选择与理由", "故事线", "关键转折及后果", "收束方向"],
                                 kind="outline", status="provisional", source="../design.md"),
        "outline/foreshadowing.md": """# 伏笔与彩蛋索引

尚无登记条目。无正文时实际状态为 planned；计划与正文证据分开。复杂长线可另建 foreshadowing/<id>.md，登记作者设计、当下作用、知情范围、强化与回收条件、正文证据及历史。
类型区分 clue、easter-egg、callback 等；实际状态采用 planned、seeded、reinforced、partially-paid、paid-off、retired。状态更新需要定稿证据，草稿变化放 changes.md。

| ID / 详情 | 类型 | 关联故事线 / 回报 | 埋设与回收窗口 | 实际状态 | 最近触及章 / 正文证据 | 下一步条件 |
| --- | --- | --- | --- | --- | --- | --- |
""",
        "outline/payoffs.md": """# 阅读回报与兑现

尚无登记条目。规划阶段用 planned 标记，不把预期进展当成已兑现。正文定稿后记录实际进展、来源与历史。

| ID | 关联阅读承诺与人物 | 前置积累 | 可见阶段进展 | 目标兑现条件 / 窗口 | 代价与后果 | 关联伏笔 | 实际状态 / 正文证据 |
| --- | --- | --- | --- | --- | --- | --- | --- |

## 节奏与维护

场景或章节、故事线或分卷、全书的回报相互支撑，章数和强度按作品调整。允许铺垫与余韵，不每章强行打脸或断在危险瞬间。延迟和取消记录原因与处理条件。
""",
        "outline/reader-state.md": """# 读者可见信息

截至定稿章：无。尚无正文已向读者呈现的信息。
这是作者工作档案，不是人物知识或真实读者反馈。不可靠叙述标明说话者；读者可能推测的解释标为假设。草稿新信息只进本章临时状态和 changes.md。

| 信息 / 问题 | 正文明确呈现什么 | 可推测解释（假设） | 尚未揭示部分 | 定稿正文来源 |
| --- | --- | --- | --- | --- |
""",
        "world/rules.md": md("世界规则", ["时代与环境", "核心规则", "限制与代价", "社会与资源", "尚未确定的边界"],
                             kind="world", status="provisional", source="../design.md"),
        "canon/timeline.md": "# 正式时间线\n\n尚无已登记事件。仅收录开篇前基线与定稿事件，未来计划见大纲。\n\n| 时间 | 事件 ID | 事实摘要 | 来源 | 状态 |\n| --- | --- | --- | --- | --- |\n",
        "chapters/ch-001/plan.md": md("第一章计划", ["章节目标", "起始处境", "参与人物及其目标", "场景与冲突", "预期变化", "需要召回的记忆", "主要阅读体验与关联回报", "伏笔动作与前置条件", "读者新增信息与章末动力"],
                                     id="ch-001", kind="chapter-plan", status="provisional", source="../../design.md"),
        "chapters/ch-001/draft.md": "# 第一章草稿\n\n未撰写正文。\n",
        "chapters/ch-001/changes.md": "# 变更提案\n\n尚无变更。章节定稿后统一应用，不把计划和推演写入正式记忆。\n\n| 对象 ID | 变更内容 | 故事时间 | 定稿来源 | 应用状态 |\n| --- | --- | --- | --- | --- |\n",
        "memory-types.md": """# 长期记忆类型

共同字段：id、kind、type、character、event（可空）、story_time、learned_at、source、acquisition、confidence、status、tags。
confidence 表示人物确信程度；记忆不等于客观真相。正文记录内容、主观理解、情绪与行为影响、修正与关联。

| 类型 ID | 用途 | 专用必填信息 | 召回触发 | 更新规则 |
| --- | --- | --- | --- | --- |
| experience | 亲历或获知的经历 | 经历和解释 | 相关人物、地点、相似处境 | 新认识关联旧记忆 |
| promise | 承诺或誓约 | 对象、内容、履行条件 | 对象出现、条件满足 | 记录履行或违背 |
| secret | 人物获知的秘密 | 秘密 ID、获知范围 | 相关人物或风险 | 记录泄露、纠正及来源 |
| relationship-change | 关系变化的记忆 | 对象、原因、前后变化 | 对象或信任选择 | 历史保留，现状同步关系档案 |
| trauma | 持续影响的创伤经历 | 触发点、反应倾向 | 相似刺激 | 记录恢复或恶化依据 |
| skill | 技能习得经历 | 技能、程度、限制 | 相关任务 | 有依据才更新程度 |
| debt | 债务或人情 | 对象、义务、清偿条件 | 对象或履约场景 | 记录清偿或变化 |
| possession | 重要物品的获得与失去 | 物品 ID、变化原因 | 物品或资源选择 | 当前持有情况同步 state |

## 扩展

新增类型时登记用途、必填字段、召回触发条件和更新规则，复用共同字段。人物专有内容可放 extensions/；不生成无内容的空记忆。
""",
        "maintenance.md": """# 维护与推演约定

## 事实边界

大纲是未来计划，canon 是世界事实，人物档案是有限认知，runs 是推演分支。暂定设计明确标记。
状态、知识与关系注明 as_of；记忆区分发生时间和获知时间。来源路径相对当前文件，ID 在本小说内稳定且唯一。

## 人物召回与 Sub Agent

主 Agent 按场景时间召回人物核心档案、当时状态、关系及相关记忆，先过滤知情范围再排序。过去场景要重建当时状态。
每个人物获得独立上下文，不包含作者计划、对方内心或未获知秘密。同轮独立推演；观察别人行动后的反应放下一轮。
人物 Sub Agent 输出局势理解、情绪与动机、决策、外在表现、内心活动、改变决定的条件和依据 ID；主 Agent 裁定行动结果。
人物 Sub Agent 不直接修改正式档案。推演输入、反应、裁定与审查存入 runs/<run-id>/ 的 inputs/、reactions/、resolution.md、review.md，场景快照存 context.md。
这些是后续写作协议，本次初始化不等于已有自动执行器。

## 定稿与修订

正文定稿时创建 final.md，从 changes.md 统一应用事件、时间线、状态、关系、知识与记忆变更，保留定稿来源。
草稿和推演不自动成为正式记忆。修订旧事件时检索来源和 ID，列出受影响的章节与人物认知，修订一致后更新索引。

## 阅读期待与长线回收

框架阶段维护 reader-promise.md、outline/payoffs.md、outline/foreshadowing.md 和 outline/reader-state.md，按工程 harness/storycraft 的规范执行。
写作前检查待兑现承诺、相关伏笔及正文证据，安排本章实际进展。人物 Sub Agent 不接收作者回报目标、未来揭示或读者全知信息。
定稿前，回报与伏笔的实际进展只登记在本章临时状态和 changes.md；定稿后依据正文更新状态、证据和读者信息的截至章。计划改动与实际发生分开记录。
""",
    }
    for cid, name in characters:
        base = f"characters/{cid}"
        files[f"{base}/profile.md"] = md(name, ["身份与背景", "价值排序", "性格与行为依据", "弱点与矛盾", "压力下的反应", "成长方向"],
                                        id=cid, kind="character", name=name, status="provisional", source="../../design.md")
        for filename, heading, sections in [
            ("goals", "目标与底线", ["长期目标", "短期目标", "优先级与代价", "不可接受的底线"]),
            ("state", "当前状态", ["所在位置", "身体与情绪", "资源与持有物", "当前处境"]),
            ("relationships", "主观关系", ["对他人的认知", "信任、依赖与冲突", "与真实关系的差异"]),
            ("knowledge", "人物知识", ["确知", "传闻", "怀疑", "误解", "未知边界"]),
        ]:
            metadata = {"character": cid, "status": "provisional", "source": "../../design.md"}
            if filename != "goals":
                metadata["as_of"] = "待定：按 design.md 统一故事时间"
            files[f"{base}/{filename}.md"] = md(f"{name}：{heading}", sections, **metadata)
        files[f"{base}/memories/index.md"] = f"# {name}的记忆索引\n\n尚无已登记记忆。不将未来计划作为经历。\n\n| 记忆 ID | 摘要 | 发生 / 获知时间 | 触发标签 | 文件 |\n| --- | --- | --- | --- | --- |\n"

    navigation = [
        ("小说概览", "novel.md"), ("设计与未决问题", "design.md"),
        ("全书大纲", "outline/overall.md"), ("伏笔", "outline/foreshadowing.md"),
        ("阅读期待", "reader-promise.md"), ("回报与兑现", "outline/payoffs.md"),
        ("读者可见信息", "outline/reader-state.md"),
        ("世界规则", "world/rules.md"), ("正式时间线", "canon/timeline.md"),
        ("第一章计划", "chapters/ch-001/plan.md"), ("记忆类型", "memory-types.md"),
        ("维护协议", "maintenance.md"),
        ("长期叙事素材库", "story-assets/index.md"),
    ]
    links = "\n".join(f"- [{label}]({path})" for label, path in navigation)
    people = "\n".join(f"- `{cid}`：[{name.replace('[', '').replace(']', '')}](characters/{cid}/profile.md)，"
                       f"[记忆](characters/{cid}/memories/index.md)" for cid, name in characters)
    files["index.md"] = f"# {title}：导航\n\n{links}\n\n## 人物召回入口\n\n{people or '尚未确定人物。'}\n\n先读取 profile、goals，再按场景时间读取 state、relationships、knowledge 和相关 memories；不直接向人物暴露完整作者档案。\n\n## 按需内容目录\n\noutline/volumes/、outline/arcs/、world/locations/、world/factions/、world/items/、canon/events/、canon/relationships/、canon/secrets/、chapters/ch-001/scenes/、runs/。空目录不进入 Git，后续按需创建。\n"
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--character", action="append", default=[], metavar="ID=NAME")
    args = parser.parse_args()
    try:
        slug, title = identifier(args.slug), single_line(args.title)
        characters = []
        for entry in args.character:
            cid, sep, name = entry.partition("=")
            if not sep:
                raise ValueError("--character 使用 ID=NAME 格式")
            characters.append((identifier(cid), single_line(name)))
        ids = [slug] + [cid for cid, _ in characters] + ["ch-001"]
        if len(ids) != len(set(ids)):
            raise ValueError("小说、人物和章节 ID 不得重复")
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("--root 必须是已有工程目录")
        files = scaffold(slug, title, characters)
        destination = root / "novels" / slug
        destination.parent.mkdir(exist_ok=True)
        destination.mkdir()  # Refuse existing directories, including empty ones.
    except (ValueError, OSError) as error:
        parser.exit(2, f"初始化未执行：{error}\n")

    try:
        for relative, content in files.items():
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        directories = ["story-assets/motifs", "outline/volumes", "outline/arcs", "outline/foreshadowing", "world/locations", "world/factions", "world/items",
                       "canon/events", "canon/relationships", "canon/secrets", "chapters/ch-001/scenes", "runs"]
        directories += [f"characters/{cid}/extensions" for cid, _ in characters]
        for relative in directories:
            (destination / relative).mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"初始化部分完成：{destination}；写入失败：{error}。保留已写入文件，请检查后补全。", file=sys.stderr)
        return 1
    print(f"已创建骨架：{destination}（{len(files)} 个 Markdown 文件，{len(characters)} 个人物）")
    print("下一步：根据共创结果填充具体设计；骨架不是完整小说框架。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
