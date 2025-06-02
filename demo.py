from smolagents import CodeAgent, LiteLLMModel, MCPClient, GradioUI
import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)

def main():
    print("🚀 Đang khởi động  MCP Client...")
    
    # Tạo model
    model = LiteLLMModel(
        model_id='openrouter/google/gemini-2.0-flash-001',
        temperature=0.2,
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    
    server_url = "http://127.0.0.1:7860/mcp"  
    # Thử kết nối với cấu hình tối giản
    try:    
        # Config
        mcp_config = {
            "url": server_url,
            "transport": "streamable-http"
        }
          
        with MCPClient(mcp_config) as tools:
            print("✅ Kết nối MCP thành công!")
            
            # Tạo agent
            agent = CodeAgent(tools=tools, model=model)
            # Khởi động UI 
            ui = GradioUI(agent)
            ui.launch(
                server_name="127.0.0.1",
                server_port=8000,
                share=False
            )
            
    except Exception as e:
        print(f"❌ Lỗi khi kết nối: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    main()