from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import logging
from shared.services.tools.variables import names_services

logger = logging.getLogger(__name__)

class WSManager:
    def __init__(self, user_id: str | int, service: str):
        self.user_conns: dict[str | int, set[WebSocket]] = defaultdict(set)
        self.user_id = user_id
        if service.upper() in names_services:
            self.service = service
        else:
            logger.error(f"Сервис {service} не найден")
            raise ValueError(f"Unknown service: {service}")

    async def connect(self, user_id: str | int | None, ws: WebSocket):
        if not user_id:
            user_id = self.user_id
        
        await ws.accept()
        self.user_conns[user_id].add(ws)
        logger.info(f"Пользователь {user_id} сервиса {self.service} был подключен")

    async def disconnect(self, user_id: str | int | None, ws: WebSocket):
        if not user_id:
            user_id = self.user_id
          
        conns = self.user_conns.get(user_id)
        if conns:
            conns.discard(ws)
            if not conns:
                self.user_conns.pop(user_id, None)
        try:
            await ws.close()
        except Exception:
            pass
        logger.info(f"Пользователь {user_id} сервиса {self.service} был отключен")
        
    async def disconnect_all_users(self):
        snapshot = {uid: (ws_set) for uid, ws_set in self.user_conns.items()}
        user_ids = list(snapshot.keys())

        for uid, ws_set in snapshot.items():
            for ws in ws_set:
                try:
                    await ws.close()
                except Exception:
                    pass
            self.user_conns.pop(uid, None)
        logger.info(f"Все пользователи сервиса {self.service} были отключены: {user_ids}")

    def check_found_user(self, user_id: str | int) -> bool | set[WebSocket]:
        ws_set = self.user_conns.get(user_id)
        if not ws_set:
            logger.warning(f"Пользователь {user_id} сервиса {self.service} не найден в активных соединениях")
            return False
        return ws_set

    async def send_to_users(self, user_ids: list[int | str] | None, payload: dict):
        dead: list[tuple[int | str, WebSocket]] = []
        if not user_ids:
            user_ids = self.user_conns

        for uid in user_ids:
            ws_set = self.check_found_user(uid)
            if not ws_set:
                continue

            for user_ws in list(ws_set):
                try:
                    await user_ws.send_json(payload)
                except WebSocketDisconnect:
                    dead.append((uid, user_ws))
                except Exception:
                    dead.append((uid, user_ws))

        for uid_dead, ws_dead in dead:
            await self.disconnect(uid_dead, ws_dead)
            
        logger.info(f"Отправлено сообщение пользователям сервиса {self.service}: адресатов={len(user_ids)}, отключено по ошибке={len(dead)}")
        