import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import LiveStream, LiveMessage, LiveViewer

User = get_user_model()

class LiveStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.stream_id = self.scope['url_route']['kwargs']['stream_id']
        self.stream_group_name = f'stream_{self.stream_id}'
        self.user = self.scope['user']

        # Join stream group
        await self.channel_layer.group_add(
            self.stream_group_name,
            self.channel_name
        )

        # Accept WebSocket connection
        await self.accept()

        # Add viewer to stream
        if self.user.is_authenticated:
            await self.add_viewer()

    async def disconnect(self, close_code):
        # Leave stream group
        await self.channel_layer.group_discard(
            self.stream_group_name,
            self.channel_name
        )

        # Remove viewer from stream
        if self.user.is_authenticated:
            await self.remove_viewer()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'webrtc_offer':
                await self.handle_webrtc_offer(data)
            elif message_type == 'webrtc_answer':
                await self.handle_webrtc_answer(data)
            elif message_type == 'webrtc_ice_candidate':
                await self.handle_webrtc_ice_candidate(data)
            elif message_type == 'stream_started':
                await self.handle_stream_started(data)
            elif message_type == 'stream_ended':
                await self.handle_stream_ended(data)
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            await self.send_error(f'Error processing message: {str(e)}')

    async def handle_chat_message(self, data):
        if not self.user.is_authenticated:
            await self.send_error('Authentication required')
            return

        content = data.get('content', '').strip()
        if not content:
            await self.send_error('Message content is required')
            return

        # Save message to database
        message = await self.save_message(content)

        # Broadcast message to all viewers
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'chat_message_broadcast',
                'message': {
                    'id': message.id,
                    'user_name': getattr(self.user, 'nom', None) or self.user.email,
                    'user_photo_url': self.user.photo.url if self.user.photo else None,
                    'content': content,
                    'created_at': message.created_at.isoformat(),
                    'is_agent': self.user.role == 'agent'
                }
            }
        )

    async def handle_webrtc_offer(self, data):
        """Handle WebRTC offer from streamer"""
        stream = await self.get_stream()
        if stream.streamer != self.user:
            await self.send_error('Only streamer can send offers')
            return

        # Broadcast offer to all viewers except streamer
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'webrtc_offer_broadcast',
                'offer': data.get('offer'),
                'streamer_id': self.user.id
            },
            exclude=[self.channel_name]
        )

    async def handle_webrtc_answer(self, data):
        """Handle WebRTC answer from viewer"""
        # Send answer directly to streamer
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'webrtc_answer_to_streamer',
                'answer': data.get('answer'),
                'viewer_id': self.user.id
            }
        )

    async def handle_webrtc_ice_candidate(self, data):
        """Handle WebRTC ICE candidate"""
        candidate = data.get('candidate')
        is_streamer = data.get('is_streamer', False)

        if is_streamer:
            # Send candidate to all viewers
            await self.channel_layer.group_send(
                self.stream_group_name,
                {
                    'type': 'webrtc_ice_candidate_to_viewers',
                    'candidate': candidate
                },
                exclude=[self.channel_name]
            )
        else:
            # Send candidate to streamer
            await self.channel_layer.group_send(
                self.stream_group_name,
                {
                    'type': 'webrtc_ice_candidate_to_streamer',
                    'candidate': candidate,
                    'viewer_id': self.user.id
                }
            )

    async def handle_stream_started(self, data):
        """Handle stream started event"""
        stream = await self.get_stream()
        if stream.streamer != self.user:
            await self.send_error('Only streamer can start stream')
            return

        # Update stream status
        await self.update_stream_status('live')

        # Broadcast to all viewers
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'stream_status_broadcast',
                'status': 'live',
                'started_at': datetime.now().isoformat()
            }
        )

    async def handle_stream_ended(self, data):
        """Handle stream ended event"""
        stream = await self.get_stream()
        if stream.streamer != self.user:
            await self.send_error('Only streamer can end stream')
            return

        # Update stream status
        await self.update_stream_status('ended')

        # Broadcast to all viewers
        await self.channel_layer.group_send(
            self.stream_group_name,
            {
                'type': 'stream_status_broadcast',
                'status': 'ended',
                'ended_at': datetime.now().isoformat()
            }
        )

    # Broadcast handlers
    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def webrtc_offer_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'webrtc_offer',
            'offer': event['offer'],
            'streamer_id': event['streamer_id']
        }))

    async def webrtc_answer_to_streamer(self, event):
        # Only send to streamer
        stream = await self.get_stream()
        if self.user == stream.streamer:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_answer',
                'answer': event['answer'],
                'viewer_id': event['viewer_id']
            }))

    async def webrtc_ice_candidate_to_viewers(self, event):
        # Send to all viewers except streamer
        stream = await self.get_stream()
        if self.user != stream.streamer:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_ice_candidate',
                'candidate': event['candidate']
            }))

    async def webrtc_ice_candidate_to_streamer(self, event):
        # Only send to streamer
        stream = await self.get_stream()
        if self.user == stream.streamer:
            await self.send(text_data=json.dumps({
                'type': 'webrtc_ice_candidate',
                'candidate': event['candidate'],
                'viewer_id': event['viewer_id']
            }))

    async def stream_status_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'stream_status',
            'status': event['status'],
            'started_at': event.get('started_at'),
            'ended_at': event.get('ended_at')
        }))

    # Database operations
    @database_sync_to_async
    def get_stream(self):
        return LiveStream.objects.get(id=self.stream_id)

    @database_sync_to_async
    def save_message(self, content):
        stream = LiveStream.objects.get(id=self.stream_id)
        return LiveMessage.objects.create(
            stream=stream,
            user=self.user,
            content=content
        )

    @database_sync_to_async
    def add_viewer(self):
        try:
            stream = LiveStream.objects.get(id=self.stream_id)
            viewer, created = LiveViewer.objects.get_or_create(
                stream=stream,
                user=self.user,
                left_at__isnull=True,
                defaults={'joined_at': datetime.now()}
            )
            
            if created:
                # Update viewer count
                stream.viewer_count = LiveViewer.objects.filter(
                    stream=stream, 
                    left_at__isnull=True
                ).count()
                if stream.viewer_count > stream.max_viewers:
                    stream.max_viewers = stream.viewer_count
                stream.save()
        except LiveStream.DoesNotExist:
            pass

    @database_sync_to_async
    def remove_viewer(self):
        try:
            stream = LiveStream.objects.get(id=self.stream_id)
            viewer = LiveViewer.objects.filter(
                stream=stream,
                user=self.user,
                left_at__isnull=True
            ).first()
            
            if viewer:
                viewer.left_at = datetime.now()
                viewer.save()
                
                # Update viewer count
                stream.viewer_count = LiveViewer.objects.filter(
                    stream=stream, 
                    left_at__isnull=True
                ).count()
                stream.save()
        except LiveStream.DoesNotExist:
            pass

    @database_sync_to_async
    def update_stream_status(self, status):
        try:
            stream = LiveStream.objects.get(id=self.stream_id)
            stream.status = status
            if status == 'live':
                stream.started_at = datetime.now()
            elif status == 'ended':
                stream.ended_at = datetime.now()
            stream.save()
        except LiveStream.DoesNotExist:
            pass

    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
