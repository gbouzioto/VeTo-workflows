from pyspark import *
from pyspark.sql import *
import sys
import json
from Graph import Graph
import time

if len(sys.argv) != 2:
	print("Usage: spark-submit hminer.py config.json", file=sys.stderr)
	sys.exit(-1)

spark = SparkSession.builder.appName('HMiner').getOrCreate()

# supress Spark INFO messages
log4j = spark._jvm.org.apache.log4j
log4j.LogManager.getRootLogger().setLevel(log4j.Level.WARN)

config_file = sys.argv[1]

with open(config_file) as fd:
		config = json.load(fd)
		nodes_dir = config["indir"]
		relations_dir = config["irdir"]
		operation = config["operation"]
		alpha = float(config["pr_alpha"]) if ("pr_alpha" in config) else None
		tol = float(config["pr_tol"]) if ("pr_tol" in config) else None
		hin_out = config["hin_out"]
		ranking_out = config["ranking_out"]
		communities_out = config["communities_out"]
		metapath = config["query"]["metapath"]
		constraints = config["query"]["constraints"]


graph = Graph()

# build HIN
graph.build(spark, metapath, nodes_dir, relations_dir, constraints)

# transform HIN to homogeneous network
hgraph = graph.transform(spark)

# when operation includes "ranking"
if operation.find("ranking") != -1:
	graph.pagerank(hgraph, alpha, tol, ranking_out)

# when operation is (not only) "ranking", it can be "ranking-community" or "community"
if operation != "ranking":
	hgraph.write(hin_out)
	# graph.lpa(hgraph, communities_out)
