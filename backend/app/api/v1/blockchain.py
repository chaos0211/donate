from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.base import get_session as get_db
from app.services.bc import BlockchainService
from app.schemas.bc import BlockResponse, BlockchainInfo

router = APIRouter(prefix="/blockchain", tags=["区块链"])


@router.get("/info", response_model=BlockchainInfo, summary="获取区块链信息")
async def get_blockchain_info(db: AsyncSession = Depends(get_db)):
    """获取区块链基本信息"""
    service = BlockchainService(db)
    return await service.get_blockchain_info()


@router.get("/blocks", response_model=List[BlockResponse], summary="获取区块列表")
async def get_blocks(
        limit: int = Query(10, ge=1, le=100, description="每页数量"),
        offset: int = Query(0, ge=0, description="偏移量"),
        db: AsyncSession = Depends(get_db)
):
    """获取区块列表，按索引倒序排列"""
    service = BlockchainService(db)
    blocks = await service.get_blocks(limit=limit, offset=offset)
    return [BlockResponse.from_orm(block) for block in blocks]


@router.get("/blocks/{block_hash}", response_model=BlockResponse, summary="根据哈希获取区块")
async def get_block_by_hash(
        block_hash: str,
        db: AsyncSession = Depends(get_db)
):
    """根据区块哈希值获取特定区块"""
    service = BlockchainService(db)
    block = await service.get_block_by_hash(block_hash)
    if not block:
        raise HTTPException(status_code=404, detail="区块不存在")
    return BlockResponse.from_orm(block)


@router.get("/latest", response_model=Optional[BlockResponse], summary="获取最新区块")
async def get_latest_block(db: AsyncSession = Depends(get_db)):
    """获取最新的区块"""
    service = BlockchainService(db)
    latest_block = await service.get_latest_block()
    if not latest_block:
        return None
    return BlockResponse.from_orm(latest_block)


@router.post("/validate", response_model=dict, summary="验证区块链")
async def validate_blockchain(db: AsyncSession = Depends(get_db)):
    """验证整个区块链的完整性和有效性"""
    service = BlockchainService(db)
    is_valid = await service.validate_chain()
    return {
        "valid": is_valid,
        "message": "区块链有效" if is_valid else "区块链无效"
    }


@router.post("/genesis", response_model=BlockResponse, summary="创建创世区块")
async def create_genesis_block(db: AsyncSession = Depends(get_db)):
    """创建创世区块（仅在没有任何区块时可用）"""
    service = BlockchainService(db)
    latest_block = await service.get_latest_block()
    if latest_block is not None:
        raise HTTPException(status_code=400, detail="创世区块已存在")

    genesis_block = await service.create_genesis_block()
    return BlockResponse.from_orm(genesis_block)