from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage


class AssistantState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str

    guardrail_allowed: bool
    guardrail_reason: str
    guardrail_category: str     
    
    
    file_path: str
    file_kind: str           
    file_error: str         
    file_profile: dict  
    
    schema_context: str      
    sql: str                 
    sql_error: str          
    query_result: str       
    
    iteration: int
    llm_calls: int
    final_response: str
    error: str 
    