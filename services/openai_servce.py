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

    def generate_content_single(self, outline: str) -> Generator[str, None, None]:
        """
        递归遍历outline，为叶子节点生成内容

        Args:
            outline: JSON格式的outline字符串

        Yields:
            流式返回处理状态和生成的content
        """
        outline = '{"outline":[{"id":"1","title":"项目总体概述及运维方案11","description":"针对本项目的深刻认识，总体概述清晰、合理，运维方案以及措施先进、成熟完全满足规范要求","children":[{"id":"1.1","title":"项目背景与目标22","description":"分析项目背景，明确项目目标与意义","children":[{"id":"1.1.1","title":"项目背景分析33","description":"分析天津港保税区消防救援支队消防物联网远程监控系统运维服务项目的背景情况"},{"id":"1.1.2","title":"项目目标与意义","description":"明确本项目的目标与实施意义，包括260家联网单位前端设备电池更换等关键任务"}]},{"id":"1.2","title":"项目需求分析","description":"全面分析项目的功能、性能和安全需求","children":[{"id":"1.2.1","title":"功能需求分析","description":"分析消防物联网远程监控系统的功能需求，包括监控中心与IDC机房场地、通讯链路等"},{"id":"1.2.2","title":"性能需求分析","description":"分析系统性能需求，包括固定IP专线带宽、物联网卡流量、视频专线带宽等"},{"id":"1.2.3","title":"安全需求分析","description":"分析系统安全需求，确保数据安全和系统稳定运行"}]},{"id":"1.3","title":"运维服务总体方案","description":"设计全面的运维服务方案，确保系统稳定运行","children":[{"id":"1.3.1","title":"运维服务范围与内容","description":"明确运维服务的范围和具体内容，包括平台软硬件运行维护和前端设备电池更换"},{"id":"1.3.2","title":"运维服务流程设计","description":"设计科学合理的运维服务流程，确保服务高效有序"},{"id":"1.3.3","title":"运维服务质量保障措施","description":"制定运维服务质量保障措施，确保服务质量达标"}]},{"id":"1.4","title":"技术方案概述","description":"概述项目技术方案，包括系统架构和关键技术路线","children":[{"id":"1.4.1","title":"系统架构概述","description":"概述消防物联网远程监控系统的整体架构"},{"id":"1.4.2","title":"关键技术路线","description":"介绍项目采用的关键技术路线和方法"},{"id":"1.4.3","title":"技术创新点","description":"阐述项目中的技术创新点和优势"}]}]},{"id":"8","title":"新增一级","description":"","children":[{"id":"8.1","title":"二级","description":"","children":[{"id":"8.1.1","title":"三级","description":"","children":[]}]}]},{"id":"2","title":"本项目投入人员团队的评价","description":"投标人提供为本项目整体人员配置方案，服务人员的技术实力、服务经验、人员配置评价","children":[{"id":"2.1","title":"人员团队总体构成","description":"描述人员团队的总体构成情况","children":[{"id":"2.1.1","title":"团队规模与结构","description":"介绍团队规模和结构，包括监控中心值守8人、前端设备运维3人、系统软件运维不少于2人"},{"id":"2.1.2","title":"团队专业能力概述","description":"概述团队的整体专业能力和技术水平"},{"id":"2.1.3","title":"团队资质证书情况","description":"介绍团队成员持有的相关资质证书，包括初级消防员证书等"}]},{"id":"2.2","title":"核心技术人员介绍","description":"详细介绍项目核心技术人员情况","children":[{"id":"2.2.1","title":"项目负责人介绍","description":"介绍项目负责人的资质、经验和能力"},{"id":"2.2.2","title":"技术负责人介绍","description":"介绍技术负责人的资质、经验和能力"},{"id":"2.2.3","title":"其他核心技术人员介绍","description":"介绍其他核心技术人员的资质、经验和能力"}]},{"id":"2.3","title":"团队经验与业绩","description":"展示团队的经验与业绩","children":[{"id":"2.3.1","title":"团队类似项目经验","description":"介绍团队在类似项目中的经验"},{"id":"2.3.2","title":"团队过往业绩展示","description":"展示团队的过往业绩和成就"},{"id":"2.3.3","title":"团队专业能力认证","description":"介绍团队成员的专业能力认证情况"}]}]},{"id":"3","title":"人员组织方案及分工职责评价","description":"人员配备方案合理，组织安排完善，经验丰富的组织方案及分工职责","children":[{"id":"3.1","title":"组织架构设计","description":"设计合理的组织架构","children":[{"id":"3.1.1","title":"项目组织架构图","description":"提供清晰的项目组织架构图"},{"id":"3.1.2","title":"管理层级设计","description":"设计合理的管理层级，确保高效管理"},{"id":"3.1.3","title":"协作机制设计","description":"设计有效的团队协作机制"}]},{"id":"3.2","title":"岗位职责划分","description":"明确划分各岗位职责","children":[{"id":"3.2.1","title":"项目经理职责","description":"明确项目经理的职责和权限"},{"id":"3.2.2","title":"技术人员职责","description":"明确技术人员的职责和分工"},{"id":"3.2.3","title":"监控中心值守人员职责","description":"明确监控中心值守人员的职责和工作要求"}]},{"id":"3.3","title":"人员工作流程","description":"设计科学合理的人员工作流程","children":[{"id":"3.3.1","title":"日常工作流程","description":"设计日常工作的流程和规范"},{"id":"3.3.2","title":"应急响应流程","description":"设计应急响应的流程和机制"},{"id":"3.3.3","title":"沟通协调机制","description":"设计团队内外沟通协调的机制"}]}]},{"id":"4","title":"前端硬件设备运维方案","description":"消防物联网前端硬件设备运维，维保、维修方案考虑全面，涵盖所有前端设备","children":[{"id":"4.1","title":"前端设备概况","description":"概述前端设备的情况","children":[{"id":"4.1.1","title":"设备类型与数量统计","description":"统计前端设备的类型和数量，包括用户信息传输装置、压力和液位传感器等"},{"id":"4.1.2","title":"设备分布情况","description":"描述前端设备在空港、海港和临港三个经济区的分布情况"},{"id":"4.1.3","title":"设备运行状态分析","description":"分析前端设备的运行状态和潜在问题"}]},{"id":"4.2","title":"设备维保方案","description":"制定设备维保方案","children":[{"id":"4.2.1","title":"日常巡检方案","description":"制定日常巡检的方案和频次"},{"id":"4.2.2","title":"定期维护方案","description":"制定定期维护的方案和计划"},{"id":"4.2.3","title":"设备更换计划","description":"制定设备更换的计划，特别是电池更换计划"}]},{"id":"4.3","title":"设备维修方案","description":"制定设备维修方案","children":[{"id":"4.3.1","title":"故障诊断流程","description":"设计设备故障的诊断流程"},{"id":"4.3.2","title":"维修响应机制","description":"设计设备维修的响应机制"},{"id":"4.3.3","title":"维修质量保障措施","description":"制定维修质量保障措施"}]},{"id":"4.4","title":"电池更换专项方案","description":"制定电池更换专项方案","children":[{"id":"4.4.1","title":"电池更换计划","description":"制定260家联网单位前端设备电池的详细更换计划"},{"id":"4.4.2","title":"电池更换流程","description":"设计电池更换的具体流程和步骤"},{"id":"4.4.3","title":"更换后测试与验收","description":"设计电池更换后的测试与验收流程"}]}]},{"id":"5","title":"软硬件故障应急处理方案","description":"软硬件故障应急处理方案措施合理性、可行性、指导性高","children":[{"id":"5.1","title":"应急处理总体方案","description":"制定应急处理的总体方案","children":[{"id":"5.1.1","title":"应急处理组织架构","description":"设计应急处理的组织架构"},{"id":"5.1.2","title":"应急响应级别定义","description":"定义不同级别的应急响应"},{"id":"5.1.3","title":"应急处理总体流程","description":"设计应急处理的总体流程"}]},{"id":"5.2","title":"硬件故障应急处理","description":"制定硬件故障的应急处理方案","children":[{"id":"5.2.1","title":"前端设备故障应急处理","description":"制定前端设备故障的应急处理流程"},{"id":"5.2.2","title":"网络设备故障应急处理","description":"制定网络设备故障的应急处理流程"},{"id":"5.2.3","title":"服务器设备故障应急处理","description":"制定服务器设备故障的应急处理流程"}]},{"id":"5.3","title":"软件故障应急处理","description":"制定软件故障的应急处理方案","children":[{"id":"5.3.1","title":"系统软件故障应急处理","description":"制定系统软件故障的应急处理流程"},{"id":"5.3.2","title":"应用软件故障应急处理","description":"制定应用软件故障的应急处理流程"},{"id":"5.3.3","title":"数据库故障应急处理","description":"制定数据库故障的应急处理流程"}]},{"id":"5.4","title":"应急处理保障措施","description":"制定应急处理的保障措施","children":[{"id":"5.4.1","title":"应急备品备件管理","description":"制定应急备品备件的管理方案"},{"id":"5.4.2","title":"应急处理培训与演练","description":"制定应急处理的培训与演练计划"},{"id":"5.4.3","title":"应急处理效果评估","description":"制定应急处理效果的评估方法"}]}]},{"id":"6","title":"人员稳定性保障措施","description":"人员稳定性保障措施非常完整，切实可行","children":[{"id":"6.1","title":"人员管理制度","description":"制定完善的人员管理制度","children":[{"id":"6.1.1","title":"人员招聘与选拔制度","description":"制定项目人员的招聘与选拔制度"},{"id":"6.1.2","title":"人员培训与发展制度","description":"制定项目人员的培训与发展制度"},{"id":"6.1.3","title":"人员考核与激励制度","description":"制定项目人员的考核与激励制度"}]},{"id":"6.2","title":"人员稳定性措施","description":"制定切实可行的人员稳定性措施","children":[{"id":"6.2.1","title":"薪酬福利保障措施","description":"制定项目人员的薪酬福利保障措施"},{"id":"6.2.2","title":"职业发展保障措施","description":"制定项目人员的职业发展保障措施"},{"id":"6.2.3","title":"工作环境保障措施","description":"制定项目人员的工作环境保障措施"}]},{"id":"6.3","title":"人员变更管理","description":"制定人员变更的管理方案","children":[{"id":"6.3.1","title":"人员变更流程","description":"制定项目人员变更的流程和审批机制"},{"id":"6.3.2","title":"人员交接管理","description":"制定项目人员交接的管理方案"},{"id":"6.3.3","title":"人员变更风险控制","description":"制定项目人员变更的风险控制措施"}]}]},{"id":"7","title":"定期预防性检查方案","description":"定期预防性检查方案非常细致、全面，可操作性强","children":[{"id":"7.1","title":"预防性检查总体方案","description":"制定预防性检查的总体方案","children":[{"id":"7.1.1","title":"检查周期与频次","description":"确定预防性检查的周期和频次"},{"id":"7.1.2","title":"检查内容与范围","description":"确定预防性检查的内容和范围"},{"id":"7.1.3","title":"检查标准与方法","description":"确定预防性检查的标准和方法"}]},{"id":"7.2","title":"硬件设备预防性检查","description":"制定硬件设备的预防性检查方案","children":[{"id":"7.2.1","title":"前端设备预防性检查","description":"制定前端设备的预防性检查方案"},{"id":"7.2.2","title":"网络设备预防性检查","description":"制定网络设备的预防性检查方案"},{"id":"7.2.3","title":"服务器设备预防性检查","description":"制定服务器设备的预防性检查方案"}]},{"id":"7.3","title":"软件系统预防性检查","description":"制定软件系统的预防性检查方案","children":[{"id":"7.3.1","title":"系统软件预防性检查","description":"制定系统软件的预防性检查方案"},{"id":"7.3.2","title":"应用软件预防性检查","description":"制定应用软件的预防性检查方案"},{"id":"7.3.3","title":"数据库预防性检查","description":"制定数据库的预防性检查方案"}]},{"id":"7.4","title":"检查结果处理","description":"制定检查结果的处理方案","children":[{"id":"7.4.1","title":"检查记录管理","description":"制定检查记录的管理方案"},{"id":"7.4.2","title":"问题整改跟踪","description":"制定问题整改的跟踪方案"},{"id":"7.4.3","title":"检查效果评估","description":"制定检查效果的评估方法"}]}]}]}'
        try:
            # 解析JSON
            outline_data = json.loads(outline)
            if not isinstance(outline_data, dict) or 'outline' not in outline_data:
                yield "错误：无效的outline数据格式"
                return

            # 递归处理outline
            yield "开始处理outline结构...\n"

            # 收集所有处理过程中的消息
            for message in self._process_outline_recursive(outline_data['outline'], "", []):
                yield message

            # 重新转换为JSON并返回
            result_json = json.dumps(outline_data, ensure_ascii=False, indent=2)
            yield f"\n处理完成！以下是更新后的outline：\n{result_json}"

        except json.JSONDecodeError as e:
            yield f"JSON解析错误: {str(e)}"
        except Exception as e:
            yield f"处理过程中发生错误: {str(e)}"

    def _process_outline_recursive(self, chapters: list, parent_path: str = "", parent_chapters: list = None):
        """
        递归处理章节列表

        Args:
            chapters: 章节列表
            parent_path: 父级路径
            parent_chapters: 上级章节列表，用于传递上下文信息

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
                content = self._generate_chapter_content(chapter, parent_path, current_parent_chapters[:-1])
                if content:
                    chapter['content'] = content
                    yield f"✅ 为章节 {chapter_id} '{chapter_title}' 生成内容完成\n"
                else:
                    yield f"❌ 为章节 {chapter_id} '{chapter_title}' 生成内容失败\n"
            else:
                # 递归处理子章节
                yield f"📁 正在处理章节 {chapter_id} '{chapter_title}' 的子章节...\n"
                for message in self._process_outline_recursive(chapter['children'], current_path, current_parent_chapters):
                    yield message

    def _generate_chapter_content(self, chapter: dict, context_path: str = "", parent_chapters: list = None) -> str:
        """
        为单个章节生成内容

        Args:
            chapter: 章节数据
            context_path: 上下文路径
            parent_chapters: 上级章节列表，每个元素包含章节id、标题和描述

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
2. 内容要有针对性和说服力，突出技术能力和优势
3. 语言要正式、规范，符合标书写作要求
4. 内容要详细具体，避免空泛的描述
5. 直接返回章节内容，不要任何额外说明或格式标记
"""

            # 构建上级章节信息
            parent_info = ""
            if parent_chapters:
                parent_info = "上级章节信息：\n"
                for parent in parent_chapters:
                    parent_info += f"- {parent['id']} {parent['title']}\n  {parent['description']}\n"

            user_prompt = f"""请为以下标书章节生成具体内容：

{parent_info if parent_info else ''}当前章节信息：
章节ID: {chapter_id}
章节标题: {chapter_title}
章节描述: {chapter_description}

请根据上述章节层级关系，生成详细的专业内容，确保与上级章节的内容逻辑相承，突出技术方案的优势和可行性。"""

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