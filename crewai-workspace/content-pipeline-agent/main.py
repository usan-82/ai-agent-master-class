from typing import List
#### `typing.List`란 리스트에 담긴 원소 타입을 표시할 때 쓰는 힌트다. (파이썬 3.9+에서는 `list[str]`처럼 써도 된다.)
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from crewai.agent import Agent
from crewai import LLM
from pydantic import BaseModel, Field
#### `BaseModel`이란 Pydantic이 제공하는 부모 클래스로, 필드 이름·타입을 선언하면 데이터 검증·변환을 도와준다.
from tools import web_search_tool
from seo_crew import SeoCrew
from virality_crew import ViralityCrew


class BlogPost(BaseModel):
    """`BlogPost`는 블로그 한 편의 모양을 고정한 설계도다."""
    title: str
    subtitle: str
    sections: List[str]


class Tweet(BaseModel):
    """트윗 한 건을 문자열 필드로 표현한 모델이다."""
    content: str
    hashtags: str


class LinkedInPost(BaseModel):
    """링크드인 게시물을 hook·본문·CTA로 나눈 모델이다."""
    hook: str
    content: str
    call_to_action: str


class Score(BaseModel):

    score: int = 0
    reason: str = ""


class ContentPipelineState(BaseModel):

    # Inputs
    content_type: str = ""
    topic: str = ""
    make_score_attempt: int | None = Field(default=None, alias="content_make_max_count")
    #### `make_score_attempt`란 “점수 평가를 최대 몇 번 수행할지”를 의미한다. (과거 입력 키 `content_make_max_count`도 alias로 지원)

    model_config = {"populate_by_name": True}

    # Internal
    max_length: int = 0
    research: str = ""
    score: Score | None = None

    # Content
    blog_post: BlogPost | None = None
    tweet: Tweet | None = None
    linkedin_post: LinkedInPost | None = None

    # Remake counters
    blog_remake_count: int = 0
    tweet_remake_count: int = 0
    linkedin_remake_count: int = 0

    # Run config
    max_score_attempts: int = 10

    # Score histories (attempt별 점수 로그용)
    blog_score_history: List[int] = []
    tweet_score_history: List[int] = []
    linkedin_score_history: List[int] = []

    # Latest audit score (리메이크 로그에 직전 점수 표시용)
    latest_audit_score: int | None = None
    latest_audit_reason: str = ""

    # Best snapshot (10회 평가 시 가장 좋은 결과로 강제 종료)
    best_score: int = -1
    best_reason: str = ""
    best_blog_post: BlogPost | None = None
    best_tweet: Tweet | None = None
    best_linkedin_post: LinkedInPost | None = None

    # Usage (간략 로그용: 호출 횟수 + 토큰 추정치)
    llm_call_count: int = 0
    prompt_tokens_est: int = 0
    completion_tokens_est: int = 0


