from .base_bot_command import BaseBotCommand

class Command(BaseBotCommand):
    help = 'Enable multiple bots'
    enable = True
    single = False

    def add_arguments(self, parser):
        parser.add_argument(
            'usernames',
            nargs='*',
            type=str,
            help='Usernames of the bots to enable'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Enable all bots'
        )