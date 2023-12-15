import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from inference import infer_tfidf
from database import base_symptom_list, diseases

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

activities = {}
'''
Format of activity. To cache user activity
{
    user_id:{
        user_id: int,
        history: [
            {
                question_id: str
                question: str
                choices: [str,]
            },...
        ],
        result: str
    },
}

Flow web
-----------------------------------------
user    - get gui 
gui     - show first question
user    - post answer
sys     - cache user's answer to ativity
        - respone to question
...
gui     - show result
-----------------------------------------

Question Schema
-----------------------------------------
1. Xac nhan
3. Hoi trieu chung (base)
    - lay cac trieu chung xuat hien nhieu o cac loai benh
4. Hoi them cac trieu chung (advance)
    - lay cac trieu chung ma chi co duy nhat o mot so benh
-----------------------------------------

Inference Sys
-----------------------------------------
1. Xac nhan
3. -> suy ra duoc van de dang gap phai la ve dinh duong, da, phoi,..
4. -> suy ra duoc can benh cu the
-----------------------------------------
'''
questions = [
    "Mỗi câu hỏi sẽ có xuất hiện các lựa chọn bên phải. Bạn sẽ chọn và nhấn nút gửi đáp án. Bạn đã sẵn sàng sử dụng hệ thống chưa ?",
    "Bạn đang gặp vấn đề gì ?", "Bạn còn bị triệu chứng nào nữa không ?"]
is_multiples = [False, True, True]
choices = [
    ('Đã sẵn sàng',),
    base_symptom_list,
    ('Trieu chung 1', 'Trieu chung 2', 'Trieu chung 3', 'Trieu chung 4')
]

knowledge = []
'''
    [{
        'disease': str,
        'symptoms': [
            {
                'symptom_id': str
                'symptom': str,
            }
        ]
    },
    ]
'''


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    user_id = len(activities)
    start_id = 0
    activities[user_id] = {
        "user_id": user_id,
        "symptoms": [],
        "history": [
            {
                "question_id": start_id,
                "question": questions[start_id],
                "is_multiple": is_multiples[start_id],
                "choices": choices[start_id],
            }
        ],
        "result": None
    }
    return templates.TemplateResponse("index.html", {"request": request, "user_id": user_id})


def most_frequent(List):
    return max(set(List), key=List.count)


@app.post("/users/{user_id}")
async def post_answer(user_id: int, request: Request):
    global knowledge

    data = await request.json()

    activity = activities[user_id]

    next_question_id = len(activity['history'])
    if next_question_id == 1:
        activity['base_symptoms'] = data

    if next_question_id == 2:
        candidate_list = set()
        for base_symptom in data:
            for disease in diseases:
                if base_symptom in disease['base_symptoms']:
                    for symptom in disease['advance_symptoms']:
                        candidate_list.add(symptom)

        choices[2] = list(candidate_list)

    if next_question_id < len(questions):
        activity['history'].append(
            {
                'question_id': next_question_id,
                'question': questions[next_question_id],
                'is_multiple': is_multiples[next_question_id],
                'choices': choices[next_question_id],
            }
        )
    else:
        preds = []
        golds = []
        symtoms = data + activity['base_symptoms']

        for name, score in infer_tfidf(symtoms):

            if score > 0.5:
                preds.append((f'{name} {round(score * 100)}%', score))
            if score > 0.8:
                golds.append((f'{name} {round(score * 100)}%', score))

        preds = sorted(preds, key=lambda x: -x[-1])
        golds = sorted(golds, key=lambda x: -x[-1])

        preds = [x[0] for x in preds]
        golds = [x[0] for x in golds]

        if len(preds) == 0:
            activity['result'] = f"Xin lỗi, tôi không biết bạn đang bị bệnh gì."
        elif len(golds) == 0:
            disease_text = ', '.join(preds)
            activity['result'] = f"Tôi không chắc, nhưng bạn đang có các dấu hiệu của bệnh {disease_text}"
        else:
            diff = list(set(preds).symmetric_difference(set(golds)))
            disease_diff = ', '.join(diff)
            disease_golds = ', '.join(golds)

            if len(diff) == 0:
                activity['result'] = f"Bạn đang mắc bệnh {disease_golds}"
            else:
                activity['result'] = f"Bạn mắc bệnh {disease_golds} và có thể mắc các bệnh sau: {disease_diff}"

    return {
        "user_id": user_id,
        "error": 0,
    }


@app.get("/users/{user_id}")
def get_answer(user_id: int):
    try:
        activity = activities[user_id]
    except:
        return {
            "error": 1
        }

    return {
        "error": 0,
        "data": activity
    }


if __name__ == '__main__':
    os.system('uvicorn server:app --host 0.0.0.0 --port 11001 --reload')
