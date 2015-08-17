from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import override, ungettext

from .conf import settings
from .models import Contact, Device, Group, Member, Post
from .providers import apns_provider


class NotificationInstances(
    type
):
    _instances = {}

    @classmethod
    def get_instance(cls, instance):
        return cls._instances[instance]

    def __new__(cls, name, parents, dct):
        instance = super(NotificationInstances, cls).__new__(
            cls, name, parents, dct
        )

        if name not in cls._instances:
            cls._instances[name] = instance

        return instance


class Notification(
    six.with_metaclass(NotificationInstances, object)
):
    setup = True

    def __init__(self, **kwargs):
        raise NotImplementedError

    @classmethod
    def schedule(cls, **kwargs):
        def _schedule():
            NotificationTask().delay(
                cls.__name__, **kwargs
            )

        connection.on_commit(_schedule)

    def load_post(self, pk):
        try:
            return Post.objects.select_related(
                'user',
                'group'
            ).get(
                pk=pk
            )
        except Post.DoesNotExist:
            self.setup = False

    def load_group(self, pk):
        return Group.objects.get(
            pk=pk
        )

    def load_user(self, pk):
        return get_user_model().objects.get(
            pk=pk
        )

    def is_muted_group(self):
        return self.group.member_set.filter(
            user=self.target,
            mute=False
        ).first() is None

    def is_ready_post(self):
        return self.post.state == self.post.state_choices.READY

    def check_condition(self):
        return True

    def check_setup(self):
        return self.setup

    def check_threshold(self):
        return True

    def get_meta(self):
        raise NotImplementedError

    def get_message(self):
        raise NotImplementedError

    def get_message_kwargs(self):
        raise NotImplementedError

    def get_devices(self, users):
        devices = Device.objects.filter(
            user__in=users
        )

        return devices

    def get_token_map(self, devices):
        token_map = {
            Device.vendor_choices.IOS: {},
            Device.vendor_choices.ANDROID: {}
        }

        for code, title in settings.LANGUAGES:
            token_map[Device.vendor_choices.IOS][code.lower()] = []
            token_map[Device.vendor_choices.ANDROID][code.lower()] = []

        for device in devices:
            token_map[device.vendor][device.locale.lower()].append(
                device.token
            )

        return token_map

    def format_message(self):
        return self.get_message().format(
            **self.get_message_kwargs()
        )

    def get_ios_push(self):
        return {
            'badge': settings.YAGA_PUSH_BADGE,
            'sound': settings.YAGA_PUSH_SOUND,
            'meta': self.get_meta(),
            'alert': self.format_message()
        }

    def get_android_message(self):
        raise NotImplementedError

    def notify(self):
        if (
            self.check_setup()
            and
            self.check_condition()
            and
            self.check_threshold()
        ):
            token_map = self.get_token_map(
                self.get_devices(
                    self.get_receivers()
                )
            )

            for code, title in settings.LANGUAGES:
                with override(code.lower()):
                    ios_receivers = token_map[
                        Device.vendor_choices.IOS
                    ][code.lower()]

                    if ios_receivers:
                        apns_provider.schedule(
                            ios_receivers,
                            **self.get_ios_push()
                        )

                    # android_receivers = token_map[
                    #     Device.vendor_choices.ANDROID
                    # ][code.lower()]

                    # if android_receivers:
                    #     gcm_provider.schedule(
                    #         android_receivers,
                    #         **self.get_android_notification_kwargs()
                    #     )


class DirectNotification(
    Notification
):
    def get_receivers(self):
        return [self.target]


class GroupNotification(
    Notification
):
    def get_exclude(self):
        return {
            'user': self.emitter
        }

    def get_receivers(self):
        members = self.group.member_set.select_related(
            'user'
        ).filter(
            status=Member.status_choices.MEMBER,
            mute=False
        ).exclude(
            **self.get_exclude()
        )

        return [member.user for member in members]


class PostGroupNotification(
    GroupNotification
):
    def check_condition(self):
        return self.is_ready_post()

    def __init__(self, **kwargs):
        self.post = self.load_post(kwargs['post'])

        if self.post:
            self.group = self.post.group
            self.emitter = self.post.user

    def check_threshold(self):
        previous_post = Post.objects.filter(
            user=self.emitter,
            group=self.group,
            state=Post.state_choices.READY
        ).exclude(
            pk=self.post.pk
        ).order_by(
            '-ready_at'
        ).first()

        if previous_post is not None:
            return (
                self.post.ready_at - settings.YAGA_PUSH_POST_WINDOW
                >
                previous_post.ready_at
            )
        else:
            return True

    def get_caption(self):
        if (
            self.post.name
            and
            self.post.namer == self.emitter
        ):
            return _(' with caption "{caption}"').format(
                caption=self.post.name
            )
        else:
            return ''

    def get_meta(self):
        return {
            'event': 'post',
            'post_id': str(self.post.pk),
            'group_id': str(self.group.pk)
        }

    def get_message(self):
        return _('{emitter} posted into {group}{caption}')

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'emitter': self.emitter.get_username(),
            'caption': self.get_caption()
        }


