import hashlib
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from app.db.models.bc import Block
from app.schemas.bc import BlockResponse, BlockchainInfo, TransactionData
import asyncio


class BlockchainService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def calculate_hash(index: int, timestamp: str, data: str, previous_hash: str, nonce: int = 0) -> str:
        """计算区块哈希值"""
        value = f"{index}{timestamp}{data}{previous_hash}{nonce}"
        return hashlib.sha256(value.encode()).hexdigest()

    @staticmethod
    def is_valid_proof(index: int, timestamp: str, data: str, previous_hash: str, nonce: int, difficulty: int) -> bool:
        """验证工作量证明"""
        hash_value = BlockchainService.calculate_hash(index, timestamp, data, previous_hash, nonce)
        return hash_value.startswith("0" * difficulty)

    @staticmethod
    def mine_block(index: int, timestamp: str, data: str, previous_hash: str, difficulty: int = 4) -> tuple[str, int]:
        """挖矿 - 寻找满足难度要求的随机数"""
        nonce = 0
        while True:
            hash_value = BlockchainService.calculate_hash(index, timestamp, data, previous_hash, nonce)
            if hash_value.startswith("0" * difficulty):
                return hash_value, nonce
            nonce += 1

    async def get_latest_block(self) -> Optional[Block]:
        """获取最新区块"""
        result = await self.db.execute(
            select(Block).order_by(desc(Block.index)).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        """根据哈希值获取区块"""
        result = await self.db.execute(
            select(Block).where(Block.hash == block_hash)
        )
        return result.scalar_one_or_none()

    async def get_blocks(self, limit: int = 10, offset: int = 0) -> List[Block]:
        """获取区块列表"""
        result = await self.db.execute(
            select(Block).order_by(desc(Block.index)).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def create_genesis_block(self) -> Block:
        """创建创世区块"""
        genesis_data = {
            "message": "Genesis Block - Blockchain Donation System",
            "timestamp": datetime.now().isoformat()
        }

        timestamp_str = datetime.now().isoformat()
        data_str = json.dumps(genesis_data, ensure_ascii=False)
        previous_hash = "0" * 64

        # 挖矿
        hash_value, nonce = self.mine_block(0, timestamp_str, data_str, previous_hash, 4)

        genesis_block = Block(
            index=0,
            data=data_str,
            previous_hash=previous_hash,
            hash=hash_value,
            nonce=nonce,
            difficulty=4
        )

        self.db.add(genesis_block)
        await self.db.commit()
        await self.db.refresh(genesis_block)
        return genesis_block

    async def add_block(self, transaction_data: TransactionData) -> Block:
        """添加新区块"""
        latest_block = await self.get_latest_block()

        if latest_block is None:
            # 如果没有区块，创建创世区块
            latest_block = await self.create_genesis_block()

        new_index = latest_block.index + 1
        timestamp_str = datetime.now().isoformat()
        data_str = json.dumps(transaction_data.dict(), ensure_ascii=False)
        previous_hash = latest_block.hash
        difficulty = 4

        # 挖矿
        hash_value, nonce = await asyncio.get_event_loop().run_in_executor(
            None, self.mine_block, new_index, timestamp_str, data_str, previous_hash, difficulty
        )

        new_block = Block(
            index=new_index,
            data=data_str,
            previous_hash=previous_hash,
            hash=hash_value,
            nonce=nonce,
            difficulty=difficulty
        )

        self.db.add(new_block)
        await self.db.commit()
        await self.db.refresh(new_block)
        return new_block

    async def validate_chain(self) -> bool:
        """验证整个区块链"""
        blocks = await self.db.execute(
            select(Block).order_by(Block.index)
        )
        block_list = blocks.scalars().all()

        if not block_list:
            return True

        # 验证每个区块
        for i, block in enumerate(block_list):
            # 验证哈希值
            calculated_hash = self.calculate_hash(
                block.index,
                block.timestamp.isoformat(),
                block.data,
                block.previous_hash,
                block.nonce
            )

            if calculated_hash != block.hash:
                return False

            # 验证工作量证明
            if not self.is_valid_proof(
                    block.index,
                    block.timestamp.isoformat(),
                    block.data,
                    block.previous_hash,
                    block.nonce,
                    block.difficulty
            ):
                return False

            # 验证前一个区块的哈希值（除了创世区块）
            if i > 0 and block.previous_hash != block_list[i - 1].hash:
                return False

        return True

    async def get_blockchain_info(self) -> BlockchainInfo:
        """获取区块链信息"""
        # 总区块数
        total_blocks_result = await self.db.execute(select(func.count(Block.id)))
        total_blocks = total_blocks_result.scalar() or 0

        # 最新区块哈希
        latest_block = await self.get_latest_block()
        latest_block_hash = latest_block.hash if latest_block else ""

        # 总交易数（除了创世区块）
        total_transactions = max(0, total_blocks - 1)

        # 验证链的有效性
        chain_validity = await self.validate_chain()

        return BlockchainInfo(
            total_blocks=total_blocks,
            latest_block_hash=latest_block_hash,
            total_transactions=total_transactions,
            chain_validity=chain_validity
        )