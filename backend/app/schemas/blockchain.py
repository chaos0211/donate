from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class BlockBase(BaseModel):
    index: int = Field(..., description="区块索引")
    data: str = Field(..., description="区块数据")
    previous_hash: str = Field(..., description="前一个区块的哈希值")
    difficulty: int = Field(default=4, description="挖矿难度")


class BlockCreate(BlockBase):
    pass


class BlockResponse(BlockBase):
    id: int
    hash: str = Field(..., description="当前区块哈希值")
    nonce: int = Field(..., description="随机数")
    timestamp: datetime = Field(..., description="区块创建时间")

    class Config:
        from_attributes = True


class BlockchainInfo(BaseModel):
    total_blocks: int = Field(..., description="总区块数")
    latest_block_hash: str = Field(..., description="最新区块哈希")
    total_transactions: int = Field(..., description="总交易数")
    chain_validity: bool = Field(..., description="区块链是否有效")


class TransactionData(BaseModel):
    donation_id: int = Field(..., description="捐赠ID")
    donor_name: str = Field(..., description="捐赠者姓名")
    recipient: str = Field(..., description="受赠者")
    amount: float = Field(..., description="捐赠金额")
    currency: str = Field(default="CNY", description="货币类型")
    message: Optional[str] = Field(None, description="捐赠留言")
    timestamp: datetime = Field(..., description="交易时间")