class InviteDirectNotification(
    DirectNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.target = self.load_user(kwargs['target'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'invite',
            'group_id': str(self.group.pk)
        }

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'emitter': self.emitter.get_username()
        }

    def get_message(self):
        return _('{emitter} has added you to {group}')


class LikeDirectNotification(
    DirectNotification
):
    def check_condition(self):
        return (
            not self.is_muted_group()
            and
            self.is_ready_post()
        )

    def __init__(self, **kwargs):
        self.post = self.load_post(kwargs['post'])

        if self.post:
            self.group = self.post.group
            self.target = self.post.user
            self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'like',
            'post_id': str(self.post.pk),
            'group_id': str(self.group.pk),
        }

    def get_message_kwargs(self):
        return {
            'emitter': self.emitter.get_username(),
            'group': self.group.name,
        }

    def get_message(self):
        return _('{emitter} liked your video in {group}')


class LeftGroupNotification(
    GroupNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'leave',
            'user_id': str(self.emitter.pk),
            'group_id': str(self.group.pk),
        }

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'emitter': self.emitter.get_username(),
        }

    def get_message(self):
        return _('{emitter} has left {group}')


class KickGroupNotification(
    GroupNotification
):
    def check_condition(self):
        return self.target.name is not None

    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.target = self.load_user(kwargs['target'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'kick',
            'user_id': str(self.target.pk),
            'group_id': str(self.group.pk),
        }

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'target': self.target.get_username(),
            'emitter': self.emitter.get_username()
        }

    def get_message(self):
        return _('{emitter} removed {target} from {group}')


class RejectGroupNotification(
    GroupNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.target = self.load_user(kwargs['target'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'reject',
            'user_id': str(self.target.pk),
            'group_id': str(self.group.pk),
        }

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'target': self.target.get_username(),
            'emitter': self.emitter.get_username()
        }

    def get_message(self):
        return _('{emitter} rejected {target} request to join {group}')


class KickDirectNotification(
    DirectNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.target = self.load_user(kwargs['target'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'kick',
            'user_id': str(self.target.pk),
            'group_id': str(self.group.pk),
        }

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'emitter': self.emitter.get_username()
        }

    def get_message(self):
        return _('{emitter} has removed you from {group}')


class RejectDirectNotification(
    DirectNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.target = self.load_user(kwargs['target'])
        self.emitter = self.load_user(kwargs['emitter'])

    def get_meta(self):
        return {
            'event': 'reject',
            'user_id': str(self.target.pk),
            'group_id': str(self.group.pk),
        }

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'emitter': self.emitter.get_username()
        }

    def get_message(self):
        return _('{emitter} has rejected your request to join {group}')


class RequestGroupNotification(
    GroupNotification
):
    def __init__(self, **kwargs):
        self.target = self.emitter = self.load_user(kwargs['emitter'])
        self.group = self.load_group(kwargs['group'])

    def get_meta(self):
        return {
            'event': 'request',
            'user_id': str(self.target.pk),
            'group_id': str(self.group.pk)
        }

    def get_message(self):
        return _('{emitter} requested to join {group}')

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'emitter': self.emitter.get_username(),
        }


class FollowGroupNotification(
    GroupNotification
):
    def __init__(self, **kwargs):
        self.target = self.emitter = self.load_user(kwargs['emitter'])
        self.group = self.load_group(kwargs['group'])

    def get_meta(self):
        return {
            'event': 'request',
            'user_id': str(self.target.pk),
            'group_id': str(self.group.pk)
        }

    def get_message(self):
        return _('{emitter} followed {group}')

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'emitter': self.emitter.get_username(),
        }


class RenameGroupNotification(
    GroupNotification
):
    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.emitter = self.load_user(kwargs['emitter'])

        self.old_name = kwargs['old_name']
        self.new_name = kwargs['new_name']

    def get_meta(self):
        return {
            'event': 'rename',
            'group_id': str(self.group.pk),
        }

    def get_message_kwargs(self):
        return {
            'emitter': self.emitter.get_username(),
            'old_name': self.old_name,
            'new_name': self.new_name
        }

    def get_message(self):
        return _('{emitter} renamed {old_name} to {new_name}')