#### `Flow[ContentPipelineState]`란 제네릭 문법으로, 이 플로우가 다루는 상태 타입이 `ContentPipelineState`임을 적어 둔 것이다.
class ContentPipelineFlow(Flow[ContentPipelineState]):
    def _est_tokens(self, text: str) -> int:
        # 토큰사용량 러프하게 추정: 영어/기호 위주 프롬프트 기준 1토큰≈4글자
        return max(1, len(text) // 4) if text else 0

    def _count_llm_usage(self, prompt: str, completion: str) -> None:
        self.state.llm_call_count += 1
        self.state.prompt_tokens_est += self._est_tokens(prompt)
        self.state.completion_tokens_est += self._est_tokens(completion)

    def _log_usage(self, where: str) -> None:
        total = self.state.prompt_tokens_est + self.state.completion_tokens_est
        print(
            f"[USAGE][{where}] calls={self.state.llm_call_count} "
            f"tokens_est≈{total} (prompt≈{self.state.prompt_tokens_est}, completion≈{self.state.completion_tokens_est})"
        )
    def _current_make_attempt(self) -> int:
        ct = self.state.content_type
        if ct == "blog":
            return self.state.blog_remake_count + 1
        if ct == "tweet":
            return self.state.tweet_remake_count + 1
        return self.state.linkedin_remake_count + 1

    def _current_score_attempt(self) -> int:
        ct = self.state.content_type
        if ct == "blog":
            return len(self.state.blog_score_history) + 1
        if ct == "tweet":
            return len(self.state.tweet_score_history) + 1
        return len(self.state.linkedin_score_history) + 1

    def _save_score_history_and_best(self) -> None:
        """현재 self.state.score를 history에 남기고 best 스냅샷을 갱신한다."""
        if self.state.score is None:
            return

        ct = self.state.content_type
        s = int(self.state.score.score)
        self.state.latest_audit_score = s
        self.state.latest_audit_reason = self.state.score.reason or ""

        if ct == "blog":
            self.state.blog_score_history.append(s)
        elif ct == "tweet":
            self.state.tweet_score_history.append(s)
        else:
            self.state.linkedin_score_history.append(s)

        if s > self.state.best_score:
            self.state.best_score = s
            self.state.best_reason = self.state.score.reason or ""
            self.state.best_blog_post = self.state.blog_post
            self.state.best_tweet = self.state.tweet
            self.state.best_linkedin_post = self.state.linkedin_post

    @start() #최초 진입점
    def init_content_pipeline(self):
        #### `self`란 “지금 이 인스턴스 자신”을 가리키는 첫 번째 인자다. 메서드 안에서 `self.state`처럼 쓴다.

        # inputs 검증
        if self.state.content_type not in ["tweet", "blog", "linkedin"]:
            raise ValueError("The content type is wrong.")
        
        if self.state.topic == "":
            raise ValueError("The topic can't be blank.")

        # 점수 평가 최대 횟수 입력 검증 및 반영
        if self.state.make_score_attempt is not None:
            if self.state.make_score_attempt < 1:
                raise ValueError("make_score_attempt must be >= 1.")
            # “점수 평가 최대 횟수”를 주제별로 조절 (평가 N회 보장 기준)
            self.state.max_score_attempts = self.state.make_score_attempt

        # 초기화
        if self.state.content_type == "tweet":
            self.state.max_length = 150
        elif self.state.content_type == "blog":
            self.state.max_length = 800
        elif self.state.content_type == "linkedin":
            self.state.max_length = 500

    @listen(init_content_pipeline)
    def conduct_research(self):
        #### `@listen(...)`란 “앞 단계가 끝나면 이 메서드를 실행하라”는 CrewAI Flow의 연결 표시다.

        researcher = Agent(
            role="Head Researcher",
            backstory="You're like a digital detective who loves digging up fascinating facts and insights. You have a knack for finding the good stuff that others miss.",
            goal=f"Find the most interesting and useful info about {self.state.topic}",
            tools=[web_search_tool],
        )

        self.state.research = researcher.kickoff(
            f"Find the most interesting and useful info about {self.state.topic}"
        )

    @router(conduct_research)
    def conduct_research_router(self):
        #### `@router`란 “이 함수가 반환하는 문자열 값으로 다음에 갈 분기 이름을 고른다”는 뜻이다.
        content_type = self.state.content_type

        if content_type == "blog":
            return "make_blog"
        elif content_type == "tweet":
            return "make_tweet"
        else:
            return "make_linkedin_post"

    # conduct_research 와 같이 agent를 쓰지 않고 output을 강제하면서 AI와 직접 대화하는 방법
    @listen(or_("make_blog", "remake_blog"))
    def handle_make_blog(self):
        #1) state에서 blog 가져오기(empty-able)
        blog_post = self.state.blog_post

        #2) llm call 위한 선언
        llm = LLM(model="openai/o4-mini", response_format=BlogPost)

        #3) llm call
        ## llm에게 요청 시 <research> , =========== 와 같은 기술을 하는 방법은 ai의 이해를 돕기 위한 프롬프트 테크닉
        ### 특히 research start-end 대신 <research>...</research> 와 같이 기술하는 방식은 Claude에서 잘먹힘.
        if blog_post is None:
            prompt = f"""
            Make a blog post with SEO practices on the topic {self.state.topic} using the following research:
            Hard constraint: Keep the total output length within {self.state.max_length} characters.

            <research>
            ================
            {self.state.research}
            ================
            </research>
            """
            result = llm.call(prompt)
            self._count_llm_usage(prompt, result)
            self._log_usage("MAKE_BLOG")
        else:
            self.state.blog_remake_count += 1
            last = (
                f"{self.state.latest_audit_score}/100"
                if self.state.latest_audit_score is not None
                else "N/A"
            )
            print(
                f"[MAKE][BLOG] remake #{self.state.blog_remake_count} "
                f"(last_audit_score={last})"
            )
            reason = self._remake_reason()
            ## 선언문을 self.state.blog_post 에 바로 담지 않고 result 에 담은 후 굳이 ${모델}.model_validate_json(result) 처리하는 이유: 
            ### CrewAI버그로 Model을 String으로 인식하는 케이스가 있어, 검증 후 'Model'을 리턴받기  위한 처리
            prompt = f"""
            You wrote this blog post on {self.state.topic}, but it does not have a good SEO score because of {reason} 
            
            Improve it.
            Hard constraint: Keep the total output length within {self.state.max_length} characters.

            <blog post>
            {self.state.blog_post.model_dump_json()}
            </blog post>

            Use the following research.

            <research>
            ================
            {self.state.research}
            ================
            </research>
            """
            result = llm.call(prompt)
            self._count_llm_usage(prompt, result)
            self._log_usage("REMAKE_BLOG")

        #### `model_validate_json`이란 JSON 문자열을 받아 필드 타입에 맞게 객체로 바꾸는 Pydantic 메서드다.
        self.state.blog_post = BlogPost.model_validate_json(result)

    @listen(or_("make_tweet", "remake_tweet"))
    def handle_make_tweet(self):

        tweet = self.state.tweet

        llm = LLM(model="openai/o4-mini", response_format=Tweet)

        if tweet is None:
            prompt = f"""
            Make a tweet that can go viral on the topic {self.state.topic} using the following research:
            Hard constraint: The combined length of tweet content + hashtags must be within {self.state.max_length} characters.

            <research>
            ================
            {self.state.research}
            ================
            </research>
            """
            result = llm.call(prompt)
            self._count_llm_usage(prompt, result)
            self._log_usage("MAKE_TWEET")
        else:
            self.state.tweet_remake_count += 1
            last = (
                f"{self.state.latest_audit_score}/100"
                if self.state.latest_audit_score is not None
                else "N/A"
            )
            print(
                f"[MAKE][TWEET] remake #{self.state.tweet_remake_count} "
                f"(last_audit_score={last})"
            )
            reason = self._remake_reason()
            prompt = f"""
            You wrote this tweet on {self.state.topic}, but it does not have a good virality score because of {reason} 
            
            Improve it.
            Hard constraint: The combined length of tweet content + hashtags must be within {self.state.max_length} characters.

            <tweet>
            {self.state.tweet.model_dump_json()}
            </tweet>

            Use the following research.

            <research>
            ================
            {self.state.research}
            ================
            </research>
            """
            result = llm.call(prompt)
            self._count_llm_usage(prompt, result)
            self._log_usage("REMAKE_TWEET")

        self.state.tweet = Tweet.model_validate_json(result)

    @listen(or_("make_linkedin_post", "remake_linkedin_post"))
    def handle_make_linkedin_post(self):

        linkedin_post = self.state.linkedin_post

        llm = LLM(model="openai/o4-mini", response_format=LinkedInPost)

        if linkedin_post is None:
            prompt = f"""
            Make a linkedin post that can go viral on the topic {self.state.topic} using the following research:
            Hard constraint: Keep the total output length within {self.state.max_length} characters.

            <research>
            ================
            {self.state.research}
            ================
            </research>
            """
            result = llm.call(prompt)
            self._count_llm_usage(prompt, result)
            self._log_usage("MAKE_LINKEDIN")
        else:
            self.state.linkedin_remake_count += 1
            last = (
                f"{self.state.latest_audit_score}/100"
                if self.state.latest_audit_score is not None
                else "N/A"
            )
            print(
                f"[MAKE][LINKEDIN] remake #{self.state.linkedin_remake_count} "
                f"(last_audit_score={last})"
            )
            reason = self._remake_reason()
            prompt = f"""
            You wrote this linkedin post on {self.state.topic}, but it does not have a good virality score because of {reason} 
            
            Improve it.
            Hard constraint: Keep the total output length within {self.state.max_length} characters.

            <linkedin_post>
            {self.state.linkedin_post.model_dump_json()}
            </linkedin_post>

            Use the following research.

            <research>
            ================
            {self.state.research}
            ================
            </research>
            """
            result = llm.call(prompt)
            self._count_llm_usage(prompt, result)
            self._log_usage("REMAKE_LINKEDIN")

        self.state.linkedin_post = LinkedInPost.model_validate_json(result)

    def _generated_content_char_count(self) -> int:
        ct = self.state.content_type
        if ct == "blog":
            bp = self.state.blog_post
            return (
                len(bp.title)
                + len(bp.subtitle)
                + sum(len(s) for s in bp.sections)
            )
        if ct == "tweet":
            tw = self.state.tweet
            return len(tw.content) + len(tw.hashtags)
        lp = self.state.linkedin_post
        return len(lp.hook) + len(lp.content) + len(lp.call_to_action)

    def _remake_reason(self) -> str:
        """
        score_router 이전(예: max_length 탈락)에서 리메이크 라벨로 들어오면 `self.state.score`가 None일 수 있다.
        그 경우엔 max_length 초과 같은 “길이 관련” 사유로 프롬프트를 구성한다.
        """
        # 1) score 단계가 이미 끝났다면, 점수 reason을 그대로 사용
        if self.state.score is not None and getattr(self.state.score, "reason", None):
            return self.state.score.reason

        # 2) 아직 score가 없다면, 현재 콘텐츠의 길이 상태를 근거로 사용
        try:
            actual = self._generated_content_char_count()
            max_len = self.state.max_length
            if actual > max_len:
                return (
                    f"it exceeds the max length requirement "
                    f"(actual length={actual}, max length={max_len})"
                )
        except Exception:
            pass

        # 3) 그마저도 계산이 안 되면 무난한 일반 사유로 대체
        return "it needs improvement"

    @router(or_(handle_make_blog, handle_make_tweet, handle_make_linkedin_post))
    def max_length_router(self):
        content_type = self.state.content_type
        max_len = self.state.max_length
        actual = self._generated_content_char_count()

        if actual <= max_len:
            if content_type == "blog":
                return "length_ok_blog"
            if content_type == "tweet":
                return "length_ok_tweet"
            return "length_ok_linkedin"
        if content_type == "blog":
            return "remake_blog"
        if content_type == "linkedin":
            return "remake_linkedin_post"
        return "remake_tweet"

    #주제 및 화제성 평가
    @listen("length_ok_blog")
    def check_seo(self):
        # .kickoff_for_each 사용 시 input마다 다양한 산업이나 위치에 대해 crew를 kick off 할 수 있음
        result = (
            SeoCrew()
            .crew()
            .kickoff(
                inputs={
                    "topic": self.state.topic,
                    "blog_post": self.state.blog_post.model_dump_json(),
                }
            )
        )
        #*** SeoCrew 클래스에 구현된 agent의 마지막 task output이 crew의 전체 output이 됨
        
        self.state.score = result.pydantic
        self._save_score_history_and_best()
        print(
            f"[AUDIT][SEO] attempt {self._current_score_attempt()}/{self.state.max_score_attempts} "
            f"score={self.state.score.score}/100"
        )

    @listen(or_("length_ok_tweet", "length_ok_linkedin"))
    def check_virality(self):
        #### 삼항 연산자 `a if 조건 else b`란 조건이 참이면 `a`, 거짓이면 `b`를 고르는 한 줄 분기다.
        result = (
            ViralityCrew()
            .crew()
            .kickoff(
                inputs={
                    "topic": self.state.topic,
                    "content_type": self.state.content_type,
                    "content": (
                        self.state.tweet.model_dump_json()
                        if self.state.content_type == "tweet"
                        else self.state.linkedin_post.model_dump_json()
                    ),
                }
            )
        )
        self.state.score = result.pydantic
        self._save_score_history_and_best()
        print(
            f"[AUDIT][VIRALITY] attempt {self._current_score_attempt()}/{self.state.max_score_attempts} "
            f"score={self.state.score.score}/100"
        )

    @router(or_(check_seo, check_virality))
    def score_router(self):

        content_type = self.state.content_type
        score = self.state.score

        attempt = len(
            self.state.tweet_score_history
            if content_type == "tweet"
            else (
                self.state.blog_score_history
                if content_type == "blog"
                else self.state.linkedin_score_history
            )
        )

        if score.score >= 75:
            return "check_passed"

        if attempt >= self.state.max_score_attempts:
            return "forced_finalize"

        if content_type == "blog":
            return "remake_blog"
        if content_type == "linkedin":
            return "remake_linkedin_post"
        return "remake_tweet"

    @listen("forced_finalize")
    def forced_finalize_content(self):
        print("🧱 Forced finalize (max attempts reached).")
        print(f"🏁 Best score: {self.state.best_score}/100")

        # best 스냅샷으로 되돌린 뒤 종료
        if self.state.content_type == "blog" and self.state.best_blog_post is not None:
            self.state.blog_post = self.state.best_blog_post
        elif self.state.content_type == "tweet" and self.state.best_tweet is not None:
            self.state.tweet = self.state.best_tweet
        elif (
            self.state.content_type == "linkedin"
            and self.state.best_linkedin_post is not None
        ):
            self.state.linkedin_post = self.state.best_linkedin_post

        # forced finalize 상황에선 점수가 85 미만일 수 있으므로, 상태 score도 best로 맞춰 로그 일관성 유지
        self.state.score = Score(score=self.state.best_score, reason=self.state.best_reason)
        return self.finalize_content()

    @listen("check_passed")
    def finalize_content(self):
        """Finalize the content"""
        print("🎉 Finalizing content...")

        if self.state.content_type == "blog":
            print(f"📝 Blog Post: {self.state.blog_post.title}")
            print(f"🔍 SEO Score: {self.state.score.score}/100")
            if self.state.blog_remake_count > 0:
                print(f"🔁 Remake attempts: {self.state.blog_remake_count}")
        elif self.state.content_type == "tweet":
            print(f"🐦 Tweet: {self.state.tweet.content}")
            print(f"🚀 Virality Score: {self.state.score.score}/100")
            if self.state.tweet_remake_count > 0:
                print(f"🔁 Remake attempts: {self.state.tweet_remake_count}")
        elif self.state.content_type == "linkedin":
            print(f"💼 LinkedIn Hook: {self.state.linkedin_post.hook}")
            print(f"🚀 Virality Score: {self.state.score.score}/100")
            if self.state.linkedin_remake_count > 0:
                print(f"🔁 Remake attempts: {self.state.linkedin_remake_count}")

        print("✅ Content ready for publication!")
        return (
            self.state.linkedin_post
            if self.state.content_type == "linkedin"
            else (
                self.state.tweet
                if self.state.content_type == "tweet"
                else self.state.blog_post
            )
        )


flow = ContentPipelineFlow()

#### `kickoff(inputs={...})`란 플로우를 시작하면서 `ContentPipelineState` 필드에 해당하는 초기값을 넘기는 호출이다.
flow.kickoff(
    inputs={
        "content_type": "tweet",
        "topic": "내 몸에 맞는 의자 찾기",
        "content_make_max_count": 10,
    },
)


# flow.plot()
