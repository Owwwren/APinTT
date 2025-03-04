from aiogram.fsm.state import StatesGroup, State

class Status(StatesGroup):
    CreateSoft_name = State()
    OpenSoftSettings = State()
    OpenSoftSettingsTargetMod = State()
    OpenSoft = State()
    test = State()
