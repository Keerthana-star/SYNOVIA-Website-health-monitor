import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class LiveDashboardConsumer(WebsocketConsumer):
    # This is the name of the group that all dashboard browsers will join
    DASHBOARD_GROUP_NAME = 'dashboard_updates'

    def connect(self):
        # When a browser connects, accept the connection
        self.accept()
        
        # Add the connection to the group to receive broadcasts
        async_to_sync(self.channel_layer.group_add)(
            self.DASHBOARD_GROUP_NAME,
            self.channel_name
        )
        
        # Send an initial connection status
        self.send(text_data=json.dumps({
            'type': 'status',
            'message': 'Real-time feed connected.',
        }))

    def disconnect(self, close_code):
        # Remove the connection from the group when disconnected
        async_to_sync(self.channel_layer.group_discard)(
            self.DASHBOARD_GROUP_NAME,
            self.channel_name
        )

    # Handler for messages sent to the group from Django views
    def send_dashboard_update(self, event):
        # Send the actual data payload to the WebSocket
        self.send(text_data=json.dumps(event['data']))

    # We generally don't need a receive method for a monitoring dashboard, 
    # as the server is pushing updates.