class MembersGroupNotification(
    GroupNotification
):
    def check_condition(self):
        return bool(self.targets)

    def __init__(self, **kwargs):
        self.group = self.load_group(kwargs['group'])
        self.targets = self.load_users(kwargs['targets'])
        self.emitter = self.load_user(kwargs['emitter'])

    def load_users(self, pks):
        return list(get_user_model().objects.filter(
            pk__in=pks
        ).exclude(
            name=None
        ))

    def get_usernames(self, users):
        return [user.get_username() for user in users]

    def get_targets_string(self):
        if len(self.targets) == 1:
            return self.targets[0].get_username()
        elif (
            settings.YAGA_PUSH_NEW_MEMBERS_LIMIT
            >=
            len(self.targets)
        ):
            users = self.get_usernames(self.targets)

            return _('{list} and {last}').format(
                list=', '.join(users[:-1]),
                last=users[-1]
            )
        else:
            users = self.get_usernames(
                self.targets[:settings.YAGA_PUSH_NEW_MEMBERS_LIMIT - 1]
            )

            count = (
                len(self.targets)
                -
                settings.YAGA_PUSH_NEW_MEMBERS_LIMIT
            ) + 1

            return ungettext(
                '{list} and {count} other',
                '{list} and {count} others',
                count
            ).format(
                list=', '.join(users),
                count=count
            )

    def get_exclude(self):
        return {
            'user__in': list(set(
                [self.emitter] + self.targets
            ))
        }

    def get_meta(self):
        return {
            'event': 'members',
            'group_id': str(self.group.pk)
        }

    def get_message_kwargs(self):
        return {
            'group': self.group.name,
            'targets': self.get_targets_string(),
            'emitter': self.emitter.get_username()
        }

    def get_message(self):
        return _('{emitter} added {targets} to {group}')


class JoinGroupNotification(
    GroupNotification
):
    def __init__(self, **kwargs):
        self.emitter = self.load_user(kwargs['emitter'])
        self.groups = self.load_groups(self.emitter)
        self.users = self.load_users(self.groups)

    def load_groups(self, user):
        return [member.group for member in user.member_set.select_related(
            'group'
        )]

    def load_users(self, groups):
        return [member.user for member in Member.objects.select_related(
            'user'
        ).filter(
            group__in=groups
        ).distinct('user')]

    def notify(self):
        self.get_message = lambda: _('{emitter} joined {instance}')

        for group in self.groups:
            self.group = group

            self.get_meta = lambda: {
                'event': 'join',
                'user_id': str(self.emitter.pk),
                'group_id': str(self.group.pk),
            }

            self.get_message_kwargs = lambda: {
                'emitter': self.emitter.get_username(),
                'instance': self.group.name,
            }

            super(JoinGroupNotification, self).notify()

        self.get_receivers = lambda: [
            contact.user for contact in Contact.objects.select_related(
                'user'
            ).filter(
                phones__contains=[self.emitter.phone.as_e164],
            ).exclude(
                user__in=self.users
            )
        ]

        self.get_meta = lambda: {
            'event': 'registration',
            'user_id': str(self.emitter.pk)
        }

        self.get_message_kwargs = lambda: {
            'emitter': self.emitter.get_username(),
            'instance': 'Yaga'
        }

        super(JoinGroupNotification, self).notify()


# class CopyFinishedNotification(
#     Notification
# ):
#     def __init__(self, **kwargs):
#         parent = self.load_post(kwargs['parent'])
#         1 / 0


class FirebaseNotification(
    Notification
):
    def check_condition(self):
        if self.type == 'direct':
            return self.target != self.emitter
        else:
            return True

    def __init__(self, **kwargs):
        self.post = self.load_post(kwargs['post'])
        self.emitter = self.load_user(kwargs['emitter'])
        self.group = self.post.group
        self.target = self.post.user

        self.type = kwargs['type']
        self.message = kwargs['message']
        self.event = kwargs['event']

        if self.type == 'list':
            self.targets = self.load_users(kwargs['targets'])
        elif self.type == 'direct':
            self.targets = [self.target]

    def load_user(self, name):
        return get_user_model().objects.get(
            name=name
        )

    def load_users(self, names):
        return list(get_user_model().objects.filter(
            name__in=names
        ).exclude(
            pk=self.target.pk
        ))

    def get_receivers(self):
        members = self.group.member_set.select_related(
            'user'
        ).filter(
            user__in=self.targets,
            status=Member.status_choices.MEMBER,
            mute=False
        )

        return [member.user for member in members]

    def get_meta(self):
        return {
            'event': self.event,
            'group_id': str(self.group.pk),
            'post_id': str(self.post.pk),
        }

    def get_message_kwargs(self):
        return {
            'emitter': self.emitter.get_username(),
            'target': self.target.get_username(),
        }

    def get_message(self):
        return _(self.message)


class ApprovedDirectNotification(
    DirectNotification
):
    def __init__(self, **kwargs):
        self.post = self.load_post(kwargs['post'])

        if self.post:
            self.target = self.post.user
            self.group = self.post.group

    def get_meta(self):
        return {
            'event': 'approve',
            'post_id': str(self.post.pk),
            'group_id': str(self.group.pk)
        }

    def get_message_kwargs(self):
        return {
            'group': self.group.name
        }

    def get_message(self):
        return _('Your post in {group} has been approved')


from .tasks import NotificationTask  # noqa # isort:skip
