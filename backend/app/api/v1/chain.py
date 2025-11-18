

from __future__ import annotations

import hashlib
import time
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends,Query
from sqlalchemy.orm import Session
from app.schemas.blockchain import ChainInfoResponse
from app.services.blockchain import BlockchainService
from app.db.base import get_session as get_db
from app.schemas.blockchain import (
    ChainInfoResponse, DonateRequest, DonateResponse,
    BlocksResponse, BlockDetail, TxByDonateResponse,
    BlockSummary, ChainTransactionInfo
)

router = APIRouter(prefix="/api/v1/chain", tags=["chain"])


# ======= 简单内存链状态：先跑通接口，后面再换成数据库模型 =======

class _ChainState:
    def __init__(self) -> None:
        # blocks: 每个 block 包含 height/hash/prev_hash/timestamp/txs 等字段
        self.blocks: List[Dict[str, Any]] = []
        self.total_amount: float = 0.0
        self.total_txs: int = 0

    @property
    def height(self) -> int:
        if not self.blocks:
            return 0
        return self.blocks[-1]["height"]

    def _calc_hash(self, payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _now_ts(self) -> int:
        return int(time.time())

    def init_genesis(self) -> None:
        """初始化创世块（如果还没有任何区块）"""
        if self.blocks:
            return
        ts = self._now_ts()
        genesis_payload = f"genesis-{ts}"
        genesis_hash = self._calc_hash(genesis_payload)
        self.blocks.append(
            {
                "height": 1,
                "hash": genesis_hash,
                "prev_hash": "0x0",
                "timestamp": ts,
                "txs": [],
                "meta": {"note": "genesis block (示例数据)"},
            }
        )

    def append_donate_tx(
        self,
        project_id: int,
        amount: float,
        donor: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> Dict[str, Any]:
        """新增一笔捐赠交易，并打包成一个新区块（简化版）。"""
        if amount <= 0:
            raise ValueError("amount 必须大于 0")

        # 确保有创世块
        self.init_genesis()

        ts = self._now_ts()
        prev_block = self.blocks[-1]
        height = prev_block["height"] + 1

        tx = {
            "tx_index": 0,
            "project_id": project_id,
            "amount": amount,
            "donor": donor,
            "remark": remark,
            "timestamp": ts,
        }

        payload = f"{height}-{prev_block['hash']}-{project_id}-{amount}-{donor}-{ts}"
        block_hash = self._calc_hash(payload)

        block = {
            "height": height,
            "hash": block_hash,
            "prev_hash": prev_block["hash"],
            "timestamp": ts,
            "txs": [tx],
            "meta": {
                "type": "donate_block",
                "project_id": project_id,
            },
        }
        self.blocks.append(block)

        # 更新链统计
        self.total_amount += amount
        self.total_txs += 1

        return block

    def get_block_by_height(self, height: int) -> Optional[Dict[str, Any]]:
        for b in self.blocks:
            if b["height"] == height:
                return b
        return None


CHAIN = _ChainState()


# =============== API 定义 ===============


@router.get("/info")
async def get_chain_info() -> Dict[str, Any]:
    """
    获取当前链的概况：高度、总捐赠笔数、总金额、最新区块哈希等。
    """
    CHAIN.init_genesis()
    latest_block = CHAIN.blocks[-1] if CHAIN.blocks else None
    return {
        "height": CHAIN.height,
        "blocks": len(CHAIN.blocks),
        "total_txs": CHAIN.total_txs,
        "total_amount": CHAIN.total_amount,
        "latest_hash": latest_block["hash"] if latest_block else None,
        "latest_timestamp": latest_block["timestamp"] if latest_block else None,
    }


@router.post("/tx/donate")
async def donate_tx(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    发起一笔捐赠交易，并生成新区块（简化版“上链”过程）。

    请求示例（前端可按需调整字段名）：
    {
      "project_id": 1,
      "amount": 100.5,
      "donor": "alice",      # 可选：当前登录用户名
      "remark": "支持一下"   # 可选
    }
    """
    project_id = payload.get("project_id")
    amount = payload.get("amount")
    donor = payload.get("donor")
    remark = payload.get("remark")

    if project_id is None or amount is None:
        raise HTTPException(status_code=400, detail="project_id 和 amount 为必填字段")

    try:
        amount_value = float(amount)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="amount 必须是数字")

    try:
        block = CHAIN.append_donate_tx(
            project_id=int(project_id),
            amount=amount_value,
            donor=donor,
            remark=remark,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    tx = block["txs"][0]
    return {
        "block_height": block["height"],
        "block_hash": block["hash"],
        "prev_hash": block["prev_hash"],
        "tx": tx,
        "chain_height": CHAIN.height,
        "total_txs": CHAIN.total_txs,
        "total_amount": CHAIN.total_amount,
    }


@router.get("/blocks")
async def list_blocks(
    offset: int = 0,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    简单列出区块列表，支持 offset/limit 分页（纯内存）。
    """
    CHAIN.init_genesis()
    total = len(CHAIN.blocks)
    start = max(0, offset)
    end = min(total, start + max(1, limit))
    items = CHAIN.blocks[start:end]

    # 为列表视图做一个轻量 summary
    def to_summary(b: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "height": b["height"],
            "hash": b["hash"],
            "prev_hash": b["prev_hash"],
            "timestamp": b["timestamp"],
            "tx_count": len(b.get("txs", [])),
            "meta": b.get("meta") or {},
        }

    return {
        "total": total,
        "offset": start,
        "limit": limit,
        "items": [to_summary(b) for b in items],
    }


@router.get("/blocks/{height}")
async def get_block(height: int) -> Dict[str, Any]:
    """
    查看某一个具体高度的区块详情（含交易列表）。
    """
    CHAIN.init_genesis()
    block = CHAIN.get_block_by_height(height)
    if not block:
        raise HTTPException(status_code=404, detail="区块不存在")

    return block




@router.get("/info", response_model=ChainInfoResponse)
async def get_chain_info(db: Session = Depends(get_db)):
    """获取链的整体状态信息"""
    chain_info = BlockchainService.get_chain_info(db)
    return ChainInfoResponse(**chain_info)


@router.post("/tx/donate", response_model=DonateResponse)
async def donate_to_chain(
        request: DonateRequest,
        db: Session = Depends(get_db)
):
    """捐赠上链"""
    try:
        # 添加捐赠到区块链
        block, transaction = BlockchainService.add_donation_to_chain(
            db=db,
            project_id=request.project_id,
            amount=request.amount,
            donor_username=request.donor_username,
            remark=request.remark,
            external_donate_id=request.external_donate_id
        )

        # 获取最新链信息用于响应
        chain_info = BlockchainService.get_chain_info(db)

        return DonateResponse(
            block_height=block.height,
            block_hash=block.block_hash,
            tx_id=transaction.id,
            tx_hash=transaction.tx_hash,
            chain_height=chain_info["height"],
            total_txs=chain_info["total_txs"],
            total_amount=chain_info["total_amount"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上链失败: {str(e)}")


@router.get("/blocks", response_model=BlocksResponse)
async def get_blocks(
        offset: int = Query(0, ge=0, description="偏移量"),
        limit: int = Query(10, ge=1, le=100, description="每页数量"),
        db: Session = Depends(get_db)
):
    """分页查询区块列表"""
    total, blocks = BlockchainService.get_blocks_paginated(db, offset, limit)

    items = []
    for block in blocks:
        items.append(BlockSummary(
            height=block.height,
            block_hash=block.block_hash,
            prev_hash=block.prev_hash,
            timestamp=block.timestamp,
            tx_count=block.tx_count,
            total_amount_in_block=block.total_amount_in_block,
            project_ids=block.project_id_summary,
            meta=block.raw_metadata
        ))

    return BlocksResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=items
    )


@router.get("/blocks/{height}", response_model=BlockDetail)
async def get_block_detail(
        height: int,
        db: Session = Depends(get_db)
):
    """根据高度查询区块详情"""
    block = BlockchainService.get_block_by_height(db, height)
    if not block:
        raise HTTPException(status_code=404, detail=f"区块高度 {height} 不存在")

    # 获取区块内的所有交易
    txs = []
    for tx in block.transactions:
        txs.append(ChainTransactionInfo(
            id=tx.id,
            project_id=tx.project_id,
            donor_username=tx.donor_username,
            amount=tx.amount,
            remark=tx.remark,
            tx_hash=tx.tx_hash,
            tx_index=tx.tx_index,
            timestamp=tx.timestamp,
            external_donate_id=tx.external_donate_id
        ))

    return BlockDetail(
        height=block.height,
        block_hash=block.block_hash,
        prev_hash=block.prev_hash,
        timestamp=block.timestamp,
        tx_count=block.tx_count,
        total_amount_in_block=block.total_amount_in_block,
        meta=block.raw_metadata,
        txs=txs
    )


@router.get("/tx/by-donate/{donate_id}", response_model=TxByDonateResponse)
async def get_transaction_by_donate_id(
        donate_id: int,
        db: Session = Depends(get_db)
):
    """通过业务侧捐赠ID查询上链状态"""
    transaction = BlockchainService.get_transaction_by_donate_id(db, donate_id)

    if not transaction:
        return TxByDonateResponse(found=False)

    return TxByDonateResponse(
        found=True,
        block_height=transaction.block.height,
        tx_hash=transaction.tx_hash,
        tx_id=transaction.id,
        amount=transaction.amount,
        timestamp=transaction.timestamp
    )