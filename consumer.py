from kafka import KafkaConsumer

consumer = KafkaConsumer('test', 
                         group_id="group2", 
                         bootstrap_servers=["localhost:9092"])
                                          
for msg in consumer:
    print(msg.value)
