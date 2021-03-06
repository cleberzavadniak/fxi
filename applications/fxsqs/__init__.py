import json

import boto3

from fxi.apps import AppBase
from fxi.table import Table

from .operations import SQSOperationsMixin


def arg_is_entry(method):
    def new_method(self, *args, **kwargs):
        entry_index = int(args[0])
        entry = self.main_list.entries[entry_index]
        return method(self, entry)

    new_method.__doc__ = method.__doc__
    return new_method


class MyTable(Table):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

    def refresh(self):
        for entry in self.entries:
            entry.mark_as('loading')
            name = entry.data['name']
            new_data = self.app.refresh_queue(name)
            entry.refresh(new_data)


class App(SQSOperationsMixin, AppBase):
    title = "SQS"

    def init(self, *args, **kwargs):
        self.client = boto3.resource('sqs', 'us-east-1')  # XXX
        self.queues = {}
        self.queues_widgets = {}
        self.main_list = MyTable(
            self,
            self.tab.interior,
            (('name',), ('count',), ('in_transit_count',)),
            ('Name', 'Messages', 'In transit')
        )

    def load_queues_list(self):
        self.info('Loading queues list...')
        for queue in self.client.queues.all():
            self.add_queue(queue)
        self.info()

    def refresh_queue(self, name):
        entry = self.queues[name]
        obj = entry['object']
        obj.reload()
        return self.add_queue(obj)

    def add_queue(self, obj):
        arn = obj.attributes['QueueArn']
        name = arn.split(':')[-1]
        entry = {
            'object': obj,
            'arn': arn,
            'name': name,
            'count': int(obj.attributes['ApproximateNumberOfMessages']),
            'in_transit_count': int(obj.attributes['ApproximateNumberOfMessagesNotVisible']),
        }
        self.queues[name] = entry
        return entry

    def refresh_queues(self):
        for name in self.queues:
            self.refresh_queue(name)

    def refresh(self):
        self.main_list.refresh()

    def initial_render(self):
        self.load_queues_list()
        self.main_list.render(self.queues)

    def render(self):
        self.enqueue(self.initial_render)

    # COMMANDS:
    @arg_is_entry
    def cmd__p(self, entry):
        """
        Print <index> queue data as collected by
        this application

        Usage: p <index>
        """
        monitor = self.open_monitor('Data')
        monitor.write(f'{entry.data}')

    @arg_is_entry
    def cmd__pa(self, entry):
        """
        Print <index> queue attributes as informed
        by Amazon.

        Usage: pa <index>
        """

        obj = entry.data['object']
        monitor = self.open_monitor('Attributes')
        monitor.write(f'{obj.attributes}')

    @arg_is_entry
    def cmd__vm(self, entry):
        """
        View messages from <index> queue
        BEWARE: it will, in fact, generate one more
        "rejection" for each message, so use it wisely.

        Usage: vm <index>

        No messages limit implemented, yet.
        """
        self.view_messages(entry.data['object'])

    @arg_is_entry
    def cmd__recover(self, entry):
        """
        Recover messages from a dead letter queue.
        It will find the corresponding "alive" queue
        automatically for you.

        Usage: recover <index>
        """

        entry.mark_as('O')
        arn = entry.data['arn']
        obj = entry.data['object']
        for other_entry in self.main_list.entries:
            if other_entry is entry:
                continue

            other_obj = other_entry.data['object']
            if 'RedrivePolicy' in other_obj.attributes:
                redrive_policy = json.loads(other_obj.attributes['RedrivePolicy'])
                if redrive_policy.get('deadLetterTargetArn', None) == arn:
                    break
        else:
            self.info('Related queue was not found!')
            entry.refresh()
            return

        other_entry.mark_as('D')
        count = self.move_messages(obj, other_obj)
        self.info(f'{count} messages moved successfuly!')

        entry.refresh()
        other_entry.refresh()

    def cmd__mv(self, index_a, index_b, num_messages=50):
        """
        Move messages from one queue to another.

        Usage: mv <index_a> <index_b> <num_messages=50>
        """

        entry_a = self.main_list.entries[int(index_a)]
        entry_b = self.main_list.entries[int(index_b)]

        entry_a.mark_as('O')
        entry_b.mark_as('D')
        obj_a = entry_a.data['object']
        obj_b = entry_b.data['object']

        count = self.move_messages(obj_a, obj_b)
        self.info(f'{count} messages moved successfuly!')

        entry_a.refresh()
        entry_b.refresh()

    @arg_is_entry
    def cmd__purge(self, entry):
        """
        Purge <index> queue

        Usage: purge <index>
        """

        obj = entry.data['object']
        name = entry.data['name']
        obj.purge()
        self.info(f'Queue {name} purged!')
        entry.refresh()
