import logging
import os
import argparse
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Literal
from fastmcp import FastMCP
from opendeepsearch.ods_agent import OpenDeepSearchAgent
from dotenv import load_dotenv
import wolframalpha
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

parser = argparse.ArgumentParser(description='Chạy ODS server')
parser.add_argument('--model-name',
                    default=os.getenv("LITELLM_SEARCH_MODEL_ID", "openrouter/google/gemini-2.0-flash-001"),
                    help='Tên model cho tìm kiếm')
parser.add_argument('--orchestrator-model',
                    default=os.getenv("LITELLM_ORCHESTRATOR_MODEL_ID", "openrouter/google/gemini-2.0-flash-001"),
                    help='Tên model cho điều phối')
parser.add_argument('--reranker',
                    choices=['jina', 'infinity'],
                    default='jina',
                    help='Reranker sử dụng (jina hoặc infinity)')
parser.add_argument('--search-provider',
                    choices=['serper', 'searxng'],
                    default='serper',
                    help='Nhà cung cấp tìm kiếm (serper hoặc searxng)')
parser.add_argument('--searxng-instance',
                    help='URL instance SearXNG (bắt buộc nếu search-provider là searxng)')
parser.add_argument('--searxng-api-key',
                    help='API key SearXNG (tùy chọn)')
parser.add_argument('--serper-api-key',
                    default=os.getenv("SERPER_API_KEY"),
                    help='API key Serper')
parser.add_argument('--openai-base-url',
                    default=os.getenv("OPENAI_BASE_URL"),
                    help='URL cơ sở OpenAI API')
parser.add_argument('--server-port',
                    type=int,
                    default=int(os.getenv("SERVER_PORT", 7860)),
                    help='Cổng chạy server')

args = parser.parse_args()

# Kiểm tra tham số
if args.search_provider == 'searxng' and not args.searxng_instance:
    logger.error("❌ SearXNG instance URL là bắt buộc khi sử dụng search-provider searxng")
    exit(1)

mcp = FastMCP(name="OpenDeepSearchServer")
search_agent = None

def initialize_search_agent():
    """Khởi tạo OpenDeepSearch agent với các tham số đã cho."""
    global search_agent
    try:
        search_agent = OpenDeepSearchAgent(
            model=args.model_name,
            reranker=args.reranker,
            search_provider=args.search_provider,
            serper_api_key=args.serper_api_key,
            searxng_instance_url=args.searxng_instance,
            searxng_api_key=args.searxng_api_key
        )
        logger.info("✅ Search agent đã được khởi tạo thành công")
    except Exception as e:
        logger.error(f"❌ Lỗi khi khởi tạo search agent: {str(e)}")
        raise

@mcp.tool()
def search_tool(query: str, max_sources: int = 2, pro_mode: bool = False) -> str:
    """
    Performs a web search and builds a context from the search results.
    """
    global search_agent
    if search_agent is None:
        initialize_search_agent()

    try:
        answer = search_agent.ask_sync(
            query=query,
            max_sources=max_sources,
            pro_mode=pro_mode
        )
        logger.info(f"🔍 Tìm kiếm thành công cho query: {query}")
        return answer
    except Exception as e:
        logger.error(f"❌ Lỗi khi thực hiện tìm kiếm: {str(e)}")
        return f"Lỗi khi thực hiện tìm kiếm: {str(e)}"

@mcp.tool()
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(Exception)
)
async def calculate(query: str) -> str:
    """
    Perform computational, mathematical, and real-world queries using Wolfram Alpha.
    """
    wolfram_client = wolframalpha.Client(os.getenv("WOLFRAM_APP_ID"))

    def run_wolfram_query():
        try:
            res = wolfram_client.query(query)
            results = []
            for pod in res.pods:
                if pod.title:
                    for subpod in pod.subpods:
                        if subpod.plaintext:
                            results.append({
                                'title': pod.title,
                                'result': subpod.plaintext
                            })

            formatted_result = {
                'queryresult': {
                    'success': bool(results),
                    'inputstring': query,
                    'pods': [
                        {
                            'title': result['title'],
                            'subpods': [{'title': '', 'plaintext': result['result']}]
                        } for result in results
                    ]
                }
            }

            final_result = "Không tìm thấy kết quả."
            pods = formatted_result.get("queryresult", {}).get("pods", [])

            for pod in pods:
                if pod.get("title") == "Result":
                    subpods = pod.get("subpods", [])
                    if subpods:
                        final_result = subpods[0].get("plaintext", "").strip()
                        break

            if final_result == "Không tìm thấy kết quả." and results:
                final_result = results[0]['result']

            logger.info(f"🧮 Tính toán thành công cho query: {query}")
            return final_result
        except Exception as e:
            logger.error(f"❌ Lỗi khi truy vấn Wolfram Alpha: {str(e)}")
            raise

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        result = await loop.run_in_executor(pool, run_wolfram_query)
    return result

if __name__ == "__main__":
    logger.info(f"🚀 Khởi động ODS server trên port {args.server_port}...")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=args.server_port)