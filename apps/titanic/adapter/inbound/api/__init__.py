from fastapi import APIRouter

from titanic.adapter.inbound.api.v1.andrews_blueprint_router import andrews_blueprint_router
from titanic.adapter.inbound.api.v1.cal_pistol_router import cal_pistol_router
from titanic.adapter.inbound.api.v1.hartley_violin_router import hartley_violin_router
from titanic.adapter.inbound.api.v1.isidor_bed_router import isidor_bed_router
from titanic.adapter.inbound.api.v1.jack_sketch_router import jack_sketch_router
from titanic.adapter.inbound.api.v1 import james_router as james_router_module
from titanic.adapter.inbound.api.v1.james_router import james_router
from titanic.adapter.outbound.pg.james_pg_repository import JamesPgRepository
from titanic.app.use_cases.james_interactor import JamesInteractor

from titanic.adapter.inbound.api.v1.rose_diamond_router import rose_diamond_router
from titanic.adapter.inbound.api.v1.ruth_corset_router import ruth_corset_router
from titanic.adapter.inbound.api.v1.smith_captain_router import smith_captain_router
from titanic.adapter.inbound.api.v1.walter_router import walter_router

titanic_router = APIRouter(prefix="/titanic", tags=["titanic"])
titanic_router.include_router(james_router)
titanic_router.include_router(walter_router)
titanic_router.include_router(andrews_blueprint_router)
titanic_router.include_router(cal_pistol_router)
titanic_router.include_router(jack_sketch_router)
titanic_router.include_router(isidor_bed_router)
titanic_router.include_router(hartley_violin_router)
titanic_router.include_router(rose_diamond_router)
titanic_router.include_router(ruth_corset_router)
titanic_router.include_router(smith_captain_router)

__all__ = ["titanic_router"]
