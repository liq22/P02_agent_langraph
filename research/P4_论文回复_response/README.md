    # P4_论文回复_response

    ## 节点定位
    本节点是父节点。
    它负责组织、约束、汇总与评审门控，不直接承载完整正文。

    ## 读取规则
    - README.md 只做入口，不承载详细正文
    - index.md 由脚本自动生成，可先为空
    - 静态 schema 与静态关系不在本节点重复维护
    - 智能体默认优先读取：README.md -> status.yaml -> index.md
    - 进入 `fix` 后，智能体不得修改 README.md 与 status.yaml

    ## 子节点
    - @P4_01_审稿意见收集/
- @P4_02_问题映射矩阵/
- @P4_03_逐点回复草稿_md/
- @P4_04_正式回复_tex_或_doc/
- @P4_05_覆盖检查/
- @P4_06_修改证据/
- @P4_07_再投稿打包/

    ## 完成标准
    - 子节点均已建立
    - 至少 1 份 AI review
    - 至少 1 份人类 review
    - 所有 comment 都已在 @review/response.yaml 中响应
    - 满足进入 `fix` 的条件

    ## TODO_AI
    - [ ] 检查子节点是否齐全
    - [ ] 检查边界是否冲突或重复
    - [ ] 完成一轮 AI review
    - [ ] 更新 @review/response.yaml
    - [ ] 检查是否满足进入 `fix` 的条件

    ## TODO_人类
    - [ ] 审核子节点划分是否合理
    - [ ] 审核 AI review 是否有效
    - [ ] 决定是否进入 `fix`
    - [ ] 如需重开节点，手动修改 stage
