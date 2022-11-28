安装spark 

1.解压安装包到/export/server/，创建软链接

```
ln -s /export/server/spark-3.1.2-bin-hadoop3.2 /export/server/spark
```

2.添加环境变量到自定义配置文件里 my_env.sh

```
vim /etc/profile.d/my_env.sh


#SPARK_HOME
export SPARK_HOME=/export/server/spark

#PYSPARK_PYTHON
export PYSPARK_PYTHON=/export/server/anaconda3/envs/pyspark/bin/python3.8
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop

```

 3.将环境变量配置在~/.bashrc文件中

```
vim ~/.bashrc

export JAVA_HOME=/export/server/jdk1.8.0_241
export PYSPARK_PYTHON=/export/server/anaconda3/envs/pyspark/bin/python3.8
```

4.启动spark local 环境 测试

```
 bin/spark-submit --master local[*] /export/server/spark/examples/src/main/python/pi.py 100
```

5.修改配置文件

配置worker.template 文件

```
mv workers.template workers

vim workers

node1
node2
node3
```

配置spark-env.sh.template文件

```
mv spark-env.sh.template spark-env.sh

vim spark-env.sh

## 设置JAVA安装目录
JAVA_HOME=/export/server/jdk

## HADOOP软件配置文件目录，读取HDFS上文件和运行YARN集群
HADOOP_CONF_DIR=/export/server/hadoop/etc/hadoop
YARN_CONF_DIR=/export/server/hadoop/etc/hadoop

## 指定spark老大Master的IP和提交任务的通信端口
# 告知Spark的master运行在哪个机器上
export SPARK_MASTER_HOST=node1
# 告知sparkmaster的通讯端口
export SPARK_MASTER_PORT=7077
# 告知spark master的 webui端口
SPARK_MASTER_WEBUI_PORT=8080

# worker cpu可用核数
SPARK_WORKER_CORES=1
# worker可用内存
SPARK_WORKER_MEMORY=1g
# worker的工作通讯地址
SPARK_WORKER_PORT=7078
# worker的 webui地址
SPARK_WORKER_WEBUI_PORT=8081

## 设置历史服务器
# 配置的意思是  将spark程序运行的历史日志 存到hdfs的/sparklog文件夹中
SPARK_HISTORY_OPTS="-Dspark.history.fs.logDirectory=hdfs://node1:8020/sparklog/ -Dspark.history.fs.cleaner.enabled=true"
```

配置spark 在hdfs 上log存档目录

```
hadoop fs -mkdir /sparklog
hadoop fs -chmod 777 /sparklog
```

配置 spark-defaults.conf文件

```
 mv spark-defaults.conf.template spark-defaults.conf
 
 vim spark-defaults.conf
 
 # 2. 修改内容, 追加如下内容
# 开启spark的日期记录功能
spark.eventLog.enabled 	true
# 设置spark日志记录的路径
spark.eventLog.dir	 hdfs://node1:8020/sparklog/ 
# 设置spark日志是否启动压缩
spark.eventLog.compress 	true
```

配置log4j.properties 文件 [可选配置]


```shell
# 1. 改名
mv log4j.properties.template log4j.properties

# 2. 修改内容 参考下图
```

![](https://pybd.yuque.com/api/filetransfer/images?url=https%3A%2F%2Fimage-set.oss-cn-zhangjiakou.aliyuncs.com%2Fimg-out%2F2021%2F09%2F08%2F20210908151736.png&sign=9baf2cdc4826e60d35e84d1c175de20def3c2f65ecfdba1c01a1ecfa9d8084ab#from=url&id=WzrZH&margin=%5Bobject%20Object%5D&originHeight=753&originWidth=1889&originalType=binary&ratio=1&status=done&style=none)  

6.将上述步骤重复到集群中的每个节点上

7.启动集群

```
# 启动全部master和worker
sbin/start-all.sh

# 或者可以一个个启动:
# 启动当前机器的master
sbin/start-master.sh
# 启动当前机器的worker
sbin/start-worker.sh

# 停止全部
sbin/stop-all.sh

# 停止当前机器的master
sbin/stop-master.sh

# 停止当前机器的worker
sbin/stop-worker.sh
```

spark on yarn 部署

spark on hive 部署

注意：jdk包选择1.8.212！！！

