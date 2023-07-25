from attrs import define
from pydantic import BaseModel


class Flower(BaseModel):
    name: str
    count: int
    cost: int
    id: int = 0



class FlowersRepository:
    flowers: list[Flower]

    def __init__(self):
        self.flowers = []

    def save(self, flower: Flower):
        flower.id = len(self.flowers) + 1
        self.flowers.append(flower)

    def get_by_id(self, id: int) -> Flower:
        for flower in self.flowers:
            if flower.id == id:
                return flower
        return None

    def get_all(self):
        return self.flowers