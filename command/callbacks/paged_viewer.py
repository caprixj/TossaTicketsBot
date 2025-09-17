from aiogram import Router, F
from aiogram.types import CallbackQuery

from component.paged_viewer.paged_viewer import pmove, phide
from resources import glob

router = Router()


@router.callback_query(F.data.contains(glob.PV_BACK_CALLBACK))
async def pv_back(callback: CallbackQuery):
    await pmove(callback, glob.PV_BACK_CALLBACK)


@router.callback_query(F.data.contains(glob.PV_FORWARD_CALLBACK))
async def pv_forward(callback: CallbackQuery):
    await pmove(callback, glob.PV_FORWARD_CALLBACK)


@router.callback_query(F.data.contains(glob.PV_HIDE_CALLBACK))
async def pv_hide(callback: CallbackQuery):
    await phide(callback)
