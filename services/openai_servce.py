import openai
import streamlit as st
from typing import Generator, Dict, Any
import json

class OpenAIService:
    """OpenAI服务类，提供流式和非流式请求功能"""
    
    def __init__(self, api_key: str, base_url: str = None, model_name: str = "gpt-3.5-turbo"):
        """
        初始化OpenAI服务
        
        Args:
            api_key: OpenAI API密钥
            base_url: 基础URL（可选，用于代理）
            model_name: 模型名称
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
    
    def stream_chat_completion(
        self, 
        messages: list, 
        temperature: float = 0.7,
        response_format: dict = None
    ) -> Generator[str, None, None]:
        """
        流式聊天完成请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数，控制随机性
            
        Yields:
            流式返回的文本片段
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                stream=True,
                **({"response_format": response_format} if response_format is not None else {})
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"错误: {str(e)}"
    
    def analyze_document(self, file_content: str, analysis_type: str = "overview") -> Generator[str, None, None]:
        """
        分析文档内容
        
        Args:
            file_content: 文档内容
            analysis_type: 分析类型 ("overview" 或 "requirements")
            
        Yields:
            流式分析结果
        """
        if analysis_type == "overview":
            system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取并总结项目概述信息。
            
请重点关注以下方面：
1. 项目名称和基本信息
2. 项目背景和目的
3. 项目规模和预算
4. 项目时间安排
5. 主要技术特点
6. 关键要求

工作要求：
1. 保持提取信息的全面性和准确性，尽量使用原文内容，不要自己编写
2. 只关注与项目实施有关的内容，不提取商务信息
3. 直接返回整理好的项目概述，除此之外不返回任何其他内容
"""
        else:  # requirements
            system_prompt = """你是一个专业的招标文件分析专家。请分析上传的招标文件，提取技术评分要求,为编写投标文件中的技术方案做准备。
            
请重点关注以下方面：
1. 理解技术评分的意思：用于编写、评比投标文件中技术标的标准，关注技术方案、实施计划、技术能力、质量控制、创新性等内容，避免混淆商务评分（资质、信誉、合同条款）和价格评分（报价金额）
2. 仅提取技术评分项及相关要求，不包括商务、价格及其他
3. 生成内容要确保是从招标文件中提取的，不要自己编写
4. 直接返回整理好的技术评分要求，除此之外不返回任何其他内容
"""
        analysis_type_cn = "项目概述" if analysis_type == "overview" else "技术评分要求"
        user_prompt = f"请分析以下招标文件内容，提取{analysis_type_cn}信息：\n\n{file_content}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 流式返回分析结果
        for chunk in self.stream_chat_completion(messages, temperature=0.3):
            yield chunk
            
    def generate_outline(self, overview: str, requirements: str) -> Generator[str, None, None]:
        """
        生成标书目录结构
        
        Args:
            overview: 项目概述信息
            requirements: 技术评分要求信息
            
        Yields:
            流式返回的JSON格式目录结构
        """
        system_prompt = """你是一个专业的标书编写专家。根据提供的项目概述和技术评分要求，生成投标文件中技术标部分的目录结构。

要求：
1. 目录结构要全面覆盖技术标的所有必要章节
2. 章节名称要专业、准确，符合投标文件规范
3. 一级目录名称要与技术评分要求中的章节名称一致，如果技术评分要求中没有章节名称，则结合技术评分要求中的内容，生成一级目录名称
4. 一共包括三级目录
5. 返回标准JSON格式，包含章节编号、标题、描述和子章节
6. 除了JSON结果外，不要输出任何其他内容

JSON格式要求：
{
  "outline": [
    {
      "id": "1",
      "title": "",
      "description": "",
      "children": [
        {
          "id": "1.1",
          "title": "",
          "description": "",
          "children":[
              {
                "id": "1.1.1",
                "title": "",
                "description": ""
              }
          ]
        }
      ]
    }
  ]
}
"""
        
        user_prompt = f"""请基于以下项目信息生成标书目录结构：

