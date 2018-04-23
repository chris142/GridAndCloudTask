import pika
from hashlib import sha512
from itertools import combinations_with_replacement, permutations


def bruteforce(hashstring):
    for i in range(1, 100):
        for comb in permutations('0123456789', i):
            str_comb = ''.join(comb)
            # print(str_comb)
            if hashstring.decode() == sha512(str_comb.encode('utf-8')).hexdigest():
                return str_comb


def handle_delivery(channel, method, header, body):
    """Called when we receive a message from RabbitMQ"""
    print(header, body)
    channel_out.basic_publish(
        body="PENDING",
        exchange='',
        routing_key='task_result',
        properties=pika.BasicProperties(headers={'task_id': header.headers.get('task_id')}),
    )
    result = bruteforce(body)
    print(result)
    channel_out.basic_publish(
        body=result,
        exchange='',
        routing_key='task_result',
        properties=pika.BasicProperties(headers={'task_id': header.headers.get('task_id')}),
    )


# Step #1: Connect to RabbitMQ using the default parameters
parameters = pika.ConnectionParameters()
connection_in = pika.BlockingConnection(parameters)
channel_in = connection_in.channel()
channel_in.queue_declare(
    queue="tasks_data",
    durable=True,
    exclusive=False,
    auto_delete=True,
)
channel_in.basic_consume(handle_delivery, queue='tasks_data')

connection_out = pika.BlockingConnection(parameters)
channel_out = connection_out.channel()
channel_out.queue_declare(
    queue="tasks_result",
    durable=True,
    exclusive=False,
    auto_delete=True,
)

channel_in.start_consuming()
