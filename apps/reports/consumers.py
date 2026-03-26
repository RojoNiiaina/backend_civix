import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Report

User = get_user_model()

class ReportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = None  # Initialize group_name early
        
        # Only allow authenticated users
        if not self.user.is_authenticated:
            await self.close()
            return

        # Create group name based on user role
        if self.user.role == 'agent':
            # Agents get all new reports
            self.group_name = 'reports_agents'
        elif self.user.role == 'admin':
            # Admins get all reports
            self.group_name = 'reports_admin'
        else:
            # Regular users only get their own report updates
            self.group_name = f'reports_user_{self.user.id}'

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group only if we joined one
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'mark_read':
                await self.handle_mark_read(data)
            elif message_type == 'get_unread_count':
                await self.handle_get_unread_count()
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            await self.send_error(f'Error processing message: {str(e)}')

    async def handle_mark_read(self, data):
        """Handle marking reports as read"""
        report_id = data.get('report_id')
        if report_id:
            # Here you would implement marking logic
            await self.send(text_data=json.dumps({
                'type': 'report_marked_read',
                'report_id': report_id
            }))

    async def handle_get_unread_count(self):
        """Handle getting unread reports count"""
        count = await self.get_unread_reports_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': count
        }))

    # Broadcast handlers
    async def report_created(self, event):
        """Handle new report notification"""
        await self.send(text_data=json.dumps({
            'type': 'new_report',
            'report': event['report']
        }))

    async def report_updated(self, event):
        """Handle report update notification"""
        await self.send(text_data=json.dumps({
            'type': 'report_updated',
            'report': event['report']
        }))

    async def report_status_changed(self, event):
        """Handle report status change notification"""
        await self.send(text_data=json.dumps({
            'type': 'report_status_changed',
            'report_id': event['report_id'],
            'old_status': event['old_status'],
            'new_status': event['new_status']
        }))

    # Database operations
    @database_sync_to_async
    def get_unread_reports_count(self):
        """Get count of unread reports for the user"""
        if self.user.role == 'agent':
            # Agents see all pending reports
            return Report.objects.filter(statut='en_attente').count()
        elif self.user.role == 'admin':
            # Admins see all pending reports
            return Report.objects.filter(statut='en_attente').count()
        else:
            # Regular users see their own pending reports
            return Report.objects.filter(user=self.user, statut='en_attente').count()

    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
