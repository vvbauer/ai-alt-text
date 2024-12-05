import os
import re
import base64
import logging as log
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


log.basicConfig(filename='alt_ai_text.log',
                filemode='a',
                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S',
                level=log.DEBUG)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_answer_from_gpt(image_url, context, its_a_file=False):
    load_dotenv()
    api_key = os.getenv("API_key")
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user",
             "content": [
                 {"type": "text", "text": f"Проанализируй картинку и составь для нее ALT-текст в контексте новости: {context}"},
                 {"type": "image_url",
                  "image_url": {"url": f"{image_url}",},
                },
                ],
            }
        ],
        # max_tokens=300,
    )
    return response.choices[0].message.content


@app.get("/api/v1/get_alt_from_url")
async def get_alt_from_url(url_to_image: str, context: str):
    regex = r"^https?:\/\/.+\.(jpg|jpeg|png|gif)$"
    if not re.match(regex, url_to_image):
        return JSONResponse(status_code=400, content={"success": False, "error": "Invalid URL"})
    else:
        alt_text = get_answer_from_gpt(image_url=url_to_image, context=context)
        if alt_text == 'error':
            return JSONResponse(status_code=500, content={"success": False, "error": "Internal server error"})
        else:
            return JSONResponse(status_code=200, content={"success": True, "url": url_to_image, "alt_text": alt_text})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)
