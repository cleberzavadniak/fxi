def move_sqs_message(message, to_queue):
    response = to_queue.send_message(
        MessageBody=message.body,
        MessageAttributes=message.message_attributes
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        message.delete()
    else:
        raise Exception('Error while trying to move message to another queue')


class SQSOperationsMixin:
    def view_messages(self, queue):
        monitor = self.open_monitor('View messages')

        while monitor.alive:
            messages = queue.receive_messages(
                MaxNumberOfMessages=10,
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            if not messages:
                self.info(f'No more messages in {queue}')
                return

            for message in messages:
                if not monitor.alive:
                    return

                monitor.write(f"{message.message_attributes}", indentation=1)
                monitor.write(f"{message.body}", indentation=1)
                monitor.hr()

    def move_messages(self, from_queue, to_queue, messages_limit=50, cherrypick=False):
        messages_count = 0

        monitor = self.open_monitor('Dead queue messages recovery')

        while messages_count < messages_limit:
            messages = from_queue.receive_messages(
                MaxNumberOfMessages=10,
                AttributeNames=['All'],
                MessageAttributeNames=['All']
            )
            if not messages:
                self.info('No more messages in {}'.format(from_queue))
                break

            for message in messages:
                monitor.write(f'Moving message {messages_count}')

                if not monitor.alive:
                    return

                if cherrypick:
                    x = input('Do you want to delete this message, send or ignore? [d|s|i] ')
                    if x in ('d', 'D', 'x', 'X'):
                        message.delete()
                        continue
                    elif x == 'i':
                        continue
                    elif x == 'p':
                        import pdb
                        import json

                        body = json.loads(message.body)
                        new_message = type('object', (), {'message_attributes': message.message_attributes})

                        def delete():
                            return message.delete()

                        new_message.delete = delete
                        print('body:', body)
                        pdb.set_trace()
                        new_message.body = json.dumps(body)
                        message = new_message

                success = move_sqs_message(message, to_queue)

                if success:
                    monitor.write(f"Message {messages_count}:")
                    monitor.write(f"{message.message_attributes}", indentation=1)
                    monitor.write(f"{message.body}", indentation=1)
                else:
                    monitor.write(f'Error when moving message {messages_count}')

                messages_count += 1
                if messages_count >= messages_limit:
                    break
        return messages_count
