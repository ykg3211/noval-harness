# 小说创作工程

本工程以 Markdown 保存小说设计、正式事实和人物记忆。

## 本地 Skill

- `novel-bootstrap`：与用户共创小说框架并初始化档案。入口为 [.agents/skills/novel-bootstrap/SKILL.md](.agents/skills/novel-bootstrap/SKILL.md)。用户要求开始一本小说、探索故事设计或初始化小说框架时，先读取该 Skill。
- `novel-continue`：先读取大纲和前序章节，与用户探讨后续剧情，再进行人物推演和章节续写。入口为 [.agents/skills/novel-continue/SKILL.md](.agents/skills/novel-continue/SKILL.md)。
- 创建或修改 Skill 本身不等于调用 Skill；不要因此开始询问用户故事设定或生成示例小说。
- `novel-revise`：与用户探讨修改主线、补充或调整人物性格，检查连带影响并更新本地 Markdown。入口为 [.agents/skills/novel-revise/SKILL.md](.agents/skills/novel-revise/SKILL.md)。
- `novel-review`：读取发布平台并召回对应说明，对指定或刚生成的章节审稿。入口为 [.agents/skills/novel-review/SKILL.md](.agents/skills/novel-review/SKILL.md)。续写交付后询问是否审稿，用户确认或已有明确授权才调用。

## 内容约定

- 工程根目录 [PROJECT.md](PROJECT.md) 保存全局发布平台，由 novel-review 读取并在缺失时收集。当前仅支持七猫小说（qimao），番茄小说（fanqie）待支持。novel-bootstrap、novel-continue、novel-revise 不召回平台属性，不以平台选择阻塞创作。

- 默认一个工程只有一本小说，自动读取现有大纲与章节，不增加选书步骤，不让用户重复描述已有剧情。现有小说可位于 `novels/<slug>/` 或工程根目录，沿用其结构，不为调用 Skill 搬迁内容。
- 新初始化的小说沿用 `novels/<slug>/` 结构；slug 只是目录标识，不作为续写前的用户选择。确有多套有效小说档案且无法根据工程约定定位时，才澄清路径。
- 大纲是未来计划，canon 是已确定事实，人物档案是有限视角；保持三者的边界。
- 推演、草稿不自动进入正式事实或长期记忆；定稿后统一提出和应用变更。
- 每条记忆保留来源、故事时间、获知方式与可信度；人物误解不等于世界事实。
- 阅读期待、爽点回报、伏笔和彩蛋共用 [harness/storycraft/reader-engagement.md](harness/storycraft/reader-engagement.md) 与 [harness/storycraft/foreshadowing.md](harness/storycraft/foreshadowing.md)。人物 Sub Agent 不接收作者的回报目标、未来揭示或读者全知信息。
- 改动已存在的小说先读取其 `index.md`、`novel.md` 和局部约定，不覆盖用户已有内容。
- 长期叙事素材通过小说 `story-assets/index.md` 统一检索；入库、变奏、去重与定稿更新遵守 [素材库规范](harness/storycraft/asset-library.md)。索引引用原伏笔和回报档案，不复制第二份事实。
- 作者可修订已有设计；正式修订记录在小说 `revisions/`，区分补充、前向发展与追溯改设定。写作前读取相关修订及待解决影响，不将旧人物阶段或失效推演当成当前状态。
