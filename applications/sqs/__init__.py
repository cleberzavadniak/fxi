import json

import boto3

from fxi.apps.base import AppBase
from fxi.apps.main_list import MainList

from .operations import SQSOperationsMixin


def arg_is_entry(method):
    def new_method(self, *args, **kwargs):
        entry_index = int(args[0])
        entry = self.entries[entry_index]
        return method(self, entry)
    return new_method


class MyMainList(MainList):
    def refresh(self):
        for entry in self.entries:
            entry.mark_as('loading')
            name = entry.data['name']
            new_data = self.parent.refresh_queue(name)
            entry.refresh(new_data)

    @arg_is_entry
    def cmd__p(self, entry):
        monitor = self.parent.open_monitor('Data')
        monitor.write(f'{entry.data}')
        monitor.update()

    @arg_is_entry
    def cmd__pa(self, entry):
        obj = entry.data['object']
        monitor = self.parent.open_monitor('Attributes')
        monitor.write(f'{obj.attributes}')

    @arg_is_entry
    def cmd__recover(self, entry):
        entry.mark_as('O')
        arn = entry.data['arn']
        obj = entry.data['object']
        for other_entry in self.entries:
            if other_entry is entry:
                continue

            other_obj = other_entry.data['object']
            if 'RedrivePolicy' in other_obj.attributes:
                redrive_policy = json.loads(other_obj.attributes['RedrivePolicy'])
                if redrive_policy.get('deadLetterTargetArn', None) == arn:
                    break
        else:
            self.parent.info('Related queue was not found!')
            entry.refresh()
            return

        other_entry.mark_as('D')
        count = self.parent.move_sqs_messages(obj, other_obj)
        self.parent.info(f'{count} messages moved successfuly!')
        self.refresh()


class App(SQSOperationsMixin, AppBase):
    title = "SQS"

    def init(self, *args, **kwargs):
        self.client = boto3.resource('sqs', 'us-east-1')  # XXX
        self.queues = {}
        self.queues_widgets = {}
        self.main_list = MyMainList(
            self,
            (('name',), ('count',), ('in_transit_count',)),
            ('Name', 'Messages', 'In transit')
        )

    def load_queues_list(self):
        for queue in self.client.queues.all():
            self.add_queue(queue)

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

    def render(self):
        self.info('Loading queues list...')
        self.load_queues_list()
        self.main_list.render(self.queues)
        self.info(None)