项目概述：
{overview}

技术评分要求：
{requirements}

请生成完整的技术标目录结构，确保覆盖所有技术评分要点。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # 流式返回目录结构
        for chunk in self.stream_chat_completion(messages, temperature=0.7, response_format={"type": "json_object"}):
            print(chunk, end="")
            yield chunk

    def generate_content_single(self, outline: str, project_overview: str = "") -> Generator[str, None, None]:
        """
        递归遍历outline，为叶子节点生成内容

        Args:
            outline: JSON格式的outline字符串
            project_overview: 项目概述信息，用于生成更准确的内容

        Yields:
            流式返回处理状态和生成的content
        """
        outline = '{"outline":[{"id":"1","title":"项目总体概述及运维方案","description":"针对本项目有深刻认识，总体概述清晰、合理，运维方案以及措施先进、成熟完全满足规范要求","children":[{"id":"1.1","title":"项目概述","description":"介绍项目背景、目标、范围、规模与预算等基本情况","children":[{"id":"1.1.1","title":"项目背景与意义","description":"阐述天津港保税区消防救援支队消防物联网远程监控系统运维服务项目的背景和重要意义"},{"id":"1.1.2","title":"项目目标与范围","description":"明确项目运维目标和具体服务范围，包括监控中心、IDC机房、通讯链路、平台软硬件及前端设备"},{"id":"1.1.3","title":"项目规模与预算","description":"详细说明项目规模和预算情况，包括各项资源配置和费用构成"}]},{"id":"1.2","title":"运维方案总体设计","description":"阐述运维服务的总体设计理念和架构","children":[{"id":"1.2.1","title":"运维服务理念与原则","description":"阐述运维服务的核心理念和基本原则"},{"id":"1.2.2","title":"运维服务体系架构","description":"设计完整的运维服务体系架构，包括组织架构、流程架构和技术架构"},{"id":"1.2.3","title":"运维服务流程设计","description":"设计标准化的运维服务流程，确保服务质量和效率"}]},{"id":"1.3","title":"运维服务内容","description":"详细说明各项运维服务的具体内容和实施方式","children":[{"id":"1.3.1","title":"监控中心与IDC机房运维","description":"阐述监控中心场地和IDC机房机柜的运维服务内容"},{"id":"1.3.2","title":"通讯链路运维","description":"说明固定IP专线、物联网卡和视频专线的运维服务内容"},{"id":"1.3.3","title":"平台软硬件运维","description":"阐述系统平台软硬件的日常维护和优化服务内容"},{"id":"1.3.4","title":"前端设备电池更换","description":"详细说明用传蓄电池和传感器电池的更换方案和实施计划"}]}]},{"id":"2","title":"本项目投入人员团队的评价","description":"展示项目实施人员配置、技术实力和同类项目实施或服务经验","children":[{"id":"2.1","title":"人员团队总体构成","description":"介绍人员团队的整体构成情况","children":[{"id":"2.1.1","title":"团队规模与配置","description":"详细说明团队总人数、专业配置和人员结构"},{"id":"2.1.2","title":"团队专业结构","description":"阐述团队成员的专业背景和技术特长分布"},{"id":"2.1.3","title":"团队资质认证","description":"列举团队成员持有的相关资质证书和专业认证"}]},{"id":"2.2","title":"核心技术人员介绍","description":"详细介绍项目核心技术人员的情况","children":[{"id":"2.2.1","title":"项目负责人资质与经验","description":"介绍项目负责人的专业资质、从业经验和项目管理能力"},{"id":"2.2.2","title":"技术骨干资质与经验","description":"介绍技术骨干的专业背景、技术能力和项目经验"},{"id":"2.2.3","title":"消防专业人员资质与经验","description":"介绍持有消防员证书等专业资质的人员情况"}]},{"id":"2.3","title":"团队业绩与经验","description":"展示团队过往的项目业绩和经验积累","children":[{"id":"2.3.1","title":"类似项目实施经验","description":"列举团队参与的类似消防物联网系统项目经验"},{"id":"2.3.2","title":"消防物联网系统运维经验","description":"详述团队在消防物联网系统运维方面的专业经验"},{"id":"2.3.3","title":"技术创新与成果","description":"展示团队在相关领域的技术创新和成果"}]}]},{"id":"3","title":"人员组织方案及分工职责","description":"详细说明人员配备方案、组织安排和职责分工","children":[{"id":"3.1","title":"组织架构设计","description":"设计合理的运维服务组织架构","children":[{"id":"3.1.1","title":"运维服务组织架构","description":"设计完整的运维服务组织架构图和说明"},{"id":"3.1.2","title":"管理层级与汇报关系","description":"明确各管理层级和汇报关系，确保信息畅通"},{"id":"3.1.3","title":"协同工作机制","description":"建立高效的团队协同工作机制，提高工作效率"}]},{"id":"3.2","title":"岗位职责划分","description":"明确各岗位的具体职责和工作内容","children":[{"id":"3.2.1","title":"项目经理职责","description":"详细说明项目经理的职责范围和工作要求"},{"id":"3.2.2","title":"技术负责人职责","description":"明确技术负责人的职责范围和技术管理要求"},{"id":"3.2.3","title":"运维人员职责","description":"划分各类运维人员的具体职责和工作内容"}]},{"id":"3.3","title":"人员配置方案","description":"详细说明各类人员的配置方案和工作安排","children":[{"id":"3.3.1","title":"监控中心值守人员配置","description":"说明8人7X24小时值守人员的配置方案和工作安排"},{"id":"3.3.2","title":"前端设备运维人员配置","description":"说明3名硬件技术人员的配置方案和工作范围"},{"id":"3.3.3","title":"系统软件运维人员配置","description":"说明不少于2名软件技术人员的配置方案和工作内容"}]}]},{"id":"4","title":"前端硬件设备运维方案","description":"全面阐述消防物联网前端硬件设备的运维、维保和维修方案","children":[{"id":"4.1","title":"前端设备概况","description":"介绍前端设备的基本情况和运维难点","children":[{"id":"4.1.1","title":"设备类型与分布","description":"详细列出前端设备的类型、数量和分布情况"},{"id":"4.1.2","title":"设备运行状态分析","description":"分析前端设备的当前运行状态和潜在问题"},{"id":"4.1.3","title":"设备运维难点分析","description":"分析前端设备运维过程中的难点和挑战"}]},{"id":"4.2","title":"设备维保方案","description":"制定前端设备的日常维保方案","children":[{"id":"4.2.1","title":"日常巡检计划","description":"制定详细的日常巡检计划，包括巡检频率、内容和标准"},{"id":"4.2.2","title":"定期维护保养","description":"制定设备定期维护保养计划，确保设备长期稳定运行"},{"id":"4.2.3","title":"设备性能优化","description":"提出设备性能优化方案，提高设备运行效率"}]},{"id":"4.3","title":"设备维修方案","description":"制定前端设备故障维修方案","children":[{"id":"4.3.1","title":"故障诊断流程","description":"建立标准化的故障诊断流程，快速定位问题"},{"id":"4.3.2","title":"维修响应机制","description":"制定高效的维修响应机制，确保及时处理故障"},{"id":"4.3.3","title":"备品备件管理","description":"建立备品备件管理制度，保障维修需求"}]},{"id":"4.4","title":"电池更换方案","description":"详细说明前端设备电池更换方案","children":[{"id":"4.4.1","title":"用传蓄电池更换方案","description":"制定260块用传蓄电池的更换方案和实施计划"},{"id":"4.4.2","title":"传感器电池更换方案","description":"制定1820块传感器电池的更换方案和实施计划"},{"id":"4.4.3","title":"电池更换质量控制","description":"建立电池更换质量控制体系，确保更换质量"}]}]},{"id":"5","title":"软硬件故障应急处理方案","description":"制定全面、合理、可行的软硬件故障应急处理方案","children":[{"id":"5.1","title":"应急处理总体架构","description":"设计应急处理的总体架构和机制","children":[{"id":"5.1.1","title":"应急响应组织","description":"建立应急响应组织架构，明确各岗位职责"},{"id":"5.1.2","title":"应急响应流程","description":"制定标准化的应急响应流程，确保快速响应"},{"id":"5.1.3","title":"应急资源保障","description":"配置必要的应急资源，确保应急处理能力"}]},{"id":"5.2","title":"故障分级与响应机制","description":"建立故障分级标准和相应的响应机制","children":[{"id":"5.2.1","title":"故障等级划分","description":"制定故障等级划分标准，明确各级故障的定义"},{"id":"5.2.2","title":"响应时间要求","description":"规定不同等级故障的响应时间和处理时限"},{"id":"5.2.3","title":"升级处理机制","description":"建立故障升级处理机制，确保重大故障得到及时处理"}]},{"id":"5.3","title":"典型故障处理预案","description":"制定典型故障的处理预案","children":[{"id":"5.3.1","title":"系统软件故障处理预案","description":"制定系统软件故障的应急处理预案"},{"id":"5.3.2","title":"网络通信故障处理预案","description":"制定网络通信故障的应急处理预案"},{"id":"5.3.3","title":"前端设备故障处理预案","description":"制定前端设备故障的应急处理预案"}]},{"id":"5.4","title":"应急演练与评估","description":"建立应急演练和评估机制","children":[{"id":"5.4.1","title":"应急演练计划","description":"制定定期应急演练计划，提高应急处理能力"},{"id":"5.4.2","title":"演练效果评估","description":"建立演练效果评估机制，持续改进应急处理能力"},{"id":"5.4.3","title":"预案持续优化","description":"根据演练结果和实际情况，持续优化应急预案"}]}]},{"id":"6","title":"人员稳定性保障措施","description":"制定完整、切实可行的人员稳定性保障措施","children":[{"id":"6.1","title":"人员管理制度","description":"建立完善的人员管理制度","children":[{"id":"6.1.1","title":"人员招聘与选拔","description":"制定科学的人员招聘与选拔机制，确保人员质量"},{"id":"6.1.2","title":"薪酬福利体系","description":"建立有竞争力的薪酬福利体系，提高员工满意度"},{"id":"6.1.3","title":"职业发展通道","description":"设计清晰的职业发展通道，增强员工归属感"}]},{"id":"6.2","title":"人员激励措施","description":"制定有效的人员激励措施","children":[{"id":"6.2.1","title":"绩效考核机制","description":"建立科学的绩效考核机制，激发员工工作积极性"},{"id":"6.2.2","title":"奖惩制度","description":"制定合理的奖惩制度，引导员工行为"},{"id":"6.2.3","title":"团队建设活动","description":"组织丰富的团队建设活动，增强团队凝聚力"}]},{"id":"6.3","title":"人员替换机制","description":"建立规范的人员替换机制","children":[{"id":"6.3.1","title":"人员替换流程","description":"制定规范的人员替换流程，确保工作连续性"},{"id":"6.3.2","title":"知识转移机制","description":"建立有效的知识转移机制，保障经验传承"},{"id":"6.3.3","title":"工作交接标准","description":"制定标准化的工作交接规范，确保无缝衔接"}]}]},{"id":"7","title":"定期预防性检查方案","description":"制定细致、全面、可操作性强的定期预防性检查方案","children":[{"id":"7.1","title":"预防性检查体系","description":"建立完整的预防性检查体系","children":[{"id":"7.1.1","title":"检查周期与频率","description":"制定合理的检查周期和频率，确保及时发现问题"},{"id":"7.1.2","title":"检查内容与标准","description":"明确检查内容和标准，确保检查质量"},{"id":"7.1.3","title":"检查方法与工具","description":"采用科学的检查方法和工具，提高检查效率"}]},{"id":"7.2","title":"系统软件检查方案","description":"制定系统软件的定期检查方案","children":[{"id":"7.2.1","title":"平台系统健康检查","description":"制定平台系统健康检查方案，确保系统稳定运行"},{"id":"7.2.2","title":"数据库性能检查","description":"制定数据库性能检查方案，优化数据处理效率"},{"id":"7.2.3","title":"安全漏洞检查","description":"制定安全漏洞检查方案，保障系统安全"}]},{"id":"7.3","title":"硬件设备检查方案","description":"制定硬件设备的定期检查方案","children":[{"id":"7.3.1","title":"监控中心设备检查","description":"制定监控中心设备检查方案，确保设备正常运行"},{"id":"7.3.2","title":"通信链路检查","description":"制定通信链路检查方案，保障数据传输畅通"},{"id":"7.3.3","title":"前端设备检查","description":"制定前端设备检查方案，确保设备状态良好"}]},{"id":"7.4","title":"检查结果处理与改进","description":"建立检查结果处理和持续改进机制","children":[{"id":"7.4.1","title":"问题分级与处理","description":"建立问题分级处理机制，确保问题得到及时解决"},{"id":"7.4.2","title":"改进措施跟踪","description":"建立改进措施跟踪机制，确保改进措施落实到位"},{"id":"7.4.3","title":"检查报告与总结","description":"制定检查报告和总结制度，为决策提供依据"}]}]}]}'
        try:
            # 解析JSON
            outline_data = json.loads(outline)
            if not isinstance(outline_data, dict) or 'outline' not in outline_data:
                yield "错误：无效的outline数据格式"
                return

            # 递归处理outline
            yield "开始处理outline结构...\n"

            # 收集所有处理过程中的消息
            for message in self._process_outline_recursive(outline_data['outline'], "", [], project_overview):
                yield message

            # 重新转换为JSON并返回
            result_json = json.dumps(outline_data, ensure_ascii=False, indent=2)
            yield f"\n处理完成！以下是更新后的outline：\n{result_json}"

        except json.JSONDecodeError as e:
            yield f"JSON解析错误: {str(e)}"
        except Exception as e:
            yield f"处理过程中发生错误: {str(e)}"

    def _process_outline_recursive(self, chapters: list, parent_path: str = "", parent_chapters: list = None, project_overview: str = ""):
        """
        递归处理章节列表

        Args:
            chapters: 章节列表
            parent_path: 父级路径
            parent_chapters: 上级章节列表，用于传递上下文信息
            project_overview: 项目概述信息

        Yields:
            处理过程中的状态消息
        """
        for i, chapter in enumerate(chapters):
            current_path = f"{parent_path}.{i}" if parent_path else str(i)
            chapter_id = chapter.get('id', f'unknown_{i}')
            chapter_title = chapter.get('title', '未命名章节')

            # 检查是否为叶子节点（没有children或children为空）
            is_leaf = 'children' not in chapter or not chapter.get('children', [])

            # 准备当前章节信息
            current_chapter_info = {
                'id': chapter_id,
                'title': chapter_title,
                'description': chapter.get('description', '')
            }

            # 构建完整的上级章节列表
            current_parent_chapters = []
            if parent_chapters:
                current_parent_chapters.extend(parent_chapters)
            current_parent_chapters.append(current_chapter_info)

            if is_leaf:
                # 为叶子节点生成内容
                # 获取同级章节（排除当前章节）
                sibling_chapters = [ch for ch in chapters if ch.get('id') != chapter_id]
                content = self._generate_chapter_content(chapter, parent_path, current_parent_chapters[:-1], sibling_chapters, project_overview)
                if content:
                    chapter['content'] = content
                    yield f"✅ 为章节 {chapter_id} '{chapter_title}' 生成内容完成\n"
                else:
                    yield f"❌ 为章节 {chapter_id} '{chapter_title}' 生成内容失败\n"
            else:
                # 递归处理子章节
                yield f"📁 正在处理章节 {chapter_id} '{chapter_title}' 的子章节...\n"
                for message in self._process_outline_recursive(chapter['children'], current_path, current_parent_chapters, project_overview):
                    yield message

    def _generate_chapter_content(self, chapter: dict, context_path: str = "", parent_chapters: list = None, sibling_chapters: list = None, project_overview: str = "") -> str:
        """
        为单个章节生成内容

        Args:
            chapter: 章节数据
            context_path: 上下文路径
            parent_chapters: 上级章节列表，每个元素包含章节id、标题和描述
            sibling_chapters: 同级章节列表，避免内容重复
            project_overview: 项目概述信息，提供项目背景和要求

        Returns:
            生成的内容字符串
        """
        try:
            chapter_id = chapter.get('id', 'unknown')
            chapter_title = chapter.get('title', '未命名章节')
            chapter_description = chapter.get('description', '')

            # 构建提示词
            system_prompt = """你是一个专业的标书编写专家，负责为投标文件的技术标部分生成具体内容。

要求：
1. 内容要专业、准确，与章节标题和描述保持一致
2. 这是技术方案，不是宣传报告，注意朴实无华，不要假大空
3. 语言要正式、规范，符合标书写作要求，但不要使用奇怪的连接词，不要让人觉得内容像是AI生成的
4. 内容要详细具体，避免空泛的描述
5. 注意避免与同级章节内容重复，保持内容的独特性和互补性
6. 直接返回章节内容，不标题，不要任何额外说明或格式标记
"""

            # 构建上下文信息
            context_info = ""
            
            # 上级章节信息
            if parent_chapters:
                context_info += "上级章节信息：\n"
                for parent in parent_chapters:
                    context_info += f"- {parent['id']} {parent['title']}\n  {parent['description']}\n"
            
            # 同级章节信息（排除当前章节）
            if sibling_chapters:
                context_info += "同级章节信息（请避免内容重复）：\n"
                for sibling in sibling_chapters:
                    if sibling.get('id') != chapter_id:  # 排除当前章节
                        context_info += f"- {sibling.get('id', 'unknown')} {sibling.get('title', '未命名')}\n  {sibling.get('description', '')}\n"

            # 构建用户提示词
            project_info = ""
            if project_overview.strip():
                project_info = f"项目概述信息：\n{project_overview}\n\n"
            
            user_prompt = f"""请为以下标书章节生成具体内容：

{project_info}{context_info if context_info else ''}当前章节信息：
章节ID: {chapter_id}
章节标题: {chapter_title}
章节描述: {chapter_description}

请根据项目概述信息和上述章节层级关系，生成详细的专业内容，确保与上级章节的内容逻辑相承，同时避免与同级章节内容重复，突出本章节的独特性和技术方案的优势。"""

            # 调用AI生成内容
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # 收集所有生成的文本
            full_content = ""
            for chunk in self.stream_chat_completion(messages, temperature=0.7):
                full_content += chunk

            return full_content.strip()

        except Exception as e:
            print(f"生成章节内容时出错: {str(e)}")
            return ""


def get_openai_service() -> OpenAIService:
    """
    获取OpenAI服务实例，使用缓存机制避免重复创建
    
    Returns:
        OpenAIService实例
    """
    # 获取当前配置
    api_key = st.session_state.get('api_key', '')
    base_url = st.session_state.get('base_url', '')
    model_name = st.session_state.get('model_name', 'gpt-3.5-turbo')
    
    if not api_key:
        raise ValueError("请先配置OpenAI API密钥")
    
    # 检查缓存的服务实例是否与当前配置匹配
    cached_service = st.session_state.get('openai_service_instance')
    if (cached_service and 
        cached_service.api_key == api_key and 
        cached_service.base_url == base_url and 
        cached_service.model_name == model_name):
        return cached_service
    
    # 创建新的服务实例并缓存
    new_service = OpenAIService(api_key, base_url, model_name)
    st.session_state.openai_service_instance = new_service
    
    return new_service

def clear_openai_service_cache():
    """清除OpenAI服务缓存"""
    if 'openai_service_instance' in st.session_state:
        del st.session_state.openai_service_instance 