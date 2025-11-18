# schemas/blockchain.py
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Any
from pydantic import BaseModel, Field

class ChainInfoResponse(BaseModel):
    """链信息响应"""
    height: int = Field(description="当前区块高度")
    blocks: int = Field(description="区块总数")
    total_txs: int = Field(description="链上捐赠总笔数")
    total_amount: Decimal = Field(description="链上捐赠总金额")
    latest_hash: Optional[str] = Field(description="最新区块哈希")
    latest_timestamp: Optional[datetime] = Field(description="最新区块时间")

class DonateRequest(BaseModel):
    """捐赠上链请求"""
    project_id: int = Field(description="公益项目ID")
    amount: Decimal = Field(gt=0, description="捐赠金额")
    donor_username: Optional[str] = Field(None, description="捐赠者用户名")
    remark: Optional[str] = Field(None, max_length=500, description="备注")
    external_donate_id: Optional[int] = Field(None, description="关联业务侧捐赠记录ID")

class DonateResponse(BaseModel):
    """捐赠上链响应"""
    block_height: int = Field(description="区块高度")
    block_hash: str = Field(description="区块哈希")
    tx_id: int = Field(description="交易ID")
    tx_hash: str = Field(description="交易哈希")
    chain_height: int = Field(description="当前链高度")
    total_txs: int = Field(description="链上总交易数")
    total_amount: Decimal = Field(description="链上总金额")

class ChainTransactionInfo(BaseModel):
    """链上交易信息"""
    id: int
    project_id: int
    donor_username: Optional[str]
    amount: Decimal
    remark: Optional[str]
    tx_hash: str
    tx_index: int
    timestamp: datetime
    external_donate_id: Optional[int]

class BlockSummary(BaseModel):
    """区块摘要"""
    height: int
    block_hash: str
    prev_hash: Optional[str]
    timestamp: datetime
    tx_count: int
    total_amount_in_block: Decimal
    project_ids: Optional[str]
    meta: Optional[Any]

class BlocksResponse(BaseModel):
    """区块列表响应"""
    total: int
    offset: int
    limit: int
    items: List[BlockSummary]

class BlockDetail(BaseModel):
    """区块详情"""
    height: int
    block_hash: str
    prev_hash: Optional[str]
    timestamp: datetime
    tx_count: int
    total_amount_in_block: Decimal
    meta: Optional[Any]
    txs: List[ChainTransactionInfo]

class TxByDonateResponse(BaseModel):
    """通过捐赠ID查询交易响应"""
    found: bool
    block_height: Optional[int]
    tx_hash: Optional[str]
    tx_id: Optional[int]
    amount: Optional[Decimal]
    timestamp: Optional[datetime]