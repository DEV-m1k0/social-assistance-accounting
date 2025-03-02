import models
from datetime import date
from sqlalchemy.sql import select
from .logging import setup_logging, logging
from typing import *


def get_user_items_by_user_id(user_id: int) -> Optional[Sequence[models.UserItem]]:
    user_items_sql = select(models.UserItem).where(models.UserItem.user_id==user_id)
    with models.Session() as session:
        return session.scalars(user_items_sql).all()
    
def get_all_user_items() -> Sequence[models.UserItem]:
    with models.Session() as session:
        return session.scalars(select(models.UserItem)).all()


class UserItem:
    __USER_ITEM: models.UserItem

    def __init__(self, user_id: int, item_id: int, count: int, date_of_receipt: date):
        self.__USER_ITEM = models.UserItem(user_id=user_id, item_id=item_id,
                                           count=count, date_of_receipt=date_of_receipt)
    
    def get(self) -> models.UserItem:
        return self.__USER_ITEM
    
    def __check_exist_user_by_id(self) -> bool:
        with models.Session() as session:
            user = session.scalar(select(models.User).where(models.User.id==self.__USER_ITEM.user_id))
        if not user:
            return False
        return True
    
    def __check_exist_item_by_id(self) -> bool:
        with models.Session() as session:
            item = session.scalar(select(models.Item).where(models.Item.id==self.__USER_ITEM.item_id))
        if not item:
            return False
        return True
    
    def __check_uniq(self):
        user_items = get_all_user_items()

        for user_item in user_items:
            if  str(self.__USER_ITEM.item_id) == str(user_item.item_id) and\
                str(self.__USER_ITEM.user_id) == str(user_item.user_id) and\
                str(self.__USER_ITEM.count) == str(user_item.count) and\
                str(self.__USER_ITEM.date_of_receipt).split(' ')[0] == str(user_item.date_of_receipt):
                print(False)
                return False

        return True

    def save(self) -> None:
        if self.__check_exist_item_by_id and self.__check_exist_user_by_id and self.__check_uniq():
            try:
                with models.Session() as session:
                    session.add(self.__USER_ITEM)
                    session.commit()
                    logging.info(f"{self.__USER_ITEM} успешно создан")
            except:
                logging.error(f"Произошла ошибка при создании {self.__USER_ITEM}", exc_info=True)
        else:
            logging.warning(f"Пользователя с id={self.__USER_ITEM.user_id} или предмета с id={self.__USER_ITEM.item_id} не существует")