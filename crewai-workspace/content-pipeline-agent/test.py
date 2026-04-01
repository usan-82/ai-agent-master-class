from typing import List
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from crewai.agent import Agent
from crewai import LLM
from pydantic import BaseModel
from tools import web_search_tool
from seo_crew import SeoCrew
from virality_crew import ViralityCrew

class MyFirstFlowState(BaseModel):

    user_id: int = 1
    is_admin: bool = False


class MyFirstFlow(Flow[MyFirstFlowState]): 

    @start()
    def first(self): 
        print('(1)first >>>>>>>>>>>>>>>>')
        print(self.state.user_id)
        print(self)
        print('(1)first <<<<<<<<<<<<<<<<')

    @listen(first)
    def second(self):
        print('(2)second >>>>>>>>>>>>>>>>')
        print(self)
        self.state.user_id = 2
        print('(2)second <<<<<<<<<<<<<<<<')

    @listen(first)
    def third(self):
        print('(3)third >>>>>>>>>>>>>>>>')
        print(self)
        print('(3)third <<<<<<<<<<<<<<<<')


    @listen(and_(second, third))
    def final(self):
        print("♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦♦")

    @router(final)
    def route(self):
        if self.state.is_admin == 2:
            return 'even'
        else:
            return 'odd'
    

    @listen('even')
    def handle_even(self):
        print("even")

    @listen("odd")
    def handle_odd(self):
        print("odd")

flow = MyFirstFlow()

flow.plot()
flow.kickoff()