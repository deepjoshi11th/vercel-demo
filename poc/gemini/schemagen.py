from typing import List

from pydantic import BaseModel


class Model(BaseModel):
    question: str
    answers: List[str]

def main():
    x = Model.model_json_schema()
    print(x)


if __name__ == "__main__":
    main()