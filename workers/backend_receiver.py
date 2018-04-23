import pika
import sqlite3

conn = sqlite3.connect('/tmp/taskscheduler.sqlite')
cr = conn.cursor()


def handle_delivery(channel, method, header, body):
    cr.execute("""UPDATE tasks SET status="DONE", result="%s" WHERE id=%s""" % (body.decode(), header.headers.get('task_id')))
    conn.commit()
    print('done')


parameters = pika.ConnectionParameters()
connection_in = pika.BlockingConnection(parameters)
channel_in = connection_in.channel()
channel_in.queue_declare(
    queue="tasks_result",
    durable=True,
    exclusive=False,
    auto_delete=True,
)
channel_in.basic_consume(handle_delivery, queue='tasks_result')

channel_in.start_consuming()
