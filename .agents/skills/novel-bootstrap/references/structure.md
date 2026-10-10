# 小说档案规范

## 目录职责

```text
novels/<slug>/
  novel.md                     简介、主题、风格、视角、篇幅与边界
  design.md                    设计决定、暂定项、未决问题和理由
  reader-promise.md            主要阅读体验、回报机制与节奏偏好
  story-assets/
    index.md                   伏笔、彩蛋、笑点与爽点统一检索入口
    motifs/                    专属梗和表现机制详情及使用历史
  index.md                     内容导航、ID 和召回入口
  outline/
    overall.md                 全书结构与转折计划
    volumes/                   分卷规划（按需）
    arcs/                      故事线与人物成长线
    foreshadowing.md            伏笔与兑现计划
    foreshadowing/              复杂长线的详情与正文证据（按需）
    payoffs.md                 阅读回报的前置积累、进展及兑现记录
    reader-state.md             截至定稿章的读者已见信息与开放问题
  world/
    rules.md                   规则、限制与代价
    locations/                 地点
    factions/                  势力
    items/                     重要物品
  canon/
    timeline.md                开篇前基线及定稿事件时间线
    events/                    事件事实
    relationships/             真实关系及变化
    secrets/                   真相、知情人和获知时间
  characters/<character-id>/
    profile.md                 身份、价值观、性格和行为依据
    goals.md                   长短期目标、优先级和底线
    state.md                   当前状态及其故事时间
    relationships.md           此人的主观关系认知
    knowledge.md               确知、传闻、怀疑、误解与未知
    memories/index.md          记忆摘要、触发标签和来源索引
    memories/<memory-id>.md    具体记忆
    extensions/                自定义人物记忆类型
  chapters/ch-001/
    plan.md                    章节目标和场景规划
    scenes/                    按需建立场景计划
    draft.md                   草稿，初始化不撰写正文
    changes.md                 事实和记忆变更提案
  runs/                        每次推演的输入、输出、裁定与审查
  memory-types.md              长期记忆类型及扩展规则
  maintenance.md               推演、定稿、修订与召回约定
```

`final.md` 仅在实际定稿时创建。空目录用于后续内容，不放伪造实体。Git 不保留空目录，入口文档记录预期路径；后续写入时按需创建。

## 元数据与标识

实体文件使用 YAML frontmatter。ID 在一本小说内唯一且稳定；改名不改 ID。`status` 使用 provisional、established、draft、final、superseded 等明确状态，不把设计成熟度和故事事实混为一谈。

```yaml
id: char-lin
kind: character
name: 林舟
status: provisional
source: design.md
```

索引写明 ID、简述、标签和相对链接；跨文件引用优先使用 ID 加 Markdown 链接。人物各分文件引用人物 ID，不重复声明同一实体 ID。`source` 路径相对于当前文件，例中仅示意字段，实际按所在目录计算。

## 事实、认知与时间

- `outline/`：作者希望将来发生什么，即使设计已确定也不是已发生事实。
- `canon/`：世界真实发生的事。初始化只纳入被采纳的开篇前基线；暂定基线明确标记。
- `characters/`：人物在对应时间点知道、相信、记得什么。真实性和确信程度分别描述。
- `runs/`：可能发生的行动和被否决的分支，不自动进入其他档案。

状态、知识和关系注明 `as_of`；历史记忆注明发生时间和获知时间，二者可能不同。时间可用 `开篇前两年`、`day-000` 等相对格式，同一小说保持一致。

秘密条目记录真相、知情人及各自获知时间；未来揭露时机放大纲。人物未获知前，不能把真相混入其推演上下文。

阅读回报与伏笔按工程 `harness/storycraft/` 的共用规范维护。outline 中既可保存未来计划，也可保存实际进展日志，但必须分开状态和证据；它们不直接授予人物知识。reader-state 记录读者见过的呈现及推测，不等于世界真相或真实读者反馈。

## 记忆条目

以下例子位于 `characters/char-lin/memories/mem-lin-001.md`：

```markdown
---
id: mem-lin-001
kind: memory
type: experience
character: char-lin
event: evt-001
story_time: 开篇前两年
learned_at: 开篇前两年
source: ../../../canon/events/evt-001.md
acquisition: witnessed
confidence: certain
status: active
tags: [信任, char-zhou]
---

# 记忆标题

## 记得的内容
人物能回忆到的经历。

## 主观理解
人物如何解释经历，可与事件真相不同。

## 情绪与行为影响
它会影响什么选择、信任或心理触发点。

## 修正与关联
后续修正引用新事件或记忆，不悄悄抹除原有误解。
```

无对应事件时 `event: null`，来源可指向 `../../../design.md`，不制造悬空 ID。`confidence` 指人物确信程度，不保证客观正确；获知方式可为 witnessed、told、inferred。当前相信的版本放知识文件，历史变化保留在记忆和事件中。

## 可扩展记忆类型

在 `memory-types.md` 登记类型 ID、用途、必填字段、召回触发条件、更新方式。基础类型可包括 experience、promise、secret、relationship-change、trauma、skill、debt、possession。扩展复用人物、时间、来源与可信度字段，并补充专用字段。

不预先生成每种类型的空记忆。人格放 profile，动态资源放 state，具体历史及其影响进入记忆。

## 供后续写作使用的维护协议

将下述规则写入 `maintenance.md`。这是工作流约定，初始化 Skill 不负责实现运行时执行器。

1. 主 Agent 按场景时间召回核心档案、当时状态、关系和相关记忆；先过滤知情范围，再排序相关性。写过去场景时依据事件重建当时状态，不能直接用最新状态。
2. 每个人物使用独立 Sub Agent 上下文；作者计划、对方内心和未获知真相不进入输入。同轮各自推演，看到别人行动后的反应进入下一轮。
3. 输出局势理解、情绪与动机、决策、外在表现、内心活动、改变决定的条件和依据 ID。主 Agent 裁定行动结果，综合成场景。
4. 人物 Sub Agent 不直接修改正式档案。输入、反应、裁定、审查分别记录在 `runs/<run-id>/`。
5. 定稿后从 `changes.md` 应用事件、时间线、人物状态、关系、知识和记忆变更；新增事实保留定稿来源。草稿和推演不能自动成为正式记忆。
6. 修改旧事件时按来源和 ID 检索依赖，列出受影响的章节与人物认知；完成一致性修订后更新索引。
