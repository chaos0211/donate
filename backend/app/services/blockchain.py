# services/blockchain.py
import hashlib
import json
from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.db.models.blockchain import Block, ChainTransaction


class BlockchainService:

    @staticmethod
    def generate_hash(content: str) -> str:
        """生成SHA256哈希"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def get_chain_info(db: Session) -> dict:
        """获取链信息"""
        # 查询最新区块
        latest_block = db.query(Block).order_by(desc(Block.height)).first()

        # 统计区块总数
        blocks_count = db.query(Block).count()

        # 统计交易总数和总金额
        stats = db.query(
            func.count(ChainTransaction.id).label('total_txs'),
            func.sum(ChainTransaction.amount).label('total_amount')
        ).first()

        return {
            "height": latest_block.height if latest_block else 0,
            "blocks": blocks_count,
            "total_txs": stats.total_txs or 0,
            "total_amount": stats.total_amount or Decimal('0.00'),
            "latest_hash": latest_block.block_hash if latest_block else None,
            "latest_timestamp": latest_block.timestamp if latest_block else None
        }

    @staticmethod
    def create_genesis_block(db: Session) -> Block:
        """创建创世区块"""
        genesis_content = f"genesis_block_{datetime.utcnow().isoformat()}"
        genesis_hash = BlockchainService.generate_hash(genesis_content)

        genesis_block = Block(
            height=0,
            block_hash=genesis_hash,
            prev_hash=None,
            timestamp=datetime.utcnow(),
            tx_count=0,
            total_amount_in_block=Decimal('0.00'),
            project_id_summary="",
            raw_metadata=json.dumps({"type": "genesis", "note": "创世区块"})
        )

        db.add(genesis_block)
        db.commit()
        db.refresh(genesis_block)
        return genesis_block

    @staticmethod
    def get_latest_block(db: Session) -> Optional[Block]:
        """获取最新区块"""
        return db.query(Block).order_by(desc(Block.height)).first()

    @staticmethod
    def add_donation_to_chain(
            db: Session,
            project_id: int,
            amount: Decimal,
            donor_username: Optional[str] = None,
            remark: Optional[str] = None,
            external_donate_id: Optional[int] = None
    ) -> Tuple[Block, ChainTransaction]:
        """添加捐赠到区块链"""

        # 获取最新区块
        latest_block = BlockchainService.get_latest_block(db)

        # 如果没有区块，创建创世区块
        if not latest_block:
            latest_block = BlockchainService.create_genesis_block(db)

        # 计算新区块信息
        new_height = latest_block.height + 1
        prev_hash = latest_block.block_hash
        timestamp = datetime.utcnow()

        # 生成交易哈希
        tx_content = f"{new_height}_{project_id}_{amount}_{donor_username or ''}_{timestamp.isoformat()}"
        tx_hash = BlockchainService.generate_hash(tx_content)

        # 生成区块哈希
        block_content = f"{prev_hash}_{timestamp.isoformat()}_{project_id}_{amount}_{donor_username or ''}"
        block_hash = BlockchainService.generate_hash(block_content)

        # 创建新区块
        new_block = Block(
            height=new_height,
            block_hash=block_hash,
            prev_hash=prev_hash,
            timestamp=timestamp,
            tx_count=1,
            total_amount_in_block=amount,
            project_id_summary=str(project_id),
            raw_metadata=json.dumps({
                "created_by": "donation_chain",
                "projects": [project_id],
                "total_amount": str(amount)
            })
        )

        db.add(new_block)
        db.flush()  # 获取区块ID

        # 创建交易记录
        transaction = ChainTransaction(
            block_id=new_block.id,
            project_id=project_id,
            donor_username=donor_username,
            amount=amount,
            remark=remark,
            tx_hash=tx_hash,
            tx_index=0,  # 目前每个区块只有一笔交易
            timestamp=timestamp,
            external_donate_id=external_donate_id
        )

        db.add(transaction)
        db.commit()

        # 刷新对象以获取最新数据
        db.refresh(new_block)
        db.refresh(transaction)

        return new_block, transaction

    @staticmethod
    def get_blocks_paginated(
            db: Session,
            offset: int = 0,
            limit: int = 10
    ) -> Tuple[int, List[Block]]:
        """分页获取区块列表"""
        total = db.query(Block).count()
        blocks = (
            db.query(Block)
            .order_by(desc(Block.height))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return total, blocks

    @staticmethod
    def get_block_by_height(db: Session, height: int) -> Optional[Block]:
        """根据高度获取区块"""
        return db.query(Block).filter(Block.height == height).first()

    @staticmethod
    def get_transaction_by_donate_id(
            db: Session,
            external_donate_id: int
    ) -> Optional[ChainTransaction]:
        """根据外部捐赠ID查询交易"""
        return db.query(ChainTransaction).filter(
            ChainTransaction.external_donate_id == external_donate_id
        ).first()