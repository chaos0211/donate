# 基于 ARM64 的 Hive Metastore 镜像（保持你当前用的那一个）
FROM louissimps/arm64-hive-metastore:3.1.3

ENV HADOOP_VERSION=3.3.6

# 安装 hadoop 客户端（纯 Java，arm64 可用）
RUN apt-get update && apt-get install -y curl tar \
 && curl -fsSL https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    | tar -xz -C /opt \
 && ln -s /opt/hadoop-${HADOOP_VERSION} /opt/hadoop \
 && rm -rf /var/lib/apt/lists/*

ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$HADOOP_HOME/bin:$PATH