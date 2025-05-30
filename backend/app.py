import os 
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from googlesearch import search
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from concurrent.futures import ThreadPoolExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_redis import RedisChatMessageHistory
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.responses import StreamingResponse
import json


load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv('GENAI_API_KEY')
if not api_key:
    raise ValueError("GENAI_API_KEY environment variable is not set")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)
llm_classifier = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=api_key)
REDIS_URL = os.getenv("REDIS_URL")
print(f"Connecting to Redis at: {REDIS_URL}")

class QuestionRequest(BaseModel):
    question: str

async def async_search(query: str, num_results: int = 3):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        urls = await loop.run_in_executor(
            pool, lambda: list(search(f"{query} site:vivita.vn/", num_results=num_results, unique=True))
        )
    return urls

async def fetch_content(url: str, session: ClientSession) -> str:
    try:
        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find("h1").text.strip() if soup.find("h1") else "Không tìm thấy tiêu đề"
            # Lấy giá bán
            price = ""
            price_tag = soup.find(class_="product-price") or soup.find(class_="price") or soup.find("span", class_="woocommerce-Price-amount")
            if price_tag:
                price = price_tag.get_text(strip=True)
            # Lấy nội dung chính
            content = soup.find("div", attrs={"class": "product-description"}) or soup.find("div", attrs={"class": "content"})
            content_text = content.text.strip() if content else ""
            # Lấy thêm thông tin từ bảng (table)
            table_text = ""
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all(["td", "th"])
                    row_text = " | ".join(col.get_text(strip=True) for col in cols)
                    table_text += row_text + "\n"
            # Lấy thêm thông tin từ danh sách (ul, li)
            ul_text = ""
            uls = soup.find_all("ul")
            for ul in uls:
                items = ul.find_all("li")
                for item in items:
                    ul_text += "- " + item.get_text(strip=True) + "\n"
            # Gộp tất cả lại
            full_content = f"{title}\nGiá bán: {price}\n{content_text}\n{table_text}\n{ul_text}\n"
            full_content = full_content.replace("\n\n", "\n").strip()
            return full_content
    except Exception as e:
        return "bạn hãy trả lời theo ý của bạn nhé"
    
async def get_content(query: str) -> str:
    urls = await async_search(query, num_results=3)
    contents = ""
    async with ClientSession() as session:
        tasks = [fetch_content(url, session) for url in urls]
        results = await asyncio.gather(*tasks)
        contents = "\n".join(results)
    return contents, urls


system_template = """
            Bạn là "Vivita Assistant", trợ lý tư vấn sản phẩm tại Vivita, hỗ trợ khách hàng với các câu hỏi về sản phẩm và dịch vụ. Hãy trả lời bằng tiếng Việt, chỉ được sử dụng thông tin sản phẩm được cung cấp và định dạng đầu ra bằng Markdown. Khi ngoài phạm vi kiến thức, lịch sự từ chối trả lời. Xưng "em" và gọi khách là anh/chị.
                Kịch bản trả lời:
                Chào khách hàng (VD: "Vivita cảm ơn câu hỏi của anh/chị, em xin trả lời như sau : ").
                Giải đáp thắc mắc:
                Xác định sản phẩm/dịch vụ (nếu cần): Xác nhận và giải thích rõ về sản phẩm/dịch vụ.
                Tính năng và lợi ích (nếu cần): Mô tả chi tiết các tính năng và lợi ích của sản phẩm.
                Hướng dẫn sử dụng (nếu có): Hướng dẫn chi tiết cách sử dụng sản phẩm.
                Khuyến nghị và tư vấn (nếu cần): Đưa ra khuyến nghị phù hợp với nhu cầu của khách hàng.
                Đề nghị khách hỏi thêm hoặc đề nghị khách liên hệ trực tiếp với Vivita nếu cần thêm thông tin.
                Khi nói về sản phẩm, bạn phải nói về sản phẩm của Vivita, không phải là bất kì sản phẩm nào khác.
                
                Lưu ý:
                - Không trả lời câu hỏi ngoài phạm vi sản phẩm và dịch vụ của Vivita.
                - Lịch sự từ chối trả lời câu hỏi không liên quan.
                - Không trả lời câu hỏi về chính trị, tôn giáo, giới tính, chủng tộc, v.v.
                - Không trả lời câu hỏi về sản phẩm của đối thủ cạnh tranh.
                - Không trả lời câu hỏi về giá cả cụ thể, chất lượng dịch vụ so sánh, v.v.
                - Không trả lời câu hỏi về thông tin cá nhân của khách hàng.
                - Không trả lời bằng tiếng Anh trừ trường hợp cần thiết.
                Sau đây là thông tin sản phẩm được cung cấp:
                {content}

            """



system_query = """
                Giả sử bạn là chuyên gia xác thực câu hỏi về sản phẩm, bạn hãy trả lời câu hỏi sau có phải là câu hỏi về sản phẩm không?
                câu hỏi về sản phẩm là câu hỏi liên quan đến tính năng, công dụng, cách sử dụng, thành phần, lợi ích, so sánh sản phẩm, v.v.
                Nếu câu hỏi là về sản phẩm thì hãy trả về "product", nếu không phải thì trả về "normal"
                Lưu ý không giải thiết câu hỏi, chỉ trả lời "product" hoặc "normal".
                Sau đây là câu hỏi:
                {human_question}
                """

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_template), 
        MessagesPlaceholder(variable_name="history"),
        ("human", "{human_question}"),
    ]
)

prompt_query = ChatPromptTemplate.from_messages(
    [
        ("system", system_query), 
        ("human", "{human_question}"),
    ]
)

def get_redis_history(session_id: str) -> BaseChatMessageHistory:
    return RedisChatMessageHistory(session_id, redis_url=REDIS_URL)

chain = prompt_template | llm

chain_with_history = RunnableWithMessageHistory(
    chain, get_redis_history, input_messages_key="human_question", history_messages_key="history"
)

chain_query = prompt_query | llm_classifier


@app.get("/")
async def home():
    return {"message": "Chào mừng đến với Vivita Assistant!"}


@app.post("/ask")
async def ask(request: QuestionRequest):
    try:
        user_input = request.question
        if not user_input:
            raise HTTPException(status_code=400, detail="Question is required")

        session_id = "admin_123"
        reference_urls = []

        verify_input = await chain_query.ainvoke({"human_question": user_input})
        print(verify_input)
        is_product_question = verify_input.content.strip().lower() == "product"

        content = ""
        if is_product_question:
            content_text, reference_urls = await get_content(user_input)
            content = content_text
        else:
            content = "Xin lỗi, tôi chỉ có thể tư vấn về các sản phẩm và dịch vụ của Vivita. Vui lòng đặt câu hỏi về sản phẩm để em hỗ trợ nhé!"
            reference_urls = []
        
        response_content = ""
        async for chunk in chain_with_history.astream(
            {"content": content, "human_question": user_input},
            config={"configurable": {"session_id": session_id}}
        ):
            response_content += chunk.content
        
        return {"answer": response_content, "reference_urls": reference_urls}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception occurred: {str(e)}") 