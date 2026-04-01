from crewai.project import CrewBase, agent, task, crew
#### `CrewBase`란 `@agent`, `@task`, `@crew` 데코레이터로 에이전트·작업·크루를 선언할 때 쓰는 기본 클래스다.
from crewai import Agent, Task, Crew
from pydantic import BaseModel


class Score(BaseModel):
    score: int
    reason: str


@CrewBase
#### `@CrewBase` 데코레이터란 이 클래스를 CrewAI 프로젝트 템플릿으로 등록해, 아래 메서드들이 에이전트/태스크 정의로 인식되게 한다.
class SeoCrew:

    @agent
    def seo_expert(self):
        # --- 에이전트 지침 (한글 요약) ---
        # 역할(role): SEO 전문가 — 블로그 글의 검색엔진 최적화를 분석하고, 점수와 상세 근거를 제시한다. 매우 까다롭게 평가해, 과한 고점은 주지 않는다.
        # 목표(goal): 블로그 SEO 분석 후 점수와 이유를 제공한다. 매우 높은 기준을 적용한다.
        # 배경(backstory): 키워드·메타·구조·가독성·검색 의도 등을 보는 숙련 SEO 전문가로 설정된다.
        return Agent(
            role="SEO Specialist",
            goal="Analyze blog posts for SEO optimization and provide a strict score (0-100) with detailed reasoning. Be extremely demanding; avoid inflated scores.",
            backstory="""You are an experienced SEO specialist with expertise in content optimization. 
            You analyze blog posts for keyword usage, meta descriptions, content structure, readability, 
            and search intent alignment to help content rank better in search engines.""",
            verbose=True,
        )

    @task
    def seo_audit(self):
        return Task(
            description="""Analyze the blog post for SEO effectiveness and provide:
            
            1. An SEO score from 0-100 based on:
               - Keyword optimization
               - Title effectiveness
               - Content structure (headers, paragraphs)
               - Content length and quality
               - Readability
               - Search intent alignment
               
            2. A clear reason explaining the score, focusing on:
               - Main strengths (if score is high)
               - Critical weaknesses that need improvement (if score is low)
               - The most important factor affecting the score
            
            Blog post to analyze: {blog_post}
            Target topic: {topic}
            """,
            expected_output="""A Score object with:
            - score: integer from 0-100 rating the SEO quality
            - reason: string explaining the main factors affecting the score""",
            agent=self.seo_expert(),
            output_pydantic=Score, #*** SeoCrew 클래스에 구현된 agent의 마지막 task output이 crew의 전체 output이 됨
        )

    @crew
    def crew(self):
        #### `Crew`란 에이전트들이 태스크를 순서대로(또는 설정대로) 수행하는 실행 단위다. `self.agents`, `self.tasks`는 `@CrewBase`가 모아 둔 목록이다.
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
        )
