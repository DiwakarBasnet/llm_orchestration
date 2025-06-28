import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

# Environment variable
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not found")

# =============================================
# Tools
@tool
def calculator(expression: str) -> str:
    """
    Performs mathematical calculations including addition, subtraction,
    multiplication, division, exponentiation and parentheses.
    
    Args:
        expression: A valid mathematical expression
    
    Returns:
        The calculated result as a string
    """
    try:
        # expression = expression.strip()
        # if not expression:
        #     return "Calculator Error"
        
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Invalid expression '{expression}' - {str(e)}"

@tool
def statistics(numbers: str) -> str:
    """
    Calculates mean, median and standard deviation for a list of numbers.
    Uses the calculator tool for mathematical operations.
    
    Args:
        numbers: Comma-separated numbers like '1,2,3,4,5'
    
    Returns:
        mean, median, and standard deviation
    """
    try:
        nums = []
        for x in numbers.split(","):
            if x.strip():
                nums.append(float(x))
        if not nums:
            return "Error: empty list of numbers"
        
        n = len(nums)
        
        # Mean calculation
        sum_expr = " + ".join(str(x) for x in nums)
        sum_result = calculator.invoke({"expression": sum_expr})
        
        mean_expr = f"{sum_result} / {n}"
        mean_result = calculator.invoke({"expression": mean_expr})
        
        # Median calculation
        sorted_nums = sorted(nums)
        mid = n // 2
        if n % 2 == 1:
            median_result = sorted_nums[mid]
        else:
            m1, m2 = sorted_nums[mid-1], sorted_nums[mid]
            median_expr = f"({m1} + {m2}) / 2"
            median_result = calculator.invoke({"expression": median_expr})
        
        # Standard deviation calculation
        var_nums = []
        for x in nums:
            temp_expr = f"({x} - {mean_result}) ** 2"
            temp_result = calculator.invoke({"expression": temp_expr})
            var_nums.append(temp_result)

        var_sum_expr = " + ".join(var_nums)
        var_sum = calculator.invoke({"expression": var_sum_expr})
        
        var_expr = f"{var_sum} / {n}"
        var_result = calculator.invoke({"expression": var_expr})

        std_expr = f"({var_result}) ** 0.5"
        std_result = calculator.invoke({"expression": std_expr})

        # Format results
        return (f"Mean: {float(mean_result)}\n"
               f"Median: {median_result}\n"
               f"Standard Deviation: {float(std_result)}")
        
    except Exception as e:
        return f"Error: {str(e)}"


# =============================================
# Langgraph agent setup
class TaskOrchestrator:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.0,
            api_key=api_key
        )
        self.tools = [calculator, statistics]
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
        )
    
    def process_task(self, user_input: str) -> str:
        """
        Process user task and return result
        
        Args:
            user_input: User's task or question
            thread_id: Conversation thread identifier for memory persistence
            
        Returns:
            Agent's response as a string
        """
        try:
            # Create message and run agent
            messages = [HumanMessage(content=user_input)]
            result = self.agent.invoke({"messages": messages})\
            
            # Extract the final message content
            if result and "messages" in result:
                final_message = result["messages"][-1]
                return final_message.content
            else:
                return "No response generated"
                
        except Exception as e:
            return f"Orchestration Error: {str(e)}"


# =============================================
# Demonstration
def run_demo():
    """Run demonstration cases"""
    print("=" * 50)
    print("LANGCHAIN MULTI-AGENT ORCHESTRATION DEMO")
    print("=" * 50)
    
    orchestrator = TaskOrchestrator(api_key=gemini_api_key)

    # Test cases
    test_cases = [
        "Calculate 25 * 4 + 100",
        "Calculate statistics for these numbers: 2,4,6,8,10",
        "What are the mean and standard deviation of: 5,10,15,20,25,30?",
        "Calculate 2+2 and then find stats for 1,2,3,4,5"
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test}")
        result = orchestrator.process_task(test)
        print(f"Result: {result}")


if __name__ == "__main__":
    run_demo()
