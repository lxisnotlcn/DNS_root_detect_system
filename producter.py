import json
from kafka import KafkaProducer

data = {"a": 1, "b": 2, "c": 3}
producer = KafkaProducer(bootstrap_servers=["172.20.74.125:9092"],
                         api_version=(0, 10, 0),
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

for i in range(0,100):
    future = producer.send("test", data, partition=0)
    result = future.get(timeout= 10)
    print(result)
