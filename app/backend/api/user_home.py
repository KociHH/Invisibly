from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)